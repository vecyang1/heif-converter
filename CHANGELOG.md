# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-09-08

### Added
- **Recursive Directory Scanning**: Added `-r` / `--recursive` flag to automatically search nested subfolders for supported photos.
- **Tilde & Quote Resilient Pathing**: Fully expanded user tilde (`~`) and stripped enclosing quotes across all argument parsing and space-recovery pipelines.
- **Auto-mkdir for Output Directories**: Automatically creates nested `--outdir` paths before invoking `sips`, preventing missing directory write failures.
- **WebP Export Support**: Bridging pipeline converting HDR/wide-gamut inputs to WebP via ColorSync-preserved intermediate PNG with `cwebp` or `Pillow`.
- **Extended Formats**: Added native support for AVIF, TIFF, BMP, and GIF outputs.
- **GitHub Actions CI Matrix**: Automated continuous integration on `macos-latest` across Python 3.9, 3.10, 3.11, 3.12, and 3.13.
- **Open Source Collaboration Templates**: GitHub Bug Report, Feature Request, and Pull Request templates in `.github/`.
- **Comprehensive Two-Sided Test Suite**: Expanded `tests/test_converter.py` to 20/20 passing tests including real live HEIC iPhone 15 Pro Max conversion, ColorSync Display P3 verification, adversarial non-image file handling, and exit code validation.
- **Executable Wrappers**: Added `bin/jpeg` executable wrapper and `--version` CLI flag.
- **Reciprocal AGPL-3.0 Licensing**: Relicensed to GNU AGPL-3.0-or-later with detailed `CONTRIBUTING.md` guidelines.

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
