from typing import List, Optional
from typing_extensions import Annotated

import pystow
import typer

from monarch_py.datamodels.category_enums import (
    AssociationCategory,
    AssociationPredicate,
    EntityCategory,
    MappingPredicate,
)
from monarch_py.utils.solr_cli_utils import (
    ensure_solr,
    get_solr,
    solr_status,
    start_solr,
    stop_solr,
)
from monarch_py.utils.utils import console, set_log_level
from monarch_py.utils.format_utils import format_output
from monarch_py.utils import cli_fields as fields

solr_app = typer.Typer()
monarchstow = pystow.module("monarch")


@solr_app.callback(invoke_without_command=True)
def callback(
    ctx: typer.Context,
    quiet: Annotated[bool, typer.Option("--quiet", "-q", help="Set log level to warning")] = False,
    debug: Annotated[bool, typer.Option("--debug", "-d", help="Set log level to debug")] = False,
):
    if ctx.invoked_subcommand is None:
        typer.secho(
            f"\n\tNo command specified\n\tTry `monarch solr --help` for more information.\n",
            fg=typer.colors.YELLOW,
        )
        raise typer.Exit()
    log_level = "DEBUG" if debug else "WARNING" if quiet else "INFO"
    set_log_level(log_level)


############################
### SOLR DOCKER COMMANDS ###
############################


@solr_app.command("start")
def start(update: bool = False):
    """Starts a local Solr container."""
    ensure_solr(overwrite=False)
    start_solr()


@solr_app.command("stop")
def stop():
    """Stops the local Solr container."""
    stop_solr()
    raise typer.Exit()


@solr_app.command("status")
def status():
    """Checks the status of the local Solr container."""
    solr_status()
    raise typer.Exit()


@solr_app.command("download")
def download(
    version: Annotated[
        str,
        typer.Argument(
            help="The version of the Solr KG to download (latest, dev, or a specific version)",
        ),
    ] = "latest",
    overwrite: Annotated[
        bool,
        typer.Option(
            "--overwrite",
            help="Overwrite the existing Solr KG if it exists",
        ),
    ] = False,
):
    """Download the Monarch Solr KG."""
    ensure_solr(version, overwrite)
    raise typer.Exit()


###########################
### SOLR QUERY COMMANDS ###
###########################


@solr_app.command("entity")
def entity(
    entity_id: Annotated[
        str,
        typer.Argument(help="The identifier of the entity to be retrieved"),
    ],
    extra: Annotated[
        bool,
        typer.Option(
            "--extra",
            "-e",
            help="Include extra fields in the output (association_counts and node_hierarchy)",
        ),
    ] = False,
    fmt: fields.FormatOption = fields.OutputFormat.json,
    output: fields.OutputOption = None,
):
    """
    Retrieve an entity by ID
    """

    solr = get_solr(update=False)
    response = solr.get_entity(entity_id, extra)
    if response is not None:
        format_output(fmt, response, output)
    else:
        console.print(f"\n[bold red]Entity {id} not found.[/]\n")
        raise typer.Exit(1)


@solr_app.command("associations")
def associations(
    category: Annotated[
        Optional[List[AssociationCategory]],
        typer.Option(
            "--category",
            "-c",
            help="Category to get associations for",
        ),
    ] = None,
    subject: Annotated[
        Optional[List[str]],
        typer.Option(
            "--subject",
            "-s",
            help="Subject ID to get associations for",
        ),
    ] = None,
    predicate: Annotated[
        Optional[List[AssociationPredicate]],
        typer.Option(
            "--predicate",
            "-p",
            help="Predicate ID to get associations for",
        ),
    ] = None,
    object: Annotated[
        Optional[List[str]],
        typer.Option(
            "--object",
            "-o",
            help="Object ID to get associations for",
        ),
    ] = None,
    entity: Annotated[
        Optional[List[str]],
        typer.Option(
            "--entity",
            "-e",
            help="Entity (subject or object) ID to get associations for",
        ),
    ] = None,
    direct: Annotated[
        bool,
        typer.Option(
            "--direct",
            "-d",
            help="Whether to exclude associations with subject/object as ancestors",
        ),
    ] = False,
    compact: Annotated[
        bool,
        typer.Option(
            "--compact",
            "-C",
            help="Whether to return a compact representation of the associations",
        ),
    ] = False,
    limit: fields.LimitOption = 20,
    offset: fields.OffsetOption = 0,
    fmt: fields.FormatOption = fields.OutputFormat.json,
    output: fields.OutputOption = None,
):
    """
    Paginate through associations
    """
    kwargs = locals()
    kwargs.pop("fmt", None)
    kwargs.pop("output", None)

    solr = get_solr(update=False)
    response = solr.get_associations(**kwargs)
    format_output(fmt, response, output)


@solr_app.command("multi-entity-associations")
def multi_entity_associations(
    entity: Annotated[
        Optional[List[str]],
        typer.Option(
            "--entity",
            "-e",
            help="Comma-separated list of entities",
        ),
    ] = None,
    counterpart_category: Annotated[
        Optional[List[str]],
        typer.Option("--counterpart-category", "-c", help="A comma-separated list of counterpart categories"),
    ] = None,
    limit: fields.LimitOption = 20,
    offset: fields.OffsetOption = 0,
    fmt: fields.FormatOption = fields.OutputFormat.json,
    output: fields.OutputOption = None,
):
    """
    Paginate through associations for multiple entities
    """
    kwargs = locals()
    kwargs.pop("fmt", None)
    kwargs.pop("output", None)
    kwargs["limit_per_group"] = kwargs.pop("limit")

    solr = get_solr(update=False)
    response = solr.get_multi_entity_associations(**kwargs)
    format_output(fmt, response, output)


