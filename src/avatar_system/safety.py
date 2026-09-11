"""
Safety validation and content moderation engine for the Human Avatar System.
Enforces Responsible AI standards, likeness protection, deepfake prevention,
and reference-image consent verification.
"""

import re
from typing import List, Set, Tuple
from avatar_system.schemas import AvatarSpec, SafetyResult


# Curated catalog of known public figures / politicians / celebrities to prevent unauthorized likeness synthesis
KNOWN_PUBLIC_FIGURES: Set[str] = {
    "elon musk", "sam altman", "donald trump", "joe biden", "barack obama",
    "taylor swift", "bill gates", "mark zuckerberg", "jensen huang", "satya nadella",
    "sundar pichai", "narendra modi", "emmanuel macron", "keanu reeves", "scarlett johansson",
    "tom cruise", "leonardo dicaprio", "angela merkel", "vladimir putin", "xi jinping",
    "queen elizabeth", "pope francis", "beyonce", "cristiano ronaldo", "lionel messi",
}

# Deceptive deepfake / impersonation intent triggers
DEEPFAKE_INTENT_TRIGGERS: List[str] = [
    r"\bdeepfake\b",
    r"\bimpersonat(e|ing|ion)\b",
    r"\blook[\s_-]?alike of\b",
    r"\bidentical clone of\b",
    r"\bfake video of\b",
    r"\bexact likeness of\b",
    r"\bpretend to be\b",
    r"\bphotomontage of\b",
]

# OpenRAIL prohibited content patterns (harm, violence, non-consensual, hate)
PROHIBITED_CONTENT_PATTERNS: List[str] = [
    r"\bnsfw\b",
    r"\bnude\b",
    r"\bnaked\b",
    r"\bexplicit\b",
    r"\bviolence\b",
    r"\bgore\b",
    r"\bblood\b",
    r"\bweapon\b",
    r"\bterroris[mt]\b",
    r"\bhate speech\b",
    r"\bracist\b",
    r"\bgenocide\b",
    r"\bharm\b",
    r"\bself[\s_-]?harm\b",
]


class SafetyEngine:
    """
    Evaluates avatar specifications and prompts for safety, consent, and policy compliance.
    """

    def __init__(
        self,
        public_figures: Set[str] = KNOWN_PUBLIC_FIGURES,
        deepfake_patterns: List[str] = DEEPFAKE_INTENT_TRIGGERS,
        prohibited_patterns: List[str] = PROHIBITED_CONTENT_PATTERNS,
    ):
        self.public_figures = {p.lower() for p in public_figures}
        self.deepfake_patterns = [re.compile(p, re.IGNORECASE) for p in deepfake_patterns]
        self.prohibited_patterns = [re.compile(p, re.IGNORECASE) for p in prohibited_patterns]

    def evaluate_spec(self, spec: AvatarSpec) -> SafetyResult:
        """
        Runs comprehensive multi-rule safety audit against an AvatarSpec.
        """
        refusal_reasons: List[str] = []
        warnings: List[str] = []
        risk_score: float = 0.0

        # Rule 1: Reference image consent verification
        if spec.reference_images and len(spec.reference_images) > 0:
            if spec.consent_status != "granted":
                refusal_reasons.append(
                    f"Consent Violation: Reference image(s) supplied with consent_status='{spec.consent_status}'. "
                    "Explicit consent_status='granted' is mandatory for reference-based generation."
                )
                risk_score += 0.5

            if spec.reference_rights_status not in {"owned", "licensed", "public_domain"}:
                refusal_reasons.append(
                    f"IP / Rights Violation: Reference image(s) have rights_status='{spec.reference_rights_status}'. "
                    "Must be 'owned', 'licensed', or 'public_domain'."
                )
                risk_score += 0.4

        # Rule 2: Search for named real-person / celebrity likeness
        combined_text = " ".join([
            spec.avatar_id,
            spec.presentation,
            spec.attire,
            spec.background,
            spec.cultural_context or "",
            spec.notes if hasattr(spec, "notes") and spec.notes else "",
            str(spec.metadata),
        ]).lower()

        for figure in self.public_figures:
            # Word-boundary search for exact figure name
            pattern = rf"\b{re.escape(figure)}\b"
            if re.search(pattern, combined_text):
                refusal_reasons.append(
                    f"Unauthorized Likeness Violation: Detected reference to public figure '{figure}'. "
                    "Generating recognizable portraits of real individuals without verified consent is prohibited."
                )
                risk_score = 1.0
                break

        # Rule 3: Deceptive deepfake intent detection
        for pattern in self.deepfake_patterns:
            if pattern.search(combined_text):
                refusal_reasons.append(
                    f"Deceptive Synthesis Violation: Match found for impersonation trigger pattern '{pattern.pattern}'."
                )
                risk_score = 1.0
                break

        # Rule 4: Prohibited harmful or NSFW content detection
        for pattern in self.prohibited_patterns:
            if pattern.search(combined_text):
                refusal_reasons.append(
                    f"OpenRAIL Policy Violation: Prohibited content keyword detected matching '{pattern.pattern}'."
                )
                risk_score = 1.0
                break

        # Warnings: Neutral attribute check
        if spec.cultural_context and not spec.cultural_context.strip():
            warnings.append("cultural_context provided but empty.")

        is_safe = len(refusal_reasons) == 0
        risk_score = min(1.0, risk_score)

        return SafetyResult(
            is_safe=is_safe,
            refusal_reasons=refusal_reasons,
            warnings=warnings,
            risk_score=risk_score,
        )

    def evaluate_text(self, text: str) -> Tuple[bool, List[str]]:
        """Quick check for arbitrary raw text string."""
        reasons = []
        lower = text.lower()
        for fig in self.public_figures:
            if re.search(rf"\b{re.escape(fig)}\b", lower):
                reasons.append(f"Named likeness detected: '{fig}'")
        for p in self.deepfake_patterns:
            if p.search(lower):
                reasons.append(f"Deepfake pattern detected: '{p.pattern}'")
        for p in self.prohibited_patterns:
            if p.search(lower):
                reasons.append(f"Prohibited content detected: '{p.pattern}'")
        return len(reasons) == 0, reasons
