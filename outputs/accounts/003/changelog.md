# Changelog — Account 003
**Updated:** 2026-03-04 22:46
**Version:** v1 → v2

## Changes

### `business_hours.days`
- **Before (v1):** Monday through Friday
- **After (v2):** Monday-Friday
- **Reason:** Confirmed/updated during onboarding call

### `emergency_routing_rules.primary.phone`
- **Before (v1):** 512-555-0303
- **After (v2):** 512-555-0300
- **Reason:** Phone number updated during onboarding

### `integration_constraints`
- **Before (v1):** ['Client: We use ServiceMax. No special restrictions on job creation.']
- **After (v2):** ['Client: We use ServiceMax. No special restrictions on job creation.', "Client: Actually add one: don't create emergency job tickets automatically. Only for non-emergency scheduling."]
- **Reason:** New constraints added during onboarding: ["Client: Actually add one: don't create emergency job tickets automatically. Only for non-emergency scheduling."]

### `fallback_message`
- **Before (v1):** Someone will call you back within 20 minutes.
- **After (v2):** Someone will call you back within 20-minute.
- **Reason:** Callback promise updated during onboarding

## New Constraints Added
- Client: Actually add one: don't create emergency job tickets automatically. Only for non-emergency scheduling.