# ADR-0002: Centralized injectable ProductParams

## Status

Accepted (shipped MVP)

## Context

Offer series (COI1030 / EDO1036) change over time; rates, margins, and fees must stay localized and overridable in tests.

## Decision

Store offer constants in `src/bondwise/params.py` as frozen `ProductParams` plus module-level `COI` / `EDO`. `simulate(..., coi=, edo=)` injects them with those defaults.

## Consequences

Offer updates touch `params.py` (and the offer-params snapshot). Callers can substitute params without forking simulator logic.
