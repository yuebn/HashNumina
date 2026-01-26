import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import urllib.parse
import streamlit.components.v1 as components

# ==========================================
# 🔑 核心配置：API Key 已通过 Secrets 安全接入
# ==========================================
DEEPSEEK_API_KEY = st.secrets.get("DEEPSEEK_API_KEY", "在此处填入Key仅作本地测试")

# 1. 页面配置与黑金视觉注入
st.set_page_config(page_title="哈希灵数 HashNumina", layout="wide")

st.markdown("""
    <style>
    .main { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: #E0E0E0; }
    .stTextInput>div>div>input { background-color: #1A1A1A; color: #00FFC2 !important; border: 1px solid #7928ca; }
    .stButton>button { 
        background: linear-gradient(45deg, #7928ca, #ff0080); 
        color: white; font-weight: bold; border: none; border-radius: 10px; height: 3em; width: 100%;
    }
    .footer { text-align: center; padding: 20px; color: #888; font-size: 0.9em; }
    .disclaimer { color: #ff4b4b; font-size: 0.85em; text-align: center; margin-bottom: 20px; font-weight: bold; }
    .privacy-box { color: #00FFC2; font-size: 0.85em; line-height: 1.6; padding: 10px; border: 1px solid rgba(0, 255, 194, 0.2); border-radius: 8px; background: rgba(0, 255, 194, 0.05); }
    .share-box { background: rgba(121, 40, 202, 0.1); padding: 20px; border-radius: 15px; border: 1px dashed #7928ca; text-align: center; margin-top: 30px; }
    .star-label { font-size: 0.9em; color: #bbb; }
    .star-value { font-size: 1.2em; color: #00FFC2; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🔮 哈希灵数 HashNumina | 解读数字能量")
st.caption("周易八星磁场扫描 + DeepSeek-V3 深度解说")
st.markdown('<p class="disclaimer">⚠️ 本网站所有预测仅供娱乐，相信科学，请勿盲目迷信</p>', unsafe_allow_html=True)

# 2. 周易扫描引擎
def analyze_numerology(phone):
    stars_config = {
        "天医(财运)": {"codes": ["13", "31", "68", "86", "49", "94", "27", "72"], "type": "吉"},
        "延年(事业)": {"codes": ["19", "91", "78", "87", "34", "43", "26", "62"], "type": "吉"},
        "生气(贵人)": {"codes": ["14", "41", "67", "76", "39", "93", "28", "82"], "type": "吉"},
        "伏位(守成)": {"codes": ["11", "22", "33", "44", "66", "77", "88", "99"], "type": "平"},
        "绝命(极端)": {"codes": ["12", "21", "69", "96", "48", "84", "37", "73"], "type": "凶"},
        "五鬼(变幻)": {"codes": ["18", "81", "79", "97", "36", "63", "24", "42"], "type": "凶"},
        "六煞(情感)": {"codes": ["16", "61", "47", "74", "38", "83", "29", "92"], "type": "凶"},
        "祸害(口舌)": {"codes": ["17", "71", "89", "98", "46", "64", "32", "23"], "type": "凶"}
    }
    star_counts = {name: 0 for name in stars_config.keys()}
    summary_counts = {"吉": 0, "凶": 0, "平": 0}
    for i in range(len(phone) - 1):
        pair = phone[i:i+2]
        for name, info in stars_config.items():
            if pair in info["codes"]:
                star_counts[name] += 1
                summary_counts[info["type"]] += 1
    scores = {"财运": 66, "事业": 62, "情感": 60, "家庭": 65}
    scores["财运"] += star_counts["天医(财运)"] * 8 - star_counts["绝命(极端)"] * 5
    scores["事业"] += star_counts["延年(事业)"] * 8 - star_counts["五鬼(变幻)"] * 6
    total_score = int(np.mean(list(scores.values())))
    return scores, star_counts, summary_counts, total_score

# 3. AI 大师解说逻辑 (已修复括号闭合问题)
def get_ai_reading(nickname, phone, scores, star_counts):
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_API_KEY}"}
    system_prompt = (
        "你是一位隐居数字丛林的命理大师。你的点评要让 Web3 人士觉得内行，也要让普通人觉得扎心。 "
        "要求：1. 使用生动比喻。2. 保持毒舌温情底色。3. 分财运、事业、感情、家庭四个维度深度解析。字数不少于 280 字。"
    )
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"用户{nickname}，手机磁场分布：{star_counts}。评分数据：{scores}。请开始深度复盘。"}
        ],
        "temperature": 0.85
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        return response.json()['choices'][0]['message']['content']
    except Exception:
        return "📡 磁场干扰严重，大师正在链上重连。"

# 4. K 线生成
def generate_pro_k_line(phone, dim_name, base_score):
    seed_val = hash(phone + dim_name) % (2**32)
    np.random.seed(seed_val)
    dates = pd.date_range(end=datetime.now() + timedelta(days=1095), periods=72, freq='ME')
    prices = np.cumsum(np.random.normal(0.12, 4.2, 72)) + base_score
    df = pd.DataFrame({'Date': dates, 'Close': prices})
    df['Open'] = df['Close'].shift(1).fillna(base_score)
    df['High'] = df[['Open', 'Close']].max(axis=1) + 1.8
    df['Low'] = df[['Open', 'Close']].min(axis=1) - 1.8
    return df

# 5. UI 布局
with st.sidebar:
    st.header("🔑 终端接入")
    user_name = st.text_input("社交昵称", placeholder="留空则以访客身份测算")
    phone_input = st.text_input("手机号码", placeholder="输入待测的11位数字")
    analyze_btn = st.button("启动哈希演算")
    st.write("---")
    st.markdown("""<div class="privacy-box"><b>🛡️ 隐私保护：</b><br>本站不设数据库，您的输入信息仅用于AI实时演算，不会被存储或转售，请放心使用。</div>""", unsafe_allow_html=True)

if analyze_btn:
    if len(phone_input) < 11:
        st.error("请输入正确的 11 位手机号")
    else:
        scores, counts, summary, total_score = analyze_numerology(phone_input)
        display_name = user_name if user_name.strip() else "匿名访客"
        st.subheader(f"🔮 {display_name}，阁下这个号码综合评分：{total_score}分")
        st.markdown(f"**⚡ 磁场能量拆解：** `{summary['吉']}个吉` | `{summary['凶']}个凶` | `{summary['平']}个平`")
        
        stars_list = list(counts.items())
        r1 = st.columns(4)
        for i in range(4):
            with r1[i]: st.markdown(f"<span class='star-label'>{stars_list[i][0]}</span><br><span class='star-value'>{stars_list[i][1]}</span>", unsafe_allow_html=True)
        r2 = st.columns(4)
        for i in range(4, 8):
            with r2[i-4]: st.markdown(f"<span class='star-label'>{stars_list[i][0]}</span><br><span class='star-value'>{stars_list[i][1]}</span>", unsafe_allow_html=True)

        st.divider()
        k_cols = st.columns(2)
        for i, (name, score) in enumerate(scores.items()):
            df = generate_pro_k_line(phone_input, name, score)
            with k_cols[i % 2]:
                st.markdown(f"#### {name} 能量趋势")
                fig = go.Figure(data=[go.Candlestick(x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], increasing_line_color='#FF3131', decreasing_line_color='#00FFC2')])
                fig.update_layout(template="plotly_dark", height=280, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
        
        st.write("---")
        st.subheader("📝 哈希灵数·大师深度解说")
        with st.spinner("大师正在审视你的哈希磁场..."):
            reading = get_ai_reading(display_name, phone_input, scores, counts)
            st.markdown(reading)
        
        st.markdown('<div class="share-box">', unsafe_allow_html=True)
        st.markdown("### 📣 同步结果到 X (Twitter)")
        share_text = f"🔮 我在 #哈希灵数 测得 2026 综合评分：{total_score}分！\n\nDeveloped by @btc1349"
        tweet_url = f"https://twitter.com/intent/tweet?text={urllib.parse.quote(share_text)}"
        st.markdown(f'<a href="{tweet_url}" target="_blank"><button style="background-color: #1DA1F2; color: white; border: none; padding: 12px 24px; border-radius: 25px; cursor: pointer; font-weight: bold; font-size: 1.1em;">🐦 分享我的财运 K 线</button></a>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

st.markdown(f"""<div class="footer"><hr>© 2026 HashNumina Terminal | 数字能量<br>开发者 X: <a href="https://x.com/btc1349" style="color: #00FFC2; text-decoration: none;">@btc1349</a></div>""", unsafe_allow_html=True)
