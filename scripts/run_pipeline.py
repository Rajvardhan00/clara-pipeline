"""
Clara Pipeline - Main Runner (No API version)
Runs Pipeline A (demo -> v1) and Pipeline B (onboarding -> v2)
No API key required.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from extractor import extract_account_data, load_transcript, split_multi_transcript
from prompt_generator import generate_agent_spec
from onboarding_updater import apply_onboarding_updates, format_changelog_md
from storage import save_memo, save_agent_spec, save_changelog, load_memo, print_summary
from task_tracker import create_task, print_board


def pipeline_a(transcript_file: str, account_id: str = None):
    print(f"\n{'='*55}")
    print(f"🚀 PIPELINE A — Demo → v1")
    print(f"   File: {transcript_file}")
    print(f"{'='*55}")

    text = load_transcript(transcript_file)
    chunks = split_multi_transcript(text)

    for chunk in chunks:
        acct_id = account_id or chunk["account_id"]
        if not acct_id:
            print("  ⚠️  Could not detect account_id, skipping.")
            continue

        print(f"\n  Processing Account {acct_id}...")
        print("  📋 Extracting account data...")
        memo = extract_account_data(chunk["text"], acct_id)
        save_memo(acct_id, memo, version="v1")

        print("  🤖 Generating agent spec v1...")
        spec = generate_agent_spec(memo, version="v1")
        save_agent_spec(acct_id, spec, version="v1")

        # ── Create task tracker entry ──────────────────────────
        task = create_task(
            account_id=acct_id,
            company_name=memo.get("company_name", "Unknown"),
            stage="demo_processed",
            unknowns=memo.get("questions_or_unknowns", [])
        )
        print(f"  📋 Task created: [{task['task_id']}] {task['status']}")
        print(f"  ✅ Account {acct_id} — v1 complete!")

    print(f"\n✅ Pipeline A complete.\n")


def pipeline_b(onboarding_file: str, account_id: str = None):
    print(f"\n{'='*55}")
    print(f"🔄 PIPELINE B — Onboarding → v2")
    print(f"   File: {onboarding_file}")
    print(f"{'='*55}")

    text = load_transcript(onboarding_file)
    chunks = split_multi_transcript(text)

    for chunk in chunks:
        acct_id = account_id or chunk["account_id"]
        if not acct_id:
            print("  ⚠️  Could not detect account_id, skipping.")
            continue

        print(f"\n  Processing Account {acct_id} (onboarding update)...")
        try:
            v1_memo = load_memo(acct_id, version="v1")
        except FileNotFoundError:
            print(f"  ❌ No v1 memo found for account {acct_id}. Run Pipeline A first.")
            continue

        print("  🔄 Merging onboarding updates...")
        result = apply_onboarding_updates(v1_memo, chunk["text"])
        v2_memo = result.get("v2_memo", {})

        save_memo(acct_id, v2_memo, version="v2")

        print("  🤖 Generating agent spec v2...")
        spec_v2 = generate_agent_spec(v2_memo, version="v2")
        save_agent_spec(acct_id, spec_v2, version="v2")

        changelog_md = format_changelog_md(acct_id, result)
        save_changelog(acct_id, changelog_md, result)

        # ── Update task tracker ────────────────────────────────
        task = create_task(
            account_id=acct_id,
            company_name=v2_memo.get("company_name", "Unknown"),
            stage="onboarding_complete",
            unknowns=result.get("still_unknown", [])
        )
        print(f"  📋 Task updated: [{task['task_id']}] {task['status']}")
        print(f"  ✅ Account {acct_id} — v2 complete!")

    print(f"\n✅ Pipeline B complete.\n")


def run_all():
    base = Path(__file__).parent.parent / "sample_data"

    print("\n" + "="*55)
    print("  🏁 RUNNING FULL CLARA PIPELINE ON ALL SAMPLE DATA")
    print("="*55)

    for f in [base/"demo_001.txt", base/"demo_002.txt",
              base/"demo_003.txt", base/"demo_004_005.txt"]:
        if f.exists():
            pipeline_a(str(f))

    for f in [base/"onboarding_001_002_003.txt", base/"onboarding_004_005.txt"]:
        if f.exists():
            pipeline_b(str(f))

    print_summary()
    print_board()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        run_all()
    elif sys.argv[1] == "demo":
        f = sys.argv[2] if len(sys.argv) > 2 else None
        acct = sys.argv[3] if len(sys.argv) > 3 else None
        if f: pipeline_a(f, acct)
    elif sys.argv[1] == "onboarding":
        f = sys.argv[2] if len(sys.argv) > 2 else None
        acct = sys.argv[3] if len(sys.argv) > 3 else None
        if f: pipeline_b(f, acct)
    elif sys.argv[1] == "summary":
        print_summary()
        print_board()
