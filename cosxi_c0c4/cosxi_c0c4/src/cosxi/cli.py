import argparse
from .pipeline import run_pipeline
from .report import write_json

def main():
    ap = argparse.ArgumentParser(description="cosxi C0/C4 pipeline")
    ap.add_argument("input_json")
    ap.add_argument("output_json")
    args = ap.parse_args()
    rep = run_pipeline(args.input_json)
    write_json(rep, args.output_json)
    print(f"[cosxi] Wrote {args.output_json}")

if __name__ == "__main__":
    main()
