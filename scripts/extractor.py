"""
Clara Pipeline - Extractor (No API version)
Extracts structured account data from transcripts using pattern matching.
Zero cost, zero API calls, works instantly.
"""

import json
import re
import sys


def extract_account_data(transcript: str, account_id: str = None) -> dict:
    t = transcript

    def find(patterns, default=None):
        for pattern in patterns:
            m = re.search(pattern, t, re.IGNORECASE | re.MULTILINE)
            if m:
                return m.group(1).strip()
        return default

    # ── Company name — header line first, then fallback ──────
    company = find([
        r"^Company:\s*(.+)$",                          # "Company: BlazeSafe Fire Protection"
        r"we'?re\s+([\w][\w\s&]+(?:LLC|Inc|Corp|Services|Systems|Protection|Contractors|HVAC|Electrical|Sprinkler|Alarm))",
    ], "Unknown Company")
    # Clean up any trailing date or junk
    if company:
        company = re.split(r'\s*\n|\s*Date:', company)[0].strip()

    # ── Contact ───────────────────────────────────────────────
    contact = find([r"Client\s*\(([^)]+)\)"], None)

    # ── Business hours ────────────────────────────────────────
    days = find([
        r"(Monday\s*(?:through|to)\s*(?:Friday|Saturday|Sunday))",
        r"(Mon\s*(?:through|to)\s*(?:Fri|Sat|Sun))",
        r"(Monday,\s*Tuesday[^,\n]+(?:Friday|Saturday))",
    ], "Monday-Friday")

    start_time = find([r"(\d{1,2}(?::\d{2})?\s*[aA][mM])\s*(?:to|-)"], "08:00")
    end_time   = find([r"(?:to|-)\s*(\d{1,2}(?::\d{2})?\s*[pP][mM])"], "17:00")
    timezone   = find([r"\b(Central|Eastern|Pacific|Mountain)\b"], "Central")

    # ── Phone numbers (only from Client lines, not Rep lines) ─
    client_lines = "\n".join(
        line for line in t.split("\n")
        if re.match(r'\s*Client', line, re.IGNORECASE)
    )
    phones = list(dict.fromkeys(re.findall(r'\b\d{3}-\d{3}-\d{4}\b', client_lines)))
    # Fallback: all phones if none found in client lines
    if not phones:
        phones = list(dict.fromkeys(re.findall(r'\b\d{3}-\d{3}-\d{4}\b', t)))

    # ── Timeout ───────────────────────────────────────────────
    raw_timeout = find([
        r'(\d+)\s*seconds?\s*(?:timeout|wait|ring|after)',
        r'(?:after|within|wait)\s*(\d+)\s*seconds?',
        r'timeout.*?(\d+)\s*sec',
    ], "30")
    timeout = int(raw_timeout) if str(raw_timeout).isdigit() else 30

    # ── Callback promise ──────────────────────────────────────
    callback = find([
        r'within\s*(\d+\s*minutes?)',
        r'(\d+[\s-]minute)\s*(?:callback|response|call back)',
    ], "15 minutes")

    # ── Emergency triggers — CLIENT lines only ────────────────
    emergency_keywords = ['leak','burst','fire alarm','discharge','sparking',
                          'smoke','cooling fail','outage','suppression','fault',
                          'arcing','live wire','power outage','server room',
                          'active water','active fire','refrigerant','temperature above']
    emergencies = []
    for line in t.split('\n'):
        if not re.match(r'\s*Client', line, re.IGNORECASE):
            continue
        # Remove "Client (Name):" prefix
        clean_line = re.sub(r'^Client\s*\([^)]+\):\s*', '', line).strip()
        if any(k in clean_line.lower() for k in emergency_keywords):
            if len(clean_line) > 10:
                emergencies.append(clean_line)

    # ── Integration constraints — CLIENT lines only ───────────
    constraint_keywords = ["servicetrade","servicetitan","servicemax",
                           "don't create","never create","do not create",
                           "no auto","manually dispatch","manually"]
    constraints = []
    for line in t.split('\n'):
        if not re.match(r'\s*Client', line, re.IGNORECASE):
            continue
        clean_line = re.sub(r'^Client\s*\([^)]+\):\s*', '', line).strip()
        if any(k in clean_line.lower() for k in constraint_keywords):
            if len(clean_line) > 10 and clean_line not in constraints:
                constraints.append(clean_line)

    # ── Services ──────────────────────────────────────────────
    services = []
    for kw, label in [("sprinkler","Fire Sprinkler"),("fire alarm","Fire Alarm"),
                       ("electrical","Electrical"),("hvac","HVAC"),
                       ("inspection","Inspection"),("install","Installation"),
                       ("repair","Repair")]:
        if kw in t.lower() and label not in services:
            services.append(label)

    # ── Unknowns ──────────────────────────────────────────────
    unknowns = []
    if not phones:
        unknowns.append("No transfer phone numbers found — need dispatch number")
    if not emergencies:
        unknowns.append("Emergency definition not clearly stated — needs confirmation")
    if len(phones) < 2:
        unknowns.append("Only one phone number found — secondary fallback number needed")

    return {
        "account_id": account_id or "unknown",
        "company_name": company,
        "primary_contact": contact,
        "business_hours": {
            "days": days,
            "start": start_time,
            "end": end_time,
            "timezone": timezone,
            "exceptions": None
        },
        "office_address": None,
        "services_supported": services,
        "emergency_definition": list(dict.fromkeys(emergencies))[:6],
        "emergency_routing_rules": {
            "primary":   {"name": "Dispatch",            "phone": phones[0] if len(phones)>0 else None},
            "secondary": {"name": "On-call / Backup",    "phone": phones[1] if len(phones)>1 else None},
            "tertiary":  {"name": "Additional Fallback", "phone": phones[2] if len(phones)>2 else None},
            "transfer_timeout_seconds": timeout,
            "fallback_message": f"Someone will call you back within {callback}."
        },
        "non_emergency_routing_rules": {
            "action": "Collect name, number, and description. Confirm next-business-day followup.",
            "notes": None
        },
        "call_transfer_rules": {
            "timeout_seconds": timeout,
            "retry_order": [p for p in phones[:3] if p],
            "fail_action": f"Apologize and promise callback within {callback}"
        },
        "integration_constraints": constraints,
        "after_hours_flow_summary": (
            f"Greet after-hours. Ask purpose. Confirm emergency. "
            f"Emergency: collect name/number/address → transfer to {phones[0] if phones else 'dispatch'}. "
            f"Fail: promise callback within {callback}. "
            f"Non-emergency: collect details, confirm next-business-day followup."
        ),
        "office_hours_flow_summary": (
            f"Greet caller. Ask purpose. Collect name and number. "
            f"Route emergency to {phones[0] if phones else 'dispatch'}, non-emergency to scheduling."
        ),
        "questions_or_unknowns": unknowns,
        "notes": f"Auto-extracted from transcript. Review emergency_definition for completeness."
    }


def load_transcript(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()


def split_multi_transcript(text: str) -> list:
    sections = re.split(r'\n---\n', text)
    results = []
    for section in sections:
        section = section.strip()
        if not section:
            continue
        match = re.search(r'Account[:\s#]*(\d+)', section, re.IGNORECASE)
        acct_id = match.group(1).zfill(3) if match else None
        results.append({"account_id": acct_id, "text": section})
    return results


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extractor.py <transcript_file>")
        sys.exit(1)
    text = load_transcript(sys.argv[1])
    chunks = split_multi_transcript(text)
    for chunk in chunks:
        data = extract_account_data(chunk["text"], chunk["account_id"])
        print(json.dumps(data, indent=2))
