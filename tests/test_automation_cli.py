"""Tests for workflow automation batch processing CLI script."""

import csv
import pytest
from pathlib import Path
from scripts.automation_cli import process_batch

def test_automation_cli_batch_processing(tmp_path):
    input_file = tmp_path / "raw_inbound.csv"
    output_file = tmp_path / "cleaned_leads.csv"
    dead_letter_file = tmp_path / "errors.csv"

    # Write sample CSV with valid and malformed rows
    with open(input_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Full Name", "Email Address", "Budget", "Formula"])
        writer.writerow(["Marcus Vance", "marcus@synth.io", "50000", "=1+2"])
        writer.writerow(["Invalid Person", "not-an-email", "1000", "safe"])

    # 1. Test Dry Run
    dry_res = process_batch(input_file, output_file, dry_run=True)
    assert dry_res["processed"] == 2
    assert dry_res["valid"] == 1
    assert dry_res["errors"] == 1
    assert not output_file.exists()

    # 2. Test Live Atomic Write
    live_res = process_batch(input_file, output_file, dry_run=False, dead_letter_path=dead_letter_file)
    assert live_res["valid"] == 1
    assert live_res["errors"] == 1
    assert output_file.exists()
    assert dead_letter_file.exists()

    # Verify formula sanitization in output
    with open(output_file, "r", encoding="utf-8") as f:
        content = f.read()
        assert "'=1+2" in content
