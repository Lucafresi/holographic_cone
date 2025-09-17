#!/usr/bin/env bash
set -euo pipefail
python src/delta_kk_locking_orchestrator.py profiles/sources.json certs/g1_lambda_kk_lock.json
python -m json.tool certs/g1_lambda_kk_lock.json
