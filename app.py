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

# --- CUSTOM CSS FOR PREMIUM DESIGN ---
main_style = """
<style>
/* Import premium Google Font */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;700;800&display=swap');

/* Apply font to everything */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* 1. White Background with Subtle Social Media/Marketing SVG Pattern */
.stApp {
    background-color: #ffffff;
    background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%236366f1' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}

/* 2. Premium URL Input Box (Huge, pill-shaped, reactive) */
div[data-baseweb="input"] {
    border-radius: 50px !important;
    background-color: #ffffff !important;
    border: 2px solid #e2e8f0 !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    box-shadow: 0 10px 25px rgba(0,0,0,0.05) !important;
    padding: 5px 15px !important;
}
div[data-baseweb="input"]:focus-within {
    border-color: #6366f1 !important;
    box-shadow: 0 15px 35px rgba(99, 102, 241, 0.2) !important;
    transform: translateY(-2px);
}
input[type="text"] {
    font-size: 1.1rem !important;
    color: #1e293b !important;
    padding: 15px !important;
}

/* 3. Reactive, "Breathing" Insight Cards */
@keyframes fadeIn { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }
.insight-card {
    background: #ffffff;
    border-radius: 20px;
    padding: 2rem;
    box-shadow: 0 4px 15px rgba(0,0,0,0.03);
    margin-bottom: 1.5rem;
    animation: fadeIn 0.6s ease-out;
    border: 1px solid #f1f5f9;
    transition: all 0.3s ease;
}
/* Mouse cursor hover reaction */
.insight-card:hover {
    transform: translateY(-8px) scale(1.01);
    box-shadow: 0 20px 40px rgba(99, 102, 241, 0.08);
    border-color: #e0e7ff;
}

/* 4. Center Logo */
.stLogoContainer {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    margin-top: -2rem; 
    margin-bottom: 2rem;
    transition: transform 0.3s ease;
}
.stLogoContainer:hover {
    transform: scale(1.05);
}

/* Standardize headings */
h1, h2, h3, h4 {
    color: #0f172a !important;
    font-weight: 800 !important;
    letter-spacing: -0.5px !important;
}
</style>
"""
st.markdown(main_style, unsafe_allow_html=True)

# --- 2. COMPANY LOGO ---
LOGO_URL = "https://i.im.ge/eBsU8z/talkxo_logo.png"

st.markdown(f'''
<div class="stLogoContainer">
    <img src="{LOGO_URL}" width="180">
</div>
''', unsafe_allow_html=True)

# --- 3. Lottie Animations ---
def load_lottieurl(url: str):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

lottie_ai_assist = load_lottieurl("https://raw.githubusercontent.com/andreasbm/web-skills/master/assets/animations/robot.json")

