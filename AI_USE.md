# AI Assistance Disclosure (AI_USE.md)

**Project**: Open-Source AI Human-Avatar Generation System (Track 02)  
**Assessment**: INCUBRIX PRIVATE LIMITED — SASTRA 2027 Graduate Hiring  
**Candidate Disclosure Policy**: Full Transparency  

---

## 1. AI Coding Assistance Tools Used

- **Primary Tool**: Google Antigravity Agentic Assistant / Gemini 3.7 Flash
- **Role in Workflow**: Senior ML Engineer + Software Architect + QA Engineer pair programmer
- **Environment**: Antigravity IDE (Local Windows Workstation)

---

## 2. Scope of AI Assistance

The AI assistant was utilized to assist with the following development phases:

1. **Architecture & Project Scaffolding**: Formulating the decoupled Local Orchestrator vs. Free Kaggle Accelerator architecture and defining directory hierarchies.
2. **Schema & Contract Authoring**: Writing Pydantic V2 models for `AvatarSpec`, `PromptBundle`, `JobBundle`, and `ProvenanceManifest`.
3. **Safety Engine Design**: Implementing regex patterns for public figure likeness detection, deepfake intent detection, and reference consent verification.
4. **Kaggle Notebook Generation**: Authoring the self-contained `avatar_generation_kaggle.ipynb` notebook with pinned diffusers/torch versions.
5. **Test Suite Authoring**: Generating comprehensive unit, integration, and end-to-end tests in `pytest`.
6. **Documentation & Benchmarking Scripts**: Structuring the technical report, reproduction instructions, and automated benchmark runners.

---

## 3. Human Oversight & Live Verification

All AI-generated code, schemas, and documentation were subjected to strict human review and verification:

1. **Zero Fabrication Policy**: Verified that benchmark results, SHA256 checksums, and test executions reflect actual local and environment runs, not mocked or hallucinated values.
2. **Credential Safety Audit**: Verified that zero Kaggle API keys, passwords, or personal access tokens are hardcoded, logged, or committed to Git.
3. **Local Execution & Debugging**: Ran pytest suite (39 tests passing at 88% code coverage) and verified CLI commands in Windows PowerShell.
4. **Licensing Verification**: Manually checked CreativeML OpenRAIL-M license terms on Hugging Face to ensure commercial and academic eligibility.

---

## 4. Prompts & Instructions Used

The full system prompt and task instructions were grounded in the INCUBRIX Track 02 Human Avatar assessment specification, prioritizing:
- Neutral, inclusive descriptors without national stereotypes.
- Strict deterministic seed assignment.
- Pre-generation safety refusal layer.
- Complete machine-readable cryptographic provenance.
- Clean reproduction on non-GPU local hardware.
