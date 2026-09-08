import os
import glob
import subprocess
from concurrent.futures import ProcessPoolExecutor
from typing import List, Optional, Tuple

# Constants for default macOS ColorSync ICC profiles
PROFILE_P3 = "/System/Library/ColorSync/Profiles/Display P3.icc"
PROFILE_SRGB = "/System/Library/ColorSync/Profiles/sRGB Profile.icc"

SUPPORTED_INPUT_EXTS = [
    "hif", "HIF",
    "heic", "HEIC",
    "heif", "HEIF",
    "png", "PNG",
    "jpg", "JPG",
    "jpeg", "JPEG",
    "tiff", "TIFF",
    "tif", "TIF",
]


def get_unique_path(path: str) -> str:
    """Returns a unique file path by appending _v2, _v3, etc. if the target file exists."""
    if not os.path.exists(path):
        return path

    base, ext = os.path.splitext(path)
    counter = 2
    while os.path.exists(f"{base}_v{counter}{ext}"):
        counter += 1
    return f"{base}_v{counter}{ext}"


def expand_input(item: str) -> List[str]:
    """Expands one input token (directory, glob, or file) into matching image files."""
    if os.path.isdir(item):
        matches = []
        for ext in SUPPORTED_INPUT_EXTS:
            matches.extend(glob.glob(os.path.join(item, f"*.{ext}")))
        return matches
    return glob.glob(item, recursive=True)


def recover_space_split_inputs(inputs: List[str]) -> List[str]:
    """
    Rejoins adjacent shell-split tokens when they form an existing file or directory path.
    Essential for unquoted arguments containing spaces (e.g., `png /path/IMG_8017 2.HEIC`).
    """
    recovered = []
    index = 0

    while index < len(inputs):
        matched = None
        for end in range(len(inputs), index, -1):
            candidate = " ".join(inputs[index:end])
            if expand_input(candidate):
                matched = candidate
                index = end
                break

        if matched is None:
            recovered.append(inputs[index])
            index += 1
        else:
            recovered.append(matched)

    return recovered


def convert_single_file(
    file_path: str,
    target_format: str,
    profile: Optional[str] = None,
    output_dir: Optional[str] = None,
    delete_source: bool = False,
    quiet: bool = False,
) -> Tuple[bool, str]:
    """
    Converts a single image file to the target format using macOS sips tool.
    Returns (success, message_or_path).
    """
    try:
        filename = os.path.basename(file_path)
        name_no_ext = os.path.splitext(filename)[0]
        normalized_format = target_format.lower()
        sips_format = "jpeg" if normalized_format == "jpg" else normalized_format
        ext = f".{normalized_format}"

        if output_dir:
            output_path = os.path.join(output_dir, f"{name_no_ext}{ext}")
        else:
            output_path = os.path.join(os.path.dirname(file_path), f"{name_no_ext}{ext}")

        output_path = get_unique_path(output_path)

        cmd = ["sips", "-s", "format", sips_format]
        if profile and os.path.exists(profile):
            cmd.extend(["--matchTo", profile])

        cmd.extend([file_path, "--out", output_path])

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            err_msg = result.stderr.strip() or "sips error"
            if not quiet:
                print(f"FAILED: {filename} -> {err_msg}")
            return False, f"FAILED: {filename} -> {err_msg}"

        out_name = os.path.basename(output_path)
        if not quiet:
            print(f"SUCCESS: {filename} -> {out_name}")

        if delete_source:
            os.remove(file_path)
            if not quiet:
                print(f"DELETED: {filename}")

        return True, output_path
    except Exception as e:
        err_str = str(e)
        if not quiet:
            print(f"ERROR: {file_path} -> {err_str}")
        return False, f"ERROR: {file_path} -> {err_str}"


def batch_convert(
    resolved_files: List[str],
    target_format: str = "png",
    profile: Optional[str] = None,
    output_dir: Optional[str] = None,
    delete_source: bool = False,
    workers: Optional[int] = None,
    quiet: bool = False,
) -> Tuple[int, int, List[Tuple[bool, str]]]:
    """
    Executes parallel batch conversion across resolved files using ProcessPoolExecutor.
    Returns (success_count, total_count, results).
    """
    if workers is None:
        workers = os.cpu_count() or 4

    if not quiet:
        print(f"🚀 Processing {len(resolved_files)} images using {workers} workers...")

    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(
                convert_single_file,
                f,
                target_format,
                profile,
                output_dir,
                delete_source,
                quiet,
            )
            for f in resolved_files
        ]
        results = [f.result() for f in futures]

    success_count = sum(1 for ok, _ in results if ok)
    return success_count, len(resolved_files), results
