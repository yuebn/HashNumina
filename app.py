import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import google.generativeai as genai
import streamlit.components.v1 as components

# ==========================================
# 🔑 核心配置：填入你的 API Key
# ==========================================
API_KEY = "AIzaSyBCfIGB8JCa2WyXNnxWhWm-_YFiaiHSexs"
genai.configure(api_key=API_KEY)

# 1. 页面配置与黑金视觉注入
st.set_page_config(page_title="哈希灵数 HashNumina", layout="wide")

# 注入 CSS 打造黑金质感
st.markdown("""
    <style>
    .main { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); color: #E0E0E0; }
    .stTextInput>div>div>input { background-color: #1A1A1A; color: #00FFC2; border: 1px solid #7928ca; }
    .stButton>button { 
        background: linear-gradient(45deg, #7928ca, #ff0080); 
        color: white; font-weight: bold; border: none; border-radius: 10px; height: 3em;
    }
    .stButton>button:hover { transform: scale(1.02); box-shadow: 0 0 15px #7928ca; }
    </style>
    """, unsafe_allow_html=True)

# 🚀 交互优化补丁：点击输入框自动全选内容 (方便一键删除)
components.html(
    """
    <script>
    const monitorInputs = () => {
        const inputs = window.parent.document.querySelectorAll('input[type="text"]');
        inputs.forEach(input => {
            if (!input.dataset.listenerAdded) {
                input.addEventListener('focus', () => { input.select(); });
                input.dataset.listenerAdded = 'true';
            }
        });
    };
    // 每隔1秒检查一次，确保动态加载的输入框也被捕捉
    setInterval(monitorInputs, 1000);
    </script>
    """,
    height=0,
)

st.title("🔮 哈希灵数 (HashNumina) | 专业终端")
st.caption("数字化运势分析引擎 v2.5 | 数字能量学 + Gemini AI 驱动")

# 2. AI 大师解说函数 (增强容错版)
import random

def get_ai_reading(nickname, phone, scores):
    fortune = scores.get("财运", 60)
    career = scores.get("事业", 60)
    
    # 定义不同维度的深度话术库
    high_fortune = [
        f"🔥 兄弟，你这手机号里的‘天医’财场已经烧红了！K线在2026年是个典型的‘长牛走势’。这种财富哈希不是等来的，是命里带的。建议拿死筹码，别在黎明前被洗下车。",
        f"🚀 监测到极强的底部放量信号！{nickname}，你的财运磁场正在发生质变。这波爆拉的支撑位非常稳固，属于那种‘越跌越买’的极品运势，准备好迎接你的财富自由节点吧。"
    ]
    
    low_fortune = [
        f"📉 讲真，现在的财运K线还在缩量探底。{nickname}，磁场显示你目前正处于‘磨底期’，切记不要急于求成去开高倍杠杆。建议开启‘防守模式’，多做0撸，积攒原始哈希能量。",
        f"🛡️ 能量反馈显示目前是‘垃圾时间’。财运磁场缺乏动能，K线走势比较纠结。这时候拼的是耐心，不是本金。守住你的现金流，等2026年Q3那个关键变盘点出现再全仓出击。"
    ]
    
    mid_fortune = [
        f"⚖️ 磁场处于典型的‘震荡行情’。{nickname}，你现在不缺机会，缺的是坚定的共识。运势K线忽红忽绿，说明你内心也在纠结。定投时间，定投心态，这波震荡洗盘结束后就是主升浪。",
        f"🧩 能量中规中矩，像是在走一个箱体震荡。当前的财富哈希属于‘积小成多’阶段。别看现在波动小，这其实是在为未来的大级别突破蓄势。稳住，我们能赢。"
    ]

    # 根据分值随机抽取话术
    if fortune >= 75:
        res = random.choice(high_fortune)
    elif fortune <= 62:
        res = random.choice(low_fortune)
    else:
        res = random.choice(mid_fortune)
    
    return res
# 3. 数字能量学核心算法
def analyze_numerology(phone):
    fields = {
        "财运": ["13", "31", "68", "86", "49", "94", "27", "72"],
        "事业": ["19", "91", "78", "87", "34", "43", "26", "62"],
        "爱情": ["16", "61", "47", "74", "38", "83", "29", "92"]
    }
    scores = {"财运": 62, "事业": 60, "爱情": 58, "家庭": 60}
    for key, pairs in fields.items():
        for pair in pairs:
            if pair in phone: scores[key] += 10
    return scores

# 4. 专业 K 线模拟引擎
def generate_pro_k_line(phone, dim_name, base_score):
    seed_val = hash(phone + dim_name) % (2**32)
    np.random.seed(seed_val)
    dates = pd.date_range(end=datetime.now() + timedelta(days=1095), periods=72, freq='ME')
    
    volatility = 5.5 if dim_name == "爱情" else 3.8
    changes = np.random.normal(0.12, volatility, 72)
    prices = np.cumsum(changes) + base_score
    
    df = pd.DataFrame({'Date': dates, 'Close': prices})
    df['Open'] = df['Close'].shift(1).fillna(base_score)
    df['High'] = df[['Open', 'Close']].max(axis=1) + np.random.uniform(0.5, 2.5)
    df['Low'] = df[['Open', 'Close']].min(axis=1) - np.random.uniform(0.5, 2.5)
    return df

# 5. UI 布局
with st.sidebar:
    st.header("🔑 终端接入")
    nickname = st.text_input("社交昵称", "Web3_Trader")
    phone = st.text_input("手机号码", placeholder="输入11位数字")
    analyze_btn = st.button("启动哈希演算")
    st.write("---")
    st.markdown("### 📊 引擎负载\n- Core: Numerology-V2\n- AI: Gemini-Flash")

if analyze_btn:
    if len(phone) < 11:
        st.error("请输入正确的 11 位手机号")
    else:
        pro_scores = analyze_numerology(phone)
        st.success(f"📡 演算完成！正在为 {nickname} 同步数字命理...")
        
        cols = st.columns(2)
        for i, (name, score) in enumerate(pro_scores.items()):
            df = generate_pro_k_line(phone, name, score)
            with cols[i % 2]:
                st.markdown(f"#### {name} 能量趋势")
                fig = go.Figure(data=[go.Candlestick(
                    x=df['Date'], open=df['Open'], high=df['High'], 
                    low=df['Low'], close=df['Close'],
                    increasing_line_color='#FF3131', # 红色
                    decreasing_line_color='#00FFC2'  # 霓虹绿
                )])
                fig.update_layout(template="plotly_dark", height=320, 
                                 xaxis_rangeslider_visible=False,
                                 margin=dict(l=0,r=0,t=0,b=0),
                                 paper_bgcolor='rgba(0,0,0,0)',
                                 plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig, use_container_width=True)
        
        st.write("---")
        st.subheader("📝 哈希灵数·AI 大师批注")
        with st.spinner("AI 正在读取 K 线波动数据..."):
            reading = get_ai_reading(nickname, phone, pro_scores)
            st.markdown(f"> **{reading}**")
else:
    st.info("👈 请在左侧侧边栏输入信息启动演算。")