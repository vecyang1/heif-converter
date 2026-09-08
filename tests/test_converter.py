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
    batch_convert,
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

    def _create_real_sample_png(self, filename: str = "sample.png") -> str:
        """Helper to create a small valid image on macOS using sips."""
        target = os.path.join(self.test_dir, filename)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        sys_icon = "/System/Library/CoreServices/Finder.app/Contents/Resources/Finder.icns"
        if os.path.exists(sys_icon):
            subprocess.run(["sips", "-s", "format", "png", "--resampleHeightWidth", "32", "32", sys_icon, "--out", target], capture_output=True)
        if not os.path.exists(target):
            # Fallback if finder icon is missing
            with open(target, "wb") as f:
                f.write(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc`\x00\x00\x00\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82")
        return target

    def _create_real_sample_heic(self, filename: str = "sample.heic") -> str:
        """Helper to create a real valid HEIC on macOS using sips."""
        src_png = self._create_real_sample_png("fixture_for_heic.png")
        target_heic = os.path.join(self.test_dir, filename)
        os.makedirs(os.path.dirname(target_heic), exist_ok=True)
        subprocess.run(["sips", "-s", "format", "heic", src_png, "--out", target_heic], capture_output=True)
        return target_heic

    def test_get_unique_path(self):
        sample = os.path.join(self.test_dir, "photo.png")
        self.assertEqual(get_unique_path(sample), sample)

        with open(sample, "w") as f:
            f.write("test")

        v2 = get_unique_path(sample)
        self.assertEqual(v2, os.path.join(self.test_dir, "photo_v2.png"))

        with open(v2, "w") as f:
            f.write("test2")

        v3 = get_unique_path(sample)
        self.assertEqual(v3, os.path.join(self.test_dir, "photo_v3.png"))

    def test_recover_space_split_inputs(self):
        spaced_file = os.path.join(self.test_dir, "My Photo 2026.heic")
        with open(spaced_file, "w") as f:
            f.write("mock")

        split_args = [os.path.join(self.test_dir, "My"), "Photo", "2026.heic"]
        recovered = recover_space_split_inputs(split_args)
        self.assertEqual(len(recovered), 1)
        self.assertEqual(recovered[0], spaced_file)

    def test_recover_space_split_inputs_no_match(self):
        split_args = ["some_file.heic", "another_file.heic"]
        recovered = recover_space_split_inputs(split_args)
        self.assertEqual(recovered, split_args)

    def test_expand_input_and_quotes(self):
        img_file = os.path.join(self.test_dir, "pic.png")
        with open(img_file, "w") as f:
            f.write("data")

        # Quoted input token
        quoted_token = f"'{img_file}'"
        expanded = expand_input(quoted_token)
        self.assertEqual(len(expanded), 1)
        self.assertEqual(expanded[0], img_file)

    def test_expand_input_recursive(self):
        sub_dir = os.path.join(self.test_dir, "2026", "trip")
        os.makedirs(sub_dir, exist_ok=True)
        img1 = os.path.join(self.test_dir, "root.png")
        img2 = os.path.join(sub_dir, "nested.heic")
        with open(img1, "w") as f:
            f.write("1")
        with open(img2, "w") as f:
            f.write("2")

        # Non-recursive directory expansion
        top_matches = expand_input(self.test_dir, recursive=False)
        self.assertEqual(len(top_matches), 1)
        self.assertIn(img1, top_matches)

        # Recursive directory expansion
        rec_matches = expand_input(self.test_dir, recursive=True)
        self.assertEqual(len(rec_matches), 2)
        self.assertIn(img1, rec_matches)
        self.assertIn(img2, rec_matches)

    def test_expand_input_tilde(self):
        home_path = "~/test_heif_temp_nonexistent.heic"
        expanded = expand_input(home_path)
        self.assertEqual(expanded, [])

    def test_cli_parser_defaults_and_version(self):
        parser = build_parser(default_format="png")
        args = parser.parse_args(["input.heic"])
        self.assertEqual(args.format, "png")
        self.assertFalse(args.flat)
        self.assertFalse(args.delete_source)
        self.assertFalse(args.quiet)
        self.assertFalse(args.recursive)

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
        self.assertIn("jpeg", cmd)
        if os.path.exists(PROFILE_SRGB):
            self.assertIn("--matchTo", cmd)
            self.assertIn(PROFILE_SRGB, cmd)

    def test_convert_single_file_outdir_auto_create(self):
        src_png = self._create_real_sample_png("auto_outdir.png")
        nested_out = os.path.join(self.test_dir, "nested", "sub_exports")
        self.assertFalse(os.path.exists(nested_out))

        success, out_path = convert_single_file(
            file_path=src_png,
            target_format="jpg",
            profile=PROFILE_SRGB,
            output_dir=nested_out,
            quiet=True,
        )

        self.assertTrue(success)
        self.assertTrue(os.path.exists(nested_out))
        self.assertTrue(os.path.exists(out_path))
        self.assertTrue(out_path.endswith(".jpg"))

    def test_live_sips_convert_real_image(self):
        src_png = self._create_real_sample_png("source.png")

        # Convert to jpg with sRGB
        out_jpg = os.path.join(self.test_dir, "converted_jpg")
        success_jpg, path_jpg = convert_single_file(
            file_path=src_png,
            target_format="jpg",
            profile=PROFILE_SRGB,
            output_dir=out_jpg,
            quiet=True,
        )
        self.assertTrue(success_jpg)
        self.assertTrue(os.path.exists(path_jpg))

        # Convert to tiff
        out_tiff = os.path.join(self.test_dir, "converted_tiff")
        success_tiff, path_tiff = convert_single_file(
            file_path=src_png,
            target_format="tiff",
            output_dir=out_tiff,
            quiet=True,
        )
        self.assertTrue(success_tiff)
        self.assertTrue(os.path.exists(path_tiff))

        # Convert to avif
        out_avif = os.path.join(self.test_dir, "converted_avif")
        success_avif, path_avif = convert_single_file(
            file_path=src_png,
            target_format="avif",
            output_dir=out_avif,
            quiet=True,
        )
        self.assertTrue(success_avif)
        self.assertTrue(os.path.exists(path_avif))

    def test_live_synthetic_heic_to_display_p3_png(self):
        """Deep verification: convert a real synthetic HEIC to Display P3 PNG and verify ICC profile."""
        heic_file = self._create_real_sample_heic("synthetic.heic")
        self.assertTrue(os.path.exists(heic_file))

        out_dir = os.path.join(self.test_dir, "synthetic_heic_output")
        success, out_path = convert_single_file(
            file_path=heic_file,
            target_format="png",
            profile=PROFILE_P3,
            output_dir=out_dir,
            quiet=True,
        )
        self.assertTrue(success)
        self.assertTrue(os.path.exists(out_path))

        # Inspect resulting image profile with sips
        res = subprocess.run(["sips", "-g", "profile", out_path], capture_output=True, text=True)
        if os.path.exists(PROFILE_P3):
            self.assertIn("Display P3", res.stdout)

    def test_batch_convert_duplicate_basenames_collision(self):
        """Verify parallel batch conversion handles identical basenames into same output dir without collision."""
        dir1 = os.path.join(self.test_dir, "dir1")
        dir2 = os.path.join(self.test_dir, "dir2")
        out_dir = os.path.join(self.test_dir, "collision_out")
        os.makedirs(dir1, exist_ok=True)
        os.makedirs(dir2, exist_ok=True)

        src1 = self._create_real_sample_png("dir1/photo.png")
        src2 = self._create_real_sample_png("dir2/photo.png")

        success_count, total, results = batch_convert(
            resolved_files=[src1, src2],
            target_format="jpg",
            output_dir=out_dir,
            workers=4,
            quiet=True,
        )
        self.assertEqual(total, 2)
        self.assertEqual(success_count, 2)
        out_files = sorted(os.listdir(out_dir))
        self.assertIn("photo.jpg", out_files)
        self.assertIn("photo_v2.jpg", out_files)

    def test_invalid_profile_handling(self):
        """Adversarial check: ensure nonexistent profile path fails explicitly and exits non-zero."""
        src = self._create_real_sample_png("prof_test.png")
        fake_profile = os.path.join(self.test_dir, "nonexistent.icc")

        # Directly via convert_single_file
        success, msg = convert_single_file(
            file_path=src,
            target_format="png",
            profile=fake_profile,
            quiet=True,
        )
        self.assertFalse(success)
        self.assertIn("Color profile not found", msg)

        # Via CLI run
        parser = build_parser()
        args = parser.parse_args([src, "--profile", fake_profile, "--quiet"])
        exit_code = run(args)
        self.assertEqual(exit_code, 1)

    def test_expand_input_glob_filtering(self):
        """Verify wildcard glob expansion excludes subdirectories and non-image files."""
        sub_dir = os.path.join(self.test_dir, "subfolder")
        os.makedirs(sub_dir, exist_ok=True)
        img_file = os.path.join(self.test_dir, "good.heic")
        text_file = os.path.join(self.test_dir, "notes.txt")
        with open(img_file, "w") as f:
            f.write("mock")
        with open(text_file, "w") as f:
            f.write("text")

        matches = expand_input(os.path.join(self.test_dir, "*"))
        self.assertIn(img_file, matches)
        self.assertNotIn(sub_dir, matches)
        self.assertNotIn(text_file, matches)

    def test_get_unique_path_with_allocated_set(self):
        """Verify get_unique_path accounts for pending pre-allocated reservations."""
        p = os.path.join(self.test_dir, "target.png")
        allocated = set()

        u1 = get_unique_path(p, existing_paths=allocated)
        self.assertEqual(u1, p)
        allocated.add(u1)

        u2 = get_unique_path(p, existing_paths=allocated)
        self.assertEqual(u2, os.path.join(self.test_dir, "target_v2.png"))
        allocated.add(u2)

        u3 = get_unique_path(p, existing_paths=allocated)
        self.assertEqual(u3, os.path.join(self.test_dir, "target_v3.png"))

    def test_webp_input_support(self):
        """Verify webp is recognized as supported input."""
        from heif_converter.core import SUPPORTED_INPUT_EXTS
        self.assertIn("webp", [e.lower() for e in SUPPORTED_INPUT_EXTS])

        webp_file = os.path.join(self.test_dir, "graphic.webp")
        with open(webp_file, "w") as f:
            f.write("data")
        matches = expand_input(self.test_dir)
        self.assertIn(webp_file, matches)

    def test_live_real_heic_image_if_present(self):
        real_heic = "/Users/vecsatfoxmailcom/Downloads/IMG_8017.HEIC"
        if not os.path.exists(real_heic):
            self.skipTest("Real iPhone HEIC file not present on this machine")

        out_dir = os.path.join(self.test_dir, "real_heic_output")
        success, out_path = convert_single_file(
            file_path=real_heic,
            target_format="png",
            profile=PROFILE_P3,
            output_dir=out_dir,
            quiet=True,
        )
        self.assertTrue(success)
        self.assertTrue(os.path.exists(out_path))
        self.assertGreater(os.path.getsize(out_path), 1000)

        # Inspect resulting image profile with sips
        res = subprocess.run(["sips", "-g", "profile", out_path], capture_output=True, text=True)
        self.assertIn("Display P3", res.stdout)

    def test_corrupted_non_image_file_handling(self):
        """Adversarial check: ensure invalid non-image file fails gracefully without unhandled exception."""
        fake_heic = os.path.join(self.test_dir, "corrupt.heic")
        with open(fake_heic, "w") as f:
            f.write("This is plain text, not a HEIC image.")

        success, msg = convert_single_file(
            file_path=fake_heic,
            target_format="png",
            output_dir=self.test_dir,
            quiet=True,
        )
        self.assertFalse(success)
        self.assertIn("FAILED", msg)

    def test_non_existent_file_handling(self):
        """Adversarial check: non-existent file path fails gracefully."""
        ghost = os.path.join(self.test_dir, "nonexistent.heic")
        success, msg = convert_single_file(
            file_path=ghost,
            target_format="png",
            quiet=True,
        )
        self.assertFalse(success)
        self.assertIn("File not found", msg)

    def test_delete_source_flag(self):
        src_png = self._create_real_sample_png("to_delete.png")
        self.assertTrue(os.path.exists(src_png))

        success, out_path = convert_single_file(
            file_path=src_png,
            target_format="jpg",
            delete_source=True,
            quiet=True,
        )
        self.assertTrue(success)
        self.assertTrue(os.path.exists(out_path))
        self.assertFalse(os.path.exists(src_png))

    def test_webp_conversion_bridging(self):
        src_png = self._create_real_sample_png("sample_webp.png")
        success, out_path = convert_single_file(
            file_path=src_png,
            target_format="webp",
            output_dir=self.test_dir,
            quiet=True,
        )
        # Webp is supported if cwebp or PIL is installed
        if shutil.which("cwebp") or importlib_has_pillow():
            self.assertTrue(success)
            self.assertTrue(os.path.exists(out_path))
            self.assertTrue(out_path.endswith(".webp"))
        else:
            self.assertFalse(success)

    def test_cli_run_end_to_end(self):
        src1 = self._create_real_sample_png("cli1.png")
        src2 = self._create_real_sample_png("cli2.png")

        parser = build_parser(default_format="jpg")
        args = parser.parse_args([src1, src2, "--flat", "--quiet"])
        exit_code = run(args)
        self.assertEqual(exit_code, 0)
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "cli1.jpg")))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "cli2.jpg")))

    def test_cli_run_failure_exit_code(self):
        """Adversarial check: non-existent files exit with non-zero code."""
        parser = build_parser()
        args = parser.parse_args(["/nonexistent/path/*.heic", "--quiet"])
        exit_code = run(args)
        self.assertEqual(exit_code, 1)

    def test_bin_scripts_executable(self):
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        bin_dir = os.path.join(root_dir, "bin")
        for script_name in ["heif-converter", "png", "jpg", "jpeg", "heic"]:
            script_path = os.path.join(bin_dir, script_name)
            self.assertTrue(os.path.exists(script_path), f"Missing {script_name}")
            self.assertTrue(os.access(script_path, os.X_OK), f"Not executable: {script_name}")

    def test_batch_convert_empty(self):
        success_count, total, results = batch_convert([], quiet=True)
        self.assertEqual(success_count, 0)
        self.assertEqual(total, 0)
        self.assertEqual(results, [])


def importlib_has_pillow() -> bool:
    try:
        import PIL  # type: ignore
        return True
    except ImportError:
        return False


if __name__ == "__main__":
    unittest.main()


