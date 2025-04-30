from importlib import resources
import os, stat, subprocess, sys

def _bin():
    name = "sqlc.exe" if os.name == "nt" else "sqlc"
    path = resources.files(__package__) / "_vendor" / name
    print(path)
    if os.name != "nt":
        mode = os.stat(path).st_mode
        if not (mode & stat.S_IXUSR):
            os.chmod(path, mode | stat.S_IXUSR)
    return str(path)

def main():
    sys.exit(subprocess.call([_bin(), *sys.argv[1:]]))
