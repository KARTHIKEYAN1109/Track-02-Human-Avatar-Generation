# Step-by-Step Reproduction Guide (REPRODUCTION.md)

**Project**: Open-Source AI Human-Avatar Generation System (Track 02)  
**Assessment**: INCUBRIX PRIVATE LIMITED — SASTRA 2027 Graduate Hiring  
**Target Environment**: Clean Windows Laptop (No Local GPU Required)  

---

## 1. Prerequisites

- **Python**: Python 3.10, 3.11, 3.12, or 3.13 installed.
- **Git**: Git installed and in PATH.
- **Kaggle Account**: Standard free Kaggle account (for GPU accelerator notebook execution).

---

## 2. Environment Setup (Local Laptop)

Open Windows PowerShell or CMD and run the following commands:

```powershell
# 1. Navigate to project root
cd d:\Track_02_Human_Avatar\human_avatar_system

# 2. Create clean virtual environment
python -m venv .venv

# 3. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 4. Install local dependencies
pip install -r requirements.txt

# 5. Install avatar-system package in editable mode
pip install -e .
```

---

## 3. Verify Local Installation

```powershell
# Verify CLI help menu and subcommands
python -m avatar_system.cli --help
```

Expected Output: Displays subcommands (`validate`, `safety-check`, `prepare`, `run`, `ingest`, `evaluate`, `benchmark`, `test`, `inspect-manifest`, `clean`).

---

## 4. Run Automated Test Suite

```powershell
# Run all 39 unit, integration, and E2E tests with code coverage
python -m pytest tests/ -v --cov=src/avatar_system
```

Expected Output: `39 passed in ~1.8s` with `~88% coverage`.

---

## 5. Validate Avatar Specifications

```powershell
# Validate baseline specs
python -m avatar_system.cli validate --spec configs/baseline_avatars.yaml

# Validate strong matrix specs
python -m avatar_system.cli validate --spec configs/strong_test_matrix.yaml

# Run safety check
python -m avatar_system.cli safety-check --spec configs/baseline_avatars.yaml
```

---

## 6. Prepare Portable Job Bundles

```powershell
# Prepare baseline jobs
python -m avatar_system.cli prepare --spec configs/baseline_avatars.yaml --out jobs/

# Prepare strong test matrix jobs
python -m avatar_system.cli prepare --spec configs/strong_test_matrix.yaml --out jobs/
```

This creates portable directories in `jobs/` containing `job.json`, `avatar_spec.json`, `prompts.json`, `seed.json`, and `safety_result.json`.

---

## 7. Run Kaggle GPU Inference (Free Accelerator)

1. Open [Kaggle](https://www.kaggle.com/) and create a new Notebook.
2. Select **Settings -> Accelerator -> GPU T4 x2** or **GPU P100**.
3. Upload `notebooks/avatar_generation_kaggle.ipynb` to the notebook.
4. Upload the `jobs/` folder (or zip) as a Dataset or working directory.
5. Click **Run All**.
6. When execution finishes, download `outputs.zip` from the `/kaggle/working/` output files pane.

---

## 8. Ingest and Validate Kaggle Outputs Locally

Place the downloaded `outputs.zip` in the project root or specify its path:

```powershell
# Ingest and validate all outputs and manifests
python -m avatar_system.cli ingest --results outputs.zip

# Compute batch adherence and diversity metrics
python -m avatar_system.cli evaluate --results outputs/
```

---

## 9. Run Local Offline Benchmark & Evidence Generation

If running locally without Kaggle GPU, execute the offline verification suite:

```powershell
# Run automated benchmark and update evidence
python scripts/run_benchmarks.py

# Or via CLI
python -m avatar_system.cli benchmark --matrix configs/strong_test_matrix.yaml
```

---

## 10. Inspect Individual Manifests

```powershell
# Inspect provenance manifest and verify SHA256 integrity
python -m avatar_system.cli inspect-manifest --path evidence/manifests/baseline_001_young_prof_100001_manifest.json
```
