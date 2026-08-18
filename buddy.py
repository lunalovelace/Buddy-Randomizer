import random
import requests
import pandas as pd
import streamlit as st

st.set_page_config(page_title="สุ่มบัดดี้", page_icon="🎁")
st.title("🎁 สุ่มบัดดี้")

# --- ลิงก์ Google Sheets ---
URL_MEMBERS = "https://docs.google.com/spreadsheets/d/1qM5rLtF_vLmBsjewqYPvAOL-grvVtQwU3dx77SVvwJY/export?format=csv"
URL_RESPONSES = "https://docs.google.com/spreadsheets/d/1yHczRQc9Y95KzIsSF14it2d4-NrwijT7D1wuos3BgAc/export?format=csv"

FORM_URL = "https://docs.google.com/forms/d/1vxw15K7QooU69Og16CrvbPS3kap9w_lXv3c3dbN313w/formResponse"
ENTRY_YOUR_NAME = "entry.822914815"
ENTRY_PICKED = "entry.880874775"

try:
    # 1. ดึงรายชื่อสมาชิกทั้งหมด
    ALL_MEMBERS = pd.read_csv(URL_MEMBERS).iloc[:, 0].dropna().astype(str).str.strip().tolist()

    # 2. ดึงข้อมูลประวัติการสุ่ม (เอามาแบบระวัง)
    try:
        df_r = pd.read_csv(URL_RESPONSES)
        # ดึงแค่คอลัมน์คนสุ่ม และคนโดนสุ่ม ออกมาเป็น List
        done_users = df_r.iloc[:, 1].dropna().astype(str).str.strip().tolist() if df_r.shape[1] >= 2 else []
        picked_buddies = df_r.iloc[:, 2].dropna().astype(str).str.strip().tolist() if df_r.shape[1] >= 3 else []
    except:
        done_users, picked_buddies = [], []

    # เลือกชื่อ
    your_name = st.selectbox("เลือกชื่อของตัวเอง:", ["-- เลือกชื่อ --"] + ALL_MEMBERS)

    if your_name != "-- เลือกชื่อ --":
        # เช็กเฉพาะชื่อที่ "เราเลือก" ว่าอยู่ใน Google Sheets หรือไม่
        if your_name in done_users:
            st.warning(f"คุณ {your_name} สุ่มไปแล้วครับ!")
        else:
            # รายชื่อที่เหลือให้สุ่ม
            available_buddies = [m for m in ALL_MEMBERS if m not in picked_buddies and m != your_name]
            
            if not available_buddies:
                st.error("ไม่เหลือชื่อให้สุ่มแล้วครับ")
            else:
                if st.button("🎲 กดสุ่มบัดดี้"):
                    picked = random.choice(available_buddies)
                    
                    # บันทึก
                    payload = {ENTRY_YOUR_NAME: your_name, ENTRY_PICKED: picked}
                    requests.post(FORM_URL, data=payload, timeout=5)
                    
                    st.success(f"สุ่มสำเร็จ! ได้บัดดี้คือ: {picked}")
                    st.balloons()
                    st.rerun()

except Exception as e:
    st.error(f"เกิดข้อผิดพลาด: {e}")

