# heif-converter

[![License: AGPL-3.0-or-later](https://img.shields.io/badge/License-AGPL--3.0--or--later-blue.svg)](LICENSE)
[![Platform: macOS](https://img.shields.io/badge/Platform-macOS-lightgrey.svg)](https://apple.com)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8+-brightgreen.svg)](https://python.org)

High-performance, multi-threaded HEIF / HEIC / HIF to PNG / JPG batch converter for macOS. Features native **ColorSync ICC color management** (Display P3 & sRGB), automatic unquoted whitespace-resilient path recovery, and non-destructive versioning.

Designed specifically for photographers, videographers, and creators working with **Sony A7S3 / A7M4** (10-bit HIF) and **Apple iPhone** (HEIC/ProRAW) media destined for AI upscaling (Topaz Photo AI), social sharing, or archival.

---

## 💡 Why This Tool?

Standard preview tools and naive image converters frequently output "washed out" or dull colors when handling modern 10-bit HDR HEIF files because they fail to map Apple/Sony Rec.2020 wide-gamut colors to proper monitor profiles.

`heif-converter` solves this by leveraging macOS's built-in `sips` engine combined with native ColorSync ICC profile matching:

- **Lossless PNG in Display P3**: Preserves 25% more color spectrum than sRGB. Ideal for AI upscaling (Topaz Photo AI), high-end displays, and Apple ecosystem viewing.
- **Compressed JPG in sRGB**: Universally compatible across legacy screens, Android, WeChat, LINE, and web applications without gamma or tint distortion.
- **Multi-threaded Performance**: Utilizes all available CPU cores via `ProcessPoolExecutor` for near-instant batch exports.
- **Smart Path Recovery**: Seamlessly handles unquoted file paths containing spaces (e.g. `png /path/IMG_8017 2.HEIC`).
- **Safe Versioning**: Never overwrites existing files; automatically appends `_v2`, `_v3` suffixes.

---

## ⚡ Quick Start

### Installation

Clone the repository and install locally:

```bash
git clone https://github.com/vecyang1/heif-converter.git
cd heif-converter
pip install .
```

Or run directly without installation:

```bash
python3 scripts/convert.py /path/to/photos
```

Or add the binaries to your `PATH`:

```bash
export PATH="$HOME/path/to/heif-converter/bin:$PATH"
```

### Shell Shortcuts (`~/.zshrc`)

Add the following to your `~/.zshrc` for effortless terminal usage:

```bash
# HEIF/HEIC image converter shortcuts
_heif_converter() {
  python3 "$HOME/Documents/A-coding/26.09.08-heif-converter/scripts/convert.py" "$@"
}
png() {
  _heif_converter --format png "$@"
}
jpg() {
  _heif_converter --format jpg "$@"
}
jpeg() {
  _heif_converter --format jpeg "$@"
}
heif() {
  _heif_converter "$@"
}
heic() {
  _heif_converter "$@"
}
```

Reload your shell:
```bash
source ~/.zshrc
```

---

## 🛠️ Usage Examples

### 1. Convert to Lossless PNG (Display P3)
Best for AI upscaling, archival, and viewing on Retina / P3 displays.

```bash
# Using the shortcut:
png /Users/username/Downloads/IMG_3618.HEIC

# Unquoted paths with spaces are automatically recovered:
png /Users/username/Downloads/IMG 8017 2.HEIC

# Entire folders:
png /Users/username/Pictures/Sony_A7S3_HIF/
```

### 2. Convert to Compatible JPG (sRGB)
Best for messaging apps, web publishing, or legacy screens.

```bash
# Using the shortcut:
jpg /Users/username/Downloads/IMG_3618.HEIC

# Direct CLI:
heif-converter --format jpg /Users/username/Downloads/IMG_3618.HEIC
```

### 3. Advanced Options

```bash
# Output directly into the same directory as input (no subfolder)
heif-converter --flat /path/to/image.heic

# Specify custom output directory
heif-converter --outdir /path/to/output /path/to/image.heic

# Delete original files after successful conversion
heif-converter --delete-source /path/to/image.heic

# Custom parallel workers (default is all available CPU cores)
heif-converter --workers 8 /path/to/folder

# Custom ICC color profile
heif-converter --profile "/path/to/custom_profile.icc" /path/to/image.heic
```

---

## 📊 Format Comparison

| Format | Color Space | Bit Depth | Profile | Recommended For |
| :--- | :--- | :--- | :--- | :--- |
| **HIF / HEIF** | BT.2020 / HDR | 10-bit | Rec.2020 HLG | Direct viewing on Mac/iOS HDR displays |
| **PNG** | Display P3 | Lossless 8/16-bit | `/System/Library/ColorSync/Profiles/Display P3.icc` | **Topaz Photo AI, Archiving, Apple Screens** |
| **JPG** | sRGB | 8-bit | `/System/Library/ColorSync/Profiles/sRGB Profile.icc` | **WeChat, LINE, Web, Legacy displays** |

---

## 🧪 Testing

Run the included unit test suite:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

---

## 🤝 Contributing & Community Reciprocation

We welcome contributions from photographers, creators, and developers! 

This repository is licensed under **AGPL-3.0-or-later** to guarantee that modifications, new camera color curves (Sony, Canon, Nikon, Fuji), and upstream performance fixes remain freely available to the entire community:
- Anyone who modifies and distributes this software or incorporates it into a network service/API must share their improvements under the same AGPL-3.0 terms.
- Please see [CONTRIBUTING.md](CONTRIBUTING.md) for local testing instructions and PR guidelines.

---

## 📄 License

GNU Affero General Public License v3.0 or later ([AGPL-3.0-or-later](LICENSE)) © 2026 V

