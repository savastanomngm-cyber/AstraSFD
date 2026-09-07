from pathlib import Path
import os
import subprocess
import sys
import venv


def main():
    root = Path(__file__).resolve().parent
    os.chdir(root)
    environment = root / ".venv"
    python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not python.exists():
        venv.create(environment, with_pip=True)
    subprocess.check_call([str(python), "-m", "pip", "install", "-r", str(root / "requirements.txt")])
    subprocess.check_call([str(python), "-m", "streamlit", "run", str(root / "terminal.py"), "--server.address", "127.0.0.1", *sys.argv[1:]])


if __name__ == "__main__":
    main()
