import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import json
import plotly.express as px

# --- 1. Moving Gradient Background (CSS Injection) ---
page_bg_img = '''
<style>
.stApp {
    background: linear-gradient(-45deg, #e0eafc, #cfdef3, #e0c3fc, #8ec5fc);
    background-size: 400% 400%;
    animation: gradient 15s ease infinite;
}
@keyframes gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
/* Add a subtle shadow to the main input box for a 3D effect */
.stTextInput>div>div>input {
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    border-radius: 10px;
}
</style>
'''
st.markdown(page_bg_img, unsafe_allow_html=True)

# --- 2. Company Logo ---
# We use columns to center the logo perfectly
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    # Replace the URL below with a link to your actual company logo!
    st.image("https://stable-chocolate-5b3k6zwiy0.edgeone.app/Talkxo%20logo-01.jpg", width=200) 

# --- 3. Main Interface ---
st.title("✨ Free AEO Analyzer")
st.write("Find out how well your website is optimized for Answer Engines (like ChatGPT & Gemini).")

url_input = st.text_input("Enter your website URL (e.g., https://example.com):")

if st.button("Scan My Website"):
    if not url_input:
        st.warning("Please enter a URL first!")
    else:
        with st.spinner("Scraping site and generating insights..."):
            try:
                # API Setup
                api_key = st.secrets["GEMINI_API_KEY"]
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')

                # Web Scraping
                headers = {'User-Agent': 'Mozilla/5.0'}
                response = requests.get(url_input, headers=headers, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Count elements for the visual chart
                h1_count = len(soup.find_all('h1'))
                h2_count = len(soup.find_all('h2'))
                p_count = len(soup.find_all('p'))
                
                data = {
                    "h1": [h1.text.strip() for h1 in soup.find_all('h1')],
                    "h2": [h2.text.strip() for h2 in soup.find_all('h2')],
                    "paragraphs": " ".join([p.text.strip() for p in soup.find_all('p')])[:3000],
                    "has_schema": len(soup.find_all('script', type='application/ld+json')) > 0
                }

                # AI Prompt
                prompt = f"""Review this website data: {json.dumps(data)}. 
                Give an AEO Score out of 100, list 2 Strengths, 2 Weaknesses, and exactly 5 actionable, tailored tips to fix the weaknesses."""
                
                result = model.generate_content(prompt).text
                st.success("Analysis Complete!")
                
                # --- 4. Visual Data Chart (Plotly) ---
                st.subheader("📊 Content Structure Breakdown")
                st.write("Answer Engines prefer dense structure. Here is how your page is built:")
                
                # Creating the Donut Chart
                chart_data = {"Element": ["Main Titles (H1)", "Sub-Titles (H2)", "Text Blocks (Paragraphs)"], 
                              "Count": [h1_count, h2_count, p_count]}
                fig = px.pie(chart_data, values="Count", names="Element", hole=0.5, 
                             color_discrete_sequence=['#4B0082', '#9370DB', '#E6E6FA'])
                
                # Make the background of the chart transparent to match our gradient
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)

                # --- 5. The AI Report ---
                st.markdown("---")
                st.markdown(result)

            except Exception as e:
                st.error(f"Oops! Something went wrong. Error details: {e}")
                st.success("Analysis Complete!")
                st.markdown(result)

            except Exception as e:
                st.error(f"Oops! Something went wrong. Error details: {e}")
