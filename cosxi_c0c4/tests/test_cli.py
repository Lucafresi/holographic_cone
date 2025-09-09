import json, sys
from pathlib import Path
from cosxi.cli import main as cli_main

def test_cli_roundtrip(tmp_path: Path):
    inp = {
        "Mpl": 2.435e18, "t0": 4.35e17, "Leff": 1.0,
        "Aprime_UV": -0.3, "Aprime_IR": -0.299999998,
        "Tbar": 1.0e-12, "coeff": {"cB":1.0,"cT":1.0}
    }
    infile = tmp_path/"in.json"; outfile = tmp_path/"out.json"
    infile.write_text(json.dumps(inp))
    sys.argv = ["cosxi.cli", str(infile), str(outfile)]
    cli_main()
    data = json.loads(outfile.read_text())
    assert "xi" in data and "rho_Lambda_t0" in data and "checks" in data
    assert data["checks"]["ward_scale_invariance"]["invariant_under_local_rescalings"] is True
