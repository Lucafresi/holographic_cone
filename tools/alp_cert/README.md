# ALP nullspace certificate (SNF over Z)

cd tools/alp_cert
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python3 axion_cert_from_ledger.py --in models/sm_uv_PASS.yaml --out cert/cert_sm_uv_PASS.json --pretty --echo
python3 axion_cert_from_ledger.py --in models/sm_uv_FAIL_with_L.yaml --out cert/cert_sm_uv_FAIL.json --pretty --echo
