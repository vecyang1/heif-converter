#!/usr/bin/env python3
"""
Standalone execution wrapper for heif-converter.
Runs directly with zero pip install required.
"""
import os
import sys

# Ensure src is on sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from heif_converter.cli import main

if __name__ == "__main__":
    main()
