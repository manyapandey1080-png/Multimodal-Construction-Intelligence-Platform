import json
import os
import re
import urllib.parse
from datetime import datetime

import streamlit as st
from PIL import Image

# Optional Gemini SDK. The app remains usable in demo mode if unavailable.
try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except Exception:
    GEMINI_AVAILABLE = False

APP_NAME = "Multimodal Construction Intelligence Platform"
MODEL_NAME = "gemini-2.5-flash"

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------- Styling ---------------------------------------
st.markdown("""
st.markdown("""
<style>
/* ================= GLOBAL THEME ================= */

:root {
    --ink: #172033;
    --muted: #64748b;
    --accent: #f59e0b;
    --panel: #ffffff;
}

.stApp {
    background: linear-gradient(
        180deg,
        #f7f9fc 0%,
        #eef2f7 100%
    );
    color: #172033;
}

.block-container {
    padding-top: 1.5rem;
    max-width: 1440px;
}

/* ================= SIDEBAR FIX ================= */

[data-testid="stSidebar"] {
    background-color: #f1f5f9 !important;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h1,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] li,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] [data-testid="stWidgetLabel"],
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
    color: #172033 !important;
}

/* Sidebar input fields */

[data-testid="stSidebar"] input {
    color: #172033 !important;
    background-color: #ffffff !important;
    -webkit-text-fill-color: #172033 !important;
}

/* Sidebar select boxes and other widgets */

[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background-color: #ffffff;
    color: #172033;
}

/* ================= HERO HEADER ================= */

.hero {
    padding: 1.35rem 1.6rem;
    border-radius: 18px;
    color: #ffffff !important;
    background: linear-gradient(
        120deg,
        #172033 0%,
        #263b5b 65%,
        #d97706 150%
    );
    box-shadow: 0 12px 30px rgba(15, 23, 42, 0.12);
    margin-bottom: 1.2rem;
}

.hero h1 {
    margin: 0;
    font-size: 2rem;
    letter-spacing: -0.03em;
    color: #ffffff !important;
}

.hero p {
    margin: 0.45rem 0 0;
    color: #e2e8f0 !important;
}

/* ================= CONTENT CARDS ================= */

.section-card {
    background: rgba(255, 255, 255, 0.96);
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 1rem 1.15rem;
    margin: 0.4rem 0 1rem;
    color: #172033;
}

.section-card h3,
.section-card p {
    color: #172033 !important;
}

.small-muted {
    color: #64748b !important;
    font-size: 0.88rem;
}

/* ================= STATUS PILLS ================= */

.pill {
    display: inline-block;
    padding: 0.28rem 0.7rem;
    border-radius: 999px;
    font-weight: 700;
    font-size: 0.78rem;
    margin: 0.15rem 0;
}

.pill-green {
    color: #166534 !important;
    background: #dcfce7;
}

.pill-amber {
    color: #92400e !important;
    background: #fef3c7;
}

.pill-red {
    color: #991b1b !important;
    background: #fee2e2;
}

.pill-blue {
    color: #1e40af !important;
    background: #dbeafe;
}

/* ================= METRIC CARDS ================= */

div[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    padding: 0.8rem;
    border-radius: 14px;
    box-shadow: 0 3px 10px rgba(15, 23, 42, 0.04);
}

div[data-testid="stMetric"] label,
div[data-testid="stMetric"] [data-testid="stMetricLabel"],
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #172033 !important;
}

/* ================= TABS FIX ================= */

.stTabs [data-baseweb="tab"] {
    color: #334155 !important;
}

.stTabs [data-baseweb="tab"] p {
    color: #334155 !important;
}

.stTabs [aria-selected="true"] {
    color: #dc2626 !important;
}

/* ================= WARNING / ALERT FIX ================= */

[data-testid="stAlert"] {
    border-radius: 12px;
}

[data-testid="stAlert"] p,
[data-testid="stAlert"] li {
    color: #172033 !important;
}

