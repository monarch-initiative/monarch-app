import csv
import json
import sys
from typing import Union, Dict, List

import typer
import yaml
from monarch_py.datamodels.model import AssociationCountList, ConfiguredBaseModel, Entity, HistoPheno, Node, Results
from rich import print_json
from rich.console import Console
from rich.table import Table

MONARCH_DATA_URL = "https://data.monarchinitiative.org/monarch-kg-dev"
SOLR_DATA_URL = f"{MONARCH_DATA_URL}/latest/solr.tar.gz"
SQL_DATA_URL = f"{MONARCH_DATA_URL}/latest/monarch-kg.db.gz"


console = Console(
    color_system="truecolor",
    stderr=True,
    style="pink1",
)


def strip_json(doc: dict, *fields_to_remove: str):
    for field in fields_to_remove:
        try:
            del doc[field]
        except KeyError:
            pass
    return doc


def escape(value: str) -> str:
    return value.replace(":", r"\:")


def dict_factory(cursor, row):
    """Converts a sqlite3 row to a dictionary."""
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}


def compare_dicts(dict1, dict2):
    """Compare two dictionaries"""
    return all([k in dict2 for k in dict1]) and all([dict1[k] == dict2[k] for k in dict2])


def dict_diff(d1, d2):
    """Return the difference between two dictionaries"""
    difference = {}
    for k in d1.keys():
        if d1[k] != d2[k]:
            difference[f"Dict-1-{k}"] = d1[k]
            difference[f"Dict-2-{k}"] = d2[k]
    return difference


def set_log_level(log_level: str):
    """Sets the log level for the application."""
    import loguru

    loguru.logger.remove()
    loguru.logger.add(sys.stderr, level=log_level)


def get_provided_by_link(provided_by: str) -> str:
    """Returns a link to the provided_by resource."""
    pb = provided_by.replace("_nodes", "").replace("_edges", "").split("_")
    base_url = "https://monarch-initiative.github.io/monarch-ingest/Sources"
    slug = f"{pb[0]}/#{'_'.join(pb[1:])}"
    return f"{base_url}/{slug}"


### Output conversion methods ###

FMT_INPUT_ERROR_MSG = (
    "Text conversion method only accepts Entity, HistoPheno, AssociationCountList, or Results objects."
)


def get_headers_from_obj(obj: ConfiguredBaseModel) -> list:
    """Return a list of headers from a pydantic model."""
    schema = type(obj).schema()
    definitions = schema["definitions"]
    this_ref = schema["properties"]["items"]["items"]["$ref"].split("/")[-1]
    headers = definitions[this_ref]["properties"].keys()
    return list(headers)


def to_json(obj: Union[ConfiguredBaseModel, Dict, List[ConfiguredBaseModel]], file: str):
    """Converts a pydantic model to a JSON string."""
    if isinstance(obj, ConfiguredBaseModel):
        json_value = obj.json(indent=4)
    elif isinstance(obj, dict):
        json_value = json.dumps(obj, indent=4)
    elif isinstance(obj, list):
        json_value = json.dumps({"items": [o.dict() for o in obj]}, indent=4)
    if file:
        with open(file, "w") as f:
            f.write(json_value)
        console.print(f"\nOutput written to {file}\n")
    else:
        print_json(json_value)


def to_tsv(obj: ConfiguredBaseModel, file: str) -> str:
    """Converts a pydantic model to a TSV string."""

    # Extract headers and rows from object
    if isinstance(obj, Entity):
        headers = obj.dict().keys()
        rows = [list(obj.dict().values())]
    elif isinstance(obj, (AssociationCountList, HistoPheno, Results)):
        if not obj.items:
            headers = get_headers_from_obj(obj)
            rows = []
        else:
            headers = obj.items[0].dict().keys()
            rows = [list(item.dict().values()) for item in obj.items]
    else:
        console.print(f"\n[bold red]{FMT_INPUT_ERROR_MSG}[/]\n")
        raise typer.Exit(1)

    fh = open(file, "w") if file else sys.stdout
    writer = csv.writer(fh, delimiter="\t")
    writer.writerow(headers)
    for row in rows:
        writer.writerow(list(row))
    if file:
        fh.close()
        console.print(f"\nOutput written to {file}\n")

    return


def to_table(obj: ConfiguredBaseModel):
    # Extract headers and rows from object
    if isinstance(obj, Node):
        console.print(f"\n[bold red]Table output not implemented for Node objects.[/]\n")
        raise typer.Exit(1)
    elif isinstance(obj, Entity):
        headers = obj.dict().keys()
        rows = [list(obj.dict().values())]
    elif isinstance(obj, (AssociationCountList, HistoPheno, Results)):
        if not obj.items:
            headers = get_headers_from_obj(obj)
            rows = []
        else:
            headers = obj.items[0].dict().keys()
            rows = [list(item.dict().values()) for item in obj.items]
    else:
        console.print(f"\n[bold red]{FMT_INPUT_ERROR_MSG}[/]\n")
        raise typer.Exit(1)

    for row in rows:
        for i, value in enumerate(row):
            if isinstance(value, list):
                row[i] = ", ".join(value)
            elif not isinstance(value, str):
                row[i] = str(value)
    title = f"{obj.__class__.__name__}: {obj.id}" if hasattr(obj, "id") else obj.__class__.__name__
    table = Table(
        title=console.rule(title),
        show_header=True,
        header_style="bold cyan",
    )
    for header in headers:
        table.add_column(header)
    for row in rows:
        table.add_row(*row)
    console.print(table)
    return


def to_yaml(obj: ConfiguredBaseModel, file: str):
    """Converts a pydantic model to a YAML string."""

    fh = open(file, "w") if file else sys.stdout

    if isinstance(obj, Entity):
        yaml.dump(obj.dict(), fh, indent=4)
    elif isinstance(obj, Results) or isinstance(obj, HistoPheno) or isinstance(obj, AssociationCountList):
        yaml.dump([item.dict() for item in obj.items], fh, indent=4)
    else:
        console.print(f"\n[bold red]{FMT_INPUT_ERROR_MSG}[/]\n")
        raise typer.Exit(1)
    if file:
        console.print(f"\nOutput written to {file}\n")
        fh.close()

    return


def format_output(fmt: str, response: Union[ConfiguredBaseModel, Dict], output: str):
    if fmt.lower() == "json":
        to_json(response, output)
    elif fmt.lower() == "tsv":
        to_tsv(response, output)
    elif fmt.lower() == "yaml":
        to_yaml(response, output)
    elif fmt.lower() == "table":
        to_table(response)
    else:
        console.print(f"\n[bold red]Format '{fmt}' not supported.[/]\n")
        raise typer.Exit(1)
