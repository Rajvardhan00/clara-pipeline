# Changelog — Account 001
**Updated:** 2026-03-05 01:50
**Version:** v1 → v2

## Changes

### `business_hours.days`
- **Before (v1):** Monday through Friday
- **After (v2):**  Monday to Friday
- **Reason:** Confirmed/updated during onboarding call

### `emergency_routing_rules.primary.phone`
- **Before (v1):** 214-555-0101
- **After (v2):**  214-555-0177
- **Reason:** Phone number updated during onboarding

### `emergency_routing_rules.secondary.phone`
- **Before (v1):** 214-555-0199
- **After (v2):**  214-555-0155
- **Reason:** Phone number updated during onboarding

### `transfer_timeout_seconds`
- **Before (v1):** 30
- **After (v2):**  60
- **Reason:** Transfer timeout confirmed during onboarding

### `emergency_definition`
- **Before (v1):** ['Client: Sprinkler head leaking or burst, fire alarm going off, anything with active water or fire. That needs someone on the phone immediately.']
- **After (v2):**  ['Client: Sprinkler head leaking or burst, fire alarm going off, anything with active water or fire. That needs someone on the phone immediately.', "Client: Add one more: if they say they smell smoke, that's also an emergency."]
- **Reason:** New emergency triggers added from onboarding: ["Client: Add one more: if they say they smell smoke, that's also an emergency."]

### `integration_constraints`
- **Before (v1):** ["Client: We use ServiceTrade for job management. But don't create sprinkler emergency jobs automatically - our dispatcher handles that manually."]
- **After (v2):**  ["Client: We use ServiceTrade for job management. But don't create sprinkler emergency jobs automatically - our dispatcher handles that manually.", "Client: Correct. Also, don't create inspection jobs automatically either. Everything goes through our coordinator."]
- **Reason:** New constraints added during onboarding: ["Client: Correct. Also, don't create inspection jobs automatically either. Everything goes through our coordinator."]

## New Constraints Added
- Client: Correct. Also, don't create inspection jobs automatically either. Everything goes through our coordinator.

## Still Unknown / Needs Clarification
- ❓ Office address not found in transcript — needs confirmation