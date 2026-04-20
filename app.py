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

# --- 1. SETTING PAGE CONFIG AND THEME (CRITICAL FOR LOOK) ---
st.set_page_config(page_title="AI Talkxo | Free AEO Analyzer", page_icon="✨", layout="wide")

# This CSS creates the premium look: particle background, centered logo, animated cards
main_style = """
<style>
/* A professional particle network background */
.stApp {
    background-color: #f8faff;
    background-image: radial-gradient(at 0% 0%, #e0eafc 0px, transparent 50%),
                      radial-gradient(at 100% 0%, #cfdef3 0px, transparent 50%),
                      radial-gradient(at 100% 100%, #e0c3fc 0px, transparent 50%),
                      radial-gradient(at 0% 100%, #8ec5fc 0px, transparent 50%);
}

/* This guarantees the logo is centrally aligned, overriding default Streamlit alignment */
.stLogoContainer {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    margin-top: -3rem; /* Adjust positioning */
}

/* Stylized Insight Cards with subtle fade-in animation */
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

/* Stylized KPIs in a row */
.kpi-container { display: flex; gap: 1rem; justify-content: center; margin: 1rem 0; }
.kpi-box {
    background: white; border-radius: 12px; padding: 1.5rem; text-align: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05); flex: 1;
}
.kpi-value { font-size: 2.5rem; font-weight: 700; color: #4B0082; }
.kpi-label { font-size: 1rem; color: #666; text-transform: uppercase; letter-spacing: 1px;}
</style>
"""
st.markdown(main_style, unsafe_allow_html=True)

# --- 2. COMPANY LOGO (True Centered) ---
# Replace the URL below with your logo image address (the one you copied)
LOGO_URL = "https://i.im.ge/eBsU8z/talkxo_logo.png"

st.markdown(f'''
<div class="stLogoContainer">
    <img src="{LOGO_URL}" width="160">
</div>
''', unsafe_allow_html=True)

# --- 3. Lottie Animations: Define helper function to load from URL ---
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Lottie URLs for cool AI vectors
lottie_ai_assist = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_96b583f7.json")
lottie_scanner = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_gh5y1v8p.json")

# --- 4. Main Interface Area (2 Columns) ---
head1, head2 = st.columns([1, 4])
with head1:
    st_lottie(lottie_ai_assist, speed=1, width=150, height=150, key="ai_robot")
with head2:
    st.title(" ✨ Free AEO Optimization Suite")
    st.write("Does your website build trust with AI Answer Engines? Our analyzer checks for information density, semantic structure, and entity-first optimization to give you an immediate AEO Score and a dynamic roadmap.")

url_input = st.text_input("Enter your website URL (e.g., https://example.com)", placeholder="Enter your website URL...")

