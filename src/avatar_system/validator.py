"""
Output and manifest validation module for the Human Avatar System.
Performs thorough image decoding, dimension checks, aspect ratio verification,
and cryptographic provenance validation.
"""

from pathlib import Path
from typing import Optional
from PIL import Image

from avatar_system.provenance import ProvenanceManager, compute_file_sha256
from avatar_system.schemas import ProvenanceManifest, ValidationResult


class OutputValidator:
    """Validates generated image files and corresponding provenance manifests."""

    @staticmethod
    def validate_image_file(
        image_path: Path,
        expected_width: Optional[int] = None,
        expected_height: Optional[int] = None,
        expected_aspect_ratio: Optional[str] = None,
    ) -> ValidationResult:
        """
        Validates that an image file exists, is non-empty, can be decoded,
        and conforms to requested dimensions and format.
        """
        errors = []
        warnings = []
        props = {}

        if not image_path.exists():
            return ValidationResult(
                is_valid=False,
                errors=[f"Image file does not exist: {image_path}"],
                warnings=[],
                image_properties={},
            )

        file_size = image_path.stat().st_size
        if file_size == 0:
            return ValidationResult(
                is_valid=False,
                errors=[f"Image file is empty (0 bytes): {image_path}"],
                warnings=[],
                image_properties={"file_size_bytes": 0},
            )

        # Attempt decoding with Pillow
        try:
            with Image.open(image_path) as img:
                img.verify()  # Verifies file integrity/header

            # Re-open for metadata extraction (verify closes/invalidates the stream)
            with Image.open(image_path) as img:
                width, height = img.size
                format_name = img.format
                mode = img.mode

                props = {
                    "width": width,
                    "height": height,
                    "format": format_name,
                    "mode": mode,
                    "file_size_bytes": file_size,
                    "sha256": compute_file_sha256(image_path),
                }

                if format_name not in {"PNG", "JPEG", "WEBP"}:
                    errors.append(f"Unsupported image format '{format_name}'. Expected PNG or JPEG.")

                if expected_width is not None and width != expected_width:
                    errors.append(f"Image width mismatch: got {width}, expected {expected_width}.")

                if expected_height is not None and height != expected_height:
                    errors.append(f"Image height mismatch: got {height}, expected {expected_height}.")

                # Aspect ratio tolerance check
                if expected_aspect_ratio:
                    ratio_parts = [float(x) for x in expected_aspect_ratio.split(":")]
                    expected_ratio = ratio_parts[0] / ratio_parts[1]
                    actual_ratio = width / height
                    if abs(actual_ratio - expected_ratio) > 0.05:
                        warnings.append(
                            f"Aspect ratio deviation: actual {actual_ratio:.3f} vs expected {expected_ratio:.3f}"
                        )

        except Exception as e:
            errors.append(f"Image decoding failed / file is corrupted: {str(e)}")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            image_properties=props,
        )

    @staticmethod
    def validate_manifest_and_image(
        manifest_path: Path,
        image_path: Optional[Path] = None,
    ) -> ValidationResult:
        """
        Validates both the provenance manifest and its linked output image.
        """
        errors = []
        warnings = []
        manifest_verified = False

        if not manifest_path.exists():
            return ValidationResult(
                is_valid=False,
                errors=[f"Manifest file does not exist: {manifest_path}"],
                manifest_verified=False,
            )

        try:
            manifest = ProvenanceManager.load_manifest(manifest_path)
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                errors=[f"Manifest schema validation failed: {str(e)}"],
                manifest_verified=False,
            )

        # Verify manifest core fields
        if not manifest.avatar_id:
            errors.append("Manifest missing avatar_id.")
        if manifest.seed is None:
            errors.append("Manifest missing seed.")
        if not manifest.model_name:
            errors.append("Manifest missing model_name.")
        if not manifest.safety_result:
            errors.append("Manifest missing safety_result.")

        target_img = image_path
        if not target_img and manifest.output_filename:
            target_img = manifest_path.parent / manifest.output_filename

        img_props = {}
        if target_img:
            img_result = OutputValidator.validate_image_file(
                target_img,
                expected_width=manifest.image_width,
                expected_height=manifest.image_height,
                expected_aspect_ratio=manifest.aspect_ratio,
            )
            errors.extend(img_result.errors)
            warnings.extend(img_result.warnings)
            img_props = img_result.image_properties

            # Check cryptographic hash match if manifest recorded sha256
            if manifest.image_sha256 and img_props.get("sha256"):
                if manifest.image_sha256 != img_props["sha256"]:
                    errors.append(
                        f"Cryptographic hash mismatch: image SHA256 '{img_props['sha256']}' "
                        f"does not match manifest record '{manifest.image_sha256}'."
                    )

        manifest_verified = len(errors) == 0
        return ValidationResult(
            is_valid=manifest_verified,
            errors=errors,
            warnings=warnings,
            image_properties=img_props,
            manifest_verified=manifest_verified,
        )
