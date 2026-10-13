# Simulated account actions

These operations affect only the current owned Paper portfolio. Read the
bound account, wallet and eligible account destinations using `paper_read`.
This does not authorize real funding, bridging, integration enablement or
wallet signing.

- Simulated deposit: prepare the existing `claim` action. Display the host's
  eligibility and simulated allocation; do not invent an amount or waive limits.
- Transfer: prepare `transfer` using verified source/destination account IDs,
  asset and amount from this same Paper portfolio. One side must be the bound
  account. Ask the user to choose a destination; no silent venue substitution.
- Distinguish total, available and reserved balance. A position's equity,
  collateral pool and spot asset are not interchangeable balances.

Publish the registered card and wait for the user's independent web review.
Use the original receipt to confirm both sides of a completed transfer. Pending
or unknown is not completed. There is no real withdrawal action in this skill.
