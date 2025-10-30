# # Pipeline (ASCII-safe skeleton)
# import sys, pandas as pd
# from pathlib import Path
# from aps_config import INPUT_DIR, OUTPUT_DIR
# from aps_normalize import normalize_and_score
# from aps_healthcheck import health_check
# from aps_render import render_pdf

# def main(csv_path: str):
#     csv_path = Path(csv_path)
#     OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
#     df = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
#     df = normalize_and_score(df)
#     hc = health_check(df)
#     print("=== APS 18-Point Health Check ===")
#     for k,v in hc.items():
#         print(f" - {k}: {v}")
#     out = OUTPUT_DIR / (csv_path.stem + "_DEMO.pdf")
#     render_pdf(df, out)
#     print(f"Wrote demo PDF -> {out}")

# if __name__ == "__main__":
#     if len(sys.argv) < 2:
#         print("Usage: RUN_ME.bat (invokes this with input\\test.csv)")
#         raise SystemExit(1)
#     main(sys.argv[1])








# Pipeline (ASCII-safe skeleton)
import sys, pandas as pd
from pathlib import Path
from aps_config import INPUT_DIR, OUTPUT_DIR
from aps_normalize import normalize_and_score
from aps_healthcheck import health_check
from aps_render import render_pdf

def main(csv_path: str):
    csv_path = Path(csv_path)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"\n=== APS Pipeline Starting ===")
    print(f"Input file: {csv_path}")
    
    # Read CSV
    df = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
    print(f"✓ Loaded {len(df)} records")
    
    # Normalize and score
    df = normalize_and_score(df)
    print(f"✓ Normalized and scored data")
    
    # Health check
    hc = health_check(df)
    print("\n=== APS 18-Point Health Check ===")
    for k, v in hc.items():
        status = v.get('status', 'UNKNOWN')
        value = v.get('value', 'N/A')
        message = v.get('message', '')
        print(f" [{status}] {k}: {value} - {message}")
    
    # Save scored CSV (Acceptance Test #8)
    csv_out = OUTPUT_DIR / (csv_path.stem + "_scored.csv")
    df.to_csv(csv_out, index=False, encoding='utf-8')
    print(f"\n✓ Wrote scored CSV -> {csv_out}")
    
    # Render PDF (pass filename for feed type detection)
    out = OUTPUT_DIR / (csv_path.stem + "_DEMO.pdf")
    render_pdf(df, out, csv_filename=csv_path.name)
    print(f"✓ Wrote demo PDF -> {out}")
    
    print("\n=== Pipeline Complete ===")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: RUN_ME.bat (invokes this with input\\test.csv)")
        raise SystemExit(1)
    main(sys.argv[1])