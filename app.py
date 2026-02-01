import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
import urllib.parse
import time
import streamlit.components.v1 as components

# ==========================================
# 🔑 核心配置与安全策略
# ==========================================
DEEPSEEK_API_KEY = st.secrets.get("DEEPSEEK_API_KEY", "sk-899d54012ab145588d06927811ff8562")
TEST_WHITELIST_STUB = "18923487413" 

if 'rate_limit' not in st.session_state:
    st.session_state['rate_limit'] = {}

# 1. 页面配置与视觉注入
st.set_page_config(page_title="多比 DuoBi", layout="wide")

st.markdown("""
    <style>
    .main { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: #E0E0E0; }
    
    /* 🚀 生动精灵 LOGO 容器 */
    .header-box {
        display: flex;
        align-items: center;
        gap: 15px;
        padding: 10px 0;
        margin-left: 0;
    }
    .brand-text {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        font-size: 2.4rem;
        color: #FFFFFF;
        margin: 0;
        letter-spacing: -1px;
    }
    .brand-subtitle {
        color: #FFD700;
        font-size: 1rem;
        margin-bottom: 20px;
        opacity: 0.9;
        margin-top: -10px;
    }

    /* 紧凑 UI 组件 */
    .stTextInput { max-width: 300px; } 
    .stTextInput>div>div>input { background-color: #f0f2f6; color: #1a1a1a !important; border: 1px solid #7928ca; font-size: 16px !important; }
    .stButton>button { 
        background: linear-gradient(45deg, #7928ca, #ff0080); 
        color: white; font-weight: bold; border: none; border-radius: 10px; height: 3.5em; width: 100%; max-width: 300px; margin-top: 10px;
    }
    .privacy-trust-box { 
        color: #000000 !important; font-size: 0.9em; line-height: 1.6; padding: 12px; border: 2px solid #00FFC2; 
        border-radius: 12px; background-color: #FFFFFF !important; margin: 10px 0; max-width: 500px;
    }
    .star-grid { display: flex; flex-wrap: wrap; max-width: 420px; margin-left: 0; justify-content: flex-start; }
    .star-item { flex: 0 0 25%; text-align: left; padding: 5px 0; }
    .star-label { font-size: 0.72em; color: #bbb; display: block; }
    .star-value { font-size: 1.05em; color: #00FFC2; font-weight: bold; display: block; }
    .footer { text-align: center; padding: 30px 10px; color: #888; font-size: 0.8em; }
    </style>
    """, unsafe_allow_html=True)

# 🚀 注入代码手绘【具象大耳精灵】LOGO
st.markdown("""
    <div class="header-box">
        <svg width="70" height="70" viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M40 50C10 20 0 70 35 65M80 50C110 20 120 70 85 65" stroke="#D1D1D1" stroke-width="3" fill="#2A2A2A"/>
            <path d="M40 50C40 30 80 30 80 50C80 75 60 85 40 50Z" fill="#333333" stroke="#D1D1D1" stroke-width="2"/>
            <circle cx="50" cy="48" r="5" fill="#00FFC2" />
            <circle cx="70" cy="48" r="5" fill="#00FFC2" />
            <path d="M48 45C48 45 50 43 52 45M68 45C68 45 70 43 72 45" stroke="#FFFFFF" stroke-width="1"/>
            <path d="M58 55L62 55L60 58Z" fill="#D1D1D1"/>
            <path d="M55 65C58 68 62 68 65 65" stroke="#00FFC2" stroke-width="1.5" stroke-linecap="round"/>
            <path d="M40 85Q60 75 80 85" stroke="#7928ca" stroke-width="3" stroke-linecap="round"/>
        </svg>
        <h1 class="brand-text">多比 DuoBi</h1>
    </div>
    <div class="brand-subtitle">周易八星磁场扫描 + DeepSeek-V3 深度解说</div>
""", unsafe_allow_html=True)

# 🚀 手机 K 线脚本补丁保持不动
components.html('<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>', height=0)

# --- 🛡️ 隐私声明、算法、K线及清空逻辑（均保持不动） ---
st.markdown("""
    <div class="privacy-trust-box">
        <b style="color:#000000;">🛡️ 隐私保护声明：</b><br>
        本站不设数据库，您的输入信息仅用于AI实时演算，不会被存储或转售。请放心使用。
    </div>
""", unsafe_allow_html=True)

u_name = st.text_input("👤 您的昵称", placeholder="访客模式可留空", key="u_name_key")
p_input = st.text_input("📱 手机号码", placeholder="输入11位待测号码", key="p_input_key")

st.markdown("**📊 选择 K 线演算维度：**")
k_select = st.radio(
    label="K线选项",
    options=["财运+事业", "感情+家庭", "全部都要 (财/事/感/家)"],
    index=0, horizontal=True, label_visibility="collapsed", key="k_select_key"
)

def analyze_numerology(phone):
    stars_cfg = {
        "天医(财)": ["13", "31", "68", "86", "49", "94", "27", "72"],
        "延年(事)": ["19", "91", "78", "87", "34", "43", "26", "62"],
        "生气(贵)": ["14", "41", "67", "76", "39", "93", "28", "82"],
        "伏位(稳)": ["11", "22", "33", "44", "66", "77", "88", "99"],
        "绝命(极)": ["12", "21", "69", "96", "48", "84", "37", "73"],
        "五鬼(变)": ["18", "81", "79", "97", "36", "63", "24", "42"],
        "六煞(情)": ["16", "61", "47", "74", "38", "83", "29", "92"],
        "祸害(口)": ["17", "71", "89", "98", "46", "64", "32", "23"]
    }
    counts = {k: 0 for k in stars_cfg.keys()}
    summary = {"吉": 0, "凶": 0, "平": 0}
    for i in range(len(phone) - 1):
        pair = phone[i:i+2]
        for name, codes in stars_cfg.items():
            if pair in codes:
                counts[name] += 1
                if name in ["天医(财)", "延年(事)", "生气(贵)"]: summary["吉"] += 1
                elif name == "伏位(稳)": summary["平"] += 1
                else: summary["凶"] += 1
    sc = {"财运": 66 + counts["天医(财)"]*8, "事业": 62 + counts["延年(事)"]*8, "情感": 60, "家庭": 65}
    return sc, counts, summary, int(np.mean(list(sc.values())))

def get_ai_reading(nickname, scores, counts):
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_API_KEY}"}
    payload = {
        "model": "deepseek-chat", "messages": [
            {"role": "system", "content": "你是一位周易数字命理大师。点评扎心、生动，不少于350字。"},
            {"role": "user", "content": f"用户{nickname}，磁场：{counts}，评分：{scores}。请复盘。"}
        ], "temperature": 0.8
    }
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=120)
        return r.json()['choices'][0]['message']['content']
    except: return "📡 大师正在闭关（网络拥堵），请点击按钮重新演算。"

analyze_btn = st.button("🚀 开始哈希演算")

if analyze_btn:
    now = time.time()
    is_white_list = (p_input == TEST_WHITELIST_STUB)
    record = st.session_state.rate_limit.get(p_input, [0, 0])
    
    if not is_white_list and record[0] >= 3 and (now - record[1] < 14400):
        wait_time = int((14400 - (now - record[1])) / 60)
        st.error(f"⚠️ 号码 {p_input} 演算过于频繁。请在
