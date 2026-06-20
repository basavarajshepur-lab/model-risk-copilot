"""CLI runner for Model Risk Copilot."""

import argparse
import json
from pathlib import Path
from dotenv import load_dotenv
from core.models import RegulatoryFramework
from core.pipeline import process_mdd
from data.sample_mdds import SAMPLE_MDDS

load_dotenv()


def main():
    parser = argparse.ArgumentParser(
        description="Model Risk Copilot — SR 11-7 / SS1/23 compliance assessment"
    )
    parser.add_argument("--file", help="Path to MDD text file")
    parser.add_argument(
        "--sample",
        choices=["strong", "partial", "weak"],
        help="Use a built-in sample MDD",
    )
    parser.add_argument(
        "--framework",
        choices=["SR117", "SS123"],
        default="SR117",
        help="Regulatory framework (default: SR117)",
    )
    parser.add_argument("--output-dir", help="Directory to save results JSON")
    args = parser.parse_args()

    if not args.file and not args.sample:
        parser.error("Provide either --file or --sample")

    if args.sample:
        key_map = {
            "strong": "RetailPD_v3.2 (Strong documentation)",
            "partial": "FraudScorer_ML (Partial documentation)",
            "weak": "SME Credit Model (Weak documentation)",
        }
        doc_text = SAMPLE_MDDS[key_map[args.sample]]
        print(f"Using sample MDD: {key_map[args.sample]}")
    else:
        path = Path(args.file)
        if not path.exists():
            print(f"File not found: {path}")
            return
        doc_text = path.read_text(encoding="utf-8")
        print(f"Loaded MDD from: {path}")

    framework = RegulatoryFramework.SR117 if args.framework == "SR117" else RegulatoryFramework.SS123
    output_dir = Path(args.output_dir) if args.output_dir else None

    result = process_mdd(doc_text, framework, output_dir)

    if not output_dir:
        print("\nFull result JSON:")
        print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
