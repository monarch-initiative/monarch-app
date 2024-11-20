from enum import Enum
from typing import Annotated, Optional

import typer

# Common options

QueryOption = Annotated[
    str,
    typer.Option(
        "--query",
        "-q",
    ),
]

LimitOption = Annotated[
    int,
    typer.Option(
        "--limit",
        "-l",
        help="The number of results to return",
    ),
]

OffsetOption = Annotated[
    int,
    typer.Option(
        "--offset",
        help="The offset of the first result to be retrieved",
    ),
]


class OutputFormat(str, Enum):
    json = "json"
    yaml = "yaml"
    tsv = "tsv"
    table = "table"


FormatOption = Annotated[
    OutputFormat,
    typer.Option(
        "--format",
        "-f",
        help="The format of the output (json, yaml, tsv, table)",
    ),
]

OutputOption = Annotated[
    Optional[str],
    typer.Option(
        "--output",
        "-O",
        help="Path to file to write command output (stdout if not specified)",
    ),
]
