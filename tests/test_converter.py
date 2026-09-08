import os
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from heif_converter.cli import build_parser, run
from heif_converter.core import (
    PROFILE_P3,
    PROFILE_SRGB,
    convert_single_file,
    expand_input,
    get_unique_path,
    recover_space_split_inputs,
)


class TestHeifConverter(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="heif_test_")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_get_unique_path(self):
        sample = os.path.join(self.test_dir, "photo.png")
        # When file does not exist, return original path
        self.assertEqual(get_unique_path(sample), sample)

        # Create file
        with open(sample, "w") as f:
            f.write("test")

        # Now should return photo_v2.png
        v2 = get_unique_path(sample)
        self.assertEqual(v2, os.path.join(self.test_dir, "photo_v2.png"))

        # Create photo_v2.png as well
        with open(v2, "w") as f:
            f.write("test2")

        v3 = get_unique_path(sample)
        self.assertEqual(v3, os.path.join(self.test_dir, "photo_v3.png"))

    def test_recover_space_split_inputs(self):
        # Create a file with spaces in name
        spaced_file = os.path.join(self.test_dir, "My Photo 2026.heic")
        with open(spaced_file, "w") as f:
            f.write("mock")

        # Simulate shell splitting without quotes: [".../My", "Photo", "2026.heic"]
        prefix = self.test_dir
        split_args = [os.path.join(prefix, "My"), "Photo", "2026.heic"]

        recovered = recover_space_split_inputs(split_args)
        self.assertEqual(len(recovered), 1)
        self.assertEqual(recovered[0], spaced_file)

    def test_recover_space_split_inputs_no_match(self):
        split_args = ["some_file.heic", "another_file.heic"]
        recovered = recover_space_split_inputs(split_args)
        self.assertEqual(recovered, split_args)

    def test_cli_parser_defaults(self):
        parser = build_parser(default_format="png")
        args = parser.parse_args(["input.heic"])
        self.assertEqual(args.format, "png")
        self.assertFalse(args.flat)
        self.assertFalse(args.delete_source)
        self.assertFalse(args.quiet)

    @patch("subprocess.run")
    def test_convert_single_file_mocked_png(self, mock_run):
        mock_res = MagicMock()
        mock_res.returncode = 0
        mock_res.stderr = ""
        mock_run.return_value = mock_res

        img_path = os.path.join(self.test_dir, "test.heic")
        with open(img_path, "w") as f:
            f.write("mock")

        success, out_path = convert_single_file(
            file_path=img_path,
            target_format="png",
            profile=PROFILE_P3,
            output_dir=self.test_dir,
            quiet=True,
        )

        self.assertTrue(success)
        self.assertTrue(out_path.endswith("test.png"))
        mock_run.assert_called_once()
        cmd = mock_run.call_args[0][0]
        self.assertIn("sips", cmd)
        self.assertIn("format", cmd)
        self.assertIn("png", cmd)
        if os.path.exists(PROFILE_P3):
            self.assertIn("--matchTo", cmd)
            self.assertIn(PROFILE_P3, cmd)

    @patch("subprocess.run")
    def test_convert_single_file_mocked_jpg(self, mock_run):
        mock_res = MagicMock()
        mock_res.returncode = 0
        mock_res.stderr = ""
        mock_run.return_value = mock_res

        img_path = os.path.join(self.test_dir, "test.heic")
        with open(img_path, "w") as f:
            f.write("mock")

        success, out_path = convert_single_file(
            file_path=img_path,
            target_format="jpg",
            profile=PROFILE_SRGB,
            output_dir=self.test_dir,
            quiet=True,
        )

        self.assertTrue(success)
        self.assertTrue(out_path.endswith("test.jpg"))
        cmd = mock_run.call_args[0][0]
        self.assertIn("sips", cmd)
        self.assertIn("jpeg", cmd)  # sips uses 'jpeg' for jpg
        if os.path.exists(PROFILE_SRGB):
            self.assertIn("--matchTo", cmd)
            self.assertIn(PROFILE_SRGB, cmd)

    def test_live_sips_convert_real_image(self):
        # Create a real small image using sips or python
        src_png = os.path.join(self.test_dir, "source.png")
        # Use sips to generate a solid color test image or convert
        cmd_gen = ["sips", "-s", "format", "png", "--resampleHeightWidth", "10", "10",
                   "/System/Library/ColorSync/Profiles/Display P3.icc", "--out", src_png]
        subprocess.run(cmd_gen, capture_output=True)

        if not os.path.exists(src_png):
            # Fallback create empty file if sips can't convert icc directly
            # Test sips with a real system icon if available
            sys_icon = "/System/Library/CoreServices/Finder.app/Contents/Resources/Finder.icns"
            if os.path.exists(sys_icon):
                subprocess.run(["sips", "-s", "format", "png", sys_icon, "--out", src_png], capture_output=True)

        if os.path.exists(src_png):
            # Convert to jpg
            out_dir = os.path.join(self.test_dir, "converted_jpg")
            os.makedirs(out_dir, exist_ok=True)
            success, out_path = convert_single_file(
                file_path=src_png,
                target_format="jpg",
                profile=PROFILE_SRGB,
                output_dir=out_dir,
                quiet=True,
            )
            self.assertTrue(success)
            self.assertTrue(os.path.exists(out_path))


    def test_bin_scripts_executable(self):
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        bin_dir = os.path.join(root_dir, "bin")
        for script_name in ["heif-converter", "png", "jpg", "heic"]:
            script_path = os.path.join(bin_dir, script_name)
            self.assertTrue(os.path.exists(script_path), f"Missing {script_name}")
            self.assertTrue(os.access(script_path, os.X_OK), f"Not executable: {script_name}")

    def test_batch_convert_empty(self):
        from heif_converter.core import batch_convert
        success_count, total, results = batch_convert([], quiet=True)
        self.assertEqual(success_count, 0)
        self.assertEqual(total, 0)
        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()

