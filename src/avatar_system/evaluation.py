"""
Evaluation and metric computation module for the Human Avatar System.
Provides structured assessments for prompt adherence, diversity coverage,
and controlled-attribute consistency without biometric overclaims.
"""

from typing import Any, Dict, List, Set
from avatar_system.schemas import AvatarSpec, ProvenanceManifest


class EvaluationEngine:
    """Computes quality, adherence, and diversity metrics across avatar batches."""

    @staticmethod
    def evaluate_prompt_adherence(manifest: ProvenanceManifest) -> Dict[str, Any]:
        """
        Evaluates how completely the structured specification attributes
        were incorporated into the positive prompt and generation metadata.
        """
        spec = manifest.avatar_spec
        prompt_lower = manifest.positive_prompt.lower()

        required_attributes = [
            ("age_band", spec.get("age_band", "")),
            ("presentation", spec.get("presentation", "")),
            ("skin_tone", spec.get("skin_tone", "")),
            ("hair", spec.get("hair", "")),
            ("hair_style", spec.get("hair_style", "")),
            ("attire", spec.get("attire", "")),
            ("background", spec.get("background", "")),
        ]

        matches = 0
        attribute_details = {}

        for attr_name, val in required_attributes:
            clean_val = str(val).lower().replace("_", " ")
            is_present = clean_val in prompt_lower
            attribute_details[attr_name] = {
                "specified": val,
                "present_in_prompt": is_present,
            }
            if is_present:
                matches += 1

        adherence_score = matches / len(required_attributes) if required_attributes else 1.0

        return {
            "avatar_id": manifest.avatar_id,
            "seed": manifest.seed,
            "adherence_score": round(adherence_score, 4),
            "matched_attributes": matches,
            "total_attributes": len(required_attributes),
            "details": attribute_details,
        }

    @staticmethod
    def evaluate_batch_diversity(manifests: List[ProvenanceManifest]) -> Dict[str, Any]:
        """
        Computes representation diversity and attribute coverage across a batch of avatars.
        """
        if not manifests:
            return {"diversity_score": 0.0, "coverage": {}}

        unique_skin_tones: Set[str] = set()
        unique_age_bands: Set[str] = set()
        unique_hairstyles: Set[str] = set()
        unique_presentations: Set[str] = set()
        unique_backgrounds: Set[str] = set()

        for m in manifests:
            spec = m.avatar_spec
            if spec.get("skin_tone"):
                unique_skin_tones.add(spec["skin_tone"])
            if spec.get("age_band"):
                unique_age_bands.add(spec["age_band"])
            if spec.get("hair_style"):
                unique_hairstyles.add(spec["hair_style"])
            if spec.get("presentation"):
                unique_presentations.add(spec["presentation"])
            if spec.get("background"):
                unique_backgrounds.add(spec["background"])

        total_samples = len(manifests)
        coverage_ratios = {
            "skin_tone_diversity": round(len(unique_skin_tones) / total_samples, 3),
            "age_band_diversity": round(len(unique_age_bands) / total_samples, 3),
            "hairstyle_diversity": round(len(unique_hairstyles) / total_samples, 3),
            "presentation_diversity": round(len(unique_presentations) / total_samples, 3),
            "background_diversity": round(len(unique_backgrounds) / total_samples, 3),
        }

        avg_diversity = sum(coverage_ratios.values()) / len(coverage_ratios)

        return {
            "total_avatars_evaluated": total_samples,
            "unique_skin_tones_count": len(unique_skin_tones),
            "unique_age_bands_count": len(unique_age_bands),
            "unique_hairstyles_count": len(unique_hairstyles),
            "unique_presentations_count": len(unique_presentations),
            "unique_backgrounds_count": len(unique_backgrounds),
            "coverage_metrics": coverage_ratios,
            "overall_diversity_score": round(avg_diversity, 4),
        }

    @staticmethod
    def evaluate_controlled_attribute_change(
        baseline_manifest: ProvenanceManifest,
        variant_manifest: ProvenanceManifest,
        expected_changed_attribute: str,
    ) -> Dict[str, Any]:
        """
        Verifies that in a controlled experiment, ONLY the targeted attribute changed
        while all other specification parameters remained strictly constant.
        """
        base_spec = baseline_manifest.avatar_spec
        var_spec = variant_manifest.avatar_spec

        invariant_keys = [
            "age_band", "presentation", "skin_tone", "hair", "hair_style",
            "attire", "background", "pose", "expression", "lighting", "aspect_ratio"
        ]

        unintended_changes = []
        target_changed = False

        for k in invariant_keys:
            base_val = base_spec.get(k)
            var_val = var_spec.get(k)
            if k == expected_changed_attribute:
                if base_val != var_val:
                    target_changed = True
            else:
                if base_val != var_val:
                    unintended_changes.append(f"Attribute '{k}' changed from '{base_val}' to '{var_val}'.")

        is_valid_controlled_test = target_changed and (len(unintended_changes) == 0)

        return {
            "test_attribute": expected_changed_attribute,
            "target_attribute_changed": target_changed,
            "baseline_value": base_spec.get(expected_changed_attribute),
            "variant_value": var_spec.get(expected_changed_attribute),
            "strictly_controlled": is_valid_controlled_test,
            "unintended_changes": unintended_changes,
        }
