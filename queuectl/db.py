from __future__ import annotations
import sqlite3
import datetime as dt
from .util import DB_PATH

def now():
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def connect():
    conn = sqlite3.connect(DB_PATH, timeout=5, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS jobs (
      id TEXT PRIMARY KEY,
      command TEXT,
      state TEXT,
      attempts INTEGER,
      max_retries INTEGER,
      run_at TEXT,
      last_output TEXT,
      last_error TEXT
    );
    """)
    return conn

def enqueue(conn, job):
    with conn:
        conn.execute(
            "INSERT INTO jobs VALUES (?, ?, 'pending', 0, ?, ?, ?, ?)",
            (job["id"], job["command"], job.get("max_retries",3), now(), None, None)
        )

def get_next(conn):
    cur = conn.cursor()
    cur.execute("BEGIN IMMEDIATE")
    job = cur.execute("SELECT * FROM jobs WHERE state='pending' AND run_at <= ? LIMIT 1", (now(),)).fetchone()
    if not job:
        conn.execute("COMMIT")
        return None
    conn.execute("UPDATE jobs SET state='processing' WHERE id=?", (job["id"],))
    conn.execute("COMMIT")
    return job

def complete(conn, job, exit_code, out, err):
    with conn:
        conn.execute("UPDATE jobs SET state='completed', last_output=?, last_error=? WHERE id=?", (out, err, job["id"]))

def retry_or_dlq(conn, job, exit_code, out, err):
    attempts = job["attempts"] + 1
    if attempts <= job["max_retries"]:
        delay = 2 ** attempts
        next_run = (dt.datetime.utcnow() + dt.timedelta(seconds=delay)).replace(microsecond=0).isoformat() + "Z"
        with conn:
            conn.execute("UPDATE jobs SET state='pending', attempts=?, run_at=?, last_output=?, last_error=? WHERE id=?",
                         (attempts, next_run, out, err, job["id"]))
    else:
        with conn:
            conn.execute("UPDATE jobs SET state='dead', attempts=?, last_output=?, last_error=? WHERE id=?",
                         (attempts, out, err, job["id"]))
