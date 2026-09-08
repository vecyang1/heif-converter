# PROJECT VAULT - 26.09.08-heif-converter

> Scope: project-local — this file governs only this project root. Cross-project truth lives in the 2nd Brain vault: /Users/vecsatfoxmailcom/Documents/Cowork/Antigravity Cowork/26.06.06 2nd Brain (contract: 00 - System/contracts/project-link-bridge.md).

> Current-state router. Read `AGENTS.md` first for operating rules, then use
> this file to find the active owner docs.

## Snapshot

- Project: 26.09.08-heif-converter
- Summary: High-performance multi-threaded HEIF/HEIC/HIF to PNG/JPG converter for macOS with Display P3 & sRGB ColorSync ICC profiling, unquoted whitespace-resilient path recovery, and non-destructive versioning.
- Current phase: Release & Registry Integration
- Last updated: 2026-09-08 20:30 by Gemini 3.8 Flash (High) (Antigravity IDE)
- Health: GREEN
- Existing docs found before init: 0

## Current Goal

- North star: Deliver a production-grade, open-source macOS HEIF converter CLI and Python package published to GitHub (`vecyang1/heif-converter`) and registered in Notion Product[OS] and 2nd Brain.
- Near-term outcome: Maintain full test coverage (9/9 passing), git push to GitHub remote, create Notion Product[OS] card, and register in 2nd Brain registries.
- Constraints: Native macOS `sips` execution; ICC profile support for Display P3 and sRGB.

## Source Pointers

| Truth Type | Owner |
| --- | --- |
| Project rules | `AGENTS.md` |
| Public/community start page | `README.md` |
| Multi-root bridge | `PROJECT_LINKS.md` |
| System architecture and module/data/integration map | `docs/architecture.md` |
| Current state, source pointers, and risks | `VAULT.md` |
| Active/backlog tasks with Created/Updated dates | `task_plan.md` |
| Dated execution evidence | `progress.md` |
| Latest resume card | `handoff.md` |
| Durable decisions | `decisions.md` |
| Folder and document boundaries | `FILE_MAP_INDEX.md` |
| Durable project docs | `docs/` |
| Runbooks and health checks | `operations/` |
| Assets, imports, exports, source material | `resources/` |
| Local project evidence | `vault/` |
| Stable cross-project memory | 2nd Brain `05 - Memory Center` |
| Cross-project router | `00 - System/registries/project-index.md` |

## Current Risks

- macOS dependency: Relies on `sips` and ColorSync profiles found on macOS systems (`/System/Library/ColorSync/Profiles/`).

## Next Actions

1. Create GitHub repository `vecyang1/heif-converter` and push main branch.
2. Register in Notion Product[OS] database.
3. Register in 2nd Brain capabilities and project index.

## Do Not

- Do not overwrite existing target files without versioning suffix (`_v2`, `_v3`).
- Do not bypass ColorSync ICC profile mapping when exporting HDR HEIF/HIF files.
