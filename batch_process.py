#!/usr/bin/env python3
"""
Batch process all JDs in jd/ folder using Claude API directly.
Fully automates the prep → API call → apply workflow without manual copy-paste.

Usage:
  1. Set ANTHROPIC_API_KEY environment variable
  2. Place JD .txt files in jd/ folder as: Company_Role.txt
  3. Run: python batch_process.py [--model claude-sonnet-4-6] [--dry-run]

Requirements:
  pip install anthropic
"""
import os
import json
import time
import argparse
from pathlib import Path
from typing import Optional

# Import from existing code
import sys
sys.path.insert(0, str(Path(__file__).parent))
from tailor_resume import (
    CV_CONTENT, build_prompt, TEMPLATE_CV, OUTPUT_DIR,
    update_document, convert_to_pdf
)
from docx import Document

# Anthropic
try:
    from anthropic import Anthropic
except ImportError:
    print("ERROR: anthropic package not installed.")
    print("Install with: pip install anthropic")
    sys.exit(1)


def sanitize_filename(name: str) -> str:
    """Make filename safe for filesystem."""
    return "".join(c if c.isalnum() or c in " -_." else "_" for c in name).strip()


def call_claude_api(client: Anthropic, prompt: str, model: str = "claude-sonnet-4-6") -> Optional[dict]:
    """Send prompt to Claude and return parsed JSON response."""
    try:
        print(f"    Calling Claude ({model})...")
        message = client.messages.create(
            model=model,
            max_tokens=4096,
            temperature=0.2,
            system="You are an expert ATS resume optimizer. Return ONLY valid JSON, no markdown, no explanation text.",
            messages=[{"role": "user", "content": prompt}]
        )
        response_text = message.content[0].text.strip()

        # Strip any markdown code fences
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()

        # Parse JSON
        data = json.loads(response_text, strict=False)
        return data

    except json.JSONDecodeError as e:
        print(f"    ERROR: Invalid JSON from Claude: {e}")
        debug_file = Path("debug_claude_response.txt")
        debug_file.write_text(response_text, encoding="utf-8")
        print(f"    Raw response saved to: {debug_file}")
        return None
    except Exception as e:
        print(f"    ERROR: API call failed: {type(e).__name__}: {e}")
        return None


def process_single_jd(jd_file: Path, client: Anthropic, model: str, responses_dir: Path) -> bool:
    """Process one JD file: generate prompt, call API, apply to docx/PDF."""
    # Extract company and role from filename
    # Expected: Company_Role.txt or Company Role.txt
    stem = jd_file.stem
    parts = stem.replace("_", " ").split(" ")
    if len(parts) >= 2:
        company = " ".join(parts[:-1])
        role = parts[-1]
    else:
        company = stem
        role = "Role"

    print(f"\n{'='*60}")
    print(f"Processing: {jd_file.name}")
    print(f"  Company: {company}")
    print(f"  Role: {role}")
    print(f"{'='*60}")

    # Read JD text
    try:
        jd_text = jd_file.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  ERROR: Could not read {jd_file}: {e}")
        return False

    # Build prompt using existing function
    print("  Building prompt...")
    prompt = build_prompt(jd_text)

    # Call Claude API
    data = call_claude_api(client, prompt, model)
    if not data:
        return False

    # Save response JSON
    response_file = responses_dir / f"{stem}.json"
    try:
        response_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  ✓ Response saved: {response_file}")
    except Exception as e:
        print(f"  ERROR: Could not save response: {e}")
        return False

    # Generate tailored resume (docx + PDF)
    print("  Generating tailored resume...")
    try:
        doc = Document(str(TEMPLATE_CV))
        doc = update_document(doc, data)

        # Output filename: Company_Role_Timestamp.docx (or just Company_Role.docx)
        safe_company = sanitize_filename(company)
        safe_role = sanitize_filename(role)
        out_docx = OUTPUT_DIR / f"{safe_company}_{safe_role}.docx"

        doc.save(str(out_docx))
        print(f"  ✓ Word saved: {out_docx.name}")

        # Convert to PDF
        pdf_result = convert_to_pdf(out_docx)
        if pdf_result:
            print(f"  ✓ PDF saved: {pdf_result.name}")
        else:
            print("  ⚠ PDF conversion skipped (no converter available)")

    except Exception as e:
        print(f"  ERROR: Failed to generate resume: {e}")
        import traceback
        traceback.print_exc()
        return False

    print(f"  ✓ Complete!")
    return True


