import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import urllib.parse
import streamlit.components.v1 as components

# ==========================================
# 🔑 核心配置
# ==========================================
DEEPSEEK_API_KEY = st.secrets.get("sk-899d54012ab145588d06927811ff8562")

# 1. 页面配置与视觉优化
st.set_page_config(page_title="哈希灵数 HashNumina", layout="wide")

st.markdown("""
    <style>
    .main { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: #E0E0E0; }
    .stTextInput>div>div>input { background-color: #f0f2f6; color: #1a1a1a !important; border: 1px solid #7928ca; font-size: 16px !important; }
    .stButton>button { 
        background: linear-gradient(45deg, #7928ca, #ff0080); 
        color: white; font-weight: bold; border: none; border-radius: 10px; height: 3.5em; width: 100%; margin-top: 10px;
    }
    .privacy-trust-box { 
        color: #000000 !important; font-size: 0.9em; line-height: 1.6; padding: 12px; border: 2px solid #00FFC2; 
        border-radius: 12px; background-color: #FFFFFF !important; margin: 10px 0; box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .star-card {
        background: rgba(255, 255, 255, 0.08); padding: 8px; border-radius: 8px; text-align: center;
        border: 1px solid rgba(0, 255, 194, 0.2); margin-bottom: 5px;
    }
    .star-label { font-size: 0.8em; color: #bbb; display: block; }
    .star-value { font-size: 1.1em; color: #00FFC2; font-weight: bold; }
    .footer { text-align: center; padding: 30px 10px; color: #888; font-size: 0.8em; }
    </style>
    """, unsafe_allow_html=True)

# 🚀 交互补丁
components.html("""<script>const m=()=>{const ins=window.parent.document.querySelectorAll('input[type="text"]');ins.forEach(i=>{if(!i.dataset.l){i.addEventListener('focus',()=>i.select());i.dataset.l='t';}});};setInterval(m, 1000);</script>""", height=0)

st.title("🔮 哈希灵数 HashNumina")
st.caption("周易八星磁场扫描 + DeepSeek-V3 深度解说")

st.markdown("""
    <div class="privacy-trust-box">
        <b style="color:#000000;">🛡️ 隐私保护声明：</b><br>
        本站不存储任何输入信息，数据仅用于实时演算，请放心使用。
    </div>
""", unsafe_allow_html=True)

# 2. 输入区域
u_name = st.text_input("👤 您的昵称", placeholder="访客模式可留空")
p_input = st.text_input("📱 手机号码", placeholder="输入11位待测号码")
analyze_btn = st.button("🚀 开始哈希演算")

# 3. 核心算法
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
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一位周易数字命理大师。点评要扎心、生动，不少于350字。"},
            {"role": "user", "content": f"用户{nickname}，磁场：{counts}，评分：{scores}。请复盘。"}
        ],
        "temperature": 0.8
    }
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=120)
        return r.json()['choices'][0]['message']['content']
    except Exception:
        return "📡 大师正在闭关（网络拥堵），请再次点击上方按钮测算。"

# 4. 展示逻辑
if analyze_btn:
    if len(p_input) < 11:
        st.warning("请输入完整的 11 位手机号")
    else:
        with st.status("🔮 正在读取哈希磁场...", expanded=True) as status:
            scores, counts, summary, total_score = analyze_numerology(p_input)
            st.write("同步 AI 命理接口中...")
            status.update(label="✅ 演算完成", state="complete", expanded=False)
        
        # --- 修改点：优化结果抬头格式 ---
        effective_name = u_name if u_name.strip() else "访客"
        st.success(f"演算成功，{effective_name}阁下您的手机号码能量分：{total_score} 分")
        
        st.markdown(f"**⚡ 磁场拆解：** `{summary['吉']}吉` | `{summary['凶']}凶` | `{summary['平']}平`")
        stars_list = list(counts.items())
        cols = st.columns([1,1,1,1])
        for i in range(8):
            with cols[i % 4]:
                st.markdown(f'<div class="star-card"><span class="star-label">{stars_list[i][0]}</span><span class="star-value">{stars_list[i][1]}</span></div>', unsafe_allow_html=True)

        st.divider()
        # --- K线配色修复 ---
        k_cols = st.columns(2)
        for idx, (name, score) in enumerate(scores.items()):
            np.random.seed(hash(p_input + name) % 1234567)
            movements = np.random.normal(0.25, 4.0, 72)
            prices = np.cumsum(movements) + score
            df = pd.DataFrame({'Date': range(72), 'Close': prices})
            df['Open'] = df['Close'].shift(1).fillna(score)
            df['High'] = df[['Open', 'Close']].max(axis=1) + 1.2
            df['Low'] = df[['Open', 'Close']].min(axis=1) - 1.2
            
            with k_cols[idx % 2]:
                st.markdown(f"#### {name} 能量趋势")
                fig = go.Figure(data=[go.Candlestick(
                    x=df['Date'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                    increasing_line_color='#00FFC2', decreasing_line_color='#FF3131' 
                )])
                fig.update_layout(template="plotly_dark", height=250, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        st.divider()
        st.subheader("📝 大师深度解说")
        with st.spinner("大师正在阅片中..."):
            reading = get_ai_reading(effective_name, scores, counts)
            st.markdown(reading)
        
        share_text = f"🔮 我在 #哈希灵数 测得 2026 综合评分：{total_score}分！"
        tweet_url = f"https://twitter.com/intent/tweet?text={urllib.parse.quote(share_text)}"
        st.markdown(f'<a href="{tweet_url}" target="_blank"><button style="background-color: #1DA1F2; color: white; border: none; padding: 12px; border-radius: 25px; font-weight: bold; width: 100%;">🐦 分享到 X (Twitter)</button></a>', unsafe_allow_html=True)

st.markdown(f'<div class="footer"><hr>© 2026 HashNumina | <a href="https://x.com/btc1349" style="color:#00FFC2;text-decoration:none;">@btc1349</a></div>', unsafe_allow_html=True)
