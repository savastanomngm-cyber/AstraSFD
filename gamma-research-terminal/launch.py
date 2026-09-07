from pathlib import Path
import os
import subprocess
import sys
import venv


def main():
    root = Path(__file__).resolve().parent
    os.chdir(root)
    requirements = root / "requirements.txt"
    environment = root / ".venv"
    python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    lockfile = environment / ".requirements-installed"

    if not python.exists():
        print("Creating virtual environment…")
        venv.create(environment, with_pip=True)

    # Only run pip install when requirements.txt is newer than the lockfile
    need_install = not lockfile.exists() or requirements.stat().st_mtime > lockfile.stat().st_mtime

    if need_install:
        print("Installing dependencies…")
        try:
            subprocess.check_call(
                [str(python), "-m", "pip", "install", "-r", str(requirements)],
                stdout=sys.stdout, stderr=sys.stderr,
            )
            lockfile.touch()
        except subprocess.CalledProcessError:
            print()
            print("=" * 60)
            print("pip install failed — likely a missing system dependency.")
            print()
            if os.name != "nt":
                print("   pyarrow may need Apache Arrow C++ to build from source.")
                print("   On macOS:")
                print("     brew install apache-arrow")
                print("   On Linux (Debian/Ubuntu):")
                print("     sudo apt install libarrow-dev")
                print()
                print("   Alternatively, try a prebuilt wheel:")
                print(f"     {python} -m pip install pyarrow")
                print()
            print("   If the issue persists, check the pip output above for the")
            print("   specific package that failed, and install its system dependency.")
            print()
            print("=" * 60)
            print()
            input("Press Return to close.")
            sys.exit(1)

    try:
        subprocess.check_call(
            [str(python), "-m", "streamlit", "run",
             str(root / "terminal.py"),
             "--server.address", "127.0.0.1",
             *sys.argv[1:]],
        )
    except KeyboardInterrupt:
        print()
        print("Gamma Lab stopped.")
    except subprocess.CalledProcessError as e:
        print()
        print("Gamma Lab could not start.")
        if e.returncode == -6:
            print("Port 8501 may be in use. Close the other Gamma Lab window first.")
        print()
        input("Press Return to close.")
        sys.exit(1)


if __name__ == "__main__":
    main()
