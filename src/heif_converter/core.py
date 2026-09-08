import glob
import os
import shutil
import subprocess
import tempfile
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
    "bmp", "BMP",
    "gif", "GIF",
    "avif", "AVIF",
    "webp", "WEBP",
]

# Formats that macOS sips natively writes
SIPS_WRITABLE_FORMATS = {
    "png": "png",
    "jpg": "jpeg",
    "jpeg": "jpeg",
    "tiff": "tiff",
    "tif": "tiff",
    "bmp": "bmp",
    "gif": "gif",
    "heic": "heic",
    "avif": "avif",
}


def get_unique_path(path: str, existing_paths: Optional[set] = None) -> str:
    """
    Returns a unique file path by appending _v2, _v3, etc. if the target file
    already exists on disk or was allocated within an existing batch reservation set.
    """
    def is_occupied(p: str) -> bool:
        if os.path.exists(p):
            return True
        if existing_paths is not None and p in existing_paths:
            return True
        return False

    if not is_occupied(path):
        return path

    base, ext = os.path.splitext(path)
    counter = 2
    while is_occupied(f"{base}_v{counter}{ext}"):
        counter += 1
    return f"{base}_v{counter}{ext}"


def expand_input(item: str, recursive: bool = False) -> List[str]:
    """
    Expands one input token (directory, glob, or file) into matching image files.
    Expands user tilde (~), strips surrounding quotes, and optionally scans recursively.
    Filters out non-image files and directories from wildcard expansions.
    """
    if not item:
        return []

    item = os.path.expanduser(item.strip("'\""))
    if not item:
        return []

    valid_exts = {e.lower() for e in SUPPORTED_INPUT_EXTS}

    if os.path.isdir(item):
        matches = []
        if recursive:
            for root, _, files in os.walk(item):
                for f in files:
                    ext = os.path.splitext(f)[1].lstrip(".").lower()
                    if ext in valid_exts:
                        matches.append(os.path.join(root, f))
        else:
            for ext in SUPPORTED_INPUT_EXTS:
                matches.extend(glob.glob(os.path.join(item, f"*.{ext}")))
        return sorted(list(set(matches)))

    if os.path.isfile(item):
        return [item]

    raw_matches = glob.glob(item, recursive=recursive)
    if not raw_matches:
        return []

    filtered = []
    for match in raw_matches:
        if os.path.isfile(match):
            ext = os.path.splitext(match)[1].lstrip(".").lower()
            if ext in valid_exts:
                filtered.append(match)
    return sorted(list(set(filtered)))


def recover_space_split_inputs(inputs: List[str], recursive: bool = False) -> List[str]:
    """
    Rejoins adjacent shell-split tokens when they form an existing file or directory path.
    Essential for unquoted arguments containing spaces (e.g., `png /path/IMG_8017 2.HEIC`).
    """
    cleaned_inputs = [token.strip("'\"") for token in inputs if token.strip("'\"")]
    recovered = []
    index = 0

    while index < len(cleaned_inputs):
        matched = None
        for end in range(len(cleaned_inputs), index, -1):
            candidate = " ".join(cleaned_inputs[index:end])
            expanded = expand_input(candidate, recursive=recursive)
            if expanded:
                matched = candidate
                index = end
                break

        if matched is None:
            recovered.append(cleaned_inputs[index])
            index += 1
        else:
            recovered.append(matched)

    return recovered


def _convert_to_webp(
    source_file: str,
    output_path: str,
    profile: Optional[str] = None,
) -> Tuple[bool, str]:
    """
    Converts an image to WebP format.
    Because macOS sips cannot write webp natively, this converts via an intermediate
    ColorSync-processed PNG using cwebp (if available) or Pillow.
    """
    has_cwebp = shutil.which("cwebp") is not None
    try:
        from PIL import Image  # type: ignore
        has_pillow = True
    except ImportError:
        has_pillow = False

    if not has_cwebp and not has_pillow:
        return False, (
            "Target format 'webp' is not natively writable by macOS sips. "
            "Please install 'cwebp' (`brew install webp`) or 'Pillow' (`pip install pillow`) to export WebP."
        )

    # Step 1: Render intermediate lossless PNG with ColorSync profile via sips
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
        tmp_png = tmp_file.name

    try:
        cmd_intermediate = ["sips", "-s", "format", "png"]
        if profile and os.path.exists(profile):
            cmd_intermediate.extend(["--matchTo", profile])
        cmd_intermediate.extend([source_file, "--out", tmp_png])

        sips_res = subprocess.run(cmd_intermediate, capture_output=True, text=True)
        if sips_res.returncode != 0:
            err = sips_res.stderr.strip() or sips_res.stdout.strip() or "intermediate sips error"
            return False, err

        # Step 2: Encode to WebP
        if has_cwebp:
            cwebp_cmd = ["cwebp", "-q", "85", tmp_png, "-o", output_path]
            cwebp_res = subprocess.run(cwebp_cmd, capture_output=True, text=True)
            if cwebp_res.returncode != 0:
                if os.path.exists(output_path):
                    try:
                        os.remove(output_path)
                    except OSError:
                        pass
                return False, cwebp_res.stderr.strip() or "cwebp encoding error"
        else:
            with Image.open(tmp_png) as img:
                img.save(output_path, "WEBP", quality=85)

        return True, output_path
    finally:
        if os.path.exists(tmp_png):
            try:
                os.remove(tmp_png)
            except OSError:
                pass


