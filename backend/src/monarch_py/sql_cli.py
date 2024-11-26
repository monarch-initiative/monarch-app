from typing import List, Optional
from typing_extensions import Annotated

import typer

from monarch_py.datamodels.category_enums import (
    AssociationCategory,
    AssociationPredicate,
)
from monarch_py.implementations.sql.sql_implementation import SQLImplementation
from monarch_py.utils.utils import console, set_log_level
from monarch_py.utils.format_utils import format_output
from monarch_py.utils import cli_fields as fields

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
    ],
    update: Annotated[
        bool,
        typer.Option(
            "--update",
            "-u",
            help="Whether to re-download the Monarch KG",
        ),
    ],
    fmt: fields.FormatOption = fields.OutputFormat.json,
    output: fields.OutputOption = None,
):
    """Retrieve an entity by ID"""
    data = SQLImplementation()
    response = data.get_entity(entity_id, update, extra)

    if not response:
        console.print(f"\nEntity '{id}' not found.\n")
        raise typer.Exit(1)
    format_output(fmt, response, output)


@sql_app.command()
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
    args = locals()
    args.pop("fmt", None)
    args.pop("output", None)

    data = SQLImplementation()
    response = data.get_associations(**args)
    format_output(fmt, response, output)
