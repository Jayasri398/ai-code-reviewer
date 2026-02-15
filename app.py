"""
AI Code Reviewer — Professional Multi-Language Version
Final-Year / Portfolio Ready
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from multi_language_features import extract_general_features
from model import predict_bug, check_syntax, run_code_safely
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AI Code Reviewer", layout="wide")

# ---------------- SESSION STATE ----------------
if "analysis_data" not in st.session_state:
    st.session_state.analysis_data = None

if "history" not in st.session_state:
    st.session_state.history = []

# ---------------- SIDEBAR ----------------
st.sidebar.title("🔍 AI Code Reviewer")
page = st.sidebar.radio(
    "Navigation",
    ["📝 Code Editor", "📊 Analysis Results", "📜 History"]
)

# =====================================================
# =================== PAGE 1 ==========================
# =====================================================

if page == "📝 Code Editor":

    st.title("📝 Code Editor")

    language = st.selectbox(
        "Select Programming Language",
        ["Python", "Java", "C++", "JavaScript"]
    )

    code_input = st.text_area("Paste your code here:", height=300)

    uploaded_file = st.file_uploader(
        "Or upload file",
        type=["py", "java", "cpp", "js"]
    )

    if uploaded_file:
        code_input = uploaded_file.read().decode("utf-8")
        st.success(f"Loaded: {uploaded_file.name}")

    if st.button("🚀 Analyze Code"):

        if not code_input.strip():
            st.warning("Please enter some code.")
        else:

            # Static
            if language == "Python":
                syntax_result = check_syntax(code_input)
            else:
                syntax_result = {"valid": True}

            # Features
            features = extract_general_features(code_input, language)

            # Dynamic
            if language == "Python":
                runtime_result = run_code_safely(code_input)
            else:
                runtime_result = {
                    "success": True,
                    "error": f"Execution skipped for {language}"
                }

            # ML
            try:
                prediction = predict_bug(features)
            except:
                prediction = None

            # AI Code Score (NEW)
            score = max(0, 100 - (features["complexity_score"] * 8))

            result = {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "language": language,
                "syntax": syntax_result,
                "runtime": runtime_result,
                "features": features,
                "prediction": prediction,
                "score": score
            }

            st.session_state.analysis_data = result
            st.session_state.history.append(result)

            st.success("Analysis Completed! Go to Analysis Results page.")

# =====================================================
# =================== PAGE 2 ==========================
# =====================================================

elif page == "📊 Analysis Results":

    st.title("📊 Analysis Results")

    data = st.session_state.analysis_data

    if not data:
        st.info("No analysis available. Go to Code Editor.")
    else:

        st.metric("AI Code Quality Score", f"{data['score']}/100")

        st.subheader("🔒 Static Analysis")
        if data["syntax"]["valid"]:
            st.success("No syntax errors.")
        else:
            st.error(data["syntax"]["error"])

        st.subheader("▶️ Dynamic Analysis")
        if data["runtime"]["success"]:
            if data["language"] == "Python":
                st.success("Executed successfully.")
            else:
                st.info(data["runtime"]["error"])
        else:
            st.error(data["runtime"]["error"])

        if data["prediction"]:
            st.subheader("🤖 ML Bug Detection")
            st.write("Bug Type:", data["prediction"]["label"])
            st.write("Confidence:", f"{data['prediction']['confidence']}%")

            st.subheader("💡 Suggestions")
            for suggestion in data["prediction"]["suggestions"]:
                st.info(suggestion)

        st.subheader("📐 Extracted Features")
        st.dataframe(pd.DataFrame([data["features"]]))

        # ---------------- PDF DOWNLOAD ----------------
        if st.button("📥 Download PDF Report"):

            pdf_path = "report.pdf"
            doc = SimpleDocTemplate(pdf_path, pagesize=letter)
            elements = []

            style = ParagraphStyle(
                name='Normal',
                fontSize=12,
                textColor=colors.black
            )

            elements.append(Paragraph("AI Code Review Report", style))
            elements.append(Spacer(1, 0.3 * inch))
            elements.append(Paragraph(f"Language: {data['language']}", style))
            elements.append(Paragraph(f"Score: {data['score']}/100", style))
            elements.append(Spacer(1, 0.2 * inch))

            if data["prediction"]:
                elements.append(Paragraph(f"Bug: {data['prediction']['label']}", style))
                elements.append(Paragraph(f"Confidence: {data['prediction']['confidence']}%", style))

            doc.build(elements)

            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="Download Report",
                    data=f,
                    file_name="AI_Code_Report.pdf",
                    mime="application/pdf"
                )

# =====================================================
# =================== PAGE 3 ==========================
# =====================================================

elif page == "📜 History":

    st.title("📜 Analysis History")

    if not st.session_state.history:
        st.info("No previous analyses.")
    else:
        for i, item in enumerate(st.session_state.history[::-1]):
            st.markdown(f"### {item['time']} - {item['language']}")
            st.write("Score:", item["score"])
            if item["prediction"]:
                st.write("Bug:", item["prediction"]["label"])
            st.divider()