if st.button("Generate My Dynamic Report", use_container_width=True):
    if not url_input:
        st.warning("Please enter a URL first!")
    else:
        with st.spinner("Scraping site and generating insights..."):
            try:
                api_key = st.secrets["GEMINI_API_KEY"]
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')

                headers = {'User-Agent': 'Mozilla/5.0'}
                response = requests.get(url_input, headers=headers, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Dynamic Scrape and Chart Data Prep
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

                # AI Prompt with explicit structure request for charts
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
                
                # Parse AI response
                response_content = model.generate_content(prompt).text
                # Remove markdown formatting if the AI returned it inside ```json blocks```
                json_str = response_content.replace('```json', '').replace('```', '').strip()
                result = json.loads(json_str)
                
                st.success("Analysis Complete!")
                st.markdown("---")

                # --- 5. THE MAIN DASHBOARD ---
                dash1, dash2, dash3 = st.columns([1, 2, 1])
                with dash2:
                    # Score Gauge - Animated and Central
                    fig_gauge = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = result['overall_score'],
                        domain = {'x': [0, 1], 'y': [0, 1]},
                        gauge = {
                            'axis': {'range': [None, 100]},
                            'bar': {'color': "#4B0082"}, # A cool deep purple
                            'steps' : [
                                {'range': [0, 60], 'color': "#f8e1e1"}, # Light Red
                                {'range': [60, 85], 'color': "#fffde8"}, # Light Yellow
                                {'range': [85, 100], 'color': "#e8fdf8"} # Light Green
                            ],
                            'threshold' : {'line': {'color': "black", 'width': 4}, 'thickness': 0.75, 'value': 90}
                        },
                        title = {'text': "Answer Engine Trust Score"}
                    ))
                    fig_gauge.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={'color': "#4B0082", 'family': "Arial"}, margin=dict(t=30, b=0, l=0, r=0))
                    st.plotly_chart(fig_gauge, use_container_width=True)

                # KPIs row: Text Metrics + Visual Charts Row
                kpi_row1, kpi_row2, kpi_row3 = st.columns(3)
                
                # Row 1: Word Count Metric
                with kpi_row1:
                    st.metric(label="📄 Total Word Count", value=f"{word_count:,}", help="Information density is key for RAG extraction.")
                # Row 2: Structure Breakdown Charts (Bar and Donut)
                with kpi_row2:
                    # Heading Bar Chart
                    heading_data = {"Type": ["H1 (Main)", "H2 (Sub)"], "Count": [len(h1_tags), len(h2_tags)]}
                    fig_bars = px.bar(heading_data, x="Type", y="Count", text="Count", 
                                       title="Heading Structure Breakdown",
                                       color_discrete_sequence=['#9370DB', '#E6E6FA'])
                    fig_bars.update_traces(textposition='inside', marker_line_color='black', marker_line_width=0.5, opacity=0.8)
                    fig_bars.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig_bars, use_container_width=True)
                    
                with kpi_row3:
                    # Content Density Donut
                    density_data = pd.DataFrame({"Category": ["Factual Data", "Filler/Fluff"], "Percent": [result['factual_density_percent'], 100-result['factual_density_percent']]})
                    fig_pie = px.pie(density_data, values="Percent", names="Category", title="Predicted Factual Density", hole=0.5, 
                                     color_discrete_sequence=['#4B0082', '#f3efff'])
                    fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig_pie, use_container_width=True)

                # Row 3: Readability Gauge + Rich Media Metric
                kpi_media1, kpi_media2, kpi_media3 = st.columns(3)
                with kpi_media1:
                    st.metric(label="Schema Found?", value="✅ Yes" if analysis_data["has_schema"] else "❌ No", help="Entity data must be provided via Schema.")
                with kpi_media2:
                    st.metric(label="Rich Media Count", value=img_count, help="Images and videos build comprehensive answer context.")
                with kpi_media3:
                    # Readability animated indicator
                    read_levels = ["4th Grade", "6th Grade", "8th Grade", "10th Grade", "12th Grade", "Grad School"]
                    read_scores = [0, 20, 40, 60, 80, 100]
                    read_value = read_scores[read_levels.index(result['readability_grade'])] if result['readability_grade'] in read_levels else 50
                    fig_read = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = read_value,
                        title = {'text': f"Predicted Readability Level<br>Grade: {result['readability_grade']}"},
                        gauge = {
                            'axis': {'range': [None, 100], 'tickvals': read_scores, 'ticktext': read_levels},
                            'bar': {'color': "#666"}, # Neutral color
                        }
                    ))
                    fig_read.update_layout(paper_bgcolor="rgba(0,0,0,0)", margin=dict(t=50, b=0, l=0, r=0))
                    st.plotly_chart(fig_read, use_container_width=True)
                
                # --- 6. THE AI REPORT (Animated "Insight Cards") ---
                st.subheader("💡 Answer Engine Intelligence Report")
                
                # Strengths Card
                st.markdown(f'''
                <div class="insight-card">
                    <h4>🏆 Notable AEO Strengths</h4>
                    <ul style="list-style-type: none; padding-left: 0;">
                        <li>{result['strengths'][0]}</li>
                        <li>{result['strengths'][1]}</li>
                    </ul>
                </div>
                ''', unsafe_allow_html=True)
                
                # Weaknesses Card
                st.markdown(f'''
                <div class="insight-card">
                    <h4>⚠️ Critical AEO Weaknesses</h4>
                    <ul style="list-style-type: none; padding-left: 0;">
                        <li>{result['weaknesses'][0]}</li>
                        <li>{result['weaknesses'][1]}</li>
                    </ul>
                </div>
                ''', unsafe_allow_html=True)
                
                # Action Plan Card (Animated delay list)
                st.markdown('<div class="insight-card"><h4>🛠️ High-Priority Actionable Roadmap (5 Tips)</h4>', unsafe_allow_html=True)
                # Instead of standard st.markdown, we iterate and animate each point.
                for i, tip in enumerate(result['action_items']):
                    time.sleep(0.1) # Create a subtle delay effect
                    st.markdown(f"* {tip}")
                st.markdown('</div>', unsafe_allow_html=True) # Close card

            except json.JSONDecodeError:
                st.error("Error: The AI response was not in a valid JSON format. Try scanning again or simplify your test URL.")
            except Exception as e:
                st.error(f"Oops! Something went wrong. Error details: {e}")
