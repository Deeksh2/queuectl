QueueCTL

This project is a small command-line based job queue system. It allows adding jobs that run shell commands, and processes them in the background through worker processes. If a job fails, it is retried using exponential backoff. After crossing the maximum retry count, the job is moved to a Dead Letter Queue (DLQ). The data is stored in a SQLite database so that jobs are not lost when the program stops.

This project was built as part of the Flam Backend Internship Assignment.



 Features

- Add jobs using a CLI command
- Workers run jobs in the background
- Retries on failure with exponential backoff (delay = 2^attempts)
- Failed jobs after retry limit are stored in a DLQ
- Job state is stored in SQLite and persists between runs

---

 How to Set Up

```bash
git clone https://github.com/Deeksh2/queuectl
cd queuectl

python3.11 -m venv .venv
source .venv/bin/activate

pip install -e .

