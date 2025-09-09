import json, subprocess, os, sys, tempfile
from cosxi.pipeline import run_pipeline
def test_cli_module_runs_and_outputs(tmp_path):
    inp = os.path.join(os.path.dirname(__file__), "..", "inputs", "baseline.json")
    out = tmp_path/"out.json"
    env = dict(os.environ)
    env["PYTHONPATH"] = os.path.join(os.path.dirname(__file__), "..", "src")
    cmd = [sys.executable, "-m", "cosxi.cli", inp, str(out)]
    r = subprocess.run(cmd, env=env, capture_output=True, text=True)
    assert r.returncode == 0
    d = json.loads(out.read_text())
    assert "xi" in d and "rho_Lambda_t0" in d
    assert d["xi"] > 0 and d["rho_Lambda_t0"] > 0