/* ================= FILE UPLOADER FIX ================= */

[data-testid="stFileUploader"] {
    background-color: #ffffff;
    border-radius: 12px;
}

[data-testid="stFileUploader"] label,
[data-testid="stFileUploader"] section,
[data-testid="stFileUploader"] small {
    color: #334155 !important;
}

/* ================= BUTTONS ================= */

div.stButton > button {
    border-radius: 10px;
    font-weight: 650;
}

/* ================= GENERAL TEXT ================= */

[data-testid="stCaptionContainer"] {
    color: #64748b;
}

hr {
    border-color: #dbe3ee;
}
</style>
""", unsafe_allow_html=True)
# ----------------------------- Helpers ---------------------------------------
def demo_mode() -> bool:
    return not bool(st.session_state.get("gemini_api_key", "").strip()) or not GEMINI_AVAILABLE

def get_client():
    key = st.session_state.get("gemini_api_key", "").strip()
    if not key:
        return None
    if not GEMINI_AVAILABLE:
        st.warning("Gemini SDK is unavailable. Install requirements.txt to enable AI analysis.")
        return None
    try:
        return genai.Client(api_key=key)
    except Exception as exc:
        st.error(f"Could not initialize Gemini client: {exc}")
        return None

def extract_json(text: str):
    """Parse JSON even if a model wraps it in Markdown fences."""
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.I)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start >= 0 and end > start:
            return json.loads(cleaned[start:end + 1])
        raise

def gemini_json(prompt: str, image: Image.Image = None):
    client = get_client()
    if client is None:
        return None
    try:
        contents = [prompt]
        if image is not None:
            contents.append(image)
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=contents,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2,
            ),
        )
        return extract_json(response.text or "")
    except Exception as exc:
        st.error(f"Gemini request failed: {exc}")
        st.info("Check the API key, network connection, and model availability. You can still use demonstration mode.")
        return None

def json_download(data, filename):
    payload = json.dumps(data, indent=2, ensure_ascii=False)
    st.download_button(
        "⬇️ Download JSON report",
        data=payload,
        file_name=filename,
        mime="application/json",
        use_container_width=False,
    )

def status_pill(text, tone="blue"):
    st.markdown(f'<span class="pill pill-{tone}">{text}</span>', unsafe_allow_html=True)

def show_json(data):
    st.json(data, expanded=True)

def inr_format(amount):
    amount = float(amount)
    if amount >= 10_000_000:
        return f"₹{amount / 10_000_000:.2f} Cr"
    if amount >= 100_000:
        return f"₹{amount / 100_000:.2f} L"
    return f"₹{amount:,.0f}"

def image_upload(label, key):
    file = st.file_uploader(label, type=["jpg", "jpeg", "png"], key=key)
    if file:
        try:
            image = Image.open(file).convert("RGB")
            st.image(image, caption=file.name, use_container_width=True)
            return image
        except Exception:
            st.error("This image could not be opened. Please upload a valid JPG or PNG.")
    return None

def safety_demo():
    return {
        "safety_score": 72,
        "overall_status": "Needs Improvement",
        "ppe_detection": {
            "helmet": {"status": "Detected on most visible workers", "compliant": True},
            "high_visibility_vest": {"status": "One worker appears without a visible vest", "compliant": False},
            "steel_toe_boots": {"status": "Not reliably verifiable from this image", "compliant": None},
            "safety_harness": {"status": "Not applicable / not clearly visible", "compliant": None}
        },
        "site_hazards": [
            {"hazard": "Unprotected edge / fall exposure", "severity": "High",
             "evidence": "Potential exposed edge in the visible work area; verify on site.",
             "corrective_remedy": "Install compliant guardrails or covers, mark the exclusion zone, and use approved fall protection."},
            {"hazard": "PPE visibility gap", "severity": "Medium",
             "evidence": "High-visibility vest is not clearly visible on at least one person.",
             "corrective_remedy": "Pause entry until required PPE is worn and checked by the site supervisor."}
        ],
        "limitations": "Demonstration output only; no image was analyzed by an AI model."
    }

def crack_demo():
    return {
        "defect_type": "Hairline",
        "estimated_crack_width_mm": 0.3,
        "confidence": "Low (demonstration)",
        "observed_pattern": "A thin surface line; scale and depth cannot be confirmed from a single photo.",
        "possible_root_causes": ["Drying shrinkage", "Surface plaster movement", "Thermal movement"],
        "recommended_repairs": [
            "Measure and map the crack; monitor for change before selecting a repair.",
            "For stable, non-structural hairline cracks, use a compatible crack filler or repair mortar after substrate preparation."
        ],
        "urgency": "Routine inspection",
        "engineer_review_required": True,
        "limitations": "Demonstration output only; not a structural diagnosis."
    }

SAFETY_PROMPT = """You are a construction-site visual safety assistant. Analyze the supplied image conservatively.
Return ONLY valid JSON matching this schema:
{
 "safety_score": integer 0-100,
 "overall_status": "Compliant"|"Needs Improvement"|"Unsafe"|"Unable to Assess",
 "ppe_detection": {
   "helmet":{"status":string,"compliant":true|false|null},
   "high_visibility_vest":{"status":string,"compliant":true|false|null},
   "steel_toe_boots":{"status":string,"compliant":true|false|null},
   "safety_harness":{"status":string,"compliant":true|false|null}
 },
 "site_hazards":[{"hazard":string,"severity":"Low"|"Medium"|"High"|"Critical",
 "evidence":string,"corrective_remedy":string}],
 "limitations":string
}
Only report visual evidence. Use null / Unable to Assess when an item cannot be verified from the image; do not infer hidden PPE.
Consider relevant workplace safety principles and Indian construction context. OSHA is a US regulatory framework; IS 456 is a concrete design code, not a PPE standard, so do not claim either is fully assessed from an image. Never claim legal compliance based on a photo. Include practical corrective actions. If imminent danger is visible, state that work should stop and a competent site safety professional should inspect."""

CRACK_PROMPT = """You are a construction defect triage assistant, not a substitute for a licensed structural engineer.
Inspect the supplied concrete/wall image and return ONLY valid JSON:
{
 "defect_type":"Hairline"|"Settlement"|"Structural Shear"|"Thermal Expansion"|"Spalling"|"Other"|"Unable to Assess",
 "estimated_crack_width_mm":number|null,
 "confidence":"Low"|"Medium"|"High",
 "observed_pattern":string,
 "possible_root_causes":[string],
 "recommended_repairs":[string],
 "urgency":"Routine inspection"|"Prompt engineer review"|"Urgent assessment"|"Immediate safety action",
 "engineer_review_required":true,
 "limitations":string
}
Estimate width only if a scale is visible; otherwise return null and explain. Do not assert root cause from a photo. Distinguish cosmetic from potentially structural only cautiously. Mention that epoxy injection, re-grouting, stitching, patch repair, or other work must be selected by a qualified engineer after diagnosis. If severe displacement, wide diagonal cracks, exposed/corroded reinforcement, or falling concrete is apparent, recommend restricting access and immediate professional assessment."""

# ----------------------------- Sidebar ---------------------------------------
with st.sidebar:
    st.markdown("## 🏗️ MCIP")
    st.caption("Skill Wallet Capstone Project 1")
    st.markdown("---")
    st.subheader("🔐 Gemini configuration")
    api_key_input = st.text_input(
        "Google Gemini API key",
        type="password",
        value=st.session_state.get("gemini_api_key", ""),
        help="Key is held in this app session only. Do not commit secrets to source control.",
        placeholder="Paste API key (optional)",
    )
    st.session_state["gemini_api_key"] = api_key_input.strip()
    if st.session_state["gemini_api_key"] and GEMINI_AVAILABLE:
        status_pill("Gemini enabled", "green")
    elif st.session_state["gemini_api_key"] and not GEMINI_AVAILABLE:
        status_pill("SDK missing — demo mode", "amber")
    else:
        status_pill("Demonstration mode", "blue")
    st.caption("AI calls send the selected image and prompt to Google Gemini when a key is provided.")
    st.markdown("---")
    st.subheader("🧭 Architecture")
    st.markdown("""
    **UI:** Streamlit  
    **Vision + assistant:** Gemini multimodal API  
    **Valuation:** transparent local estimator  
    **Rendering concept:** Pollinations prompt link  
    **Storage:** session state only  
    **Deployment:** Streamlit Community Cloud
    """)
    st.markdown("---")
    st.subheader("Modules")
    st.markdown("1. Site Safety & PPE Audit  \n2. Crack Diagnostics  \n3. Planning & Valuation  \n4. Daily Site Assistant")
    st.caption("No external database is required.")

# ----------------------------- Header ----------------------------------------
st.markdown(f"""
<div class="hero">
  <h1>🏗️ {APP_NAME}</h1>
  <p>Visual safety triage, defect assessment, project estimation, and weather-aware site guidance.</p>