def generate_summary_report(results: list, summary_path: Path):
    """Generate a markdown summary of all processed JDs."""
    lines = [
        "# Batch Processing Summary",
        f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "| Company | Role | ATS Score | Status | Output |",
        "|---------|------|-----------|--------|--------|"
    ]

    success_count = sum(1 for _, success in results if success)
    for jd_file, success in results:
        stem = jd_file.stem
        response_file = Path("responses") / f"{stem}.json"

        if success:
            try:
                data = json.loads(response_file.read_text(encoding="utf-8"))
                company = data.get("company_name", "N/A")
                role = data.get("role_title", "N/A")
                ats = data.get("ats_match_percentage", 0)
                status = "✓ Success"
                output = f"{company}_{role}.docx"
            except Exception:
                company = stem.split("_")[0] if "_" in stem else stem
                role = "Role"
                ats = "?"
                status = "✓ Partial"
                output = "see above"
        else:
            parts = stem.replace("_", " ").split(" ")
            company = " ".join(parts[:-1]) if len(parts) >= 2 else stem
            role = parts[-1] if len(parts) >= 2 else "Role"
            ats = "-"
            status = "✗ Failed"
            output = "-"

        lines.append(f"| {company} | {role} | {ats}% | {status} | {output} |")

    lines.extend([
        "",
        f"**Total**: {len(results)} | **Success**: {success_count} | **Failed**: {len(results) - success_count}"
    ])

    summary_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n  Summary report: {summary_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Batch process JDs using Claude API - no manual copy-paste needed"
    )
    parser.add_argument(
        "--jd-dir",
        default="jd",
        help="Directory containing JD .txt files (default: jd/)"
    )
    parser.add_argument(
        "--model",
        default="claude-sonnet-4-6",
        help="Claude model to use (default: claude-sonnet-4-6)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be processed without actually calling API"
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip JDs that already have a response file"
    )
    args = parser.parse_args()

    # Setup directories
    jd_dir = Path(args.jd_dir)
    responses_dir = Path("responses")
    responses_dir.mkdir(exist_ok=True)

    if not jd_dir.exists():
        print(f"Creating directory: {jd_dir}/")
        jd_dir.mkdir(parents=True)
        print(f"\nPlace your JD .txt files in {jd_dir}/")
        print("Filename format: Company_Role.txt")
        print("Example: Titanbay_Senior_Analytics_Engineer.txt")
        print("\nThen re-run: python batch_process.py")
        return

    # Find all JD files
    jd_files = list(jd_dir.glob("*.txt"))
    if not jd_files:
        print(f"No .txt files found in {jd_dir}/")
        print("Add your JD files and re-run.")
        return

    # If not dry-run, check API key
    if not args.dry_run:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("ERROR: ANTHROPIC_API_KEY environment variable not set.")
            print("\nSet it with:")
            print("  export ANTHROPIC_API_KEY='your-api-key-here'  # Linux/Mac")
            print("  set ANTHROPIC_API_KEY=your-api-key-here       # Windows CMD")
            print("  $env:ANTHROPIC_API_KEY='your-api-key-here'   # PowerShell")
            print("\nGet your API key from: https://console.anthropic.com/")
            sys.exit(1)

        # Initialize client
        try:
            client = Anthropic(api_key=api_key)
        except Exception as e:
            print(f"ERROR: Failed to initialize Anthropic client: {e}")
            sys.exit(1)
    else:
        client = None  # Not needed for dry-run

    print(f"Found {len(jd_files)} JD file(s) in {jd_dir}/")
    print(f"Model: {args.model}")
    print(f"Responses will be saved to: {responses_dir}/")
    print(f"Resumes will be saved to: {OUTPUT_DIR}/")

    if args.dry_run:
        print("\nDRY RUN - would process:")
        for jd_file in jd_files:
            print(f"  - {jd_file.name}")
        print("\nRemove --dry-run to actually process.")
        return

    # Process each JD
    results = []  # (jd_file, success) tuples

    for idx, jd_file in enumerate(jd_files, 1):
        print(f"\n[{idx}/{len(jd_files)}] ", end="")

        # Check if response already exists
        stem = jd_file.stem
        response_file = responses_dir / f"{stem}.json"
        if args.skip_existing and response_file.exists():
            print(f"{jd_file.name} - skipping (response exists)")
            results.append((jd_file, True))  # Count as success for summary
            continue

        try:
            success = process_single_jd(jd_file, client, args.model, responses_dir)
            results.append((jd_file, success))

            # Rate limit friendly: small pause between calls
            if idx < len(jd_files):
                time.sleep(2)

        except KeyboardInterrupt:
            print("\n\nInterrupted by user.")
            break
        except Exception as e:
            print(f"\n  UNEXPECTED ERROR: {e}")
            import traceback
            traceback.print_exc()
            results.append((jd_file, False))

    # Generate summary report
    summary_file = Path("batch_summary.md")
    generate_summary_report(results, summary_file)

    # Final stats
    success_count = sum(1 for _, success in results if success)
    print(f"\n{'='*60}")
    print(f"BATCH COMPLETE")
    print(f"  Total processed: {len(results)}")
    print(f"  Successful:      {success_count}")
    print(f"  Failed:          {len(results) - success_count}")
    print(f"{'='*60}")
    print(f"\nNext steps:")
    print(f"  1. Review tailored resumes in: {OUTPUT_DIR}/")
    print(f"  2. Check summary report: {summary_file}")
    print(f"  3. Raw API responses in: responses/")


if __name__ == "__main__":
    main()