@solr_app.command("search")
def search(
    q: fields.QueryOption = ":*",
    category: Annotated[
        Optional[List[EntityCategory]],
        typer.Option("--category", "-c"),
    ] = None,
    in_taxon_label: Annotated[
        Optional[str],
        typer.Option("--in-taxon-label", "-t"),
    ] = None,
    facet_fields: Annotated[
        Optional[List[str]],
        typer.Option("--facet-fields", "-ff"),
    ] = None,
    facet_queries: Annotated[
        Optional[List[str]],
        typer.Option("--facet-queries", "-fq"),
    ] = None,
    limit: fields.LimitOption = 20,
    offset: fields.OffsetOption = 0,
    fmt: fields.FormatOption = fields.OutputFormat.json,
    output: fields.OutputOption = None,
    # sort: str = typer.Option(None, "--sort", "-s"),
):
    """
    Search for entities
    """
    kwargs = locals()
    kwargs.pop("fmt", None)
    kwargs.pop("output", None)

    solr = get_solr(update=False)
    response = solr.search(**kwargs)
    format_output(fmt, response, output)


@solr_app.command("autocomplete")
def autocomplete(
    q: Annotated[str, typer.Argument(help="Query string to autocomplete against")],
    fmt: fields.FormatOption = fields.OutputFormat.json,
    output: fields.OutputOption = None,
):
    """
    Return entity autcomplete matches for a query string
    """
    solr = get_solr(update=False)
    response = solr.autocomplete(q)
    format_output(fmt, response, output)


@solr_app.command("histopheno")
def histopheno(
    subject: Annotated[str, typer.Argument(help="The subject of the association")],
    fmt: fields.FormatOption = fields.OutputFormat.json,
    output: fields.OutputOption = None,
):
    """
    Retrieve the histopheno associations for a given subject
    """

    if not subject:
        console.print("\n[bold red]Subject ID required.[/]\n")
        raise typer.Exit(1)

    solr = get_solr(update=False)
    response = solr.get_histopheno(subject)
    format_output(fmt, response, output)


@solr_app.command("association-counts")
def association_counts(
    entity_id: Annotated[str, typer.Argument(help="The entity to get association counts for")],
    fmt: fields.FormatOption = fields.OutputFormat.json,
    output: fields.OutputOption = None,
):
    """
    Retrieve the association counts for a given entity
    """
    solr = get_solr(update=False)
    response = solr.get_association_counts(entity_id)
    format_output(fmt, response, output)


@solr_app.command("association-table")
def association_table(
    entity_id: Annotated[
        str,
        typer.Argument(
            help="The entity to get associations for",
        ),
    ],
    category: Annotated[
        AssociationCategory,
        typer.Argument(
            help="The association category to get associations for, ex. biolink:GeneToPhenotypicFeatureAssociation",
        ),
    ],
    q: Annotated[
        Optional[str],
        typer.Option("--query", "-q"),
    ] = None,
    traverse_orthologs: Annotated[
        bool,
        typer.Option(
            "--traverse-orthologs",
            "-t",
            help="Whether to traverse orthologs when getting associations",
        ),
    ] = False,
    sort: Annotated[
        Optional[List[str]],
        typer.Option("--sort", "-s"),
    ] = None,
    limit: fields.LimitOption = 20,
    offset: fields.OffsetOption = 0,
    fmt: fields.FormatOption = fields.OutputFormat.json,
    output: fields.OutputOption = None,
):
    solr = get_solr(update=False)
    response = solr.get_association_table(
        entity=entity_id,
        category=category,
        traverse_orthologs=traverse_orthologs,
        sort=sort,
        q=q,
        limit=limit,
        offset=offset,
    )
    format_output(fmt, response, output)


@solr_app.command("mappings")
def mappings(
    entity_id: Annotated[
        Optional[List[str]],
        typer.Option("--entity-id", "-e", help="entity ID to get mappings for"),
    ] = None,
    subject_id: Annotated[
        Optional[List[str]],
        typer.Option("--subject-id", "-s", help="subject ID to get mappings for"),
    ] = None,
    predicate_id: Annotated[
        Optional[List[MappingPredicate]],
        typer.Option("--predicate-id", "-p", help="predicate ID to get mappings for"),
    ] = None,
    object_id: Annotated[
        Optional[List[str]],
        typer.Option("--object-id", "-o", help="object ID to get mappings for"),
    ] = None,
    mapping_justification: Annotated[
        Optional[List[str]],
        typer.Option(
            "--mapping-justification",
            "-m",
            help="mapping justification to get mappings for",
        ),
    ] = None,
    limit: fields.LimitOption = 20,
    offset: fields.OffsetOption = 0,
    fmt: fields.FormatOption = fields.OutputFormat.json,
    output: fields.OutputOption = None,
):
    args = locals()
    args.pop("fmt", None)
    args.pop("output", None)

    solr = get_solr(update=False)
    response = solr.get_mappings(**args)
    format_output(fmt, response, output)
