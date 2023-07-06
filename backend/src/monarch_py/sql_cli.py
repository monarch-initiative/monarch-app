from typing import List

import typer
from monarch_py.implementations.sql.sql_implementation import SQLImplementation
from monarch_py.utils.utils import console, format_output, set_log_level
from typing_extensions import Annotated

sql_app = typer.Typer()
app_state = {"log_level": "WARNING"}


@sql_app.callback(invoke_without_command=True)
def callback(
    ctx: typer.Context,
    quiet: Annotated[bool, typer.Option("--quiet", "-q", help="Set log level to warning")] = False,
    debug: Annotated[bool, typer.Option("--debug", "-d", help="Set log level to debug")] = False,
):
    if ctx.invoked_subcommand is None:
        typer.secho(
            f"\n\tNo command specified\n\tTry `monarch sql --help` for more information.\n",
            fg=typer.colors.YELLOW,
        )
        raise typer.Exit()
    log_level = "DEBUG" if debug else "WARNING" if quiet else "INFO"
    set_log_level(log_level)


@sql_app.command()
def entity(
    id: str = typer.Argument(None, help="The identifier of the entity to be retrieved"),
    extra: bool = typer.Option(
        False,
        "--extra",
        "-e",
        help="Include extra fields in the output (association_counts and node_hierarchy)",
    ),
    update: bool = typer.Option(False, "--update", "-u", help="Whether to re-download the Monarch KG"),
    fmt: str = typer.Option(
        "json",
        "--format",
        "-f",
        help="The format of the output (json, yaml, tsv, table)",
    ),
    output: str = typer.Option(None, "--output", "-o", help="The path to the output file"),
):
    """Retrieve an entity by ID

    Args:
        id (str): The identifier of the entity to be retrieved
        update (bool): = Whether to re-download the Monarch KG. Default False
        fmt (str): The format of the output (json, yaml, tsv, table). Default JSON
        output (str): The path to the output file. Default stdout
    """
    if not id:
        console.print("\n[bold red]Entity ID required.[/]\n")
        raise typer.Exit(1)

    data = SQLImplementation()
    response = data.get_entity(id, update, extra)

    if not response:
        console.print(f"\nEntity '{id}' not found.\n")
        raise typer.Exit(1)
    format_output(fmt, response, output)


@sql_app.command()
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
    """Paginate through associations

    Args:
        category: A comma-separated list of categories
        subject: A comma-separated list of subjects
        predicate: A comma-separated list of predicates
        object: A comma-separated list of objects
        entity: A comma-separated list of entities
        limit: The number of associations to return
        offset: The offset of the first association to be retrieved
        fmt: The format of the output (json, yaml, tsv, table)
        output: The path to the output file (stdout if not specified)
    """
    args = locals()
    args.pop("fmt", None)
    args.pop("output", None)

    data = SQLImplementation()
    response = data.get_associations(**args)
    format_output(fmt, response, output)
