import os
import shutil
import sys
import time

import docker
import pystow
import typer
from monarch_py.implementations.solr.solr_implementation import SolrImplementation
from monarch_py.utils.utils import MONARCH_DATA_URL, console

monarchstow = pystow.module("monarch")


def check_for_docker():
    try:
        docker.from_env()
    except docker.errors.DockerException:
        typer.secho(
            f"\n\tDocker not found\n\tPlease install Docker, and refer to:",
            fg=typer.colors.RED,
        )
        typer.secho(
            f"\tmonarch solr --help\n",
            fg=typer.colors.WHITE,
            bg=typer.colors.BLACK,
        )
        raise typer.Exit()


def ensure_solr(version: str = "latest", overwrite: bool = False) -> None:
    """Download and unpack the monarch solr kg, and check permissions."""
    data_path = monarchstow.base / "solr" / "data"
    # When untarred solr won't necessarily use the same file names for index segments etc
    # so the untarred path needs to be removed before updating
    if overwrite:
        shutil.rmtree(data_path, ignore_errors=True)
    monarchstow.ensure_untar(url=f"{MONARCH_DATA_URL}/{version}/solr.tar.gz", force=overwrite)
    if sys.platform in ["linux", "linux2", "darwin"]:
        stat_info = os.stat(data_path)
        if stat_info.st_gid != 8983:
            console.print(
                f"""
Solr container requires write access to {monarchstow.base}.
Please run the following command to set permissions:
    [grey84 on black]sudo chgrp -R 8983 {monarchstow.base} && \ [/]
    [grey84 on black]sudo chmod -R g+w {monarchstow.base}[/]
            """
            )
            sys.exit(1)


def check_for_solr(dc: docker.DockerClient, quiet: bool = False):
    if not quiet:
        console.print("\nChecking for Solr container...")
    c = dc.containers.list(all=True, filters={"name": "monarch_solr"})
    return None if not c else c[0]


def get_solr(update: bool = False):
    """Checks for Solr data and container, and returns a SolrImplementation."""
    if update:
        ensure_solr(update)
    if check_for_solr(dc=docker.from_env(), quiet=True):
        return SolrImplementation()
    else:
        console.print("\nNo Solr container found!\nStart a Solr container with [bold]monarch solr start[/].")
        sys.exit(1)


def start_solr():
    """Starts a local Solr container."""
    data = monarchstow.join("solr", "data")
    dc = docker.from_env()
    c = check_for_solr(dc, quiet=True)
    if not c:
        try:
            c = dc.containers.run(
                "solr:8",
                ports={"8983": 8983},
                volumes=[f"{data}:/opt/solr-data"],
                environment=["SOLR_HOME=/opt/solr-data"],
                name="monarch_solr",
                command="",
                detach=True,
            )
            time.sleep(10)
            console.print(f"{c.name} {c.status}")
        except Exception as e:
            console.print(f"Error instantiating monarch solr container: {e}")
            raise e
    else:
        try:
            c.start()
        except Exception as e:
            console.print(f"Error running existing container {c.name} ({c.status}) - {e}")
            raise e


def stop_solr():
    """Stops the local Solr container."""
    c = check_for_solr(dc=docker.from_env(), quiet=True)
    if c:
        try:
            console.print(f"Stopping {c.name}...")
            c.stop()
            c.remove()
        except Exception as e:
            console.print(f"Error stopping container {c.name} ({c.status}) - {e}")
            raise e


def solr_status():
    c = check_for_solr(dc=docker.from_env())
    if not c:
        console.print(
            """
No monarch_solr container found. 

Download the Monarch Solr KG and start a local solr instance:
    [grey84 on black]monarch solr start[/]
"""
        )
    else:
        console.print(
            f"""
Found monarch_solr container: {c.id}
Container status: {c.status}
        """
        )
        if c.status == "exited":
            console.print(
                """
Start the container using:
    [grey84 on black]monarch solr start[/]
"""
            )
        if c.status == "running":
            console.print(
                """
You can create a new container with
    [grey84 on black]monarch solr stop[/]
    [grey84 on black]monarch solr start[/]
"""
            )
