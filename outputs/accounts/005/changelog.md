# Changelog — Account 005
**Updated:** 2026-03-04 22:46
**Version:** v1 → v2

## Changes

### `business_hours.days`
- **Before (v1):** Monday through Friday
- **After (v2):** Monday-Friday
- **Reason:** Confirmed/updated during onboarding call

### `emergency_routing_rules.primary.phone`
- **Before (v1):** 310-555-0505
- **After (v2):** 310-555-0522
- **Reason:** Phone number updated during onboarding

### `emergency_definition`
- **Before (v1):** ['Client: Active sprinkler discharge, burst pipe, visible water damage from sprinkler, fire suppression system failure.', 'Client: Never create sprinkler discharge jobs in our system automatically. Dispatcher must do it.']
- **After (v2):** ['Client: Active sprinkler discharge, burst pipe, visible water damage from sprinkler, fire suppression system failure.', 'Client: Never create sprinkler discharge jobs in our system automatically. Dispatcher must do it.', "Client: Also add: if they say the building fire panel is showing a fault, that's an emergency."]
- **Reason:** New emergency triggers added from onboarding: ["Client: Also add: if they say the building fire panel is showing a fault, that's an emergency."]

### `integration_constraints`
- **Before (v1):** ['Client: Never create sprinkler discharge jobs in our system automatically. Dispatcher must do it.']
- **After (v2):** ['Client: Never create sprinkler discharge jobs in our system automatically. Dispatcher must do it.', "Client: Expand that: don't auto-create ANY job types. We want everything manually dispatched. Clara just collects and routes."]
- **Reason:** New constraints added during onboarding: ["Client: Expand that: don't auto-create ANY job types. We want everything manually dispatched. Clara just collects and routes."]

### `fallback_message`
- **Before (v1):** Someone will call you back within 15 minutes.
- **After (v2):** Someone will call you back within 10-minute.
- **Reason:** Callback promise updated during onboarding

## New Constraints Added
- Client: Expand that: don't auto-create ANY job types. We want everything manually dispatched. Clara just collects and routes.