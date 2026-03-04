"""
Clara Pipeline - Onboarding Updater (No API version)
Merges onboarding transcript data into v1 memo to produce v2 + changelog.
Zero cost, zero API calls.
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from extractor import extract_account_data, split_multi_transcript


def apply_onboarding_updates(v1_memo: dict, onboarding_transcript: str) -> dict:
    """Merge onboarding data into v1 memo, producing v2 + changelog."""

    new_data = extract_account_data(onboarding_transcript, v1_memo.get("account_id"))

    changelog = []
    v2 = json.loads(json.dumps(v1_memo))  # deep copy

    def log_change(field, old, new, reason):
        if str(old) != str(new):
            changelog.append({
                "field": field,
                "old_value": old,
                "new_value": new,
                "reason": reason,
            })

    # ── Business hours ─────────────────────────────────────────
    # FIX: use safe .get() with fallback dicts — prevents KeyError when v1 memo
    # was built from a sparse demo transcript that lacked business_hours entirely.
    v1_bh = v1_memo.get("business_hours") or {}
    new_bh = new_data.get("business_hours") or {}
    if "business_hours" not in v2:
        v2["business_hours"] = {}
    for key in ["days", "start", "end", "timezone"]:
        old_val = v1_bh.get(key)
        new_val = new_bh.get(key)
        if new_val and new_val != old_val:
            v2["business_hours"][key] = new_val
            log_change(f"business_hours.{key}", old_val, new_val,
                       "Confirmed/updated during onboarding call")

    # ── Phone numbers ──────────────────────────────────────────
    v1_routing = v1_memo.get("emergency_routing_rules") or {}
    for role in ["primary", "secondary", "tertiary"]:
        old_p = v1_routing.get(role, {}).get("phone")
        new_p = (new_data.get("emergency_routing_rules") or {}).get(role, {}).get("phone")
        if new_p and new_p != old_p:
            if "emergency_routing_rules" not in v2:
                v2["emergency_routing_rules"] = {}
            if role not in v2["emergency_routing_rules"]:
                v2["emergency_routing_rules"][role] = {}
            v2["emergency_routing_rules"][role]["phone"] = new_p
            v2["call_transfer_rules"]["retry_order"] = [
                v2["emergency_routing_rules"].get(r, {}).get("phone")
                for r in ["primary", "secondary", "tertiary"]
                if v2["emergency_routing_rules"].get(r, {}).get("phone")
            ]
            log_change(f"emergency_routing_rules.{role}.phone", old_p, new_p,
                       "Phone number updated during onboarding")

    # ── Timeout ────────────────────────────────────────────────
    old_t = v1_routing.get("transfer_timeout_seconds")
    new_t = (new_data.get("emergency_routing_rules") or {}).get("transfer_timeout_seconds")
    if new_t and new_t != old_t:
        v2["emergency_routing_rules"]["transfer_timeout_seconds"] = new_t
        v2["call_transfer_rules"]["timeout_seconds"] = new_t
        log_change("transfer_timeout_seconds", old_t, new_t,
                   "Transfer timeout confirmed during onboarding")

    # ── Emergency definition — only add clean NEW items ────────
    old_em = v1_memo.get("emergency_definition") or []
    new_em = new_data.get("emergency_definition") or []
    clean_new_em = [
        e for e in new_em
        if e not in old_em
        and not e.lower().startswith("rep:")
        and len(e) > 10
    ]
    if clean_new_em:
        merged = old_em + clean_new_em
        v2["emergency_definition"] = merged
        log_change("emergency_definition", old_em, merged,
                   f"New emergency triggers added from onboarding: {clean_new_em}")

    # ── Integration constraints — only clean NEW items ─────────
    old_c = v1_memo.get("integration_constraints") or []
    new_c = new_data.get("integration_constraints") or []
    clean_new_c = [
        c for c in new_c
        if c not in old_c
        and not c.lower().startswith("rep:")
        and len(c) > 10
    ]
    if clean_new_c:
        merged_c = old_c + clean_new_c
        v2["integration_constraints"] = merged_c
        log_change("integration_constraints", old_c, merged_c,
                   f"New constraints added during onboarding: {clean_new_c}")

    # ── Services supported — merge new services ────────────────
    # FIX: onboarding may introduce new service lines; merge them in.
    old_svc = v1_memo.get("services_supported") or []
    new_svc = new_data.get("services_supported") or []
    added_svc = [s for s in new_svc if s not in old_svc]
    if added_svc:
        merged_svc = old_svc + added_svc
        v2["services_supported"] = merged_svc
        log_change("services_supported", old_svc, merged_svc,
                   f"New services identified during onboarding: {added_svc}")

    # ── Callback message ───────────────────────────────────────
    old_cb = v1_routing.get("fallback_message")
    new_cb = (new_data.get("emergency_routing_rules") or {}).get("fallback_message")
    if new_cb and new_cb != old_cb:
        v2["emergency_routing_rules"]["fallback_message"] = new_cb
        v2["call_transfer_rules"]["fail_action"] = new_cb
        log_change("fallback_message", old_cb, new_cb,
                   "Callback promise updated during onboarding")

    # ── Resolve unknowns that onboarding answered ──────────────
    old_unknowns = v1_memo.get("questions_or_unknowns") or []
    new_phones = [
        (new_data.get("emergency_routing_rules") or {}).get(r, {}).get("phone")
        for r in ["primary", "secondary", "tertiary"]
        if (new_data.get("emergency_routing_rules") or {}).get(r, {}).get("phone")
    ]
    resolved, still_unknown = [], []
    for u in old_unknowns:
        if "phone" in u.lower() and new_phones:
            resolved.append(u)
        elif "emergency" in u.lower() and new_data.get("emergency_definition"):
            resolved.append(u)
        elif "address" in u.lower() and new_data.get("office_address"):
            resolved.append(u)
        else:
            still_unknown.append(u)

    v2["questions_or_unknowns"] = still_unknown
    v2["_meta"] = {
        "version": "v2",
        "generated_at": datetime.now().isoformat(),
        "pipeline": "Clara Automation Pipeline",
    }

    return {
        "v2_memo": v2,
        "changelog": changelog,
        "new_constraints": clean_new_c if clean_new_c else [],
        "resolved_unknowns": resolved,
        "still_unknown": still_unknown,
    }


def format_changelog_md(account_id: str, data: dict) -> str:
    lines = [
        f"# Changelog — Account {account_id}",
        f"**Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Version:** v1 → v2",
        "",
        "## Changes",
    ]
    for change in data.get("changelog", []):
        lines += [
            f"\n### `{change['field']}`",
            f"- **Before (v1):** {change['old_value']}",
            f"- **After (v2):**  {change['new_value']}",
            f"- **Reason:** {change['reason']}",
        ]
    if data.get("new_constraints"):
        lines += ["\n## New Constraints Added"] + [f"- {c}" for c in data["new_constraints"]]
    if data.get("resolved_unknowns"):
        lines += ["\n## Resolved Unknowns"] + [f"- ✅ {r}" for r in data["resolved_unknowns"]]
    if data.get("still_unknown"):
        lines += ["\n## Still Unknown / Needs Clarification"] + [f"- ❓ {u}" for u in data["still_unknown"]]
    if not data.get("changelog"):
        lines += ["\n_No changes detected — onboarding confirmed existing configuration._"]
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python onboarding_updater.py <v1_memo.json> <onboarding_transcript.txt>")
        sys.exit(1)
    with open(sys.argv[1]) as f:
        v1 = json.load(f)
    with open(sys.argv[2]) as f:
        transcript = f.read()
    result = apply_onboarding_updates(v1, transcript)
    print(json.dumps(result, indent=2))