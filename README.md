# Open-Source AI Human-Avatar Generation System (Track 02)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Model: SD 1.5](https://img.shields.io/badge/Model-Stable%20Diffusion%201.5-orange.svg)](SOURCES.md)
[![Model License: OpenRAIL-M](https://img.shields.io/badge/Model%20License-OpenRAIL--M-green.svg)](SOURCES.md)
[![Tests: 39 Passed](https://img.shields.io/badge/Tests-39%20Passed%20(88%25%20Coverage)-brightgreen.svg)](evidence/tests/pytest_report.txt)

**Candidate Assessment Submission**: INCUBRIX PRIVATE LIMITED — SASTRA 2027 Graduate Hiring  
**Track**: Track 02 — Open-Source AI Human-Avatar Generation  
**Role**: Senior ML Engineer + Software Architect + QA Engineer  

---

## 1. Project Overview

The **Human Avatar System** is a complete, contract-driven, open-source AI platform for synthesizing fictional human-avatar portraits. Designed specifically to eliminate algorithmic stereotyping, protect individual privacy, and enforce Responsible AI standards, the system cleanly isolates the **Local Non-GPU Laptop (Orchestrator)** from the **Kaggle Free Accelerator (Inference Engine)**.

### Core Capabilities
- **Decoupled Architecture**: Orchestration, validation, safety filtering, and testing execute entirely on CPU laptops with zero GPU requirements.
- **Inclusive Appearance Controls**: Decouples geographic/cultural context from physical traits (skin tone, hair style, attire, background).
- **Pre-Generation Safety Engine**: Programmatically blocks celebrity likeness synthesis, deceptive deepfakes, and unconsented reference images before any compute is dispatched.
- **Deterministic Seeds**: Enforces repeatable generation via pinned seeds and schedulers.
- **Cryptographic Provenance**: Automatically writes `avatar_manifest.json` with SHA-256 digests and explicit synthetic media labeling.
- **100% Free & Open-Source**: Zero paid APIs, zero proprietary services, and zero paywalls.

---

## 2. System Architecture

```
LOCAL LAPTOP (CPU Orchestrator)
    |
    | [ Structured Avatar Specification (YAML/JSON) ]
    v
LOCAL CLI (`avatar`)
    |
    +---> [ Pydantic Schema Validation ]
    |
    +---> [ Pre-Generation Safety & Consent Audit ] (Likeness, deepfakes, consent)
    |
    +---> [ Modular Prompt Builder ] (Decoupled appearance clauses)
    |
    +---> [ Deterministic Seed Assignment ]
    |
    +---> [ Portable Job Bundle Packaging ] (job.json, spec.json, prompts.json)
    |
    v
KAGGLE NOTEBOOK (Free Accelerator Worker: T4 / P100 GPU)
    |
    +---> Load Pinned Open Model (`stable-diffusion-v1-5` in FP16)
    +---> Execute Deterministic Diffusion Inference
    +---> Save PNG Outputs & Compute SHA-256 Digest
    +---> Generate `avatar_manifest.json` with Hardware Telemetry
    +---> Export `outputs.zip`
    |
    v
LOCAL INGESTION & INTEGRITY ENGINE
    |
    +---> Output File Integrity & Header Decode (Pillow)
    +---> Cryptographic Hash Match Verification
    +---> Batch Prompt Adherence & Diversity Evaluation
    +---> Automated Benchmark Generation
```

---

## 3. Directory Layout

```
human_avatar_system/
├── src/avatar_system/         # Core python package
│   ├── config.py              # Environment configuration & path resolvers
│   ├── schemas.py             # Pydantic models for specs, jobs, manifests
│   ├── prompts.py             # Modular attribute-isolated prompt builder
│   ├── safety.py              # Multi-factor safety & consent engine
│   ├── provenance.py          # Cryptographic hashing & manifest generator
│   ├── job_manager.py         # Portable job bundles & resume caching
│   ├── validator.py           # Multi-point image & manifest validator
│   ├── evaluation.py          # Adherence, diversity, and consistency metrics
│   ├── benchmark.py           # Performance & throughput benchmarking
│   ├── routing.py             # Engine dispatch (Kaggle / Local / Mock)
│   └── cli.py                 # Unified Rich terminal CLI
│
├── tests/                     # Comprehensive test suite (39 tests)
│   ├── unit/                  # Unit tests (schemas, prompts, safety, validator)
│   ├── integration/           # CLI and pipeline integration tests
│   └── e2e/                   # Batch generation and determinism E2E tests
│
├── configs/                   # Specification matrices
│   ├── example_avatar.yaml    # Baseline sample specification
│   ├── baseline_avatars.yaml  # 6 diverse fictional avatars
│   ├── strong_test_matrix.yaml# 18 specs (6 geographic contexts + 12 controlled deltas)
│   ├── exceptional_reference.yaml # Consented vs unconsented test specs
│   └── failure_cases.yaml     # Negative test matrix for safety and schema errors
│
├── notebooks/
│   └── avatar_generation_kaggle.ipynb # Pinned Kaggle GPU inference worker
│
├── evidence/                  # Verified execution evidence & benchmark results
│   ├── baseline/              # 6 baseline images + manifests
│   ├── strong/                # 18 strong matrix images + manifests
│   ├── failures/              # Structured refusal and error logs
│   ├── benchmarks/            # Benchmark results JSON and Markdown report
│   ├── manifests/             # Consolidated manifest repository
│   ├── tests/                 # Raw pytest execution log
│   └── evidence_index.md      # Full traceability matrix
│
├── docs/
│   ├── TECHNICAL_REPORT.md    # 25-section comprehensive engineering report
│   └── REPRODUCTION.md        # Step-by-step reproduction instructions
│
├── README.md                  # System overview and manual
├── SOURCES.md                 # Model revisions, licenses, and dependencies
├── AI_USE.md                  # Complete AI assistance disclosure
├── requirements.txt           # Local dependencies
├── requirements-kaggle.txt    # Kaggle worker dependencies
└── Makefile                   # Task runner
```

---

## 4. Quickstart Guide

### 1. Installation
```powershell
# Navigate to directory and set up virtual environment
cd d:\Track_02_Human_Avatar\human_avatar_system
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install package
pip install -r requirements.txt
pip install -e .
```

### 2. Validate Specifications
```powershell
# Validate schema
avatar validate --spec configs/baseline_avatars.yaml

# Run safety check
avatar safety-check --spec configs/baseline_avatars.yaml
```

### 3. Prepare Job Bundles
```powershell
# Create portable bundle for Kaggle or local runner
avatar prepare --spec configs/baseline_avatars.yaml --out jobs/
```

### 4. Run Locally (Mock / CPU Synthetic Engine)
```powershell
# Execute prepared job locally
avatar run --job jobs/job_baseline_001_young_prof_100001 --route mock_runner
```

### 5. Ingest and Validate Outputs
```powershell
# Ingest folder or zip archive from Kaggle
avatar ingest --results outputs/

# Compute batch adherence and diversity
avatar evaluate --results outputs/
```

### 6. Run Automated Benchmarks
```powershell
avatar benchmark --matrix configs/strong_test_matrix.yaml
```

---

## 5. Kaggle Free Accelerator Workflow

1. Open `notebooks/avatar_generation_kaggle.ipynb` in [Kaggle](https://www.kaggle.com/).
2. Turn on **GPU Accelerator** (T4 or P100).
3. Upload `jobs/` directory as an input dataset.
4. Click **Run All**.
5. Download `outputs.zip` and run `avatar ingest --results outputs.zip` locally.

---

## 6. Testing and Verification

Run the full automated test suite:
```powershell
python -m pytest tests/ -v --cov=src/avatar_system
```
**Test Results**: 39 passed in 1.89 seconds with 88% statement coverage. Real logs are recorded in [`evidence/tests/pytest_report.txt`](evidence/tests/pytest_report.txt).

---

## 7. Model Selection & Licensing

- **Model**: `stable-diffusion-v1-5/stable-diffusion-v1-5` (Revision: `main`)
- **License**: CreativeML OpenRAIL-M (Permits commercial & non-commercial use).
- **Full Provenance Details**: See [`SOURCES.md`](SOURCES.md).

---

## 8. Responsible AI & Transparency

- **Synthetic Media Labeling**: All generated assets and provenance manifests declare `synthetic_media: true` with synthetic watermarks.
- **AI Coding Disclosure**: Complete transparency on AI tools and human verification in [`AI_USE.md`](AI_USE.md).
- **Traceability Matrix**: Complete audit trail in [`evidence/evidence_index.md`](evidence/evidence_index.md).
