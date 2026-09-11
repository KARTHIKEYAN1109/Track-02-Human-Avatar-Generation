"""
Prompt builder module for the Human Avatar System.
Provides modular, attribute-isolated prompt assembly using neutral, inclusive descriptors.
"""

from typing import Dict, Optional
from avatar_system.schemas import AvatarSpec, PromptBundle


# Curated standard negative prompt library for photorealistic portrait generation
DEFAULT_NEGATIVE_PROMPT = (
    "deformed, distorted, disfigured, poorly drawn face, bad anatomy, wrong proportions, "
    "extra eyes, extra limbs, amputee, unnatural skin texture, blurry, low resolution, "
    "jpeg artifacts, watermark, signature, text, logo, oversaturated, cartoon, 3d render, "
    "uncanny valley, cloned face, grotesque, morbid, poorly framed, cropped head"
)


class PromptBuilder:
    """
    Builds modular, deterministic prompts from structured AvatarSpec instances.
    Maintains clean isolation between physical appearance, cultural/geographic context,
    attire, background, and photographic parameters.
    """

    def __init__(self, default_negative_prompt: str = DEFAULT_NEGATIVE_PROMPT):
        self.default_negative_prompt = default_negative_prompt

    def _format_age(self, age_band: str) -> str:
        mapping = {
            "child": "a young child",
            "young_adult": "a young adult in their early 20s",
            "adult": "an adult in their 30s",
            "middle_aged": "a middle-aged person in their late 40s",
            "senior": "a senior person in their 60s with subtle natural aging lines",
        }
        return mapping.get(age_band.lower().replace(" ", "_"), f"a {age_band.replace('_', ' ')} person")

    def _format_skin_tone(self, skin_tone: str) -> str:
        clean = skin_tone.lower().replace("_", " ")
        return f"{clean} skin tone"

    def _format_hair(self, hair_color: str, hair_style: str) -> str:
        color = hair_color.lower().replace("_", " ")
        style = hair_style.lower().replace("_", " ")
        return f"{style} {color} hair"

    def _format_attire(self, attire: str) -> str:
        clean = attire.lower().replace("_", " ")
        return f"wearing {clean}"

    def _format_expression(self, expression: str) -> str:
        clean = expression.lower().replace("_", " ")
        return f"{clean} expression"

    def _format_background(self, background: str) -> str:
        clean = background.lower().replace("_", " ")
        return f"set against a {clean} background"

    def _format_lighting(self, lighting: str) -> str:
        clean = lighting.lower().replace("_", " ")
        return f"illuminated by {clean} lighting"

    def _format_pose(self, pose: str) -> str:
        clean = pose.lower().replace("_", " ")
        return f"{clean}"

    def _format_presentation(self, presentation: str) -> str:
        clean = presentation.lower().replace("_", " ")
        return f"{clean} aesthetic"

    def build_prompt_bundle(
        self,
        spec: AvatarSpec,
        model_type: str = "sd-1.5",
        custom_negative: Optional[str] = None,
    ) -> PromptBundle:
        """
        Assembles positive and negative prompts deterministically from individual attribute clauses.
        """
        # Step 1: Generate isolated structured clauses
        clauses: Dict[str, str] = {
            "subject": self._format_age(spec.age_band),
            "presentation": self._format_presentation(spec.presentation),
            "skin_tone": self._format_skin_tone(spec.skin_tone),
            "hair": self._format_hair(spec.hair, spec.hair_style),
            "expression": self._format_expression(spec.expression),
            "pose": self._format_pose(spec.pose),
            "attire": self._format_attire(spec.attire),
            "background": self._format_background(spec.background),
            "lighting": self._format_lighting(spec.lighting),
        }

        # Step 2: Assemble positive prompt with photographic quality anchors
        # Note: Keeps physical attributes decoupled from geography/nationality.
        subject_part = (
            f"Fictional portrait of {clauses['subject']}, {clauses['presentation']}, "
            f"{clauses['skin_tone']}, {clauses['hair']}, {clauses['expression']}, {clauses['pose']}"
        )
        environment_part = f"{clauses['attire']}, {clauses['background']}, {clauses['lighting']}"
        photo_quality_part = (
            "sharp focus, professional portrait photography, 85mm lens, f/1.8 aperture, "
            "photorealistic, natural skin texture, finely detailed eyes"
        )

        positive_prompt = f"{subject_part}, {environment_part}, {photo_quality_part}"

        # Step 3: Handle negative prompt
        negative_prompt = custom_negative or self.default_negative_prompt

        return PromptBundle(
            positive_prompt=positive_prompt,
            negative_prompt=negative_prompt,
            structured_clauses=clauses,
            model_compatibility=model_type,
        )
