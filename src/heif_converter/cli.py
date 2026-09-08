import argparse
import os
import sys
from typing import List, Optional

from .core import (
    PROFILE_P3,
    PROFILE_SRGB,
    batch_convert,
    expand_input,
    recover_space_split_inputs,
)

__version__ = "1.2.1"


def build_parser(default_format: str = "png") -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Professional Image Converter (Multi-threaded & Color Managed via macOS ColorSync)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"heif-converter {__version__}",
        help="Show program's version number and exit",
    )
    parser.add_argument(
        "inputs",
        nargs="+",
        help="Input files, directories, or globs (supports spaces in unquoted paths)",
    )
    parser.add_argument(
        "--format",
        default=default_format,
        choices=["png", "jpg", "jpeg", "tiff", "heic", "avif", "bmp", "gif", "webp"],
        help="Target image format",
    )
    parser.add_argument(
        "-r", "--recursive",
        action="store_true",
        help="Recursively scan subdirectories for matching images",
    )
    parser.add_argument(
        "--profile",
        help="Path to ICC color profile (default: Display P3 for PNG, sRGB for JPG/JPEG)",
    )
    parser.add_argument(
        "--outdir",
        help="Output directory (defaults to 'converted_<format>' inside input dir)",
    )
    parser.add_argument(
        "--flat",
        action="store_true",
        help="Store converted images in the same directory as input files",
    )
    parser.add_argument(
        "--delete-source",
        action="store_true",
        help="Delete original files after successful conversion",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=os.cpu_count() or 4,
        help="Number of parallel workers",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress informational stdout output",
    )
    return parser


def run(args: argparse.Namespace) -> int:
    # Resolve inputs (recovering unquoted paths with spaces, expanding tilde and quotes)
    recursive = getattr(args, "recursive", False)
    recovered_inputs = recover_space_split_inputs(args.inputs, recursive=recursive)
    resolved_files: List[str] = []
    unmatched_inputs: List[str] = []

    for item in recovered_inputs:
        expanded = expand_input(item, recursive=recursive)
        if expanded:
            resolved_files.extend(expanded)
        else:
            unmatched_inputs.append(item)

    resolved_files = sorted(list(set([os.path.abspath(os.path.expanduser(f)) for f in resolved_files])))

    if unmatched_inputs and not args.quiet:
        print(f"⚠️ Warning: The following input(s) did not match any supported images: {unmatched_inputs}", file=sys.stderr)

    if not resolved_files:
        if not args.quiet:
            print(f"No valid image files found for: {args.inputs}", file=sys.stderr)
        return 1

    # Determine default ICC profile if not explicitly specified
    profile: Optional[str] = args.profile
    if profile:
        profile = os.path.abspath(os.path.expanduser(profile.strip("'\"")))
        if not os.path.exists(profile):
            if not args.quiet:
                print(f"Error: Specified color profile not found: {args.profile}", file=sys.stderr)
            return 1
    else:
        fmt = args.format.lower()
        if fmt == "png":
            profile = PROFILE_P3 if os.path.exists(PROFILE_P3) else None
        elif fmt in ["jpg", "jpeg"]:
            profile = PROFILE_SRGB if os.path.exists(PROFILE_SRGB) else None

    # Determine output directory
    output_dir: Optional[str] = args.outdir
    if output_dir:
        output_dir = os.path.abspath(os.path.expanduser(output_dir.strip("'\"")))
        os.makedirs(output_dir, exist_ok=True)
    elif not args.flat:
        common_dir = os.path.dirname(resolved_files[0])
        if all(os.path.dirname(f) == common_dir for f in resolved_files):
            output_dir = os.path.join(common_dir, f"converted_{args.format}")
            os.makedirs(output_dir, exist_ok=True)

    success_count, total, _ = batch_convert(
        resolved_files=resolved_files,
        target_format=args.format,
        profile=profile,
        output_dir=output_dir,
        delete_source=args.delete_source,
        workers=args.workers,
        quiet=args.quiet,
    )

    if not args.quiet:
        print(f"\n🎉 Done! {success_count}/{total} images converted.")
        if output_dir:
            print(f"📂 Output location: {output_dir}")

    return 0 if (total > 0 and success_count == total) else 1


def main() -> None:
    parser = build_parser(default_format="png")
    args = parser.parse_args()
    sys.exit(run(args))


def main_png() -> None:
    """Preset command entry point for PNG conversion (Display P3)."""
    parser = build_parser(default_format="png")
    args = parser.parse_args()
    sys.exit(run(args))


def main_jpg() -> None:
    """Preset command entry point for JPG conversion (sRGB)."""
    parser = build_parser(default_format="jpg")
    args = parser.parse_args()
    sys.exit(run(args))


def main_jpeg() -> None:
    """Preset command entry point for JPEG conversion (sRGB)."""
    parser = build_parser(default_format="jpeg")
    args = parser.parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()
