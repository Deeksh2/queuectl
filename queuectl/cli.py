import json
import typer
import subprocess
import sys
from rich.table import Table
from rich.console import Console
from .db import connect, enqueue, connect
from .util import is_alive, send_term
from .worker import run_worker

app = typer.Typer()
console = Console()

@app.command()
def status():
    conn = connect()
    rows = conn.execute("SELECT state, COUNT(*) FROM jobs GROUP BY state").fetchall()
    table = Table(title="Queue Status")
    table.add_column("State")
    table.add_column("Count")
    for r in rows:
        table.add_row(r["state"], str(r[1]))
    console.print(table)

@app.command()
def enqueue_job(job: str):
    conn = connect()
    enqueue(conn, json.loads(job))
    console.print("[green]Job Enqueued[/green]")

@app.command()
def list(state: str = None):
    conn = connect()
    if state:
        rows = conn.execute("SELECT * FROM jobs WHERE state=?", (state,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM jobs").fetchall()
    table = Table(title="Jobs")
    table.add_column("id")
    table.add_column("state")
    table.add_column("cmd")
    for r in rows:
        table.add_row(r["id"], r["state"], r["command"])
    console.print(table)

@app.command()
def worker():
    run_worker()
