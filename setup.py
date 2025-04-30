import os
import stat
import typing
import pathlib
import platform
import urllib.request




from setuptools import setup
from setuptools.command.build_py import build_py as _build_py


def _asset_name(version: str) -> str:
    sys_os = {"Linux": "linux", "Darwin": "macos", "Windows": "windows"}[platform.system()]
    arch   = {"x86_64": "amd64", "AMD64": "amd64",
              "arm64": "arm64",  "aarch64": "arm64"}.get(platform.machine(), platform.machine())
    ext    = "tar.gz" if sys_os != "windows" else "zip"
    return f"sqlc_{version}_{sys_os}_{arch}.{ext}"

def _copy_sqlc(root: pathlib.Path, dest: pathlib.Path):
    for p in root.rglob("sqlc*"):
        if p.is_file():
            p.rename(dest / p.name)

def _make_executable(path: pathlib.Path):
    if os.name != "nt":
        mode = path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        path.chmod(mode)

class build_py(_build_py):
    
    
    @typing.override
    def run(self):
        
        version = self.distribution.metadata.version
        
        assert version is not None
        
        dest_dir = pathlib.Path(self.build_lib, "sqlc_py", "_vendor")
        dest_dir.mkdir(parents=True, exist_ok=True)

        asset = _asset_name(version)
        url = f"https://github.com/sqlc-dev/sqlc/releases/download/v{version}/{asset}"
        tgt = dest_dir / asset
        print(url)
        print(tgt)
        urllib.request.urlretrieve(url, tgt)

        if asset.endswith(".zip"):
            import zipfile, tempfile
            with zipfile.ZipFile(tgt) as zf, tempfile.TemporaryDirectory() as tmp:
                zf.extractall(tmp)
                _copy_sqlc(pathlib.Path(tmp), dest_dir)
        else:  # tar.gz
            import tarfile
            with tarfile.open(tgt, "r:gz") as tf:
                tf.extractall(dest_dir)
        _make_executable(dest_dir / ("sqlc.exe" if os.name == "nt" else "sqlc"))
        super().run()


setup(cmdclass={"build_py": build_py})


