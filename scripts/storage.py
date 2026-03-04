"""
Clara Pipeline - Storage Manager
Handles saving/loading all pipeline outputs in correct folder structure
"""

import json
import os
from datetime import datetime
from pathlib import Path


BASE_OUTPUT_DIR = Path(__file__).parent.parent / "outputs" / "accounts"


def get_account_dir(account_id: str, version: str) -> Path:
    """Get the directory for a specific account version."""
    path = BASE_OUTPUT_DIR / account_id / version
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_memo(account_id: str, memo: dict, version: str = "v1") -> str:
    """Save account memo JSON."""
    # Add metadata
    memo["_meta"] = {
        "version": version,
        "generated_at": datetime.now().isoformat(),
        "pipeline": "Clara Automation Pipeline"
    }
    dirpath = get_account_dir(account_id, version)
    filepath = dirpath / "account_memo.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(memo, f, indent=2)
    print(f"  ✅ Saved memo: {filepath}")
    return str(filepath)


def save_agent_spec(account_id: str, spec: dict, version: str = "v1") -> str:
    """Save Retell agent spec JSON."""
    spec["_meta"] = {
        "version": version,
        "generated_at": datetime.now().isoformat()
    }
    dirpath = get_account_dir(account_id, version)
    filepath = dirpath / "agent_spec.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2)
    print(f"  ✅ Saved agent spec: {filepath}")
    return str(filepath)


def save_changelog(account_id: str, changelog_md: str, changelog_json: dict) -> str:
    """Save changelog files."""
    # Save under account root (not versioned - spans v1→v2)
    dirpath = BASE_OUTPUT_DIR / account_id
    dirpath.mkdir(parents=True, exist_ok=True)

    md_path = dirpath / "changelog.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(changelog_md)

    json_path = dirpath / "changelog.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(changelog_json, f, indent=2)

    print(f"  ✅ Saved changelog: {md_path}")
    return str(md_path)


def load_memo(account_id: str, version: str = "v1") -> dict:
    """Load account memo from storage."""
    filepath = BASE_OUTPUT_DIR / account_id / version / "account_memo.json"
    if not filepath.exists():
        raise FileNotFoundError(f"No memo found for account {account_id} {version}")
    with open(filepath) as f:
        return json.load(f)


def load_agent_spec(account_id: str, version: str = "v1") -> dict:
    """Load agent spec from storage."""
    filepath = BASE_OUTPUT_DIR / account_id / version / "agent_spec.json"
    if not filepath.exists():
        raise FileNotFoundError(f"No agent spec found for account {account_id} {version}")
    with open(filepath) as f:
        return json.load(f)


def list_accounts() -> list:
    """List all account IDs with existing outputs."""
    if not BASE_OUTPUT_DIR.exists():
        return []
    return [d.name for d in BASE_OUTPUT_DIR.iterdir() if d.is_dir()]


def print_summary():
    """Print a summary of all stored accounts."""
    accounts = list_accounts()
    print(f"\n{'='*50}")
    print(f"📁 CLARA PIPELINE - OUTPUT SUMMARY")
    print(f"{'='*50}")
    if not accounts:
        print("No accounts processed yet.")
        return
    for acct in sorted(accounts):
        acct_dir = BASE_OUTPUT_DIR / acct
        versions = [d.name for d in acct_dir.iterdir() if d.is_dir()]
        has_changelog = (acct_dir / "changelog.md").exists()
        print(f"\n  Account {acct}:")
        print(f"    Versions: {', '.join(sorted(versions))}")
        print(f"    Changelog: {'✅' if has_changelog else '❌'}")
    print(f"\n{'='*50}\n")
