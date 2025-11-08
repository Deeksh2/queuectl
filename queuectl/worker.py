import time, signal
from .db import connect, get_next, complete, retry_or_dlq
from .executor import run_command

STOP = False

def stop(sig, frame):
    global STOP
    STOP = True

signal.signal(signal.SIGTERM, stop)
signal.signal(signal.SIGINT, stop)

def run_worker():
    conn = connect()
    while not STOP:
        job = get_next(conn)
        if not job:
            time.sleep(0.5)
            continue
        exit_code, out, err = run_command(job["command"])
        if exit_code == 0:
            complete(conn, job, exit_code, out, err)
        else:
            retry_or_dlq(conn, job, exit_code, out, err)
