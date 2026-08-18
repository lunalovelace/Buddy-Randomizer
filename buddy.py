import random
import requests
import pandas as pd
import streamlit as st

st.set_page_config(page_title="สุ่มบัดดี้", page_icon="🎁")
st.title("🎁 สุ่มบัดดี้")

# --- 1. ลิงก์ Google Sheets ---
# ชีทที่ 1: รายชื่อสมาชิกทั้งหมด (คอลัมน์ A)
URL_MEMBERS = "https://docs.google.com/spreadsheets/d/1qM5rLtF_vLmBsjewqYPvAOL-grvVtQwU3dx77SVvwJY/export?format=csv"

# ชีทที่ 2: ชีทที่ใช้เก็บผลการสุ่ม (คอลัมน์ B = คนที่กดสุ่มแล้ว, คอลัมน์ C = บัดดี้ที่ถูกเลือกไปแล้ว)
URL_RESPONSES = "https://docs.google.com/spreadsheets/d/1yHczRQc9Y95KzIsSF14it2d4-NrwijT7D1wuos3BgAc/export?format=csv"

# ลิงก์ส่งข้อมูลกลับ Google Form เพื่อบันทึกลงชีทที่ 2
FORM_URL = "https://docs.google.com/forms/d/1vxw15K7QooU69Og16CrvbPS3kap9w_lXv3c3dbN313w/formResponse"
ENTRY_YOUR_NAME = "entry.822914815"
ENTRY_PICKED = "entry.880874775"

try:
    # 1. ดึงรายชื่อสมาชิกทั้งหมด
    ALL_MEMBERS = pd.read_csv(URL_MEMBERS).iloc[:, 0].dropna().astype(str).str.strip().tolist()

    # 2. ดึงประวัติคนที่เคยกดสุ่มไปแล้วจาก Google Sheets ชีทตอบกลับ
    done_users = []
    picked_buddies = []
    try:
        df_r = pd.read_csv(URL_RESPONSES)
        if df_r.shape[1] >= 2:
            done_users = df_r.iloc[:, 1].dropna().astype(str).str.strip().tolist()
        if df_r.shape[1] >= 3:
            picked_buddies = df_r.iloc[:, 2].dropna().astype(str).str.strip().tolist()
    except Exception:
        pass # ถ้ายังไม่มีคนสุ่มเลย ให้เป็นลิสต์ว่าง

    # เลือกชื่อตัวเอง
    your_name = st.selectbox("เลือกชื่อของตัวเอง:", ["-- เลือกชื่อ --"] + ALL_MEMBERS)

    if your_name != "-- เลือกชื่อ --":
        # 🟢 เช็กจุดที่ 1: ถ้าเคยสุ่มแล้ว (มีชื่อใน done_users) ให้ดักทันที
        if your_name in done_users:
            st.warning("เอ็งสุ่มไปแล้วไม่ใช่เหรอะ!")
            st.error("❌ ไม่สามารถกดสุ่มซ้ำได้แล้วครับ")
        else:
            # 🟢 เช็กจุดที่ 2: ตัดคนที่โดนคนอื่นสุ่มไปแล้ว (picked_buddies) ออกจากตัวเลือก
            available_buddies = [m for m in ALL_MEMBERS if m not in picked_buddies]

            # 🟢 เช็กจุดที่ 3: ตัดชื่อตัวเองออก ไม่ให้สุ่มได้ตัวเอง
            possible_choices = [name for name in available_buddies if name != your_name]

            if len(possible_choices) == 0:
                st.error("เกิดข้อผิดพลาดในการสุ่ม (ไม่เหลือชื่อให้สุ่มแล้ว หรือเหลือแค่ชื่อตัวเอง) แคปไปบอกหมิวที")
            else:
                if st.button("🎲 กดสุ่มบัดดี้", type="primary"):
                    picked = random.choice(possible_choices)

                    # บันทึกผลส่งกลับไปที่ Google Form / Sheets
                    payload = {
                        ENTRY_YOUR_NAME: your_name,
                        ENTRY_PICKED: picked
                    }
                    headers = {"User-Agent": "Mozilla/5.0"}
                    requests.post(FORM_URL, data=payload, headers=headers)

                    st.success("สำเร็จ")
                    st.markdown(f"### 🎉 จับได้: **{picked}**")
                    st.info("อย่าลืมแคปหน้าจอเก็บไว้เป็นความลับนะ!")
                    st.balloons()

except Exception as e:
    st.error("เกิดข้อผิดพลาดในการดึงข้อมูลจาก Google Sheets")
