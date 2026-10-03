"""Exercise package assembly with fake installers; no downloads or app launches."""
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest


@pytest.mark.parametrize("pack_succeeds", [True, False])
def test_build_uses_locked_dependencies_and_cleans_only_its_temp_dir(tmp_path, pack_succeeds):
    repo = tmp_path / "repo"
    repo.mkdir()
    source = Path(__file__).resolve().parents[1]
    for name in (
        "build_dxt.sh", "manifest.json", "pyproject.toml", "uv.lock",
        "things_server.py", "url_scheme.py", "formatters.py",
    ):
        shutil.copy2(source / name, repo / name)
    (repo / "dist").mkdir()
    previous = repo / "dist" / "previous.dxt"
    previous.write_text("keep this package")
    binaries = tmp_path / "bin"
    binaries.mkdir()
    scratch = tmp_path / "scratch"
    scratch.mkdir()
    uv = binaries / "uv"
    uv.write_text(f"#!{sys.executable}\n" + '''import pathlib, sys
args = sys.argv[1:]
if args[:2] == ["python", "find"]:
    print(sys.executable)
elif args[0] == "export":
    assert "--locked" in args and "--no-dev" in args and "--no-emit-project" in args
    pathlib.Path(args[args.index("--output-file") + 1]).write_text("# locked dependencies")
elif args[:2] == ["pip", "install"]:
    assert "--require-hashes" in args
    pathlib.Path(args[args.index("--target") + 1]).mkdir(parents=True)
else:
    raise AssertionError(args)
''')
    dxt = binaries / "dxt"
    dxt.write_text(f"#!{sys.executable}\n" + f'''import pathlib, sys
pathlib.Path(__file__).with_name("packed").write_text("invoked")
assert sys.argv[1] == "pack"
package = pathlib.Path(sys.argv[2])
for name in ("main.py", "url_scheme.py", "formatters.py", "lib"):
    assert (package / "server" / name).exists()
assert (package / "manifest.json").exists()
if not {pack_succeeds!r}:
    sys.exit(1)
pathlib.Path(sys.argv[3]).write_text("assembled package")
''')
    uv.chmod(0o755)
    dxt.chmod(0o755)
    result = subprocess.run(
        ["bash", str(repo / "build_dxt.sh")], cwd=tmp_path,
        env={**os.environ, "PATH": f"{binaries}:{os.environ['PATH']}", "TMPDIR": str(scratch)},
        capture_output=True, text=True,
    )
    assert (result.returncode == 0) is pack_succeeds, result.stderr
    assert (binaries / "packed").exists()
    assert previous.read_text() == "keep this package"
    assert list(scratch.iterdir()) == []
    if pack_succeeds:
        assert (repo / "dist" / "things-mcp-0.4.0.dxt").exists()
