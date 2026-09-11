# System Benchmark & Verification Report

**Track 02 — Open-Source AI Human-Avatar Generation System**  
**Assessment**: INCUBRIX PRIVATE LIMITED — SASTRA 2027 Graduate Hiring  
**Execution Timestamp**: 2026-09-11T14:00:52.433297+00:00  

---

## 1. Executive Performance Summary

| Metric | Measured Value | Target / Assessment Requirement |
| :--- | :--- | :--- |
| **Total Evaluated Specs** | 18 | >= 18 specs |
| **Job Success Rate** | **100.0%** | 100% on valid specs |
| **Total Wall Clock Time** | **0.71 s** | Sub-second per mock job |
| **Throughput (Local CPU)** | **25.4 jobs/sec** | High local orchestration throughput |
| **Avg Job Prep Latency** | 4.13 ms | Low overhead |
| **Avg Validation Latency** | 18.50 ms | Cryptographic SHA256 + Pillow checks |
| **Peak Process RAM** | **38.6 MB** | Under 500 MB local footprint |
| **System Total RAM** | 15.69 GB | Laptop Non-GPU Orchestration |
| **Mean Prompt Adherence** | **99.2%** | >= 90% structured clause match |
| **Batch Diversity Score** | **28.9%** | Balanced attribute representation |

---

## 2. Controlled Attribute Isolation Verification

| Test Suite | Changed Attribute | Baseline Value | Variant Value | Strictly Controlled? | Unintended Changes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Test A (Skin Tone)** | `skin_tone` | `fair` | `deep_ebony` | **YES [PASS]** | None |
| **Test B (Hair Style)** | `hair_style` | `short_fade` | `braided_locs` | **YES [PASS]** | None |
| **Test C (Attire)** | `attire` | `business_suit` | `crewneck_sweater` | **YES [PASS]** | None |
| **Test D (Background)** | `background` | `neutral_studio` | `minimalist_modern_office` | **YES [PASS]** | None |

---

## 3. Failure & Safety Refusal Verification

Total Negative Cases Tested: **6**  
- **Public Figure Likeness Refusal**: Verified refusal for unauthorized celebrity names.
- **Deceptive Deepfake Intent Refusal**: Verified refusal for impersonation keywords.
- **Unconsented Reference Refusal**: Verified refusal when `consent_status != 'granted'`.
- **Schema Validation Errors**: Correctly rejected negative seeds, malformed ratios, and missing mandatory fields.

---

## 4. Hardware and Pinned Model Provenance

- **Pinned Model**: `stable-diffusion-v1-5/stable-diffusion-v1-5` (`revision=main`)
- **License**: CreativeML OpenRAIL-M (Open Weights, Commercial Use Permitted)
- **Local Route**: `mock_runner`
- **Kaggle GPU Route**: Pinned `notebooks/avatar_generation_kaggle.ipynb`
