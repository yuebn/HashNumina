import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import urllib.parse
import streamlit.components.v1 as components

# ==========================================
# 🔑 核心配置：API Key
# ==========================================
DEEPSEEK_API_KEY = st.secrets.get("sk-899d54012ab145588d06927811ff8562")

# 1. 页面配置与视觉注入
st.set_page_config(page_title="哈希灵数 HashNumina", layout="wide")

st.markdown("""
    <style>
    .main { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: #E0E0E0; }
    .stTextInput>div>div>input { background-color: #f0f2f6; color: #1a1a1a !important; border: 1px solid #7928ca; font-size: 16px !important; }
    .stButton>button { 
        background: linear-gradient(45deg, #7928ca, #ff0080); 
        color: white; font-weight: bold; border: none; border-radius: 10px; height: 3.5em; width: 100%; margin-top: 10px;
    }
    
    /* ✨ 核心修改：隐私声明改为白底黑字，增强信任感 */
    .privacy-trust-box { 
        color: #000000 !important; 
        font-size: 0.95em; 
        line-height: 1.6; 
        padding: 15px; 
        border: 2px solid #00FFC2; 
        border-radius: 12px; 
        background-color: #FFFFFF !important; 
        margin: 15px 0;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    
    .mobile-card {
        background: rgba(255, 255, 255, 0.05);
        padding: 12px 15px;
        border-radius: 10px;
        border-left: 4px solid #00FFC2;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .footer { text-align: center; padding: 40px 10px; color: #888; font-size: 0.85em; }
    </style>
    """, unsafe_allow_html=True)

# 🚀 手机端交互补丁
components.html("""<script>const m=()=>{const ins=window.parent.document.querySelectorAll('input[type="text"]');ins.forEach(i=>{if(!i.dataset.l){i.addEventListener('focus',()=>i.select());i.dataset.l='t';}});};setInterval(m,1000);</script>""", height=0)

st.title("🔮 哈希灵数 HashNumina")
st.caption("周易八星磁场扫描 + DeepSeek-V3 深度解说")

# --- 🛡️ 隐私声明位置保持不动，仅修改颜色 ---
st.markdown("""
    <div class="privacy-trust-box">
        <b style="color:#000000;">🛡️ 隐私保护声明：</b><br>
        本站不设数据库，您的输入信息仅用于AI实时演算，演算完毕即刻销毁，不会被存储或转售。请放心使用。
    </div>
""", unsafe_allow_html=True)

# 2. 输入区域
with st.container():
    u_name = st.text_input("👤 您的昵称", placeholder="访客模式可留空")
    p_input = st.text_input("📱 手机号码", placeholder="输入11位待测号码")
    analyze_btn = st.button("🚀 开始哈希演算")

# 3. 算法逻辑
def analyze_numerology(phone):
    stars_cfg = {
        "天医(财运)": ["13", "31", "68", "86", "49", "94", "27", "72"],
        "延年(事业)": ["19", "91", "78", "87", "34", "43", "26", "62"],
        "生气(贵人)": ["14", "41", "67", "76", "39", "93", "28", "82"],
        "伏位(守成)": ["11", "22", "33", "44", "66", "77", "88", "99"],
        "绝命(极端)": ["12", "21", "69", "96", "48", "84", "37", "73"],
        "五鬼(变幻)": ["18", "81", "79", "97", "36", "63", "24", "42"],
        "六煞(情感)": ["16", "61", "47", "74", "38", "83", "29", "92"],
        "祸害(口舌)": ["17", "71", "89", "98", "46", "64", "32", "23"]
    }
    counts = {k: 0 for k in stars_cfg.keys()}
    summary = {"吉": 0, "凶": 0, "平": 0}
    for i in range(len(phone) - 1):
        pair = phone[i:i+2]
        for name, codes in stars_cfg.items():
            if pair in codes:
                counts[name] += 1
                if name in ["天医(财运)", "延年(事业)", "生气(贵人)"]: summary["吉"] += 1
                elif name == "伏位(守成)": summary["平"] += 1
                else: summary["凶"] += 1
    sc = {"财运": 66 + counts["天医(财运)"]*8, "事业": 62 + counts["延年(事业)"]*8, "情感": 60, "家庭": 65}
    return sc, counts, summary, int(np.mean(list(sc.values())))

def get_ai_reading(nickname, scores, counts):
    url = "https://api.deepseek.com/chat/completions"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_API_KEY}"}
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一位数字命理大师。点评要扎心、专业，不少于280字。"},
            {"role": "user", "content": f"用户{nickname}，磁场：{counts}，评分：{scores}。请复盘。"}
        ],
        "temperature": 0.85
    }
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=50)
        return r.json()['choices'][0]['message']['content']
    except: return "📡 网络连接超时。请点击按钮重新演算。"

# 4. 响应逻辑
if analyze_btn:
    if len(p_input) < 11:
        st.warning("请输入完整的 11 位手机号")
    else:
        # 增加状态提示解决手机无响应感
        with st.status("🔮 正在连接哈希节点...", expanded=True) as status:
            st.write("正在演算八星磁场...")
            scores, counts, summary, total_score = analyze_numerology(p_input)
            st.write("正在同步 AI 命理接口...")
            status.update(label="✅ 演算完成", state="complete", expanded=False)
        
        effective_name = u_name if u_name.strip() else "匿名访客"
        st.success(f"演算成功！{effective_name} 总评分：{total_score}")
        
        st.markdown(f"**⚡ 磁场拆解：** `{summary['吉']}吉` | `{summary['凶']}凶` | `{summary['平']}平`")
        for name, val in counts.items():
            st.markdown(f'<div class="mobile-card"><span>{name}</span><span style="color:#00FFC2; font-weight:bold;">{val}</span></div>', unsafe_allow_html=True)

        st.divider()
        for name, score in scores.items():
            st.markdown(f"#### {name} 能量趋势")
            df = pd.DataFrame({'C': np.cumsum(np.random.normal(0.12, 4.2, 72)) + score})
            fig = go.Figure(data=[go.Candlestick(x=list(range(72)), open=df['C']-1, high=df['C']+2, low=df['C']-2, close=df['C'], increasing_line_color='#FF3131', decreasing_line_color='#00FFC2')])
            fig.update_layout(template="plotly_dark", height=280, xaxis_rangeslider_visible=False, margin=dict(l=5,r=5,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        st.write("---")
        st.subheader("📝 大师深度解说")
        with st.spinner("大师正在阅片中，请稍候..."):
            reading = get_ai_reading(effective_name, scores, counts)
            st.markdown(reading)
        
        # 分享按钮
        share_text = f"🔮 我在 #哈希灵数 测得 2026 综合评分：{total_score}分！"
        tweet_url = f"https://twitter.com/intent/tweet?text={urllib.parse.quote(share_text)}"
        st.markdown(f'<a href="{tweet_url}" target="_blank"><button style="background-color: #1DA1F2; color: white; border: none; padding: 12px; border-radius: 25px; font-weight: bold; width: 100%;">🐦 分享到 X (Twitter)</button></a>', unsafe_allow_html=True)

st.markdown(f'<div class="footer"><hr>© 2026 HashNumina | <a href="https://x.com/btc1349" style="color:#00FFC2;text-decoration:none;">@btc1349</a></div>', unsafe_allow_html=True)
