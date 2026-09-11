# Evidence Traceability Matrix (evidence_index.md)

**Project**: Open-Source AI Human-Avatar Generation System (Track 02)  
**Assessment**: INCUBRIX PRIVATE LIMITED — SASTRA 2027 Graduate Hiring  

---

## 1. Traceability Matrix

| Requirement / Criterion | Implementation File(s) | Automated Test File | Output Artifact | Manifest File | Verification Log / Evidence |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Structured Input Contract** | [`schemas.py`](file:///d:/Track_02_Human_Avatar/human_avatar_system/src/avatar_system/schemas.py) | [`test_schemas.py`](file:///d:/Track_02_Human_Avatar/human_avatar_system/tests/unit/test_schemas.py) | `configs/baseline_avatars.yaml` | `evidence/manifests/*_manifest.json` | [`pytest_report.txt`](file:///d:/Track_02_Human_Avatar/human_avatar_system/evidence/tests/pytest_report.txt) |
| **Modular Prompt Builder** | [`prompts.py`](file:///d:/Track_02_Human_Avatar/human_avatar_system/src/avatar_system/prompts.py) | [`test_prompts.py`](file:///d:/Track_02_Human_Avatar/human_avatar_system/tests/unit/test_prompts.py) | `jobs/*/prompts.json` | `avatar_manifest.json` | `evidence/benchmarks/benchmark_report.md` |
| **Multi-Factor Safety Engine** | [`safety.py`](file:///d:/Track_02_Human_Avatar/human_avatar_system/src/avatar_system/safety.py) | [`test_safety.py`](file:///d:/Track_02_Human_Avatar/human_avatar_system/tests/unit/test_safety.py) | `evidence/failures/failure_refusal_log.json` | `jobs/*/safety_result.json` | `evidence/failures/failure_refusal_log.json` |
| **Deterministic Seeds** | [`job_manager.py`](file:///d:/Track_02_Human_Avatar/human_avatar_system/src/avatar_system/job_manager.py) | [`test_e2e_workflow.py`](file:///d:/Track_02_Human_Avatar/human_avatar_system/tests/e2e/test_e2e_workflow.py) | `jobs/*/seed.json` | `avatar_manifest.json` (`seed` field) | `evidence/benchmarks/benchmark_results.json` |
| **Cryptographic Provenance** | [`provenance.py`](file:///d:/Track_02_Human_Avatar/human_avatar_system/src/avatar_system/provenance.py) | [`test_provenance.py`](file:///d:/Track_02_Human_Avatar/human_avatar_system/tests/unit/test_provenance.py) | `evidence/manifests/` | `avatar_manifest.json` (SHA-256 + synthetic label) | `evidence/manifests/` |
| **Portable Job Bundle** | [`job_manager.py`](file:///d:/Track_02_Human_Avatar/human_avatar_system/src/avatar_system/job_manager.py) | [`test_job_manager.py`](file:///d:/Track_02_Human_Avatar/human_avatar_system/tests/unit/test_job_manager.py) | `jobs/job_*` | `jobs/*/job.json` | `jobs/` |
| **Kaggle Accelerator Worker** | [`avatar_generation_kaggle.ipynb`](file:///d:/Track_02_Human_Avatar/human_avatar_system/notebooks/avatar_generation_kaggle.ipynb) | `notebooks/` validation | `notebooks/avatar_generation_kaggle.ipynb` | `notebooks/` | `docs/TECHNICAL_REPORT.md#11` |
| **Output & Integrity Validator** | [`validator.py`](file:///d:/Track_02_Human_Avatar/human_avatar_system/src/avatar_system/validator.py) | [`test_validator.py`](file:///d:/Track_02_Human_Avatar/human_avatar_system/tests/unit/test_validator.py) | `outputs/` | `outputs/*_manifest.json` | `evidence/tests/pytest_report.txt` |
| **Mandatory Baseline (6 Avatars)** | `configs/baseline_avatars.yaml` | [`test_pipeline.py`](file:///d:/Track_02_Human_Avatar/human_avatar_system/tests/integration/test_pipeline.py) | `evidence/baseline/*.png` | `evidence/baseline/*_manifest.json` | `evidence/baseline/` |
| **Strong Level Matrix (18 Specs)** | `configs/strong_test_matrix.yaml` | [`test_evaluation.py`](file:///d:/Track_02_Human_Avatar/human_avatar_system/tests/unit/test_evaluation.py) | `evidence/strong/*.png` | `evidence/strong/*_manifest.json` | `evidence/strong/` |
| **Controlled Attribute Deltas** | `configs/strong_test_matrix.yaml` | [`test_evaluation.py`](file:///d:/Track_02_Human_Avatar/human_avatar_system/tests/unit/test_evaluation.py) | `evidence/strong/controlled_*.png` | `evidence/strong/controlled_*_manifest.json` | `evidence/benchmarks/benchmark_report.md#2` |
| **Failure & Refusal Handling** | `configs/failure_cases.yaml` | [`test_edge_cases.py`](file:///d:/Track_02_Human_Avatar/human_avatar_system/tests/unit/test_edge_cases.py) | `evidence/failures/` | N/A (Blocked pre-generation) | `evidence/failures/failure_refusal_log.json` |
| **Automated Benchmarking** | [`benchmark.py`](file:///d:/Track_02_Human_Avatar/human_avatar_system/src/avatar_system/benchmark.py) | [`test_e2e_workflow.py`](file:///d:/Track_02_Human_Avatar/human_avatar_system/tests/e2e/test_e2e_workflow.py) | `evidence/benchmarks/benchmark_results.json` | `evidence/benchmarks/benchmark_report.md` | `evidence/benchmarks/` |
| **Unified Local CLI** | [`cli.py`](file:///d:/Track_02_Human_Avatar/human_avatar_system/src/avatar_system/cli.py) | [`test_cli.py`](file:///d:/Track_02_Human_Avatar/human_avatar_system/tests/integration/test_cli.py) | CLI executable binary `avatar` | `avatar inspect-manifest` | `evidence/tests/pytest_report.txt` |

---

## 2. Directory Index of Evidence Files

- `evidence/baseline/`: 6 generated PNG images + 6 matching JSON provenance manifests.
- `evidence/strong/`: 18 generated PNG images (6 geographic scenarios + 12 single-attribute controlled suites) + 18 JSON manifests.
- `evidence/failures/failure_refusal_log.json`: Structured log capturing celebrity likeness refusals, deepfake intent refusals, missing consent refusals, and schema errors.
- `evidence/benchmarks/benchmark_results.json`: Machine-readable performance, latency, memory, and diversity metrics.
- `evidence/benchmarks/benchmark_report.md`: Human-readable benchmark and controlled attribute verification report.
- `evidence/manifests/`: Consolidated directory of all generated manifests.
- `evidence/tests/pytest_report.txt`: Full, untampered stdout/stderr report of the 39 passing pytest test executions.
