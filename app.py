import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import json
import plotly.graph_objects as go
import plotly.express as px
from streamlit_lottie import st_lottie
import pandas as pd
import time

# --- 1. SETTING PAGE CONFIG AND THEME ---
st.set_page_config(page_title="AI Talkxo | Free AEO Analyzer", page_icon="✨", layout="wide")

main_style = """
<style>
.stApp {
    background-color: #f8faff;
    background-image: radial-gradient(at 0% 0%, #e0eafc 0px, transparent 50%),
                      radial-gradient(at 100% 0%, #cfdef3 0px, transparent 50%),
                      radial-gradient(at 100% 100%, #e0c3fc 0px, transparent 50%),
                      radial-gradient(at 0% 100%, #8ec5fc 0px, transparent 50%);
}
.stLogoContainer {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    margin-top: -3rem; 
}
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.insight-card {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 10px 30px rgba(0,0,0,0.05);
    margin-bottom: 1.5rem;
    animation: fadeIn 0.6s ease-out;
    border: 1px solid rgba(0,0,0,0.02);
}
</style>
"""
st.markdown(main_style, unsafe_allow_html=True)

# --- 2. COMPANY LOGO ---
# Make sure to replace this with your actual logo link again!
LOGO_URL = "https://i.im.ge/eBsU8z/talkxo_logo.png"

st.markdown(f'''
<div class="stLogoContainer">
    <img src="{LOGO_URL}" width="160">
</div>
''', unsafe_allow_html=True)

# --- 3. Lottie Animations (WITH SAFETY NET) ---
def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# Using a more stable GitHub raw link for the animation
lottie_ai_assist = load_lottieurl("https://raw.githubusercontent.com/andreasbm/web-skills/master/assets/animations/robot.json")

# --- 4. Main Interface Area ---
head1, head2 = st.columns([1, 4])
with head1:
    # THE FIX: If the animation loads, show it. If it fails, show an emoji. No crashing!
    if lottie_ai_assist:
        st_lottie(lottie_ai_assist, speed=1, width=150, height=150, key="ai_robot")
    else:
        st.markdown("<h1 style='text-align: center; font-size: 80px;'>🤖</h1>", unsafe_allow_html=True)

with head2:
    st.title("✨ Free AEO Optimization Suite")
    st.write("Does your website build trust with AI Answer Engines? Our analyzer checks for information density, semantic structure, and entity-first optimization to give you an immediate AEO Score and a dynamic roadmap.")

url_input = st.text_input("Enter your website URL (e.g., https://example.com)", placeholder="Enter your website URL...")

if st.button("Generate My Dynamic Report", use_container_width=True):
    if not url_input:
        st.warning("Please enter a URL first!")
    else:
        if not url_input.startswith(('http://', 'https://')):
            url_input = 'https://' + url_input
            
        with st.spinner("Scraping site and generating insights..."):
            try:
                api_key = st.secrets["GEMINI_API_KEY"]
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')

                headers = {'User-Agent': 'Mozilla/5.0'}
                response = requests.get(url_input, headers=headers, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                h1_tags = soup.find_all('h1')
                h2_tags = soup.find_all('h2')
                p_tags = soup.find_all('p')
                img_count = len(soup.find_all('img'))
                text_content = " ".join([p.text.strip() for p in p_tags])
                word_count = len(text_content.split())
                
                analysis_data = {
                    "h1": [h.text.strip() for h in h1_tags],
                    "h2": [h.text.strip() for h in h2_tags],
                    "word_count": word_count,
                    "has_schema": bool(soup.find('script', type='application/ld+json'))
                }

                prompt = f"""Review this website data for Answer Engine Optimization (AEO): {json.dumps(analysis_data)}.
                Provide your analysis as a JSON object with these exact keys:
                'overall_score' (number 1-100),
                'factual_density_percent' (estimated % of data versus fluff),
                'readability_grade' (simulated Flesch-Kincaid score like '8th Grade'),
                'semantic_structure_score' (1-100 based on heading hierarchy),
                'strengths' (list of 2 strings with a leading emoji),
                'weaknesses' (list of 2 strings with a leading emoji),
                'action_items' (list of exactly 5 tailored, actionable advice points with emojis)
                """
                
                response_content = model.generate_content(prompt).text
                json_str = response_content.replace('```json', '').replace('```', '').strip()
                result = json.loads(json_str)
                
                st.success("Analysis Complete!")
                st.markdown("---")

                # --- 5. THE MAIN DASHBOARD ---
                dash1, dash2, dash3 = st.columns([1, 2, 1])
                with dash2:
                    fig_gauge = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = result['overall_score'],
                        domain = {'x': [0, 1], 'y': [0, 1]},
                        gauge = {
                            'axis': {'range': [None, 100]},
                            'bar': {'color': "#4B0082"}, 
                            'steps' : [
                                {'range': [0, 60], 'color': "#f8e1e1"},
                                {'range': [60, 85], 'color': "#fffde8"},
                                {'range': [85, 100], 'color': "#e8fdf8"}
                            ],
                            'threshold' : {'line': {'color': "black", 'width': 4}, 'thickness': 0.75, 'value': 90}
                        },
                        title = {'text': "Answer Engine Trust Score"}
                    ))
                    fig_gauge.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={'color': "#4B0082", 'family': "Arial"}, margin=dict(t=30, b=0, l=0, r=0))
                    st.plotly_chart(fig_gauge, use_container_width=True)

                kpi_row1, kpi_row2, kpi_row3 = st.columns(3)
                
                with kpi_row1:
                    st.metric(label="📄 Total Word Count", value=f"{word_count:,}", help="Information density is key for RAG extraction.")
                with kpi_row2:
                    heading_data = {"Type": ["H1 (Main)", "H2 (Sub)"], "Count": [len(h1_tags), len(h2_tags)]}
                    fig_bars = px.bar(heading_data, x="Type", y="Count", text="Count", 
                                       title="Heading Structure Breakdown",
                                       color_discrete_sequence=['#9370DB', '#E6E6FA'])
                    fig_bars.update_traces(textposition='inside', marker_line_color='black', marker_line_width=0.5, opacity=0.8)
                    fig_bars.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig_bars, use_container_width=True)
                    
                with kpi_row3:
                    density_data = pd.DataFrame({"Category": ["Factual Data", "Filler/Fluff"], "Percent": [result['factual_density_percent'], 100-result['factual_density_percent']]})
                    fig_pie = px.pie(density_data, values="Percent", names="Category", title="Predicted Factual Density", hole=0.5, 
                                     color_discrete_sequence=['#4B0082', '#f3efff'])
                    fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig_pie, use_container_width=True)

                kpi_media1, kpi_media2, kpi

            except json.JSONDecodeError:
                st.error("Error: The AI response was not in a valid JSON format. Try scanning again or simplify your test URL.")
            except Exception as e:
                st.error(f"Oops! Something went wrong. Error details: {e}")
