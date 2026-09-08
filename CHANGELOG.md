# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.2] - 2026-09-08

### Added
- Open-source standalone repository layout with `pyproject.toml`, standard CLI entry points (`heif-converter`, `png-convert`, `jpg-convert`).
- Executable binary wrappers in `bin/` (`bin/heif-converter`, `bin/png`, `bin/jpg`, `bin/heic`).
- Comprehensive unit and integration test suite in `tests/test_converter.py` covering path recovery, mock sips commands, live sips execution, and collision avoidance.
- V.A.U.L.T. method project governance and architecture documentation.
- Project registration into Notion Product[OS] and 2nd Brain capabilities registry.

### Changed
- Refactored core logic into `heif_converter.core` and `heif_converter.cli` with clean programmatic interfaces (`batch_convert`, `convert_single_file`).

### Fixed
- Preserved space-resilient recovery for unquoted shell arguments (e.g. `png /path/IMG_8017 2.HEIC`).
- Non-destructive unique naming (`_v2`, `_v3`) when output files already exist.

## [1.1.0] - 2026-04-30

### Added
- Native macOS ColorSync ICC color profiling (`Display P3` for PNG, `sRGB` for JPG/JPEG).
- Parallel multi-core batch processing using `ProcessPoolExecutor`.
