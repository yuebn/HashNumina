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
st.set_page_config(page_title="多比 duobi", layout="wide")

# 🎨 注入静态 LOGO 与精致样式（去除动画）
st.markdown("""
    <style>
    .main { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: #E0E0E0; }
    
    /* 静态 LOGO 区域 */
    .logo-container {
        display: flex;
        align-items: center;
        margin-bottom: 20px;
        padding-top: 10px;
    }
    .logo-text {
        font-family: 'Inter', 'Helvetica Neue', sans-serif;
        font-weight: 800;
        font-size: 2.2rem;
        margin-left: 12px;
        color: #FFFFFF;
        letter-spacing: -1px;
    }
    .logo-icon-svg {
        filter: drop-shadow(0 0 5px rgba(0, 255, 194, 0.3));
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

# 🚀 插入静态 SVG LOGO
st.markdown("""
    <div class="logo-container">
        <svg class="logo-icon-svg" width="45" height="45" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect width="100" height="100" rx="15" fill="#1a1a1a" />
            <path d="M25 65L40 50L55 60L75 35" stroke="#00FFC2" stroke-width="8" stroke-linecap="round" stroke-linejoin="round" />
            <circle cx="75" cy="35" r="5" fill="#FF3131" />
        </svg>
        <span class="logo-text">多比 duobi</span>
    </div>
""", unsafe_allow_html=True)

st.caption("周易八星磁场扫描 + DeepSeek-V3 深度解说")

# 🛡️ 隐私保护声明（白底黑字保持不动）
st.markdown("""
    <div class="privacy-trust-box">
        <b style="color:#000000;">🛡️ 隐私保护声明：</b><br>
        本站不设数据库，您的输入信息仅用于AI实时演算，不会被存储或转售。请放心使用。
    </div>
""", unsafe_allow_html=True)

# --- 核心逻辑封存（输入、算法、K线、清空机制） ---

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
        st.error(f"⚠️ 号码 {p_input} 演算过于频繁。请在 {wait_time} 分钟后再试。")
    elif len(p_input) < 11:
        st.warning("请输入完整的 11 位手机号")
    else:
        if not is_white_list:
            st.session_state.rate_limit[p_input] = [record[0] + 1, now]

        with st.status("🔮 正在读取哈希磁场...", expanded=False) as status:
            scores, counts, summary, total_score = analyze_numerology(p_input)
            status.update(label="✅ 演算完成", state="complete")
        
        effective_name = u_name if u_name.strip() else "访客"
        st.success(f"演算成功，{effective_name}阁下您的手机号码能量分：{total_score} 分")
        
        st.markdown(f"**⚡ 磁场解盘：** `{summary['吉']}吉` | `{summary['凶']}凶` | `{summary['平']}平`")
        star_html = '<div class="star-grid">'
        for label, val in counts.items():
            star_html += f'<div class="star-item"><span class="star-label">{label}</span><span class="star-value">{val}</span></div>'
        star_html += '</div>'
        st.markdown(star_html, unsafe_allow_html=True)

        st.divider()
        st.markdown("### 📊 项目月线运势 K 线图")
        ganzhi_months = ["庚子", "辛丑", "壬寅", "癸卯", "甲辰", "乙巳", "丙午", "丁未", "戊申", "己酉", "庚戌", "辛亥"]
        
        display_list = []
        if k_select == "财运+事业": display_list = [("财运", scores["财运"]), ("事业", scores["事业"])]
        elif k_select == "感情+家庭": display_list = [("情感", scores["情感"]), ("家庭", scores["家庭"])]
        else: display_list = [("财运", scores["财运"]), ("事业", scores["事业"]), ("情感", scores["情感"]), ("家庭", scores["家庭"])]

        k_cols = st.columns(2)
        for idx, (name, score) in enumerate(display_list):
            np.random.seed(hash(p_input + name) % 1000000)
            steps = 12
            c_prices = np.cumsum(np.random.normal(0, 3.5, steps)) + np.linspace(0, 10, steps) + score
            df = pd.DataFrame({'Month': ganzhi_months, 'Close': c_prices, 'Open': np.roll(c_prices, 1)})
            df.loc[0, 'Open'] = score - 2
            df['High'] = df[['Open', 'Close']].max(axis=1) + 1.5
            df['Low'] = df[['Open', 'Close']].min(axis=1) - 1.5
            
            with k_cols[idx % 2]:
                st.markdown(f"#### {name} 运势")
                fig = go.Figure(data=[go.Candlestick(x=df['Month'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                                                      increasing_line_color='#00FFC2', decreasing_line_color='#FF3131')])
                fig.update_layout(template="plotly_dark", height=260, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=10,b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'responsive': True})

        if k_select != "全部都要 (财/事/感/家)":
            st.info("💡 财运/事业/感情/家庭 这四项都要演算吗？请返回首页重新选择演算选项。")

        st.write("---")
        st.subheader("📝 大师深度解说")
        with st.spinner("大师正在阅片中..."):
            reading = get_ai_reading(effective_name, scores, counts)
            st.markdown(reading)
        
        share_text = f"🔮 我在 #多比duobi 测得 2026 综合评分：{total_score}分！"
        st.markdown(f'<a href="https://twitter.com/intent/tweet?text={urllib.parse.quote(share_text)}" target="_blank"><button style="background-color: #1DA1F2; color: white; border: none; padding: 12px; border-radius: 25px; font-weight: bold; width: 100%; max-width: 300px;">🐦 分享到 X (Twitter)</button></a>', unsafe_allow_html=True)
        
        st.write("") 
        if st.button("🔄 演算新号码", key="reset_trigger"):
            st.session_state["u_name_key"] = ""
            st.session_state["p_input_key"] = ""
            st.rerun()

st.markdown(f'<div class="footer"><hr>© 2026 多比 duobi | <a href="https://x.com/btc1349" style="color:#00FFC2;text-decoration:none;">@btc1349</a></div>', unsafe_allow_html=True)
