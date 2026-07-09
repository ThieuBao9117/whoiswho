"""
CSB Backend Launcher - chay script nay de giu uvicorn alive.
Dung: python keep_alive.py
"""
import subprocess, sys, time, os, signal

BACKEND_DIR = r"C:\WHO\csbwhoiswho\backend"
PYTHON = r"C:\WHO\csbwhoiswho\backend\venv\Scripts\python.exe"
CMD = [PYTHON, "-m", "uvicorn", "app.main:app",
       "--host", "127.0.0.1", "--port", "7000",
       "--loop", "asyncio", "--http", "h11",
       "--timeout-keep-alive", "5",
       "--log-level", "info"]

def start():
    proc = subprocess.Popen(
        CMD,
        cwd=BACKEND_DIR,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
    )
    print(f"[{time.strftime('%H:%M:%S')}] Started PID={proc.pid}", flush=True)
    return proc

def main():
    print("CSB WHO Backend Launcher started", flush=True)
    proc = start()
    while True:
        try:
            time.sleep(3)
            ret = proc.poll()
            if ret is not None:
                print(f"[{time.strftime('%H:%M:%S')}] Backend exited code={ret}, restarting...", flush=True)
                time.sleep(2)
                proc = start()
        except KeyboardInterrupt:
            print("Shutting down...")
            proc.terminate()
            break

if __name__ == "__main__":
    main()
