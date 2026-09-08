# Architecture & Color Pipeline: heif-converter

## App Summary

`heif-converter` is a high-performance macOS batch conversion tool for modern High Efficiency Image Files (HEIF/HIF) found on modern cameras like Sony A7S3/A7M4 and iPhones. It fixes the common "washed out" look by correctly mapping HDR Rec.2020 colors to standard color spaces (Display P3 for lossless PNG, sRGB for JPG).

## System Diagram

```
[ Input HEIF / HIF / HEIC / JPG / PNG ]
                   │
                   ▼
     [ Token Recovery & Expansion ]
 (rejoins unquoted arguments with spaces)
                   │
                   ▼
    [ Multi-threaded Dispatcher ]
 (ProcessPoolExecutor across CPU cores)
                   │
                   ▼
         [ macOS sips Engine ]
 ├── PNG  --> --matchTo Display P3.icc (Wide-gamut lossless)
 └── JPEG --> --matchTo sRGB Profile.icc (Universal standard)
                   │
                   ▼
      [ Non-destructive Output ]
 (Checks collision -> appends _v2, _v3)
```

## Module Map

- `src/heif_converter/core.py`: Core logic for file discovery, space recovery, collision detection, and `sips` invocation.
- `src/heif_converter/cli.py`: Command-line interface with preset entry points (`heif-converter`, `png-convert`, `jpg-convert`).
- `scripts/convert.py`: Zero-install direct runner.
- `bin/`: Shell executable wrappers for `PATH` integration (`heif-converter`, `png`, `jpg`, `heic`).

## Data And Storage

- **Input Formats**: `.hif`, `.heic`, `.heif`, `.png`, `.jpg`, `.jpeg`, `.tiff`, `.tif`
- **Output Formats**: `.png`, `.jpg`, `.jpeg`, `.tiff`, `.webp`
- **Output Structure**: Default creates `converted_<format>/` subfolder in the same directory as source, or preserves flat structure with `--flat`, or routes to `--outdir`.
- **Conflict Strategy**: If destination file exists, appends non-destructive `_v2`, `_v3` suffixes.

## Integrations And External Services

- **macOS sips (Scriptable Image Processing System)**: Native operating system image conversion engine.
- **macOS ColorSync ICC Profiles**:
  - Display P3: `/System/Library/ColorSync/Profiles/Display P3.icc`
  - sRGB: `/System/Library/ColorSync/Profiles/sRGB Profile.icc`
- **Shell Integrations**: Native shortcuts `png`, `jpg`, `jpeg`, `heif`, `heic` integrated via `~/.zshrc`.

## Runtime And Deployment

- **Runtime**: Python 3.8+ on macOS. No external third-party package dependencies needed for core execution.
- **Packaging**: Standard `pyproject.toml` using `setuptools` build backend.
- **Repository**: Public GitHub repo `https://github.com/vecyang1/heif-converter`.

## Update Triggers

- Update when macOS ColorSync profile locations change or when additional format flags (e.g. AVIF) are added.
- Update when camera manufacturer color curves (e.g., Sony S-Cinetone HEIF) require specialized ICC LUT mappings.