def convert_single_file(
    file_path: str,
    target_format: str,
    profile: Optional[str] = None,
    output_dir: Optional[str] = None,
    delete_source: bool = False,
    quiet: bool = False,
    target_output_path: Optional[str] = None,
) -> Tuple[bool, str]:
    """
    Converts a single image file to the target format using macOS sips tool.
    Accepts an optional pre-allocated target_output_path to prevent concurrency race conditions.
    Returns (success, message_or_path).
    """
    try:
        file_path = os.path.abspath(os.path.expanduser(file_path.strip("'\"")))
        if not os.path.isfile(file_path):
            err_msg = f"File not found: {file_path}"
            if not quiet:
                print(f"FAILED: {err_msg}")
            return False, err_msg

        filename = os.path.basename(file_path)
        name_no_ext = os.path.splitext(filename)[0]
        normalized_format = target_format.lower().lstrip(".")
        ext = f".{normalized_format}"

        # Validate explicit profile path if provided
        if profile:
            profile = os.path.abspath(os.path.expanduser(profile.strip("'\"")))
            if not os.path.exists(profile):
                err_msg = f"Color profile not found: {profile}"
                if not quiet:
                    print(f"FAILED: {filename} -> {err_msg}")
                return False, f"FAILED: {filename} -> {err_msg}"

        if target_output_path:
            output_path = os.path.abspath(os.path.expanduser(target_output_path.strip("'\"")))
            parent_dir = os.path.dirname(output_path)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)
        elif output_dir:
            output_dir = os.path.abspath(os.path.expanduser(output_dir.strip("'\"")))
            os.makedirs(output_dir, exist_ok=True)
            output_path = get_unique_path(os.path.join(output_dir, f"{name_no_ext}{ext}"))
        else:
            output_path = get_unique_path(os.path.join(os.path.dirname(file_path), f"{name_no_ext}{ext}"))

        # Handle WebP format via bridging helper
        if normalized_format == "webp":
            success, result_str = _convert_to_webp(file_path, output_path, profile)
            if not success:
                if not quiet:
                    print(f"FAILED: {filename} -> {result_str}")
                return False, f"FAILED: {filename} -> {result_str}"
        else:
            # Map format for sips
            sips_format = SIPS_WRITABLE_FORMATS.get(normalized_format, normalized_format)
            cmd = ["sips", "-s", "format", sips_format]
            if profile and os.path.exists(profile):
                cmd.extend(["--matchTo", profile])

            cmd.extend([file_path, "--out", output_path])

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                err_msg = result.stderr.strip() or result.stdout.strip() or "sips error"
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
    Pre-allocates collision-free output paths to prevent parallel worker write contention.
    Returns (success_count, total_count, results).
    """
    if not resolved_files:
        return 0, 0, []

    if workers is None:
        workers = os.cpu_count() or 4

    if output_dir:
        output_dir = os.path.abspath(os.path.expanduser(output_dir.strip("'\"")))
        os.makedirs(output_dir, exist_ok=True)

    # Pre-allocate collision-free unique destination paths
    normalized_format = target_format.lower().lstrip(".")
    ext = f".{normalized_format}"
    allocated_paths: set = set()
    conversion_tasks: List[Tuple[str, str]] = []

    for f in resolved_files:
        filename = os.path.basename(f)
        name_no_ext = os.path.splitext(filename)[0]
        if output_dir:
            candidate_dst = os.path.join(output_dir, f"{name_no_ext}{ext}")
        else:
            candidate_dst = os.path.join(os.path.dirname(f), f"{name_no_ext}{ext}")
        unique_dst = get_unique_path(candidate_dst, existing_paths=allocated_paths)
        allocated_paths.add(unique_dst)
        conversion_tasks.append((f, unique_dst))

    if not quiet:
        print(f"🚀 Processing {len(resolved_files)} images using {workers} workers...")

    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(
                convert_single_file,
                file_path=src,
                target_format=target_format,
                profile=profile,
                output_dir=None,
                delete_source=delete_source,
                quiet=quiet,
                target_output_path=dst,
            )
            for src, dst in conversion_tasks
        ]
        results = [f.result() for f in futures]

    success_count = sum(1 for ok, _ in results if ok)
    return success_count, len(resolved_files), results
