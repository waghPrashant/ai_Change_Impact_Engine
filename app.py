import streamlit as st
import json
import openai

# 🔑 Set your OpenAI key
openai.api_key = "YOUR_API_KEY"

# Load data
with open("dependencies.json") as f:
    dependencies = json.load(f)

with open("incidents.json") as f:
    incidents = json.load(f)

# 🔹 Function: Get impacted services
def get_impacted_services(changed_service):
    impacted = set()
    queue = [changed_service]

    while queue:
        service = queue.pop(0)
        if service not in impacted:
            impacted.add(service)
            for dep in dependencies.get(service, []):
                queue.append(dep)

    return list(impacted)

# 🔹 Function: AI Risk Analysis
from openai import OpenAI
client = OpenAI()

def analyze_risk(change_desc, services):
    change_desc = change_desc.lower()

    risk = "Low"
    score = 0.3
    focus = []
    
    # 🔴 High-risk patterns
    if "null" in change_desc or "exception" in change_desc:
        risk = "High"
        score = 0.85
        focus.append("Null handling")

    if "timeout" in change_desc or "latency" in change_desc:
        risk = "High"
        score = 0.8
        focus.append("API timeout / retries")

    if "duplicate" in change_desc or "async" in change_desc:
        risk = "High"
        score = 0.9
        focus.append("Concurrency / idempotency")

    # 🟠 Medium-risk patterns
    if "rounding" in change_desc or "calculation" in change_desc:
        if risk != "High":
            risk = "Medium"
            score = 0.6
        focus.append("Calculation accuracy")

    if "deployment" in change_desc or "release" in change_desc:
        if risk != "High":
            risk = "Medium"
            score = 0.65
        focus.append("Regression risk")

    return {
        "risk": risk,
        "score": score,
        "impact": services,
        "focus": focus,
        "tests": ["Edge cases", "Integration tests"]
    }

# 🔹 UI
st.title("🚀 AI Change Impact & Risk Engine")

change_desc = st.text_area("Enter Change Description")
service = st.selectbox("Select Changed Service", list(dependencies.keys()))

if st.button("Analyze Impact"):
    impacted_services = get_impacted_services(service)

    st.subheader("Impacted Services")
    st.write(impacted_services)

    result = analyze_risk(change_desc, impacted_services)

    st.subheader("AI Risk Analysis")
    st.code(result, language="json")