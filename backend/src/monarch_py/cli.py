import importlib
from pathlib import Path
from typing import List, Optional

import typer
from monarch_py import solr_cli, sql_cli
from monarch_py.api.config import oak
from monarch_py.utils.solr_cli_utils import check_for_docker
from monarch_py.utils.utils import set_log_level, format_output
from typing_extensions import Annotated


app = typer.Typer()
app.add_typer(solr_cli.solr_app, name="solr")
app.add_typer(sql_cli.sql_app, name="sql")


@app.callback(invoke_without_command=True)
def callback(
    ctx: typer.Context,
    version: Annotated[
        Optional[bool], typer.Option("--version", "-v", help="Show the currently installed version", is_eager=True)
    ] = None,
    # verbose: Annotated[int, typer.Option("--verbose", "-v", count=True)] = 0,
    quiet: Annotated[bool, typer.Option("--quiet", "-q", help="Set log level to warning")] = False,
    debug: Annotated[bool, typer.Option("--debug", "-d", help="Set log level to debug")] = False,
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
    schema_dir = Path(importlib.util.find_spec(f"monarch_py.datamodels.{schema_name}").origin).parent
    schema_path = schema_dir / Path(schema_name + ".yaml")
    with open(schema_path, "r") as schema_file:
        print(schema_file.read())
    raise typer.Exit()


### "Aliases" for Solr CLI ###


@app.command("entity")
def entity(
    id: str = typer.Argument(None, help="The identifier of the entity to be retrieved"),
    extra: bool = typer.Option(
        False,
        "--extra",
        "-e",
        help="Include extra fields in the output (association_counts and node_hierarchy)",
    ),
    fmt: str = typer.Option(
        "json",
        "--format",
        "-f",
        help="The format of the output (json, yaml, tsv, table)",
    ),
    output: str = typer.Option(None, "--output", "-o", help="The path to the output file"),
):
    """
    Retrieve an entity by ID

    Args:
        id: The identifier of the entity to be retrieved
        fmt: The format of the output (json, yaml, tsv, table)
        output: The path to the output file (stdout if not specified)

    """
    solr_cli.entity(**locals())


@app.command("associations")
def associations(
    category: List[str] = typer.Option(None, "--category", "-c", help="Comma-separated list of categories"),
    subject: List[str] = typer.Option(None, "--subject", "-s", help="Comma-separated list of subjects"),
    predicate: List[str] = typer.Option(None, "--predicate", "-p", help="Comma-separated list of predicates"),
    object: List[str] = typer.Option(None, "--object", "-o", help="Comma-separated list of objects"),
    entity: List[str] = typer.Option(None, "--entity", "-e", help="Comma-separated list of entities"),
    direct: bool = typer.Option(
        False,
        "--direct",
        "-d",
        help="Whether to exclude associations with subject/object as ancestors",
    ),
    limit: int = typer.Option(20, "--limit", "-l", help="The number of associations to return"),
    offset: int = typer.Option(0, "--offset", help="The offset of the first association to be retrieved"),
    fmt: str = typer.Option(
        "json",
        "--format",
        "-f",
        help="The format of the output (json, yaml, tsv, table)",
    ),
    output: str = typer.Option(None, "--output", "-o", help="The path to the output file"),
):
    """
    Paginate through associations

    Args:
        category: A comma-separated list of categories
        subject: A comma-separated list of subjects
        predicate: A comma-separated list of predicates
        object: A comma-separated list of objects
        entity: A comma-separated list of entities
        limit: The number of associations to return
        direct: Whether to exclude associations with subject/object as ancestors
        offset: The offset of the first association to be retrieved
        fmt: The format of the output (json, yaml, tsv, table)
        output: The path to the output file (stdout if not specified)
    """
    solr_cli.associations(**locals())


@app.command("search")
def search(
    q: str = typer.Option(None, "--query", "-q"),
    category: List[str] = typer.Option(None, "--category", "-c"),
    in_taxon_label: str = typer.Option(None, "--in-taxon-label", "-t"),
    facet_fields: List[str] = typer.Option(None, "--facet-fields", "-ff"),
    facet_queries: List[str] = typer.Option(None, "--facet-queries"),
    limit: int = typer.Option(20, "--limit", "-l"),
    offset: int = typer.Option(0, "--offset"),
    fmt: str = typer.Option(
        "json",
        "--format",
        "-f",
        help="The format of the output (json, yaml, tsv, table)",
    ),
    output: str = typer.Option(None, "--output", "-o", help="The path to the output file"),
    # sort: str = typer.Option(None, "--sort", "-s"),
):
    """
    Search for entities

    Args:
        q: The query string to search for
        category: The category of the entity
        in_taxon_label: The taxon label to filter by
        limit: The number of entities to return
        offset: The offset of the first entity to be retrieved
        fmt: The format of the output (json, yaml, tsv, table)
        output: The path to the output file (stdout if not specified)
    """
    solr_cli.search(**locals())


@app.command("autocomplete")
def autocomplete(
    q: str = typer.Argument(None, help="Query string to autocomplete against"),
    fmt: str = typer.Option(
        "json",
        "--format",
        "-f",
        help="The format of the output (json, yaml, tsv, table)",
    ),
    output: str = typer.Option(None, "--output", "-o", help="The path to the output file"),
):
    """
    Return entity autcomplete matches for a query string

    Args:
        q: The query string to autocomplete against
        fmt: The format of the output (json, yaml, tsv, table)
        output: The path to the output file (stdout if not specified)

    """
    solr_cli.autocomplete(**locals())


@app.command("histopheno")
def histopheno(
    subject: str = typer.Argument(None, help="The subject of the association"),
    fmt: str = typer.Option(
        "json",
        "--format",
        "-f",
        help="The format of the output (json, yaml, tsv, table)",
    ),
    output: str = typer.Option(None, "--output", "-o", help="The path to the output file"),
):
    """
    Retrieve the histopheno data for an entity by ID

    Args:
        subject: The subject of the association

    Optional Args:
        fmt (str): The format of the output (json, yaml, tsv, table). Default JSON
        output (str): The path to the output file. Default stdout
    """
    solr_cli.histopheno(**locals())


@app.command("association-counts")
def association_counts(
    entity: str = typer.Argument(None, help="The entity to get association counts for"),
    fmt: str = typer.Option(
        "json",
        "--format",
        "-f",
        help="The format of the output (json, yaml, tsv, table)",
    ),
    output: str = typer.Option(None, "--output", "-o", help="The path to the output file"),
):
    """
    Retrieve association counts for an entity by ID

    Args:
        entity: The entity to get association counts for
        fmt: The format of the output (json, yaml, tsv, table). Default JSON
        output: The path to the output file. Default stdout

    Returns:
        A list of association counts for the given entity containing association type, label and count
    """
    solr_cli.association_counts(**locals())


@app.command("association-table")
def association_table(
    entity: str = typer.Argument(..., help="The entity to get associations for"),
    category: str = typer.Argument(
        ...,
        help="The association category to get associations for, ex. biolink:GeneToPhenotypicFeatureAssociation",
    ),
    q: str = typer.Option(None, "--query", "-q"),
    limit: int = typer.Option(5, "--limit", "-l"),
    offset: int = typer.Option(0, "--offset"),
    fmt: str = typer.Option(
        "json",
        "--format",
        "-f",
        help="The format of the output (json, yaml, tsv, table)",
    ),
    output: str = typer.Option(None, "--output", "-o", help="The path to the output file"),
):
    solr_cli.association_table(**locals())


@app.command("compare")
def compare(
    subjects: str = typer.Argument(..., help="Comma separated list of subjects to compare"),
    objects: str = typer.Argument(..., help="Comma separated list of objects to compare"),
    fmt: str = typer.Option(
        "json",
        "--format",
        "-f",
        help="The format of the output (json, yaml, tsv, table)",
    ),
    output: str = typer.Option(None, "--output", "-o", help="The path to the output file"),
):
    """Compare two entities using semantic similarity via OAK"""
    subjects = subjects.split(",")
    objects = objects.split(",")
    response = oak().compare(subjects, objects)
    format_output(fmt, response, output)


@app.command("multi-entity-associations")
def multi_entity_associations(
    entity: List[str] = typer.Option(None, "--entity", "-e", help="Comma-separated list of entities"),
    counterpart_category: List[str] = typer.Option(None, "--counterpart-category", "-c"),
    limit: int = typer.Option(20, "--limit", "-l"),
    offset: int = typer.Option(0, "--offset"),
    fmt: str = typer.Option(
        "json",
        "--format",
        "-f",
        help="The format of the output (json, yaml, tsv, table)",
    ),
    output: str = typer.Option(None, "--output", "-o", help="The path to the output file"),
):
    """
    Paginate through associations for multiple entities

    Args:
        entity: A comma-separated list of entities
        counterpart_category: A comma-separated list of counterpart categories
        limit: The number of associations to return
        offset: The offset of the first association to be retrieved
        fmt: The format of the output (json, yaml, tsv, table)
        output: The path to the output file (stdout if not specified)
    """
    solr_cli.multi_entity_associations(**locals())


if __name__ == "__main__":
    app()
