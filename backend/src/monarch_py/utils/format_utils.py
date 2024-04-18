import sys
import json
import yaml
from typing import Dict, List, Tuple, Union

import typer
from rich import print_json
from rich.table import Table

from monarch_py.datamodels.model import (
    AssociationCountList,
    ConfiguredBaseModel,
    Entity,
    HistoPheno,
    Node,
    Release,
    Results,
)
from monarch_py.utils.utils import console

FMT_INPUT_ERROR_MSG = """Text conversion method only accepts the following object types:
    Entity
    HistoPheno
    AssociationCountList
    Release
    Results
"""
# VALID_MODELS = [Entity, HistoPheno, AssociationCountList, Release, Results]


### Converters ###


def get_headers_from_obj(obj: ConfiguredBaseModel) -> list:
    """Return a list of headers from a pydantic model."""
    if isinstance(obj, Entity):
        headers = obj.model_dump().keys()
    elif isinstance(obj, (AssociationCountList, HistoPheno, Results)):
        if obj.items:
            headers = obj.items[0].model_dump().keys()
        else:
            schema = type(obj).model_json_schema()
            definitions = schema["definitions"]
            this_ref = schema["properties"]["items"]["items"]["$ref"].split("/")[-1]
            headers = definitions[this_ref]["properties"].keys()
    else:
        console.print(f"\n[bold red]{FMT_INPUT_ERROR_MSG}[/]")
        raise typer.Exit(1)
    return list(headers)


def get_headers_and_rows(obj: ConfiguredBaseModel) -> Tuple[str, str]:
    """Converts a pydantic model to a TSV string."""
    if isinstance(obj, (Entity, Release)):
        headers = obj.model_dump().keys()
        rows = [list(obj.model_dump().values())]
    elif isinstance(obj, (AssociationCountList, HistoPheno, Results)):
        if not obj.items:
            headers = get_headers_from_obj(obj)
            rows = []
        else:
            headers = obj.items[0].model_dump().keys()
            rows = [list(item.model_dump().values()) for item in obj.items]
    else:
        console.print(f"\n[bold red]{FMT_INPUT_ERROR_MSG}[/]")
        raise typer.Exit(1)
    return headers, rows


### Printers/writers ###


def to_json(
    obj: Union[ConfiguredBaseModel, Dict, List[ConfiguredBaseModel]], file: str = None, print_output: bool = True
) -> str:
    """Converts a pydantic model to a JSON string."""
    if isinstance(obj, ConfiguredBaseModel):
        json_value = obj.model_dump_json(indent=4)
    elif isinstance(obj, dict):
        json_value = json.dumps(obj, indent=4)
    elif isinstance(obj, list):
        # json_value = json.dumps({"items": [o.model_dump_json() for o in obj]}, indent=4)
        json_value = json.dumps([json.loads(o.model_dump_json(indent=4)) for o in obj])
    if file:
        with open(file, "w") as f:
            f.write(json_value)
        console.print(f"\nOutput written to {file}\n")
    elif print_output and not file:
        print_json(json_value)
    return json_value


def to_tsv(obj: ConfiguredBaseModel, file: str = None, print_output: bool = True) -> str:
    """Prints or writes a pydantic model to a TSV file/stdout."""
    headers, rows = get_headers_and_rows(obj)
    tsv = ""
    tsv += "\t".join(headers)
    for row in rows:
        row = "\t".join([str(r) for r in row])
        tsv += f"\n{row}"
    if file:
        with open(file, "w") as f:
            f.write(tsv)
        console.print(f"\nOutput written to {file}\n")
    elif print_output:
        console.print(tsv)
    return tsv


def to_table(obj: ConfiguredBaseModel, print_output: bool = True) -> Table:
    """Prints a pydantic model as a rich Table."""
    if isinstance(obj, Node):
        console.print(f"\n[bold red]Table output not implemented for Node objects.[/]\n")
        raise typer.Exit(1)
    headers, rows = get_headers_and_rows(obj)
    for row in rows:
        for i, value in enumerate(row):
            if isinstance(value, list) and all(isinstance(v, str) for v in value):
                row[i] = ", ".join(value)
            elif not isinstance(value, str):
                row[i] = str(value)
            else:
                row[i] = value
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
    if print_output:
        console.print(table)
    return table


def to_yaml(obj: ConfiguredBaseModel, file: str = None, print_output: bool = True) -> Union[Dict, List[Dict]]:
    """Converts a pydantic model to a YAML string."""
    if isinstance(obj, (Entity, Release)):
        o = obj.model_dump()
    elif isinstance(obj, (Results, HistoPheno, AssociationCountList)):
        o = [item.model_dump() for item in obj.items]
    else:
        console.print(f"\n[bold red]{FMT_INPUT_ERROR_MSG}[/]\n")
        raise typer.Exit(1)
    if file:
        fh = open(file, "w")
        yaml.dump(o, fh, indent=4)
        console.print(f"\nOutput written to {file}\n")
        fh.close()
    elif print_output and not file:
        yaml.dump(o, sys.stdout, indent=4)
    return yaml.dump(o)


def format_output(fmt: str, response: Union[ConfiguredBaseModel, Dict], output: str = None):
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
