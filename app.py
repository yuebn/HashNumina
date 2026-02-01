import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
import urllib.parse
import streamlit.components.v1 as components

# ==========================================
# 🔑 核心配置：API Key
# ==========================================
DEEPSEEK_API_KEY = st.secrets.get("DEEPSEEK_API_KEY", "sk-899d54012ab145588d06927811ff8562")

# 1. 页面配置与视觉注入
st.set_page_config(page_title="多比 duobi", layout="wide")

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
        border-radius: 12px; background-color: #FFFFFF !important; margin: 10px 0;
    }
    .star-grid {
        display: flex; flex-wrap: wrap; max-width: 420px; margin-left: 0; justify-content: flex-start;
    }
    .star-item { flex: 0 0 25%; text-align: left; padding: 5px 0; }
    .star-label { font-size: 0.72em; color: #bbb; display: block; }
    .star-value { font-size: 1.05em; color: #00FFC2; font-weight: bold; display: block; }
    .footer { text-align: center; padding: 30px 10px; color: #888; font-size: 0.8em; }
    /* 选项组样式微调 */
    .stCheckbox { margin-bottom: -10px; }
    </style>
    """, unsafe_allow_html=True)

# 🚀 手机 K 线脚本补丁
components.html('<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>', height=0)

st.title("🔮 多比 duobi")
st.caption("周易八星磁场扫描 + DeepSeek-V3 深度解说")

# --- 🛡️ 隐私文案还原 ---
st.markdown("""
    <div class="privacy-trust-box">
        <b style="color:#000000;">🛡️ 隐私保护声明：</b><br>
        本站不设数据库，您的输入信息仅用于AI实时演算，不会被存储或转售。请放心使用。
    </div>
""", unsafe_allow_html=True)

# 2. 输入区域与选项组
u_name = st.text_input("👤 您的昵称", placeholder="访客模式可留空")
p_input = st.text_input("📱 手机号码", placeholder="输入11位待测号码")

st.write("🎯 **请选择需要显示的 K 线运势组：**")
col_opt1, col_opt2 = st.columns(2)
with col_opt1:
    show_finance = st.checkbox("💰 财运 + 事业", value=False)
with col_opt2:
    show_emotion = st.checkbox("❤️ 感情 + 家庭", value=False)

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
        "model": "deepseek-chat", "messages": [
            {"role": "system", "content": "你是一位周易数字命理大师。点评扎心、生动，不少于350字。"},
            {"role": "user", "content": f"用户{nickname}，磁场：{counts}，评分：{scores}。请复盘。"}
        ], "temperature": 0.8
    }
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=120)
        return r.json()['choices'][0]['message']['content']
    except: return "📡 大师正在闭关（网络拥堵），请点击按钮重新演算。"

# 4. 展示逻辑
if analyze_btn:
    if len(p_input) < 11:
        st.warning("请输入完整的 11 位手机号")
    else:
        with st.status("🔮 正在读取哈希磁场...", expanded=False) as status:
            scores, counts, summary, total_score = analyze_numerology(p_input)
            status.update(label="✅ 演算完成", state="complete")
        
        effective_name = u_name if u_name.strip() else "访客"
        st.success(f"演算成功，{effective_name}阁下您的手机号码能量分：{total_score} 分")
        
        # --- ⚡ 磁场解盘：布局保持不动 ---
        st.markdown(f"**⚡ 磁场解盘：** `{summary['吉']}吉` | `{summary['凶']}凶` | `{summary['平']}平`")
        star_html = '<div class="star-grid">'
        for label, val in counts.items():
            star_html += f'<div class="star-item"><span class="star-label">{label}</span><span class="star-value">{val}</span></div>'
        star_html += '</div>'
        st.markdown(star_html, unsafe_allow_html=True)

        st.divider()
        # --- 🚀 K 线显示筛选逻辑 ---
        st.markdown("### 📊 项目月线运势 K 线图 (理数预测)")
        ganzhi_months = ["庚子", "辛丑", "壬寅", "癸卯", "甲辰", "乙巳", "丙午", "丁未", "戊申", "己酉", "庚戌", "辛亥"]
        
        # 确定需要显示的维度
        display_dims = []
        if show_finance: display_dims.extend(["财运", "事业"])
        if show_emotion: display_dims.extend(["情感", "家庭"])
        # 如果都没选，默认显示财运事业
        if not show_finance and not show_emotion: display_dims = ["财运", "事业"]

        k_cols = st.columns(2)
        for idx, dim_name in enumerate(display_dims):
            score = scores[dim_name]
            np.random.seed(hash(p_input + dim_name) % 1000000)
            steps = 12
            noise = np.random.normal(0, 3.5, steps)
            trend = np.linspace(0, 10, steps) * (1 if score > 65 else -0.5)
            c_prices = np.cumsum(noise) + trend + score
            df = pd.DataFrame({'Month': ganzhi_months, 'Close': c_prices, 'Open': np.roll(c_prices, 1)})
            df.loc[0, 'Open'] = score - 2.0
            df['High'] = df[['Open', 'Close']].max(axis=1) + 1.5
            df['Low'] = df[['Open', 'Close']].min(axis=1) - 1.5
            
            with k_cols[idx % 2]:
                st.markdown(f"#### {dim_name} 维度运势")
                fig = go.Figure(data=[go.Candlestick(
                    x=df['Month'], open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'],
                    increasing_line_color='#00FFC2', decreasing_line_color='#FF3131'
                )])
                fig.update_layout(
                    template="plotly_dark", height=280, xaxis_rangeslider_visible=False,
                    margin=dict(l=0,r=0,t=10,b=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)'),
                    yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.05)', side='right')
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'responsive': True})
        
        # --- 🚀 新增引导文字 ---
        st.info("💡 财运事业感情家庭这四项都要算吗？请返回首页重新选择。")

        st.divider()
        st.subheader("📝 大师深度解说")
        with st.spinner("大师正在演算中..."):
            reading = get_ai_reading(effective_name, scores, counts)
            st.markdown(reading)
        
        share_text = f"🔮 我在 #多比duobi 测得 2026 综合评分：{total_score}分！"
        st.markdown(f'<a href="https://twitter.com/intent/tweet?text={urllib.parse.quote(share_text)}" target="_blank"><button style="background-color: #1DA1F2; color: white; border: none; padding: 12px; border-radius: 25px; font-weight: bold; width: 100%;">🐦 分享到 X (Twitter)</button></a>', unsafe_allow_html=True)

st.markdown(f'<div class="footer"><hr>© 2026 多比 duobi | <a href="https://x.com/btc1349" style="color:#00FFC2;text-decoration:none;">@btc1349</a></div>', unsafe_allow_html=True)
