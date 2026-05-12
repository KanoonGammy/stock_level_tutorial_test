# -*- coding: utf-8 -*-
"""
Service Level Explained — สำหรับผู้บริหาร
จาก Prophet Forecast + Confidence Interval สู่การตัดสินใจเชิงกลยุทธ์
Case Study: ระบบบริหารเหรียญกษาปณ์ (Coin Management System)
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from scipy import stats

# ────────────────────────────────────────────────────────────────────────────
# CONFIG
# ────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Service Level Explained",
    page_icon="🪙",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Brand-ish palette
PRIMARY = "#1f4e79"     # navy
ACCENT = "#c89b3c"      # gold
SUCCESS = "#2e7d32"
WARN = "#c62828"
NEUTRAL = "#6c757d"

st.markdown(
    f"""
    <style>
      .big-number {{
        font-size: 2.4rem;
        font-weight: 700;
        color: {PRIMARY};
      }}
      .kpi-label {{
        color: {NEUTRAL};
        font-size: 0.9rem;
      }}
      .callout {{
        background: #f5f7fb;
        border-left: 5px solid {PRIMARY};
        padding: 14px 18px;
        border-radius: 6px;
        margin: 10px 0;
      }}
      .callout-warn {{
        background: #fff5f5;
        border-left: 5px solid {WARN};
        padding: 14px 18px;
        border-radius: 6px;
        margin: 10px 0;
      }}
      .callout-success {{
        background: #f1f8f1;
        border-left: 5px solid {SUCCESS};
        padding: 14px 18px;
        border-radius: 6px;
        margin: 10px 0;
      }}
      .step-pill {{
        display: inline-block;
        background: {PRIMARY};
        color: white;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 0.85rem;
        margin-bottom: 8px;
      }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ────────────────────────────────────────────────────────────────────────────
# SAMPLE DATA  (จำลองข้อมูลความต้องการเหรียญกษาปณ์รายวัน)
# ────────────────────────────────────────────────────────────────────────────
@st.cache_data
def generate_coin_demand(n_days: int = 180, seed: int = 7) -> pd.DataFrame:
    """จำลองอุปสงค์เหรียญรายวัน (หน่วย: ถุง 1,000 เหรียญ) ที่ศูนย์กระจายภูมิภาค."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=n_days, freq="D")

    t = np.arange(n_days)
    base = 1000 + 1.2 * t                                 # trend
    weekly = 180 * np.sin(2 * np.pi * t / 7 - 0.6)        # ลด-เพิ่มตามวันในสัปดาห์
    monthly = 120 * np.sin(2 * np.pi * t / 30)            # รอบเงินเดือน
    noise = rng.normal(0, 90, n_days)
    spikes = np.where(rng.random(n_days) < 0.03, rng.normal(350, 80, n_days), 0)

    y = base + weekly + monthly + noise + spikes
    y = np.clip(y, 200, None).round().astype(int)
    return pd.DataFrame({"ds": dates, "y": y})


@st.cache_data
def simulate_prophet_forecast(df: pd.DataFrame, horizon: int = 30,
                              interval_width: float = 0.95, seed: int = 11):
    """จำลองผลลัพธ์แบบ Prophet: yhat / yhat_lower / yhat_upper"""
    rng = np.random.default_rng(seed)
    last_t = len(df)
    future_dates = pd.date_range(df["ds"].max() + pd.Timedelta(days=1),
                                 periods=horizon, freq="D")

    # ในชีวิตจริงเราจะเทรน Prophet — ที่นี่จำลองด้วยสูตรเดิม + uncertainty
    t = np.arange(last_t, last_t + horizon)
    base = 1000 + 1.2 * t
    weekly = 180 * np.sin(2 * np.pi * t / 7 - 0.6)
    monthly = 120 * np.sin(2 * np.pi * t / 30)
    yhat = base + weekly + monthly

    # uncertainty ที่ขยายตามอนาคต (เหมือน Prophet)
    sigma = 90 + 1.6 * np.sqrt(np.arange(horizon))
    z = stats.norm.ppf(0.5 + interval_width / 2)
    lower = yhat - z * sigma
    upper = yhat + z * sigma

    future = pd.DataFrame({
        "ds": future_dates,
        "yhat": yhat.round(),
        "yhat_lower": lower.round(),
        "yhat_upper": upper.round(),
        "sigma": sigma.round(2),
    })
    return future


# ────────────────────────────────────────────────────────────────────────────
# NAVIGATION
# ────────────────────────────────────────────────────────────────────────────
STEPS = [
    ("🏠 หน้าแรก",            "เริ่มต้นที่นี่"),
    ("1️⃣ Service Level คืออะไร", "ปูพื้นแบบเข้าใจง่าย"),
    ("2️⃣ ปัญหาคลาสสิก",      "เก็บมากเปลือง เก็บน้อยขาด"),
    ("3️⃣ Forecast ตัวเดียวไม่พอ", "ทำไมต้องมีช่วงความเชื่อมั่น"),
    ("4️⃣ Prophet + CI",       "เครื่องมือที่เลือกใช้"),
    ("5️⃣ CI ↔ Service Level",  "หัวใจของแนวคิดนี้"),
    ("6️⃣ Safety Stock & Reorder Point", "คำนวณจริง"),
    ("7️⃣ Case Study: เหรียญกษาปณ์", "ลองเล่นกับตัวเลข"),
    ("8️⃣ Optimization 360°",   "ต่อยอดทุกมิติ"),
    ("9️⃣ Decision Framework",  "สำหรับผู้บริหาร"),
]

with st.sidebar:
    st.markdown(f"## 🪙 Service Level\n#### สำหรับผู้บริหาร")
    st.caption("Prophet Forecast → Confidence Interval → Decision")
    st.markdown("---")
    choice = st.radio("เลือกขั้นตอน", [s[0] for s in STEPS], index=0,
                      label_visibility="collapsed")
    st.markdown("---")
    st.markdown(f"<small style='color:{NEUTRAL}'>Case Study: ระบบบริหารเหรียญกษาปณ์<br>"
                f"Lead time = 1 วัน (ส่วนกลาง → ภูมิภาค)</small>",
                unsafe_allow_html=True)

# ────────────────────────────────────────────────────────────────────────────
# DATA (shared)
# ────────────────────────────────────────────────────────────────────────────
demand_df = generate_coin_demand(180)

# ════════════════════════════════════════════════════════════════════════════
# PAGE 0 — HOME
# ════════════════════════════════════════════════════════════════════════════
if choice.startswith("🏠"):
    st.markdown(f"<span class='step-pill'>OVERVIEW</span>", unsafe_allow_html=True)
    st.title("เข้าใจ Service Level ผ่าน Prophet + Confidence Interval")
    st.subheader("คู่มือผู้บริหาร: ตัดสินใจเรื่อง 'พอ vs เหลือ' บนพื้นฐานข้อมูล")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("<div class='kpi-label'>ปัญหาที่แก้</div>", unsafe_allow_html=True)
        st.markdown("<div class='big-number'>Stock-out</div>", unsafe_allow_html=True)
        st.caption("ของหมดตอนลูกค้าต้องการ = สูญเสียทั้งเงินและความเชื่อมั่น")
    with c2:
        st.markdown("<div class='kpi-label'>เครื่องมือ</div>", unsafe_allow_html=True)
        st.markdown("<div class='big-number'>Prophet + CI</div>", unsafe_allow_html=True)
        st.caption("พยากรณ์ความต้องการพร้อมระบุ 'ความไม่แน่นอน'")
    with c3:
        st.markdown("<div class='kpi-label'>ผลลัพธ์</div>", unsafe_allow_html=True)
        st.markdown("<div class='big-number'>Optimization</div>", unsafe_allow_html=True)
        st.caption("ตั้ง Safety Stock / Reorder Point ที่ Service Level ที่ต้องการ")

    st.markdown("---")
    st.markdown("""
    ### 🎯 สิ่งที่ผู้บริหารจะได้จากแอปนี้
    1. **เข้าใจ Service Level** โดยไม่ต้องรู้คณิตศาสตร์ลึก
    2. **เห็นว่า Forecast + Confidence Interval** มีพลังกว่าการเดาด้วยค่าเฉลี่ย
    3. **ลองปรับ Service Level** เพื่อดูว่าต้องเก็บสต๊อกเหรียญเพิ่มเท่าไหร่ และจะลดโอกาสขาดได้แค่ไหน
    4. **เห็นภาพการต่อยอด** ไปสู่ Inventory, ขนส่ง, แรงงาน, ต้นทุน
    """)

    st.markdown("<div class='callout'>"
                "💡 <b>กดเลือกขั้นตอนทางซ้าย</b> เพื่อเริ่มทำความเข้าใจทีละลำดับ<br>"
                "แนะนำให้ไล่ดูตั้งแต่ขั้นที่ 1 → 9 จะได้ภาพรวมที่ดีที่สุด"
                "</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("##### 📊 ตัวอย่างข้อมูลที่จะใช้ในกรณีศึกษา")
    fig = px.line(demand_df.tail(90), x="ds", y="y",
                  title="อุปสงค์เหรียญรายวัน ณ ศูนย์กระจายภูมิภาค (90 วันล่าสุด)",
                  labels={"ds": "วันที่", "y": "จำนวน (ถุง × 1,000 เหรียญ)"})
    fig.update_traces(line_color=PRIMARY)
    fig.update_layout(height=350, margin=dict(l=10, r=10, t=50, b=10))
    st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# PAGE 1 — WHAT IS SERVICE LEVEL
# ════════════════════════════════════════════════════════════════════════════
elif choice.startswith("1️⃣"):
    st.markdown("<span class='step-pill'>STEP 1</span>", unsafe_allow_html=True)
    st.title("Service Level คืออะไร?")
    st.subheader("ความน่าจะเป็นที่เรา 'มีของพอ' ให้กับความต้องการ")

    st.markdown("""
    > **นิยามง่าย ๆ**: Service Level = โอกาส (%) ที่เราจะ **มีของพร้อมจ่าย**
    > เมื่อมีคำสั่งซื้อ/คำขอเข้ามา
    """)

    c1, c2 = st.columns([1.2, 1])
    with c1:
        st.markdown("""
        #### ลองคิดเป็นเรื่องใกล้ตัว 🏪

        ถ้าร้านสะดวกซื้อตั้ง **Service Level = 95%** สำหรับน้ำเปล่า
        แปลว่า: ใน 100 ครั้งที่มีคนเดินมาซื้อ จะมีน้ำให้ **95 ครั้ง**
        และอาจขาดได้ **5 ครั้ง**

        ตัวเลขนี้ไม่ได้มาเฉย ๆ — มันสะท้อน **ต้นทุนของการเลือก** ระหว่าง:
        - **เก็บเยอะ** → ลูกค้าไม่ผิดหวัง แต่ต้นทุนสต๊อก/พื้นที่/ของเสียสูง
        - **เก็บน้อย** → ประหยัด แต่เสี่ยงขาด เสียโอกาส เสียความเชื่อมั่น
        """)

    with c2:
        # Visual: Service Level vs Coverage area under curve
        x = np.linspace(-4, 4, 500)
        y = stats.norm.pdf(x)
        z95 = stats.norm.ppf(0.95)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x, y=y, fill="tozeroy",
                                 fillcolor="rgba(31,78,121,0.15)",
                                 line=dict(color=PRIMARY, width=2),
                                 name="ความต้องการที่เป็นไปได้"))
        fig.add_trace(go.Scatter(
            x=x[x <= z95], y=y[x <= z95], fill="tozeroy",
            fillcolor="rgba(46,125,50,0.5)",
            line=dict(color=SUCCESS, width=0),
            name="95% ที่เราครอบคลุม"))
        fig.add_vline(x=z95, line_dash="dash", line_color=WARN,
                      annotation_text="ระดับสต๊อกที่ตั้งไว้",
                      annotation_position="top right")
        fig.update_layout(
            title="Service Level 95% = สต๊อกครอบคลุมพื้นที่สีเขียว",
            xaxis_title="ความต้องการ (เทียบกับค่าเฉลี่ย)",
            yaxis_title="ความน่าจะเป็น",
            showlegend=False, height=340,
            margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("#### Service Level ทั่วไปในธุรกิจ")
    df_levels = pd.DataFrame({
        "อุตสาหกรรม": ["FMCG", "อะไหล่รถยนต์", "ยาช่วยชีวิต",
                        "เหรียญกษาปณ์ (เงินสด)", "วัสดุก่อสร้างทั่วไป"],
        "Service Level": ["95%", "97-99%", "99.9%", "98-99.5%", "90-95%"],
        "เหตุผล": [
            "หาทดแทนได้ง่าย ของหมดอายุไว",
            "ลูกค้ารอไม่ได้ มีโทษหากซ่อมไม่ทัน",
            "ขาดไม่ได้เด็ดขาด ชีวิตคน",
            "เป็นโครงสร้างพื้นฐานทางการเงินของประเทศ",
            "ลูกค้ารอได้บ้าง ราคาแข่งขันสำคัญกว่า"],
    })
    st.dataframe(df_levels, use_container_width=True, hide_index=True)


# ════════════════════════════════════════════════════════════════════════════
# PAGE 2 — CLASSIC DILEMMA
# ════════════════════════════════════════════════════════════════════════════
elif choice.startswith("2️⃣"):
    st.markdown("<span class='step-pill'>STEP 2</span>", unsafe_allow_html=True)
    st.title("ปัญหาคลาสสิก: เก็บมากก็เปลือง เก็บน้อยก็ขาด")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='callout-warn'><b>เก็บน้อยเกินไป</b><br>"
                    "❌ ของหมดเมื่อต้องการ<br>"
                    "❌ เสียโอกาสทางการขาย / เสียภาพลักษณ์<br>"
                    "❌ ต้องส่งด่วน → ค่าขนส่งพุ่ง<br>"
                    "❌ พนักงานสาขาไม่มีอะไรขายให้ลูกค้า"
                    "</div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='callout-warn'><b>เก็บมากเกินไป</b><br>"
                    "❌ ต้นทุนเก็บรักษา (พื้นที่/ประกัน/แรงงาน)<br>"
                    "❌ เงินจมในสต๊อก ไปลงทุนอย่างอื่นไม่ได้<br>"
                    "❌ เสี่ยงของเสีย/ล้าสมัย (สำหรับสินค้าบางประเภท)<br>"
                    "❌ ภาระโลจิสติกส์เพิ่ม"
                    "</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 💡 ทำไม Service Level ถึงเป็น 'ตัวกลาง' ที่ตอบโจทย์?")
    st.markdown("""
    เพราะมันบังคับให้ผู้บริหาร **ระบุระดับความเสี่ยงที่ยอมรับได้** อย่างชัดเจน
    แล้วใช้ข้อมูล (ไม่ใช่ความรู้สึก) คำนวณกลับว่าต้องเก็บเท่าไร

    ตัวอย่างเชิงเปรียบเทียบ:
    """)

    # Interactive cost trade-off
    target_sl = st.slider("ลองเลื่อนดู: ถ้าตั้ง Service Level ที่...",
                          50, 99, 95, 1, format="%d%%")
    z = stats.norm.ppf(target_sl / 100)
    mu, sigma = 1000, 200
    stock = mu + z * sigma
    holding_cost = stock * 0.02
    stockout_prob = 100 - target_sl

    k1, k2, k3 = st.columns(3)
    k1.metric("ระดับสต๊อกที่ต้องเก็บต่อวัน", f"{stock:,.0f} ถุง",
              f"+{(stock - mu):,.0f} ถุงเหนือค่าเฉลี่ย")
    k2.metric("ต้นทุนเก็บรักษา (สมมติ 2%)", f"{holding_cost:,.0f} หน่วย/วัน")
    k3.metric("โอกาสที่จะขาด", f"{stockout_prob}%",
              delta=f"-{99 - stockout_prob}%" if target_sl <= 99 else None,
              delta_color="inverse")

    st.info("ลองเลื่อนสไลเดอร์ดู — จะเห็นว่ายิ่งตั้ง Service Level สูง "
            "ต้องเก็บเพิ่มขึ้นแบบ **ไม่เป็นเชิงเส้น** "
            "(จาก 95% → 99% ใช้สต๊อกเพิ่มมากกว่า 90% → 95% เกือบเท่าตัว)")

    # Visualization
    sl_range = np.arange(50, 100)
    stock_range = mu + stats.norm.ppf(sl_range / 100) * sigma
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=sl_range, y=stock_range,
                              mode="lines", line=dict(color=PRIMARY, width=3),
                              name="สต๊อกที่ต้องเก็บ"))
    fig.add_vline(x=target_sl, line_dash="dash", line_color=ACCENT)
    fig.add_hline(y=stock, line_dash="dot", line_color=ACCENT)
    fig.update_layout(
        title="ความสัมพันธ์: Service Level ↔ สต๊อกที่ต้องเก็บ",
        xaxis_title="Service Level (%)", yaxis_title="สต๊อกที่ต้องเก็บ (ถุง)",
        height=380, margin=dict(l=10, r=10, t=50, b=10))
    st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# PAGE 3 — WHY POINT FORECAST IS NOT ENOUGH
# ════════════════════════════════════════════════════════════════════════════
elif choice.startswith("3️⃣"):
    st.markdown("<span class='step-pill'>STEP 3</span>", unsafe_allow_html=True)
    st.title("ทำไม Forecast ตัวเดียวไม่พอ?")

    st.markdown("""
    #### สมมติว่ามีเพื่อนสองคน

    - **คนที่ A**: "พรุ่งนี้จะมีคนมาขอเหรียญ **1,000 ถุง**" *(ตัวเดียวเป๊ะ ๆ)*
    - **คนที่ B**: "ผม **มั่นใจ 95%** ว่าจำนวนจะอยู่ระหว่าง **750 – 1,250 ถุง**"

    ถามผู้บริหาร: ใครเอาไปวางแผนได้ดีกว่ากัน?
    """)

    st.markdown("<div class='callout-success'>"
                "✅ <b>คนที่ B ดีกว่า</b> — เพราะเขาบอก 'ขอบเขตของความไม่แน่นอน' "
                "ทำให้เราตั้งสต๊อกได้อย่างชาญฉลาด: "
                "เก็บแค่ 1,000 = เสี่ยงขาด 50% / เก็บ 1,250 = ปลอดภัย ~97.5%"
                "</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### Forecast 2 แบบ — ภาพชัดทันที")

    days = np.arange(1, 31)
    truth = 1000 + 50 * np.sin(days / 3) + np.random.default_rng(3).normal(0, 80, 30)
    point_forecast = 1000 + 50 * np.sin(days / 3)
    upper = point_forecast + 200
    lower = point_forecast - 200

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=days, y=upper, fill=None, mode="lines",
                              line=dict(width=0), showlegend=False))
    fig.add_trace(go.Scatter(x=days, y=lower, fill="tonexty", mode="lines",
                              fillcolor="rgba(31,78,121,0.15)",
                              line=dict(width=0),
                              name="ช่วงความเชื่อมั่น 95% (Prophet)"))
    fig.add_trace(go.Scatter(x=days, y=point_forecast, mode="lines",
                              line=dict(color=PRIMARY, width=2),
                              name="Forecast เฉลี่ย (yhat)"))
    fig.add_trace(go.Scatter(x=days, y=truth, mode="markers",
                              marker=dict(color=WARN, size=7),
                              name="ค่าจริงที่เกิดขึ้น"))
    fig.update_layout(
        title="Forecast ตัวเดียว vs Forecast พร้อมช่วงความเชื่อมั่น",
        xaxis_title="วันในอนาคต", yaxis_title="ความต้องการ (ถุง)",
        height=420, margin=dict(l=10, r=10, t=50, b=10))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    👉 จะเห็นว่าค่าจริง (จุดสีแดง) **เด้งไปมารอบ ๆ** เส้นค่าเฉลี่ย
    ถ้าเก็บสต๊อกตาม yhat อย่างเดียว ก็จะ **ขาดประมาณครึ่งหนึ่งของเวลาทั้งหมด**
    """)