</div>
""", unsafe_allow_html=True)

st.warning("Important: Outputs are decision-support estimates, not certifications or engineering approvals. Photos can miss hazards and structural defects. Follow applicable local law, site procedures, and review by competent safety / structural professionals.")

tab1, tab2, tab3, tab4 = st.tabs([
    "🦺 Site Safety & PPE Audit",
    "🧱 Crack Diagnostics",
    "📐 Planning & Valuation",
    "🌦️ Daily Site Assistant",
])

# ============================= TAB 1 ==========================================
with tab1:
    st.subheader("Site Safety & PPE Audit · Epic 2")
    st.write("Upload a site photo to generate a visual PPE checklist and hazard register.")
    image = image_upload("Construction site photo (JPG / PNG)", "safety_image")
    col_a, col_b = st.columns([1, 2])
    with col_a:
        run_safety = st.button("🔎 Analyze safety image", type="primary", use_container_width=True, disabled=image is None)
    with col_b:
        st.caption("Best results: clear, well-lit images with workers and work areas visible.")
    if run_safety:
        with st.spinner("Reviewing visible PPE and site hazards..."):
            result = gemini_json(SAFETY_PROMPT, image) if not demo_mode() else None
            if result is None:
                result = safety_demo()
                result["limitations"] = "Demonstration fallback: add a valid Gemini API key to analyze the uploaded image."
            st.session_state["safety_result"] = result
    result = st.session_state.get("safety_result")
    if result:
        score = result.get("safety_score", 0)
        status = str(result.get("overall_status", "Unable to Assess"))
        m1, m2, m3 = st.columns(3)
        m1.metric("Visual safety score", f"{score}/100" if isinstance(score, (int, float)) else "N/A")
        m2.metric("Overall status", status)
        m3.metric("Hazards listed", len(result.get("site_hazards", [])))
        status_pill(status, "green" if status.lower() == "compliant" else "red" if status.lower() == "unsafe" else "amber")
        st.markdown("#### PPE detection checklist")
        ppe = result.get("ppe_detection", {})
        cols = st.columns(4)
        for idx, (key, item) in enumerate(ppe.items()):
            item = item if isinstance(item, dict) else {"status": str(item), "compliant": None}
            with cols[idx % 4]:
                st.markdown(f"**{key.replace('_',' ').title()}**")
                compliant = item.get("compliant")
                tone = "green" if compliant is True else "red" if compliant is False else "amber"
                label = "Compliant" if compliant is True else "Not compliant" if compliant is False else "Unverified"
                status_pill(label, tone)
                st.caption(item.get("status", "No details provided"))
        st.markdown("#### Site hazard register")
        hazards = result.get("site_hazards", [])
        if not hazards:
            st.success("No hazards were returned. This does not prove the site is hazard-free.")
        for hazard in hazards:
            with st.expander(f"{hazard.get('hazard','Hazard')} · {hazard.get('severity','Unknown')}"):
                sev = hazard.get("severity", "Medium")
                status_pill(sev, "red" if sev in ("High", "Critical") else "amber" if sev == "Medium" else "green")
                st.write("**Evidence:**", hazard.get("evidence", "Not specified"))
                st.write("**Corrective remedy:**", hazard.get("corrective_remedy", "Consult the site safety officer."))
        if result.get("limitations"):
            st.caption("Limitations: " + str(result["limitations"]))
        json_download(result, f"site_safety_report_{datetime.now():%Y%m%d_%H%M%S}.json")
    else:
        st.info("Upload a photo and select **Analyze safety image**. Without a Gemini key, a clearly labelled demo report is shown.")

# ============================= TAB 2 ==========================================
with tab2:
    st.subheader("Crack Diagnostics & Structural Integrity · Epic 2")
    st.write("Use this as preliminary defect triage only. A photograph cannot establish crack depth, movement, or structural capacity.")
    crack_image = image_upload("Concrete / wall surface photo (JPG / PNG)", "crack_image")
    if st.button("🧪 Assess visible defect", type="primary", use_container_width=False, disabled=crack_image is None):
        with st.spinner("Assessing visible crack pattern..."):
            result = gemini_json(CRACK_PROMPT, crack_image) if not demo_mode() else None
            if result is None:
                result = crack_demo()
                result["limitations"] = "Demonstration fallback: add a valid Gemini API key for image-specific AI output."
            st.session_state["crack_result"] = result
    result = st.session_state.get("crack_result")
    if result:
        c1, c2, c3 = st.columns(3)
        c1.metric("Defect category", result.get("defect_type", "Unable to Assess"))
        width = result.get("estimated_crack_width_mm")
        c2.metric("Estimated width", f"{width} mm" if width is not None else "Not measurable")
        c3.metric("Urgency", result.get("urgency", "Needs review"))
        status_pill(result.get("urgency", "Review"), "red" if "Immediate" in str(result.get("urgency")) or "Urgent" in str(result.get("urgency")) else "amber")
        st.markdown("#### Observed pattern")
        st.write(result.get("observed_pattern", "No description returned."))
        st.markdown("#### Possible root causes")
        for cause in result.get("possible_root_causes", []):
            st.markdown(f"- {cause}")
        st.markdown("#### Recommended next steps / repairs")
        for repair in result.get("recommended_repairs", []):
            st.markdown(f"- {repair}")
        if result.get("engineer_review_required", True):
            st.info("Engineer review required before repair selection, especially for diagonal cracks, displacement, recurring cracks, corrosion, or spalling.")
        if result.get("limitations"):
            st.caption("Limitations: " + str(result["limitations"]))
        json_download(result, f"crack_diagnostic_{datetime.now():%Y%m%d_%H%M%S}.json")
    else:
        st.info("Upload a surface image to begin.")

# ============================= TAB 3 ==========================================
with tab3:
    st.subheader("Planning & Real Estate Valuation · Epic 3")
    st.write("A transparent early-stage estimator. Edit assumptions with local BOQ rates and market comparables before using for a real project.")
    left, right = st.columns([1, 1])
    with left:
        structure = st.selectbox("Structure type", ["Residential apartment", "Independent house", "Commercial office", "Warehouse / industrial shed", "Institutional building"])
        area = st.number_input("Built-up area (sq ft)", min_value=100, max_value=5_000_000, value=2000, step=100)
        tier = st.selectbox("Location tier", ["Tier 1", "Tier 2", "Tier 3"])
        completion = st.slider("Physical completion", min_value=0, max_value=100, value=35, step=5)
        quality = st.selectbox("Construction specification", ["Economy", "Standard", "Premium"], index=1)
    rate_base = {
        "Residential apartment": 2100, "Independent house": 2300,
        "Commercial office": 2800, "Warehouse / industrial shed": 1500,
        "Institutional building": 2500
    }[structure]
    tier_factor = {"Tier 1": 1.25, "Tier 2": 1.0, "Tier 3": 0.82}[tier]
    quality_factor = {"Economy": 0.82, "Standard": 1.0, "Premium": 1.35}[quality]
    rate = rate_base * tier_factor * quality_factor
    total_budget = area * rate
    incurred = total_budget * completion / 100
    market_factor = {"Tier 1": 1.55, "Tier 2": 1.25, "Tier 3": 1.05}[tier]
    market_value = total_budget * market_factor * (0.65 + 0.35 * completion / 100)
    # Conceptual quantities, intentionally rough rules of thumb for preliminary planning.
    cement_bags = area * 0.40
    steel_kg = area * 4.0
    with right:
        st.markdown("#### Estimated project snapshot")
        st.metric("Indicative project budget", inr_format(total_budget))
        st.metric("Capital expenditure incurred", inr_format(incurred), f"{completion}% physical completion")
        st.metric("Indicative current asset value", inr_format(market_value))
        st.metric("Indicative cost rate", f"₹{rate:,.0f} / sq ft")
        st.progress(completion / 100, text=f"Milestone progress · {completion}% complete")
        st.caption("Valuation is a simplified model, not a formal property valuation. It excludes land cost, financing, taxes, approvals, and project-specific conditions unless reflected in the entered assumptions.")
    st.markdown("#### Preliminary material planning")
    q1, q2, q3 = st.columns(3)
    q1.metric("Cement", f"{cement_bags:,.0f} bags", "Approx. 50 kg bags")
    q2.metric("Reinforcement steel", f"{steel_kg/1000:,.2f} tonnes")
    q3.metric("Concrete / BOQ review", "Required", "Confirm using structural drawings")
    st.caption("Material rules of thumb vary substantially by structural system, spans, foundations, storeys, mix design, and specifications. Do not procure materials from these figures alone.")
    st.markdown("---")
    st.markdown("#### Conceptual 3D architectural rendering prompt")
    render_style = st.selectbox("Rendering style", ["Photorealistic architectural visualization", "Minimal contemporary design", "Sustainable green building", "Isometric construction progress view"])
    floors = st.number_input("Approximate floors", min_value=1, max_value=100, value=2)
    render_prompt = (
        f"{render_style} of a {structure.lower()}, {area:,} square feet built-up area, "
        f"{floors} floors, located in an Indian {tier} city, {quality.lower()} specification, "
        "realistic Indian urban context, accurate proportions, professional architectural visualization, "
        "daylight, clear facade materials, no text, no logos. Conceptual design only."
    )
    st.text_area("Generated prompt", value=render_prompt, height=100, key="render_prompt_box")
    encoded_prompt = urllib.parse.quote(render_prompt, safe="")
    pollinations_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=768&nologo=true"
    st.link_button("🎨 Open concept rendering (Pollinations AI)", pollinations_url)
    st.caption("This opens a third-party image-generation endpoint. Do not submit confidential project details. Generated imagery is conceptual and not a construction drawing.")
    budget_report = {
        "structure_type": structure, "built_up_sqft": area, "location_tier": tier,
        "specification": quality, "completion_percent": completion,
        "estimated_cost_per_sqft_inr": round(rate, 2),
        "estimated_total_project_budget_inr": round(total_budget, 2),
        "estimated_capex_incurred_inr": round(incurred, 2),
        "indicative_asset_value_inr": round(market_value, 2),
        "estimated_cement_bags_50kg": round(cement_bags),
        "estimated_steel_kg": round(steel_kg),
        "render_prompt": render_prompt,
        "assumptions_note": "Preliminary estimates only; validate using local BOQ, structural drawings, contractor quotes, and registered valuation."
    }
    json_download(budget_report, "planning_valuation_estimate.json")

# ============================= TAB 4 ==========================================
with tab4:
    st.subheader("Daily Site Assistant & Weather-Aware Advisory · Epic 5")
    weather = st.selectbox("Current / forecast site condition", ["Normal", "High Wind", "Heavy Rain", "Extreme Heat"])
    alerts = {
        "Normal": ("Routine controls", "Continue work under the approved method statement. Maintain housekeeping, PPE checks, access routes, lifting plans, and daily toolbox talks.", "blue"),
        "High Wind": ("Wind / lifting alert", "Suspend crane, hoist, scaffold, and work-at-height operations when wind exceeds equipment or site-plan limits. Secure loose materials and signage; follow manufacturer wind thresholds.", "red"),
        "Heavy Rain": ("Rain / electrical / access alert", "Stop work in flooded or unstable areas. Isolate and inspect electrical equipment, protect temporary power with appropriate RCD/GFCI protection, check excavations and slopes, and prevent runoff from undermining foundations. Reassess concrete placement and curing with the engineer.", "red"),
        "Extreme Heat": ("Heat stress alert", "Provide drinking water, shaded recovery, acclimatization, and work-rest cycles. Monitor workers for heat illness. Adjust work timing and follow local heat-stress procedures; protect fresh concrete and follow the approved curing specification.", "amber"),
    }
    title, message, tone = alerts[weather]
    st.markdown(f'<div class="section-card"><h3>{title}</h3><p>{message}</p></div>', unsafe_allow_html=True)
    status_pill(weather, tone)
    st.caption("Apply the project-specific emergency plan and equipment manufacturer limits; this advisory does not replace the site supervisor's stop-work authority.")
    st.markdown("---")
    st.markdown("#### Construction engineering assistant")
    st.caption("Ask about sequencing, method statements, quality checks, materials, safety planning, or construction terminology. For high-risk decisions, consult the responsible engineer.")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    user_question = st.chat_input("Ask a construction or site-planning question...")
    if user_question:
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.markdown(user_question)
        with st.chat_message("assistant"):
            with st.spinner("Preparing guidance..."):
                answer = None
                client = get_client() if not demo_mode() else None
                if client:
                    try:
                        history_text = "\n".join(
                            f'{m["role"].upper()}: {m["content"]}'
                            for m in st.session_state.chat_history[-10:]
                        )
                        response = client.models.generate_content(
                            model=MODEL_NAME,
                            contents=(
                                "You are a careful construction engineering assistant. Give concise, practical, "
                                "risk-aware guidance. Ask clarifying questions when project context is missing. "
                                "Never certify structural safety or replace a licensed engineer, site safety officer, "
                                "local code, approved drawings, or method statement. State assumptions. Current weather "
                                f"condition selected: {weather}.\n\nConversation:\n{history_text}"
                            ),
                        )
                        answer = response.text
                    except Exception as exc:
                        st.error(f"Assistant request failed: {exc}")
                if not answer:
                    answer = (
                        f"**Demo response for: {user_question}**\n\n"
                        f"Current selected condition: **{weather}**. Start with the approved drawings and method statement, "
                        "identify the relevant hazard/quality acceptance criteria, and record the inspection before work proceeds. "
                        "If this affects structural stability, lifting, excavation, electrical safety, or work at height, pause the "
                        "affected activity and consult the responsible site engineer or safety officer. Add a Gemini API key for "
                        "interactive AI responses."
                    )
                st.markdown(answer)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("Clear chat"):
            st.session_state.chat_history = []
            st.rerun()

st.markdown("---")
st.caption("Multimodal Construction Intelligence Platform · Skill Wallet Capstone Project 1 · Session-only data; no database configured.")
