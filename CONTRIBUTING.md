# Contributing to heif-converter

Thank you for your interest in contributing to `heif-converter`! We welcome contributions, improvements, bug reports, and feature requests from the creator and developer community.

---

## 📜 Reciprocal Open Source (AGPL-3.0)

`heif-converter` is licensed under the **GNU Affero General Public License v3.0 or later (AGPL-3.0-or-later)**. 

### Why AGPL-3.0?
The goal of this project is to foster a genuinely open, reciprocal creative toolchain:
- **Share-Alike / Copyleft**: If you modify, extend, or build upon `heif-converter` and distribute it (or host it as a service/API), you are required to share your improvements under the same AGPL-3.0 license.
- **Preventing Closed-Source Enclosure**: Proprietary wrappers and cloud platforms cannot absorb community contributions into closed-source silos without releasing their enhancements.
- By contributing, you agree that your contributions will be licensed under AGPL-3.0-or-later.

---

## 💡 Ways to Contribute

1. **Camera & Format Support**:
   - Adding ICC profiles and color curves for new cameras (e.g., Canon EOS R5/R6 HIF, Nikon Z8/Z9 HLG, Fujifilm X-T5/X-H2 HIF, Hasselblad).
   - Tone-mapping curve adjustments for specific creative LUT workflows.
2. **Performance & Reliability**:
   - Benchmarks on Apple Silicon (M1/M2/M3/M4) vs Intel Macs.
   - Robust path handling and edge cases in diverse shell environments (zsh, bash, fish).
3. **Bug Reports & Edge Cases**:
   - Color shifts or highlight clipping in specific camera firmwares.
   - Files with uncommon metadata tags or corrupt headers.

---

## 🛠️ Local Development & Testing

### 1. Clone & Set Up

The project has **zero external third-party dependencies**; it leverages Python standard library and native macOS `sips`:

```bash
git clone https://github.com/vecyang1/heif-converter.git
cd heif-converter
```

### 2. Run the Test Suite

Run the full unit and live integration test suite:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Make sure all tests pass before submitting your PR.

### 3. Add Tests for New Features

When adding features or fixing bugs, please add corresponding test cases in `tests/test_converter.py`.

---

## 🚀 Pull Request Guidelines

1. **Fork the Repository**: Create your feature branch (`git checkout -b feature/my-feature`).
2. **Keep Commits Clean**: Use clear, descriptive commit messages (e.g. `feat: add Canon HIF color profile mapping`, `fix: resolve spaces in folder paths`).
3. **Verify Tests**: Ensure `PYTHONPATH=src python3 -m unittest discover -s tests -v` passes 100%.
4. **Update Documentation**: Update `README.md` and `CHANGELOG.md` under `[Unreleased]` if introducing user-visible changes or new CLI flags.
5. **Open a PR**: Submit a Pull Request to `vecyang1/heif-converter` describing the problem and your solution.

Thank you for helping make image conversion faster, more accurate, and truly open!
