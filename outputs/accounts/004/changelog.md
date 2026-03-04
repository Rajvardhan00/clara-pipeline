# Changelog — Account 004
**Updated:** 2026-03-05 01:50
**Version:** v1 → v2

## Changes

### `business_hours.days`
- **Before (v1):** Monday through Saturday
- **After (v2):**  Monday-Friday
- **Reason:** Confirmed/updated during onboarding call

### `emergency_routing_rules.primary.phone`
- **Before (v1):** 602-555-0404
- **After (v2):**  602-555-0499
- **Reason:** Phone number updated during onboarding

### `emergency_definition`
- **Before (v1):** ["Client: Data center clients call at all hours if cooling fails. That's a true emergency. Regular HVAC issues can wait.", 'Client: Cooling failure in a data center, complete HVAC system down in a hospital or medical facility, refrigerant leak. Those are emergencies.']
- **After (v2):**  ["Client: Data center clients call at all hours if cooling fails. That's a true emergency. Regular HVAC issues can wait.", 'Client: Cooling failure in a data center, complete HVAC system down in a hospital or medical facility, refrigerant leak. Those are emergencies.', 'Client: Yes. Add one more: if a caller says a server room temperature is above 85 degrees, treat as emergency.']
- **Reason:** New emergency triggers added from onboarding: ['Client: Yes. Add one more: if a caller says a server room temperature is above 85 degrees, treat as emergency.']

### `integration_constraints`
- **Before (v1):** ['Client: We use ServiceTitan. No restrictions.']
- **After (v2):**  ['Client: We use ServiceTitan. No restrictions.', 'Client: New rule: never create jobs for competitor accounts. If they mention another HVAC company handled it previously, just take a message.']
- **Reason:** New constraints added during onboarding: ['Client: New rule: never create jobs for competitor accounts. If they mention another HVAC company handled it previously, just take a message.']

### `fallback_message`
- **Before (v1):** Someone will call you back within 15 minutes.
- **After (v2):**  Someone will call you back within 15-minute.
- **Reason:** Callback promise updated during onboarding

## New Constraints Added
- Client: New rule: never create jobs for competitor accounts. If they mention another HVAC company handled it previously, just take a message.

## Still Unknown / Needs Clarification
- ❓ Office address not found in transcript — needs confirmation