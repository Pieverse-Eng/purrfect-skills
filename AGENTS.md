# Venue Skill Instructions

## Research ownership

Hosted market discovery, reference candles, and cross-venue cost comparison
are implemented by fx tools. Platform owns configured-venue detection.
Keep venue execution instructions and public market command references in
the skills; do not duplicate the hosted research workflow or its fee tables.

## Wrapper and vendor skills

When a venue skill is a wrapper/router around vendored skills:

- Every vendored `SKILL.md` behind that wrapper must include both fields in its
  frontmatter:

  ```yaml
  disable-model-invocation: true
  user-invocable: false
  ```

- These fields prevent vendor skills from being selected or invoked as peers of
  the wrapper. The wrapper remains the single discoverable routing entry point.
- Preserve both fields whenever vendored skills are imported or refreshed.