# --- 4. Main Interface Area ---
head1, head2, head3 = st.columns([1, 4, 1])
with head2:
    col_anim, col_text = st.columns([1, 5])
    with col_anim:
        if lottie_ai_assist:
            st_lottie(lottie_ai_assist, speed=1, width=100, height=100, key="ai_robot")
        else:
            st.markdown("<h1 style='text-align: center; font-size: 60px;'>🤖</h1>", unsafe_allow_html=True)
    with col_text:
        # Broken into safe strings to prevent GitHub from chopping the line
        header_html = "<h1 style='text-align: left; margin-bottom: 0;'>Free AEO Optimization Suite</h1>"
        st.markdown(header_html, unsafe_allow_html=True)
        
        desc_html = """
        <p style='font-size: 1.1rem; color: #64748b; margin-top: 5px;'>
        Does your website build trust with AI Answer Engines? Our analyzer checks for information density, semantic structure, and entity-first optimization.
        </p>
        """
        st.markdown(desc_html, unsafe_allow_html=True)

    st.write("") # Spacing
    url_input = st.text_input("", placeholder="Drop your website URL here (e.g., letshyphen.com) 🚀")

    if st.button("✨ Generate My Dynamic Report", use_container_width=True):
        if not url_input:
            st.warning("Please enter a URL first!")
        else:
            if not url_input.startswith(('http://', 'https://')):
                url_input = 'https://' + url_input
                
            with st.spinner("Analyzing neural structure and entity density..."):
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
                    
                    st.success("✅ Analysis Complete!")
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
                                'bar': {'color': "#6366f1"}, 
                                'steps' : [
                                    {'range': [0, 60], 'color': "#fee2e2"},
                                    {'range': [60, 85], 'color': "#fef9c3"},
                                    {'range': [85, 100], 'color': "#dcfce3"}
                                ],
                                'threshold' : {'line': {'color': "#0f172a", 'width': 4}, 'thickness': 0.75, 'value': 90}
                            },
                            title = {'text': "AI Engine Trust Score", 'font': {'color': '#0f172a', 'size': 24}}
                        ))
                        fig_gauge.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={'family': "Plus Jakarta Sans"}, margin=dict(t=50, b=0, l=0, r=0))
                        st.plotly_chart(fig_gauge, use_container_width=True)

                    kpi_row1, kpi_row2, kpi_row3 = st.columns(3)
                    
                    with kpi_row1:
                        st.metric(label="📄 Total Word Count", value=f"{word_count:,}", help="Information density is key for RAG extraction.")
                    with kpi_row2:
                        heading_data = {"Type": ["H1 (Main)", "H2 (Sub)"], "Count": [len(h1_tags), len(h2_tags)]}
                        fig_bars = px.bar(heading_data, x="Type", y="Count", text="Count", 
                                           title="Heading Structure Breakdown",
                                           color_discrete_sequence=['#818cf8', '#c7d2fe'])
                        fig_bars.update_traces(textposition='inside', marker_line_color='black', marker_line_width=0, opacity=0.9, borderradius=8)
                        fig_bars.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font={'family': "Plus Jakarta Sans"})
                        st.plotly_chart(fig_bars, use_container_width=True)
                        
                    with kpi_row3:
                        density_data = pd.DataFrame({"Category": ["Factual Data", "Filler/Fluff"], "Percent": [result['factual_density_percent'], 100-result['factual_density_percent']]})
                        fig_pie = px.pie(density_data, values="Percent", names="Category", title="Predicted Factual Density", hole=0.6, 
                                         color_discrete_sequence=['#6366f1', '#f1f5f9'])
                        fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font={'family': "Plus Jakarta Sans"})
                        st.plotly_chart(fig_pie, use_container_width=True)

                    kpi_media1, kpi_media2, kpi_media3 = st.columns(3)
                    
                    with kpi_media1:
                        st.metric(label="Schema Found?", value="✅ Verified" if analysis_data["has_schema"] else "❌ Missing", help="Entity data must be provided via Schema.")
                    with kpi_media2:
                        st.metric(label="Rich Media Count", value=img_count, help="Images and videos build comprehensive answer context.")
                    with kpi_media3:
                        read_levels = ["4th Grade", "6th Grade", "8th Grade", "10th Grade", "12th Grade", "Grad School"]
                        read_scores = [0, 20, 40, 60, 80, 100]
                        read_value = read_scores[read_levels.index(result['readability_grade'])] if result['readability_grade'] in read_levels else 50
                        fig_read = go.Figure(go.Indicator(
                            mode = "gauge+number",
                            value = read_value,
                            title = {'text': f"Readability Level<br><span style='font-size:0.8em;color:gray'>Grade: {result['readability_grade']}</span>", 'font': {'color': '#0f172a'}},
                            gauge = {
                                'axis': {'range': [None, 100], 'tickvals': read_scores, 'ticktext': read_levels},
                                'bar': {'color': "#94a3b8"}, 
                            }
                        ))
                        fig_read.update_layout(paper_bgcolor="rgba(0,0,0,0)", margin=dict(t=50, b=0, l=0, r=0), font={'family': "Plus Jakarta Sans"})
                        st.plotly_chart(fig_read, use_container_width=True)
                    
                    # --- 6. THE AI REPORT ---
                    st.markdown("<br><h2 style='text-align:center;'>💡 Answer Engine Intelligence Report</h2><br>", unsafe_allow_html=True)
                    
                    st.markdown(f'''
                    <div class="insight-card">
                        <h4 style="color: #0f172a;">🏆 Notable AEO Strengths</h4>
                        <ul style="list-style-type: none; padding-left: 0; color: #475569; font-size: 1.1rem; line-height: 1.6;">
                            <li style="margin-bottom: 10px;">{result['strengths'][0]}</li>
                            <li>{result['strengths'][1]}</li>
                        </ul>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    st.markdown(f'''
                    <div class="insight-card">
                        <h4 style="color: #0f172a;">⚠️ Critical AEO Weaknesses</h4>
                        <ul style="list-style-type: none; padding-left: 0; color: #475569; font-size: 1.1rem; line-height: 1.6;">
                            <li style="margin-bottom: 10px;">{result['weaknesses'][0]}</li>
                            <li>{result['weaknesses'][1]}</li>
                        </ul>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    st.markdown('<div class="insight-card"><h4 style="color: #0f172a;">🛠️ High-Priority Actionable Roadmap</h4>', unsafe_allow_html=True)
                    for i, tip in enumerate(result['action_items']):
                        time.sleep(0.1) 
                        st.markdown(f"<p style='color: #475569; font-size: 1.1rem; margin-bottom: 12px;'>* {tip}</p>", unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True) 

                except json.JSONDecodeError:
                    st.error("Error: The AI response was not in a valid JSON format. Try scanning again or simplify your test URL.")
                except Exception as e:
                    st.error(f"Oops! Something went wrong. Error details: {e}")
