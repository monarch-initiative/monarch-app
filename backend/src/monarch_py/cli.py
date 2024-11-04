import importlib
import importlib.util
from pathlib import Path
from typing import Annotated, List, Optional

import typer

from monarch_py import solr_cli, sql_cli
from monarch_py.api.config import semsimian
from monarch_py.api.additional_models import SemsimMetric
from monarch_py.datamodels.category_enums import (
    AssociationCategory,
    AssociationPredicate,
    EntityCategory,
    MappingPredicate,
)
from monarch_py.utils.solr_cli_utils import check_for_docker
from monarch_py.utils.utils import (
    set_log_level,
    get_release_metadata,
    get_release_versions,
)
from monarch_py.utils.format_utils import format_output
from monarch_py.utils import cli_fields as fields


app = typer.Typer()
app.add_typer(solr_cli.solr_app, name="solr")
app.add_typer(sql_cli.sql_app, name="sql")


@app.callback(invoke_without_command=True)
def callback(
    ctx: typer.Context,
    version: Annotated[
        Optional[bool],
        typer.Option(
            "--version",
            "-v",
            help="Show the currently installed version",
            is_eager=True,
        ),
    ] = None,
    quiet: Annotated[
        bool,
        typer.Option(
            "--quiet",
            "-q",
            help="Set log level to warning",
        ),
    ] = False,
    debug: Annotated[
        bool,
        typer.Option(
            "--debug",
            "-d",
            help="Set log level to debug",
        ),
    ] = False,
    # verbose: Annotated[int, typer.Option("--verbose", "-v", count=True)] = 0,
):
    if version and ctx.invoked_subcommand is None:
        from monarch_py import __version__

        typer.echo(f"monarch_py version: {__version__}")
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        typer.secho(
            f"\n\tNo command specified\n\tTry `monarch --help` for more information.\n",
            fg=typer.colors.YELLOW,
        )
        raise typer.Exit()
    if ctx.invoked_subcommand != "compare":
        check_for_docker()
    set_log_level(log_level="DEBUG" if debug else "WARNING" if quiet else "INFO")
    return


@app.command("test")
def test():
    """Test the CLI"""
    typer.secho("\n\tTesting monarch_py CLI\n", fg=typer.colors.GREEN)


@app.command("schema")
def schema():
    """
    Print the linkml schema for the data model
    """
    schema_name = "model"
    import_path = f"monarch_py.datamodels.{schema_name}"
    schema_module_spec = importlib.util.find_spec(
        f"monarch_py.datamodels.{schema_name}"
    )
    if schema_module_spec is None or schema_module_spec.origin is None:
        print(f"No python module found at {import_path}")
        raise typer.Exit(code=1)
    schema_dir = Path(schema_module_spec.origin).parent
    schema_path = schema_dir / f"{schema_name}.yaml"
    with open(schema_path, "r") as schema_file:
        print(schema_file.read())
    raise typer.Exit()


### "Aliases" for Solr CLI ###


@app.command("entity")
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
    solr_cli.entity(**locals())


@app.command("associations")
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
    solr_cli.associations(**locals())


@app.command("multi-entity-associations")
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
        typer.Option(
            "--counterpart-category",
            "-c",
        ),
    ] = None,
    limit: fields.LimitOption = 20,
    offset: fields.OffsetOption = 0,
    fmt: fields.FormatOption = fields.OutputFormat.json,
    output: fields.OutputOption = None,
):
    """
    Paginate through associations for multiple entities
    """
    solr_cli.multi_entity_associations(**locals())


@app.command("search")
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
    solr_cli.search(**locals())


@app.command("autocomplete")
def autocomplete(
    q: Annotated[str, typer.Argument(help="Query string to autocomplete against")],
    fmt: fields.FormatOption = fields.OutputFormat.json,
    output: fields.OutputOption = None,
):
    """
    Return entity autcomplete matches for a query string
    """
    solr_cli.autocomplete(**locals())


@app.command("histopheno")
def histopheno(
    subject: Annotated[str, typer.Argument(help="The subject of the association")],
    fmt: fields.FormatOption = fields.OutputFormat.json,
    output: fields.OutputOption = None,
):
    """
    Retrieve the histopheno data for an entity by ID
    """
    solr_cli.histopheno(**locals())


@app.command("association-counts")
def association_counts(
    entity: Annotated[
        str, typer.Argument(help="The entity to get association counts for")
    ],
    fmt: fields.FormatOption = fields.OutputFormat.json,
    output: fields.OutputOption = None,
):
    """
    Retrieve association counts for an entity by ID
    """
    solr_cli.association_counts(**locals())


@app.command("association-table")
def association_table(
    entity: Annotated[
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
    fmt: fields.FormatOption = fields.OutputFormat.json,
    output: fields.OutputOption = None,
):
    solr_cli.association_table(**locals())


### CLI Commands for Semsimian ###


@app.command("compare")
def compare(
    subjects: Annotated[
        str,
        typer.Argument(
            help="Comma separated list of subjects to compare",
        ),
    ],
    objects: Annotated[
        str,
        typer.Argument(
            help="Comma separated list of objects to compare",
        ),
    ],
    metric: Annotated[
        SemsimMetric,
        typer.Option(
            "--metric",
            "-m",
            help="The metric to use for comparison",
        ),
    ] = SemsimMetric.ANCESTOR_INFORMATION_CONTENT,
    fmt: fields.FormatOption = fields.OutputFormat.json,
    output: fields.OutputOption = None,
):
    """Compare two sets of phenotypes using semantic similarity via SemSimian"""
    subjects_list = subjects.split(",")
    objects_list = objects.split(",")
    response = semsimian().compare(subjects_list, objects_list, metric)
    format_output(fmt, response, output)


### Misc CLI Commands ###


@app.command("mappings")
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
    solr_cli.mappings(**locals())


### CLI Commands for Release Info ###


@app.command("releases")
def releases(
    dev: Annotated[
        bool,
        typer.Option(
            "--dev",
            help="Get dev releases of the KG (default is False)",
        ),
    ] = False,
    limit: fields.LimitOption = 0,
):
    """
    List all available releases of the Monarch Knowledge Graph
    """
    get_release_versions(dev, limit, print_info=True)


@app.command("release")
def release(
    release_ver: str = typer.Argument(
        help="The release version to get metadata for"
    ),
    fmt: fields.FormatOption = fields.OutputFormat.json,
    output: fields.OutputOption = None,
):
    """
    Retrieve metadata for a specific release
    """
    release_info = get_release_metadata(release_ver)
    format_output(fmt, release_info, output)


if __name__ == "__main__":
    app()
