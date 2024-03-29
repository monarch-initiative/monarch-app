from typing import List
from typing_extensions import Annotated

import typer

from monarch_py.datamodels.category_enums import (
    AssociationCategory,
    AssociationPredicate,
)
from monarch_py.implementations.sql.sql_implementation import SQLImplementation
from monarch_py.utils.utils import console, set_log_level
from monarch_py.utils.format_utils import format_output

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
    category: List[AssociationCategory] = typer.Option(
        None, "--category", "-c", help="Category to get associations for"
    ),
    subject: List[str] = typer.Option(None, "--subject", "-s", help="Subject ID to get associations for"),
    predicate: List[AssociationPredicate] = typer.Option(
        None, "--predicate", "-p", help="Predicate ID to get associations for"
    ),
    object: List[str] = typer.Option(None, "--object", "-o", help="Object ID to get associations for"),
    entity: List[str] = typer.Option(
        None, "--entity", "-e", help="Entity (subject or object) ID to get associations for"
    ),
    direct: bool = typer.Option(
        False,
        "--direct",
        "-d",
        help="Whether to exclude associations with subject/object as ancestors",
    ),
    compact: bool = typer.Option(
        False,
        "--compact",
        "-C",
        help="Whether to return a compact representation of the associations",
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
        direct: Whether to exclude associations with subject/object as ancestors
        compact: Whether to return a compact representation of the associations
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
