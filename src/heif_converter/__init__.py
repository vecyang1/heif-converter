"""
heif-converter: Professional High-Performance HEIF/HEIC/HIF to PNG/JPG Converter for macOS.
Multi-threaded, space-resilient, with native Display P3 / sRGB ColorSync ICC profiling.
"""

__version__ = "1.2.0"
__author__ = "V"

from .core import (
    PROFILE_P3,
    PROFILE_SRGB,
    convert_single_file,
    batch_convert,
    recover_space_split_inputs,
    get_unique_path,
    expand_input,
)

__all__ = [
    "PROFILE_P3",
    "PROFILE_SRGB",
    "convert_single_file",
    "batch_convert",
    "recover_space_split_inputs",
    "get_unique_path",
    "expand_input",
]
