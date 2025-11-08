import os, signal

DB_PATH = os.path.join(os.getcwd(), "queuectl.db")

def is_alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except:
        return False

def send_term(pid):
    try:
        os.kill(pid, signal.SIGTERM)
    except:
        pass
