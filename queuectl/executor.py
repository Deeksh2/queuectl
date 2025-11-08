import subprocess

def run_command(command, timeout=300):
    try:
        cp = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
        return cp.returncode, cp.stdout, cp.stderr
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"