# ════════════════════════════════════════════════════════════════════════════
# PAGE 4 — PROPHET INTRO
# ════════════════════════════════════════════════════════════════════════════
elif choice.startswith("4️⃣"):
    st.markdown("<span class='step-pill'>STEP 4</span>", unsafe_allow_html=True)
    st.title("Prophet + Confidence Interval")
    st.subheader("เครื่องมือพยากรณ์ที่ใจดีกับผู้บริหาร")

    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("""
        #### Prophet คืออะไร?
        - เป็น Library จาก Meta (Facebook) สำหรับ **พยากรณ์ข้อมูลตามเวลา**
        - ออกแบบให้ใช้ง่าย ไม่ต้องเป็น Data Scientist เก่งมาก
        - จุดแข็งคือ **เห็นแนวโน้ม + ฤดูกาล + วันหยุด** ได้พร้อมกัน
        - ทุกการพยากรณ์มาพร้อม **3 ค่า**:
            - `yhat` — ค่าพยากรณ์ (กลาง)
            - `yhat_lower` — ขอบล่างของช่วงความเชื่อมั่น
            - `yhat_upper` — ขอบบนของช่วงความเชื่อมั่น
        """)
    with c2:
        st.markdown("""
        #### ทำไมเลือก Prophet?
        ✅ จับ **Seasonality** ที่ซับซ้อน (รายสัปดาห์ × รายเดือน × รายปี)
        ✅ ใส่ **Holiday Effect** ได้ (สงกรานต์, สิ้นปี, วันจ่ายเงินเดือนราชการ)
        ✅ ทนต่อข้อมูลที่หายไป (Missing Data)
        ✅ ผลลัพธ์ **อธิบายได้** — ผู้บริหารดูกราฟแล้วเข้าใจ
        ✅ **CI สร้างขึ้นโดยอัตโนมัติ** ไม่ต้องสมมติว่าเป็น Normal ก่อน
        """)

    st.markdown("---")
    st.markdown("#### ผลลัพธ์จริงที่ได้จาก Prophet (จำลอง)")

    interval = st.select_slider("เลือกความกว้างของ Confidence Interval",
                                 options=[0.50, 0.80, 0.90, 0.95, 0.99],
                                 value=0.95,
                                 format_func=lambda x: f"{int(x*100)}%")

    forecast = simulate_prophet_forecast(demand_df, horizon=30, interval_width=interval)

    fig = go.Figure()
    # ข้อมูลในอดีต
    hist = demand_df.tail(60)
    fig.add_trace(go.Scatter(x=hist["ds"], y=hist["y"],
                              mode="lines+markers",
                              line=dict(color=NEUTRAL, width=1.5),
                              marker=dict(size=4),
                              name="ข้อมูลจริง (อดีต)"))
    # CI band
    fig.add_trace(go.Scatter(x=forecast["ds"], y=forecast["yhat_upper"],
                              fill=None, mode="lines", line=dict(width=0),
                              showlegend=False))
    fig.add_trace(go.Scatter(x=forecast["ds"], y=forecast["yhat_lower"],
                              fill="tonexty", mode="lines",
                              fillcolor="rgba(31,78,121,0.18)",
                              line=dict(width=0),
                              name=f"ช่วงความเชื่อมั่น {int(interval*100)}%"))
    fig.add_trace(go.Scatter(x=forecast["ds"], y=forecast["yhat"],
                              mode="lines",
                              line=dict(color=PRIMARY, width=2.5),
                              name="yhat (พยากรณ์)"))
    fig.update_layout(
        title=f"Prophet Forecast — Horizon 30 วันข้างหน้า (CI {int(interval*100)}%)",
        xaxis_title="วันที่", yaxis_title="ความต้องการ (ถุง)",
        height=460, margin=dict(l=10, r=10, t=50, b=10))
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(forecast.head(7), use_container_width=True, hide_index=True)


