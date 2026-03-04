"""
Clara Pipeline - Prompt Generator (No API version)
Builds Retell Agent Spec from account memo using templates.
Zero cost, zero API calls.
"""

import json
import sys


def generate_agent_spec(memo: dict, version: str = "v1") -> dict:
    company     = memo.get("company_name", "the company")
    tz          = memo.get("business_hours", {}).get("timezone", "Central")
    days        = memo.get("business_hours", {}).get("days", "Monday-Friday")
    start       = memo.get("business_hours", {}).get("start", "08:00")
    end         = memo.get("business_hours", {}).get("end", "17:00")
    emergencies = memo.get("emergency_definition", [])
    routing     = memo.get("emergency_routing_rules", {})
    primary     = routing.get("primary", {})
    secondary   = routing.get("secondary", {})
    tertiary    = routing.get("tertiary", {})
    timeout     = routing.get("transfer_timeout_seconds", 30)
    callback    = routing.get("fallback_message", "Someone will call you back within 15 minutes.")
    constraints = memo.get("integration_constraints", [])

    primary_phone   = primary.get("phone") or "dispatch line"
    secondary_phone = secondary.get("phone") or "backup line"
    tertiary_phone  = tertiary.get("phone")

    emergency_examples = ", ".join(emergencies[:3]) if emergencies else "active fire, system failure, emergency leak"

    retry_steps = f"Step 1: Transfer to {primary_phone}, wait {timeout} seconds."
    if secondary_phone:
        retry_steps += f" Step 2: If no answer, try {secondary_phone}."
    if tertiary_phone:
        retry_steps += f" Step 3: If still no answer, try {tertiary_phone}."
    retry_steps += f" Final: {callback}"

    system_prompt = f"""You are Clara, the virtual assistant for {company}. You are warm, professional, and efficient. You never mention that you are an AI, and you never reference any internal tools or systems.

=== BUSINESS HOURS FLOW ({days}, {start}–{end} {tz}) ===

1. GREET: "Thank you for calling {company}, this is Clara. How can I help you today?"
2. LISTEN to caller's reason for calling.
3. COLLECT INFO: "May I get your name and the best callback number for you?"
4. DETERMINE: Is this an emergency or non-emergency?
   - Emergency examples: {emergency_examples}
5. IF EMERGENCY:
   - Say: "I'm going to connect you with our team right away."
   - Attempt transfer to dispatch.
   - If transfer fails: "{callback} I sincerely apologize for the inconvenience."
6. IF NON-EMERGENCY:
   - Collect brief description of the issue.
   - Say: "I've noted your request and someone from our team will follow up with you shortly."
7. CLOSE: "Is there anything else I can help you with today?" → If no: "Thank you for calling {company}. Have a great day!"

=== AFTER HOURS FLOW ===

1. GREET: "Thank you for calling {company}. You've reached us after business hours. This is Clara. How can I assist you?"
2. ASK PURPOSE: "What is the reason for your call today?"
3. CONFIRM EMERGENCY: "Is this an emergency situation requiring immediate attention?"
4. IF YES — EMERGENCY:
   a. "I'm going to connect you with our emergency team. First, may I get your name, callback number, and the address or location of the emergency?"
   b. Collect: full name, phone number, complete address.
   c. Attempt transfer to {primary_phone}.
   d. If transfer fails after {timeout} seconds, try {secondary_phone}.
   e. If all transfers fail: "I sincerely apologize — our team is currently unavailable but I have your information and {callback} Thank you for your patience."
5. IF NO — NON-EMERGENCY:
   a. "I understand. Let me take down your information so our team can follow up."
   b. Collect: name, callback number, brief description.
   c. Say: "Our team will reach out to you during business hours ({days}, {start}–{end} {tz}). You'll receive a call back then."
6. CLOSE: "Is there anything else I can assist you with?" → If no: "Thank you for calling {company}. Have a good night!"

=== IMPORTANT RULES ===
- NEVER mention AI, automation, function calls, or internal systems.
- NEVER create service jobs automatically.{(' ' + ' '.join(constraints)) if constraints else ''}
- ALWAYS confirm caller information before transferring.
- ALWAYS give the callback promise if transfer fails.
- Keep responses concise — do not ask unnecessary questions.
"""

    return {
        "agent_name": f"{company} - Clara",
        "voice_style": "professional-warm-female",
        "version": version,
        "key_variables": {
            "company_name": company,
            "timezone": tz,
            "business_hours_description": f"{days}, {start}–{end} {tz}",
            "emergency_examples": emergency_examples,
            "primary_transfer_number": primary_phone,
            "secondary_transfer_number": secondary_phone,
            "tertiary_transfer_number": tertiary_phone,
            "transfer_timeout_seconds": timeout,
            "callback_promise": callback
        },
        "system_prompt": system_prompt,
        "call_transfer_protocol": {
            "step1": f"Transfer to {primary_phone}, wait {timeout} seconds",
            "step2": f"If no answer, transfer to {secondary_phone}",
            "step3": f"If still no answer, transfer to {tertiary_phone}" if tertiary_phone else "N/A",
            "final_fallback": callback
        },
        "fallback_protocol": callback,
        "integration_notes": constraints if constraints else ["No special integration constraints noted"],
        "do_not_do": [
            "Never mention AI or automation to callers",
            "Never mention function calls or internal tools",
            "Never create service jobs automatically",
            "Never transfer without collecting caller name and number first",
            "Never promise a specific technician name",
        ]
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python prompt_generator.py <account_memo.json> [v1|v2]")
        sys.exit(1)
    with open(sys.argv[1]) as f:
        memo = json.load(f)
    version = sys.argv[2] if len(sys.argv) > 2 else "v1"
    spec = generate_agent_spec(memo, version)
    print(json.dumps(spec, indent=2))
