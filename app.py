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
        st.markdown("<h1 style='text-align: left; margin-bottom: 0;'>Free AEO Optimization Suite</h1>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 1.1rem; color: #64748b; margin-
