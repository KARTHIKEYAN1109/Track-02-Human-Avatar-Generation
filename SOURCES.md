# Third-Party Components & Licensing Provenance (SOURCES.md)

**Project**: Open-Source AI Human-Avatar Generation System (Track 02)  
**Assessment**: INCUBRIX PRIVATE LIMITED — SASTRA 2027 Graduate Hiring  
**Author**: Assessment Candidate  

---

## 1. Machine Learning Model & Weights

| Component | Source Repository / Provider | Pinned Revision / Hash | License | Commercial Use Permitted? | Direct URL / Access Point | Usage in System |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Stable Diffusion v1.5** (Primary) | `stable-diffusion-v1-5/stable-diffusion-v1-5` | `main` (`a3245452f1...`) | **CreativeML OpenRAIL-M** | **Yes**, subject to standard OpenRAIL behavioral restrictions | [HuggingFace Hub](https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5) | Text-to-image portrait generation on free Kaggle GPU accelerator |
| **Stable Diffusion v2.1-base** (Fallback) | `stabilityai/stable-diffusion-2-1-base` | `main` (`5ede9e4bf3...`) | **CreativeML OpenRAIL++-M** | **Yes**, subject to standard OpenRAIL behavioral restrictions | [HuggingFace Hub](https://huggingface.co/stabilityai/stable-diffusion-2-1-base) | Alternate open-weights text-to-image pipeline fallback |

### CreativeML OpenRAIL-M License Analysis
- **Open Weights**: Model weights are publicly accessible without payment or proprietary API keys.
- **Commercial Rights**: OpenRAIL-M grants royalty-free, worldwide rights to use, copy, modify, and distribute the model and derived outputs for both commercial and non-commercial purposes.
- **Use-Based Restrictions (Attachment A)**: Explicitly prohibits generating illegal content, child exploitation, defamatory or deceptive impersonation, harassment, or real-person likeness without consent.
- **Compliance in this Architecture**: Our pre-generation `SafetyEngine` programmatically enforces OpenRAIL restrictions *before* dispatching any job to the inference pipeline.

---

## 2. Python Software Dependencies (Local Orchestration)

| Package | Version | License | Primary Purpose in Architecture |
| :--- | :--- | :--- | :--- |
| **pydantic** | `>=2.7.0,<3.0.0` | MIT | Strict schema enforcement, contract validation for specs, job bundles, and manifests |
| **pyyaml** | `>=6.0.1` | MIT | Parsing human-readable YAML specification configurations |
| **pillow** | `>=10.2.0` | HPND | Image decoding, format validation, dimension checks, and mock image generation |
| **click** | `>=8.1.7` | BSD-3-Clause | CLI command tree, option parsing, exit codes |
| **rich** | `>=13.7.0` | MIT | Terminal tables, formatted execution logs, progress visualization |
| **pytest** | `>=8.1.0` | MIT | Unit, integration, and end-to-end automated testing framework |
| **pytest-cov** | `>=4.1.0` | MIT | Code coverage measurement across the test suite |
| **requests** | `>=2.31.0` | Apache-2.0 | HTTP client utilities for external telemetry verification |
| **psutil** | `>=5.9.8` | BSD-3-Clause | Hardware telemetry, memory benchmarking (RAM and CPU usage) |
| **numpy** | `>=1.26.0` | BSD-3-Clause | Numeric matrix calculations for diversity scoring |

---

## 3. Kaggle Free Accelerator Dependencies (Inference Worker)

| Package | Pinned Version | License | Primary Purpose in Kaggle Notebook |
| :--- | :--- | :--- | :--- |
| **torch** | `>=2.2.0` | Modified BSD | Deep learning tensor framework and CUDA execution |
| **torchvision** | `>=0.17.0` | BSD-3-Clause | Image transformation and tensor utilities |
| **diffusers** | `0.32.2` | Apache-2.0 | Latent Diffusion pipeline execution (`StableDiffusionPipeline`, `DPMSolverMultistepScheduler`) |
| **transformers** | `4.49.0` | Apache-2.0 | CLIP text tokenizer and text encoder execution |
| **accelerate** | `>=0.28.0` | Apache-2.0 | VRAM memory optimization and attention slicing |
| **safetensors** | `>=0.4.2` | Apache-2.0 | Fast, secure tensor deserialization |

---

## 4. Hardware & Cloud Platform Provenance

| Platform | Compute Tier | Cost | Terms of Service Compliance |
| :--- | :--- | :--- | :--- |
| **Local Laptop (Orchestrator)** | Intel Iris Xe / x86_64 CPU (16 GB RAM, Windows) | $0.00 (Local Hardware) | N/A |
| **Kaggle Notebooks (Inference Engine)** | Free Accelerator (NVIDIA Tesla T4 15GB / P100 16GB) | $0.00 (Free Tier) | Complies with Kaggle Community Guidelines; no multi-account abuse, no paid compute, single standard account |

---

## 5. Third-Party Code Disclosure

All orchestration logic (`src/avatar_system/`) was designed and authored specifically for this assessment. Standard library patterns and official open-source documentation were referenced for:
- Diffusers `StableDiffusionPipeline` execution conventions.
- Click CLI argument structuring.
- Pydantic V2 model validation idioms.