# ════════════════════════════════════════════════════════════════════════════
# PAGE 5 — CI ↔ SERVICE LEVEL MAPPING
# ════════════════════════════════════════════════════════════════════════════
elif choice.startswith("5️⃣"):
    st.markdown("<span class='step-pill'>STEP 5</span>", unsafe_allow_html=True)
    st.title("หัวใจของแนวคิด: CI ↔ Service Level")

    st.markdown("""
    > **ข้อสังเกตสำคัญ**
    > ถ้า `yhat_upper` ของ Prophet ครอบคลุมความต้องการ **95% (ขอบบน)**
    > นั่นก็คือ **Service Level = 95%** โดยตรง
    > ไม่ต้องไปคำนวณ `Z × σ × √L` แบบสูตรเก่าอีก
    """)

    st.markdown("---")
    st.markdown("#### ⚠️ จุดที่คนเข้าใจผิดบ่อยที่สุด: ใช้ yhat ตัวเดียว = Service Level 50%")
    st.markdown("""
    เพราะ `yhat` คือ **ค่ามัธยฐาน** (50th percentile) ของการพยากรณ์
    แปลว่ามีโอกาส **50%** ที่ demand จริงจะสูงกว่า `yhat` → **ของขาด 50% ของเวลา**

    ดังนั้นถ้าวางแผนสต๊อกด้วย `yhat` อย่างเดียว = ตั้ง Service Level ไว้ที่ **50%** โดยไม่รู้ตัว
    """)

    look_table = pd.DataFrame({
        "ดูค่าไหนใน Output ของ Prophet": [
            "ใช้ `yhat` (ค่าเฉลี่ย/มัธยฐาน) อย่างเดียว",
            "ใช้ `yhat_upper` ที่ Prophet default (interval_width = 0.80)",
            "ใช้ `yhat_upper` ที่ตั้ง interval_width = 0.90",
            "ใช้ `yhat_upper` ที่ตั้ง interval_width = 0.95",
            "ใช้ `yhat_upper` ที่ตั้ง interval_width = 0.99",
        ],
        "Percentile (ฝั่งบน)": ["50th", "90th", "95th", "97.5th", "99.5th"],
        "Service Level จริง": ["50% ⚠️", "90%", "95%", "97.5%", "99.5%"],
    })
    st.dataframe(look_table, use_container_width=True, hide_index=True)

    st.markdown("<div class='callout-warn'>"
                "💡 <b>บทเรียนสำหรับผู้บริหาร:</b> "
                "การใช้ค่าพยากรณ์เฉลี่ยมาเป็นเป้าสต๊อก = ยอมรับโดยปริยายว่า "
                "<b>เราจะของขาด 1 ใน 2 ครั้ง</b> — ซึ่งแทบไม่มีองค์กรไหนยอมรับได้"
                "</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### แต่ต้องระวัง: 'one-tail' กับ 'two-tail'")

    c1, c2 = st.columns([1.2, 1])
    with c1:
        st.markdown("""
        Prophet ให้ CI แบบ **two-tail** เช่น 95% CI = ครอบคลุม **2.5% ขอบล่าง + 2.5% ขอบบน**
        แต่สำหรับ Service Level เราสนใจแค่ **ฝั่งบน** (ไม่ขาด)

        | สิ่งที่ต้องการ | ตั้ง `interval_width` ใน Prophet |
        |---|---|
        | Service Level 50% (ใช้ yhat) | 0.00 |
        | Service Level 75% | 0.50 |
        | Service Level 90% (Prophet default) | 0.80 |
        | Service Level 95% | 0.90 |
        | Service Level 97.5% | 0.95 |
        | Service Level 99% | 0.98 |
        | Service Level 99.5% | 0.99 |

        **สูตรแปลง**: `interval_width = 2 × SL − 1`
        เทียบกลับ: **Service Level = (1 + interval_width) / 2**
        """)

    with c2:
        sl = st.slider("ลองเลือก Service Level ที่ต้องการ", 80, 99, 95, 1,
                        format="%d%%")
        iw = 2 * sl / 100 - 1
        st.metric("ตั้ง interval_width ใน Prophet", f"{iw:.2f}",
                  help="prophet.Prophet(interval_width=...)")
        st.code(f"""from prophet import Prophet

m = Prophet(interval_width={iw:.2f})
m.fit(df)
future = m.make_future_dataframe(periods=30)
forecast = m.predict(future)

# yhat_upper คือ Service Level {sl}%
safety_stock = forecast['yhat_upper'] - forecast['yhat']""",
                  language="python")

    st.markdown("---")
    st.markdown("#### เปรียบเทียบกับสูตรคลาสสิก (Z × σ × √L)")
    comp_df = pd.DataFrame({
        "ประเด็น": ["สมมติว่า Demand เป็น Normal",
                      "จับ Trend ได้",
                      "จับ Seasonality ได้",
                      "จับวันหยุดได้",
                      "Uncertainty เปลี่ยนตามเวลา",
                      "อธิบายให้ผู้บริหารฟังง่าย"],
        "Z × σ × √L (Classic)": ["✅ ต้องสมมติ", "❌", "❌", "❌", "❌ คงที่",
                                  "🟡 ต้องอธิบาย Z"],
        "Prophet + CI": ["❌ ไม่ต้องสมมติ", "✅", "✅", "✅",
                          "✅ ขยายตามอนาคต", "✅ ดูกราฟเข้าใจเลย"],
    })
    st.dataframe(comp_df, use_container_width=True, hide_index=True)

    st.markdown("<div class='callout'>"
                "🎯 <b>สรุป Step นี้:</b> ใช้ <code>yhat_upper</code> จาก Prophet "
                "(ที่ตั้ง <code>interval_width</code> ให้ถูก) "
                "เป็น <b>ระดับสต๊อกเป้าหมาย</b> ได้เลย — ตรงไปตรงมา ไม่ต้องคูณอะไรเพิ่ม"
                "</div>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# PAGE 6 — SAFETY STOCK & REORDER POINT
# ════════════════════════════════════════════════════════════════════════════
elif choice.startswith("6️⃣"):
    st.markdown("<span class='step-pill'>STEP 6</span>", unsafe_allow_html=True)
    st.title("Safety Stock & Reorder Point")
    st.subheader("จากตัวเลข Prophet สู่นโยบายสต๊อก")

    st.markdown("""
    #### นิยามที่ผู้บริหารควรจำ
    - **Safety Stock (สต๊อกสำรอง)** = ส่วนเกินที่กันไว้รองรับความไม่แน่นอน
    - **Reorder Point (จุดสั่งซื้อใหม่)** = เมื่อสต๊อกลดลงถึงจุดนี้ ต้องสั่งใหม่ทันที
    - **Lead Time** = เวลาที่ใช้ในการเติมสต๊อก (Case นี้ = **1 วัน**)
    """)

    st.markdown("---")
    st.markdown("#### สูตรง่าย ๆ (สำหรับ Lead Time = L วัน)")

    st.latex(r"\text{Safety Stock} = \hat{y}_{\text{upper}} - \hat{y}_{\text{avg}}")
    st.latex(r"\text{Reorder Point} = \hat{y}_{\text{avg}} \times L + \text{Safety Stock}")

    st.markdown("---")
    st.markdown("#### ลองคำนวณกัน")

    c1, c2 = st.columns([1, 1.5])
    with c1:
        avg_demand = st.number_input("ค่าพยากรณ์เฉลี่ย (yhat) ต่อวัน", 100, 5000, 1000, 50)
        upper_demand = st.number_input("ค่าขอบบน (yhat_upper) ต่อวัน", 100, 8000, 1280, 50)
        lead_time = st.number_input("Lead Time (วัน)", 1, 30, 1, 1)
        ss = max(upper_demand - avg_demand, 0)
        rop = avg_demand * lead_time + ss

    with c2:
        st.metric("Safety Stock (สต๊อกสำรอง)", f"{ss:,.0f} ถุง")
        st.metric("Reorder Point (จุดสั่งซื้อใหม่)", f"{rop:,.0f} ถุง",
                  f"= {avg_demand:,} × {lead_time} + {ss:,}")
        st.markdown(f"<div class='callout-success'>"
                    f"<b>นโยบาย:</b> เมื่อสต๊อกที่ศูนย์ภูมิภาคลดลงต่ำกว่า "
                    f"<b>{rop:,.0f} ถุง</b> ให้สั่งเติมจากส่วนกลางทันที<br>"
                    f"<b>เป้าหมาย:</b> Service Level ตามที่ตั้งใน yhat_upper"
                    f"</div>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# PAGE 7 — CASE STUDY: COIN MANAGEMENT
# ════════════════════════════════════════════════════════════════════════════
elif choice.startswith("7️⃣"):
    st.markdown("<span class='step-pill'>STEP 7 · CASE STUDY</span>",
                unsafe_allow_html=True)
    st.title("🪙 Case Study: ระบบบริหารเหรียญกษาปณ์")
    st.subheader("ส่วนกลาง → ศูนย์กระจายภูมิภาค (Lead Time = 1 วัน)")

    st.markdown("""
    **สถานการณ์**
    - ส่วนกลาง (กรุงเทพฯ) ผลิตเหรียญและจัดส่งให้ศูนย์ภูมิภาค
    - ศูนย์ภูมิภาคจ่ายให้ธนาคารพาณิชย์ในพื้นที่
    - การขนส่งใช้เวลา **1 วัน** (Lead Time)
    - **โจทย์ของผู้บริหาร**: ตั้ง Service Level เท่าไรดี? ต้องเก็บสต๊อกเท่าไร?
    """)

    st.markdown("---")

    target_sl = st.slider("🎚️ ตั้งระดับ Service Level เป้าหมาย",
                          80, 99, 95, 1, format="%d%%")
    iw = 2 * target_sl / 100 - 1

    forecast = simulate_prophet_forecast(demand_df, horizon=30, interval_width=iw)

    # คำนวณตัวชี้วัด
    avg_demand = forecast["yhat"].mean()
    avg_upper = forecast["yhat_upper"].mean()
    safety_stock = avg_upper - avg_demand
    rop = avg_demand * 1 + safety_stock  # lead time = 1

    # KPI
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Forecast เฉลี่ย/วัน", f"{avg_demand:,.0f} ถุง")
    k2.metric("Safety Stock", f"{safety_stock:,.0f} ถุง",
              f"+{safety_stock/avg_demand*100:.1f}% เหนือค่าเฉลี่ย")
    k3.metric("Reorder Point", f"{rop:,.0f} ถุง")
    k4.metric("Service Level", f"{target_sl}%",
              f"-{100 - target_sl}% โอกาสขาด", delta_color="inverse")

    # Visualization
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=forecast["ds"], y=forecast["yhat_upper"],
                              fill=None, mode="lines", line=dict(width=0),
                              showlegend=False))
    fig.add_trace(go.Scatter(x=forecast["ds"], y=forecast["yhat"],
                              fill="tonexty", mode="lines",
                              fillcolor="rgba(46,125,50,0.18)",
                              line=dict(color=PRIMARY, width=2),
                              name="ค่าพยากรณ์ yhat"))
    fig.add_hline(y=rop, line_dash="dash", line_color=WARN,
                  annotation_text=f"Reorder Point = {rop:,.0f}",
                  annotation_position="top left")
    fig.add_hline(y=avg_upper, line_dash="dot", line_color=ACCENT,
                  annotation_text=f"ระดับสต๊อกเป้าหมาย (Service Level {target_sl}%)",
                  annotation_position="top right")
    fig.update_layout(
        title="แผนการเติมสต๊อก 30 วันข้างหน้า",
        xaxis_title="วันที่", yaxis_title="ความต้องการ (ถุง)",
        height=440, margin=dict(l=10, r=10, t=50, b=10))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("#### 💰 ผลกระทบเชิงเศรษฐศาสตร์")

    holding_cost_per_bag = st.number_input("ต้นทุนเก็บรักษา (บาท/ถุง/วัน)",
                                            0.5, 50.0, 5.0, 0.5)
    stockout_cost_per_bag = st.number_input("ต้นทุนความเสียหายเมื่อขาด (บาท/ถุง)",
                                             10, 1000, 200, 10)

    expected_short = avg_demand * (100 - target_sl) / 100 * 0.5  # หยาบ ๆ
    daily_holding = avg_upper * holding_cost_per_bag
    daily_stockout = expected_short * stockout_cost_per_bag
    total = daily_holding + daily_stockout

    c1, c2, c3 = st.columns(3)
    c1.metric("ต้นทุนเก็บรักษา/วัน", f"{daily_holding:,.0f} บาท")
    c2.metric("ต้นทุนคาดการณ์ของการขาด/วัน",
              f"{daily_stockout:,.0f} บาท")
    c3.metric("รวมต้นทุน/วัน", f"{total:,.0f} บาท")

    # Optimal SL curve
    sls = np.arange(80, 100)
    z_arr = stats.norm.ppf(sls / 100)
    sigma_avg = forecast["sigma"].mean()
    ss_arr = z_arr * sigma_avg
    upper_arr = avg_demand + ss_arr
    short_arr = avg_demand * (100 - sls) / 100 * 0.5
    holding_arr = upper_arr * holding_cost_per_bag
    stockout_arr = short_arr * stockout_cost_per_bag
    total_arr = holding_arr + stockout_arr

    opt_sl = sls[np.argmin(total_arr)]

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=sls, y=holding_arr, mode="lines",
                               line=dict(color=PRIMARY, width=2),
                               name="ต้นทุนเก็บรักษา"))
    fig2.add_trace(go.Scatter(x=sls, y=stockout_arr, mode="lines",
                               line=dict(color=WARN, width=2),
                               name="ต้นทุนคาดการณ์ของการขาด"))
    fig2.add_trace(go.Scatter(x=sls, y=total_arr, mode="lines",
                               line=dict(color=ACCENT, width=3),
                               name="ต้นทุนรวม"))
    fig2.add_vline(x=opt_sl, line_dash="dash", line_color=SUCCESS,
                   annotation_text=f"จุดที่ต้นทุนต่ำสุด ≈ {opt_sl}%")
    fig2.update_layout(
        title="หา 'Optimal Service Level' จากการ Trade-off ต้นทุน",
        xaxis_title="Service Level (%)", yaxis_title="บาท/วัน",
        height=400, margin=dict(l=10, r=10, t=50, b=10))
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown(f"<div class='callout-success'>"
                f"📌 <b>ข้อสรุปสำหรับผู้บริหาร:</b> "
                f"ภายใต้สมมติฐานต้นทุนนี้ ระดับที่เหมาะสมที่สุดอยู่ที่ "
                f"<b>Service Level ≈ {opt_sl}%</b><br>"
                f"แต่ถ้าให้น้ำหนัก 'ความเชื่อมั่นต่อระบบเงินสดของประเทศ' มากกว่า "
                f"ก็สามารถยอมจ่ายค่าเก็บรักษาเพิ่มเพื่อตั้งให้สูงกว่านี้"
                f"</div>", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# PAGE 8 — 360° OPTIMIZATION
# ════════════════════════════════════════════════════════════════════════════
elif choice.startswith("8️⃣"):
    st.markdown("<span class='step-pill'>STEP 8</span>", unsafe_allow_html=True)
    st.title("Optimization 360°: ต่อยอดทุกมิติ")
    st.subheader("จาก Prophet + CI สู่การปรับปรุงทั่วทั้งห่วงโซ่")

    st.markdown("""
    เมื่อรู้ `yhat`, `yhat_upper`, และ Service Level เป้าหมายแล้ว
    ข้อมูลชุดเดียวกันนี้สามารถนำไปต่อยอดในหลายมิติได้:
    """)

    tabs = st.tabs(["📦 Inventory", "🚚 Transportation", "👥 Workforce",
                    "💰 Cash Flow", "🏭 Production"])

    with tabs[0]:
        st.markdown("""
        ### Inventory Optimization
        - **Multi-echelon**: ตั้ง Service Level **แต่ละชั้น** (กลาง / ภูมิภาค / สาขา) แยกกัน
          - ส่วนกลางตั้งสูง (99%) ภูมิภาคต่ำลง (95%) เพื่อสมดุลความเสี่ยง
        - **ABC Analysis × Service Level**: เหรียญที่หายากตั้ง SL สูง / เหรียญใหญ่ ๆ ที่ใช้น้อย ตั้ง SL ต่ำ
        - **Dynamic Safety Stock**: เปลี่ยน Safety Stock ตามช่วงเวลา (ก่อนสงกรานต์ / สิ้นปี ↑↑)
        """)
        st.info("💡 **กระทำได้ทันที**: นำ `yhat_upper` ของแต่ละชนิดเหรียญ "
                "มาเป็น Stock Target รายชนิด แทนการตั้งเลขกลม ๆ เดียวกันหมด")

    with tabs[1]:
        st.markdown("""
        ### Transportation Optimization
        - **Truck Sizing**: ขนาดรถบรรทุก = `yhat_upper × Lead Time` (อย่างน้อย)
        - **Frequency Optimization**: ถ้า CI กว้างมาก → ส่งบ่อยขึ้นเพื่อลด Safety Stock
        - **Route Planning**: ใช้ Forecast แยกตามภูมิภาค → จัด Multi-stop Route ที่มีประสิทธิภาพ
        - **Backhaul**: ขากลับจากภูมิภาค → ขนเหรียญเก่าคืนส่วนกลางเพื่อ Recycle
        """)
        # mini sim
        cap_required = st.slider("จำลองความจุรถต่อเที่ยว (ถุง)",
                                  500, 3000, 1500, 100)
        avg_upper_demand = 1300
        trips_needed = np.ceil(avg_upper_demand / cap_required)
        st.metric("จำนวนเที่ยวต่อวัน (โดยประมาณ)", f"{trips_needed:.0f} เที่ยว")

    with tabs[2]:
        st.markdown("""
        ### Workforce Planning
        - **Staff at Distribution Center**: คน × ชั่วโมง ≥ `yhat_upper` ÷ Throughput
        - **Shift Scheduling**: ใช้ Seasonal Component ของ Prophet หา 'วันที่ต้องเสริมกำลัง'
        - **Cross-training**: รับมือกับ Demand Spike ที่อยู่นอก yhat_upper (Tail Risk)
        """)

    with tabs[3]:
        st.markdown("""
        ### Cash Flow / Treasury
        - **Working Capital**: Safety Stock = เงินสดที่จมในระบบ
        - **Funding Plan**: ถ้า Safety Stock เพิ่ม X ล้าน → ต้องเตรียมเงินสดทุนหมุนเวียนเพิ่ม
        - **Interest Cost Modeling**: ประเมินต้นทุนทางการเงินจากการถือสต๊อกที่ Service Level ต่าง ๆ
        """)

    with tabs[4]:
        st.markdown("""
        ### Production / Minting Schedule
        - ใช้ Forecast รวมระดับประเทศ → วางแผน Mint รายเดือน/รายไตรมาส
        - Smooth Production: ผลิตคงที่ × เก็บส่วนเกินช่วง low season → ลด Idle Capacity
        - Energy & Material Procurement: ล็อกราคาวัตถุดิบล่วงหน้าตาม Forecast
        """)

    st.markdown("---")
    st.markdown("#### 🧭 ภาพรวม: Prophet เป็น 'แกน' ของ Operating System ใหม่")
    st.markdown("""
    ```
                        ┌─────────────────────┐
                        │  Prophet Forecast   │
                        │  yhat + CI (95%)    │
                        └──────────┬──────────┘
                                   │
                ┌──────────────────┼──────────────────┐
                ▼                  ▼                  ▼
        ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
        │  Inventory   │  │ Transportation│  │  Workforce   │
        │   Policy     │  │   Planning   │  │  Scheduling  │
        └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
               │                 │                 │
               └─────────────────┼─────────────────┘
                                 ▼
                       ┌──────────────────┐
                       │  Cost / Service  │
                       │   Optimization   │
                       └──────────────────┘
    ```
    """)


# ════════════════════════════════════════════════════════════════════════════
# PAGE 9 — DECISION FRAMEWORK FOR EXECUTIVES
# ════════════════════════════════════════════════════════════════════════════
elif choice.startswith("9️⃣"):
    st.markdown("<span class='step-pill'>STEP 9 · FOR EXECUTIVES</span>",
                unsafe_allow_html=True)
    st.title("Decision Framework สำหรับผู้บริหาร")

    st.markdown("#### 🧩 4 คำถามที่ผู้บริหารควรถามทีม Operations")
    st.markdown("""
    1. **เราใช้ Service Level เท่าไรในแต่ละสาย/ภูมิภาค/ประเภทสินค้า?**
       — ถ้าตอบ "ใช้เลขเดียวกันหมด" = มีโอกาส **เสียโอกาสปรับให้เหมาะ**

    2. **เลขที่ใช้มีที่มาจากข้อมูลหรือสัญชาตญาณ?**
       — ที่มาจาก Forecast + CI = ดี / ที่มาจาก "เคยทำกันมา" = ควรทบทวน

    3. **มี Back-test ความแม่นยำของ Forecast เมื่อไรครั้งล่าสุด?**
       — Forecast ที่ดี = ค่าจริงตกในช่วง CI ตามสัดส่วนที่ตั้งไว้ (เช่น 95% CI → 95% ของข้อมูลจริงตกใน band)

    4. **ถ้ายก Service Level ขึ้น 1% จะกระทบต้นทุนเท่าไร?**
       — ถ้าทีมตอบไม่ได้ทันที = ยังไม่มี Cost Curve อย่างที่เห็นใน Step 7
    """)

    st.markdown("---")
    st.markdown("#### 📋 Roadmap แนะนำ (90 วัน)")

    roadmap = pd.DataFrame({
        "ระยะ": ["0-30 วัน", "31-60 วัน", "61-90 วัน"],
        "เป้าหมาย": [
            "Baseline & Quick Wins",
            "Pilot Implementation",
            "Scale & Institutionalize"],
        "กิจกรรมหลัก": [
            "• รวบรวมข้อมูลอุปสงค์ย้อนหลัง 2 ปี\n"
            "• เทรน Prophet ใน 1 ศูนย์นำร่อง\n"
            "• สร้าง Cost Curve เพื่อกำหนด Optimal SL",
            "• ขยายไป 3-5 ศูนย์\n"
            "• เชื่อม Forecast เข้าระบบ ERP/WMS\n"
            "• สร้าง Dashboard ติดตามผล SL จริง vs เป้า",
            "• ครอบคลุมทุกศูนย์\n"
            "• Re-train Prophet อัตโนมัติทุกเดือน\n"
            "• ขยายการใช้งานไปสู่ Workforce + Transportation"],
        "KPI": [
            "Forecast MAPE < 10%",
            "Service Level จริง ≥ เป้า 95%",
            "ลด Safety Stock 15% โดย SL ไม่ลด"],
    })
    st.dataframe(roadmap, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("#### ⚠️ ความเสี่ยงที่ต้องระวัง")
    st.markdown("""
    - **Model Drift**: Pattern อุปสงค์เปลี่ยน → Forecast แย่ลงโดยไม่รู้ตัว → ต้องมีระบบ alert
    - **Black Swan**: ภัยพิบัติ / นโยบายเปลี่ยน → CI ของ Prophet อาจไม่ครอบคลุม
      → ควรมี **Scenario Buffer** เพิ่มเติม
    - **Data Quality**: ข้อมูลอุปสงค์ที่บันทึก ≠ อุปสงค์จริง (เช่น ของหมดทำให้ไม่บันทึก)
      → ต้องแก้ที่ต้นน้ำ
    - **Over-fitting Seasonality**: ใส่ฤดูกาลเยอะเกินจน CI แคบเกินจริง
      → Back-test ทุกครั้ง
    """)

    st.markdown("---")
    st.markdown("#### 🎯 One-page Summary")
    st.markdown(f"""
    <div class='callout'>
    <b>หลักการ</b><br>
    Service Level ที่เลือก × Prophet (yhat + CI) → Safety Stock & Reorder Point ที่ถูกต้อง
    → Inventory / Transportation / Workforce ที่ปรับให้เหมาะ → ต้นทุนรวมต่ำที่สุด
    ภายใต้ระดับบริการที่ยอมรับได้

    <br><br><b>ของขวัญสำคัญที่สุดจากแนวคิดนี้</b><br>
    เปลี่ยนคำถาม "ต้องเก็บสต๊อกเท่าไร?" จาก <i>การเดา</i> เป็น <i>การเลือก</i>
    Service Level ที่ทั้งองค์กรเห็นตรงกัน — และให้คณิตศาสตร์ทำที่เหลือ
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.caption("© Service Level Explained — สำหรับการประชุมผู้บริหาร · "
                "สร้างด้วย Streamlit + Prophet + Plotly")
