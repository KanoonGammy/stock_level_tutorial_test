# 🪙 Service Level Explained — Prophet + Confidence Interval

แอปพลิเคชัน Streamlit ที่อธิบายแนวคิด **Service Level** สำหรับผู้บริหารระดับสูง
ผ่านกรณีศึกษา **ระบบบริหารเหรียญกษาปณ์** (Coin Management System)
โดยใช้ผลลัพธ์จาก **Prophet Forecast** + **Confidence Interval** เป็นเครื่องมือหลัก

---

## 🎯 จุดประสงค์

แอปนี้ออกแบบเพื่อให้ผู้บริหาร / ผู้ที่ไม่ใช่นักวิเคราะห์ข้อมูล สามารถเข้าใจ:

1. **Service Level** คืออะไร และทำไมจึงสำคัญ
2. ทำไม Forecast ตัวเดียวจึง **ไม่พอ** ต่อการตัดสินใจ
3. ทำไม **Prophet + Confidence Interval** จึงเหนือกว่าสูตรคลาสสิก (Z·σ·√L)
4. การคำนวณ **Safety Stock** และ **Reorder Point** ที่ใช้ได้จริง
5. การประยุกต์ใช้กับ **ระบบเหรียญกษาปณ์** (Lead time = 1 วัน)
6. การต่อยอดสู่ **Optimization 360°** (Inventory, Transportation, Workforce, Cash Flow, Production)
7. **Decision Framework** สำหรับผู้บริหารและ Roadmap 90 วัน

---

## 📂 โครงสร้างโปรเจ็กต์

```
.
├── app.py              # Streamlit application (main)
├── requirements.txt    # Python dependencies
└── README.md           # this file
```

---

## 🚀 วิธีรันบนเครื่องตัวเอง (Local)

```bash
# 1) clone repo
git clone <your-repo-url>
cd <repo-name>

# 2) สร้าง virtual environment (แนะนำ)
python -m venv venv
source venv/bin/activate          # macOS/Linux
# venv\Scripts\activate           # Windows

# 3) ติดตั้ง dependencies
pip install -r requirements.txt

# 4) รันแอป
streamlit run app.py
```

แอปจะเปิดที่ `http://localhost:8501` โดยอัตโนมัติ

---

## ☁️ Deploy ขึ้น Streamlit Community Cloud (ฟรี)

1. Push โค้ดทั้งหมดขึ้น GitHub
2. ไปที่ [https://share.streamlit.io](https://share.streamlit.io)
3. เลือก Repo / Branch / `app.py`
4. กด **Deploy**

แอปจะได้ URL สาธารณะให้แชร์ให้ผู้บริหารดูได้เลย

---

## 🧭 9 ขั้นตอนของแอป

| Step | หัวข้อ | สิ่งที่ผู้ใช้ได้เรียนรู้ |
|------|--------|----------------------|
| 🏠 หน้าแรก | Overview | ภาพรวมและเป้าหมายของแอป |
| 1️⃣ | Service Level คืออะไร | นิยามและตัวอย่างใกล้ตัว |
| 2️⃣ | ปัญหาคลาสสิก | Trade-off ระหว่างเก็บมาก vs เก็บน้อย |
| 3️⃣ | Forecast ตัวเดียวไม่พอ | ทำไมต้องมี Confidence Interval |
| 4️⃣ | Prophet + CI | เครื่องมือพยากรณ์และจุดแข็ง |
| 5️⃣ | CI ↔ Service Level | หัวใจของแนวคิด |
| 6️⃣ | Safety Stock & Reorder Point | คำนวณจริง |
| 7️⃣ | Case Study: เหรียญกษาปณ์ | Interactive Simulator |
| 8️⃣ | Optimization 360° | ต่อยอดทุกมิติ |
| 9️⃣ | Decision Framework | สำหรับผู้บริหาร + Roadmap |

---

## 💡 แนวคิดหลัก (TL;DR)

```
Prophet ให้ผลลัพธ์: yhat, yhat_lower, yhat_upper

ถ้าตั้ง interval_width = 2 × Service Level - 1
แล้ว yhat_upper = ระดับสต๊อกเป้าหมายโดยตรง (one-tail)

Safety Stock  = yhat_upper - yhat
Reorder Point = yhat × Lead Time + Safety Stock
```

ข้อดีเหนือสูตรคลาสสิก `Z × σ × √L`:
- ไม่ต้องสมมติว่า Demand เป็น Normal
- จับ Trend / Seasonality / Holiday ได้
- Uncertainty ขยายตามอนาคต
- อธิบายให้ผู้บริหารฟังเข้าใจง่ายผ่านกราฟ

---

## 📝 หมายเหตุ

- แอปนี้ **จำลอง** ผลลัพธ์ของ Prophet เพื่อความรวดเร็วในการ deploy
  หากต้องการใช้กับข้อมูลจริง ให้ติดตั้ง `prophet` เพิ่มเติม
  (`pip install prophet`) และแทนที่ฟังก์ชัน `simulate_prophet_forecast()` ด้วยการเทรน Prophet จริง
- ข้อมูลอุปสงค์เหรียญในกรณีศึกษาเป็นข้อมูล **สังเคราะห์** เพื่อการเรียนรู้

---

## 📜 License

MIT — ใช้ได้อย่างเสรีในงานราชการและการศึกษา
