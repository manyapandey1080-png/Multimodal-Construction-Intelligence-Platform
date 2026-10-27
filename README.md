# Multimodal Construction Intelligence Platform
**Skill Wallet Capstone Project 1**

A Streamlit application with four modules:
1. Site Safety & PPE Audit
2. Crack Diagnostics & Structural Integrity
3. Planning & Real Estate Valuation
4. Daily Site Assistant & Weather-Aware Advisory

## Run locally
Python 3.10+ is recommended.

```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

Open the local Streamlit URL shown in the terminal.

## Gemini setup
- Create a Gemini API key through Google AI Studio.
- Paste the key into the password field in the app sidebar.
- The key is stored in Streamlit session state only and is not written to a local file.
- If no key is provided, the app remains usable in demonstration mode. Demo results are explicitly labelled and are not based on the uploaded image.

The app uses the `google-genai` Python SDK and the `gemini-2.5-flash` model name. If that model is unavailable for your account or region, update `MODEL_NAME` in `app.py` to a supported multimodal Gemini model.

## Deploy on Streamlit Community Cloud
1. Create a GitHub repository and add `app.py`, `requirements.txt`, and `README.md`.
2. In Streamlit Community Cloud, create an app from that repository and select `app.py` as the main file.
3. Deploy. Users can paste their Gemini API key in the sidebar at runtime.

For a team deployment, prefer Streamlit secrets or a managed secret store instead of asking each user to paste a key. Never commit API keys into Git.

## Features and limitations
- Image uploads accept JPG/JPEG/PNG.
- Gemini vision output is requested as JSON; output parsing and API failures are handled gracefully.
- Safety and crack reports can be downloaded as JSON.
- Planning figures are transparent illustrative heuristics, not a bill of quantities, contractor quotation, or formal valuation.
- The Pollinations AI button opens a third-party prompt-based image endpoint. It may have its own availability, privacy, and usage policies.
- No external database is required; chat history and uploaded images remain in session memory while the session is active.

## Safety / engineering disclaimer
This is a capstone prototype and decision-support tool. A single image cannot verify full PPE compliance, detect every hazard, measure a crack reliably without a scale, or determine structural integrity. OSHA is a US workplace-safety framework; IS 456 is an Indian concrete design code and is not a PPE checklist. Always apply applicable Indian regulations, project specifications, approved drawings, and review by competent safety and structural professionals. Do not use the material heuristics for procurement without a project-specific BOQ.
