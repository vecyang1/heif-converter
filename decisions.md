> Scope: project-local. Decision register for 26.09.08-heif-converter. Cross-project decisions live in 2nd Brain decisions.md.

# Decisions Register

| ID | Title | Date | Status | Context & Rationale |
|---|---|---|---|---|
| D-001 | Standalone GitHub Repo Migration | 2026-09-08 | Accepted | Extracted from `~/.gemini/antigravity/skills/heif-converter` into standalone A-coding root and public GitHub repo (`vecyang1/heif-converter`) under MIT license. |
| D-002 | ColorSync ICC Profile Defaults | 2026-09-08 | Accepted | Map PNG exports to Display P3 by default to preserve wide gamut color; map JPG exports to sRGB to ensure universal device compatibility. |
| D-003 | Non-destructive Versioning | 2026-09-08 | Accepted | Use `_v2`, `_v3` suffixes when target output exists instead of silently overwriting user media. |
| D-004 | Shell Space Recovery | 2026-09-08 | Accepted | Implement greedy re-joining of space-split tokens in Python so unquoted file paths containing spaces resolve cleanly. |
