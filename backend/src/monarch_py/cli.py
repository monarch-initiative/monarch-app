import importlib
import importlib.util
from pathlib import Path
from typing import Annotated, Optional

import typer

from monarch_py import solr_cli, sql_cli
from monarch_py.api.config import semsimian
from monarch_py.api.additional_models import SemsimMetric
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
    schema_module_spec = importlib.util.find_spec(f"monarch_py.datamodels.{schema_name}")
    if schema_module_spec is None or schema_module_spec.origin is None:
        print(f"No python module found at {import_path}")
        raise typer.Exit(code=1)
    schema_dir = Path(schema_module_spec.origin).parent
    schema_path = schema_dir / f"{schema_name}.yaml"
    with open(schema_path, "r") as schema_file:
        print(schema_file.read())
    raise typer.Exit()


### "Aliases" for Solr CLI ###


app.command("entity")(solr_cli.entity)
app.command("associations")(solr_cli.associations)
app.command("multi-entity-associations")(solr_cli.multi_entity_associations)
app.command("search")(solr_cli.search)
app.command("autocomplete")(solr_cli.autocomplete)
app.command("histopheno")(solr_cli.histopheno)
app.command("association-counts")(solr_cli.association_counts)
app.command("association-table")(solr_cli.association_table)
app.command("mappings")(solr_cli.mappings)


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
    release_ver: str = typer.Argument(help="The release version to get metadata for"),
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
