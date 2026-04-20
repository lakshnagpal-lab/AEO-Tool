import streamlit as st
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import json

# --- Visual Interface for Your Website ---
st.title("🔍 Free AEO Analyzer")
st.write("Find out how well your website is optimized for Answer Engines (like ChatGPT & Gemini).")

url_input = st.text_input("Enter your website URL (e.g., https://example.com):")

if st.button("Scan My Website"):
    if not url_input:
        st.warning("Please enter a URL first!")
    else:
        with st.spinner("Scraping site and asking AI for advice..."):
            try:
                # Setup the AI safely using hidden secrets
                api_key = st.secrets["GEMINI_API_KEY"]
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')

                # Scrape the user's website
                headers = {'User-Agent': 'Mozilla/5.0'}
                response = requests.get(url_input, headers=headers, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                data = {
                    "h1": [h1.text.strip() for h1 in soup.find_all('h1')],
                    "h2": [h2.text.strip() for h2 in soup.find_all('h2')],
                    "paragraphs": " ".join([p.text.strip() for p in soup.find_all('p')])[:3000],
                    "has_schema": len(soup.find_all('script', type='application/ld+json')) > 0
                }

                # Ask the AI for the custom report
                prompt = f"""Review this website data: {json.dumps(data)}. 
                Give an AEO Score out of 100, list 2 Strengths, 2 Weaknesses, and exactly 5 actionable, tailored tips to fix the weaknesses."""
                
                result = model.generate_content(prompt).text
                
                # Show the result to your user
                st.success("Analysis Complete!")
                st.markdown(result)

            except Exception as e:
                st.error("Oops! Something went wrong. Error details: {e}")
