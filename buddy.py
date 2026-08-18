import random
import requests
import pandas as pd
import streamlit as st

st.title("🎁 สุ่มบัดดี้")

# --- 1. ใส่ข้อมูล Google Form ของคุณตรงนี้ ---
FORM_ID = "1vxw15K7QooU69Og16CrvbPS3kap9w_lXv3c3dbN313w"
ENTRY_YOUR_NAME = "entry.822914815"  
ENTRY_PICKED = "entry.1201390400"     

# --- 2. ลิงก์ Google Sheets (แชร์ Anyone with the link แล้ว) ---
sheet_url = "https://docs.google.com/spreadsheets/d/1yHczRQc9Y95KzISsF14it2d4-NrwijT7D1wuos3BgAc/export?format=csv"

try:
    df = pd.read_csv(sheet_url)
    
    # ดึงรายชื่อทั้งหมดจากคอลัมน์แรก
    ALL_MEMBERS = df.iloc[:, 0].dropna().tolist()
    
    # ดูว่าใครเคยสุ่มไปแล้วบ้างจาก Form Response (คอลัมน์ 2 และ 3)
    done_users = []
    picked_buddies = []
    
    if df.shape[1] >= 3:
        done_users = df.iloc[:, 1].dropna().tolist()
        picked_buddies = df.iloc[:, 2].dropna().tolist()

    # รายชื่อบัดดี้ที่ยังเหลืออยู่
    available_buddies = [name for name in ALL_MEMBERS if name not in picked_buddies]

    your_name = st.selectbox("เลือกชื่อของตัวเอง:", ["-- เลือกชื่อของตัวเอง --"] + ALL_MEMBERS)

    if your_name != "-- เลือกชื่อ --":
        # เช็คว่าคนนี้เคยสุ่มไปแล้วหรือยัง
        if your_name in done_users:
            idx = done_users.index(your_name)
            already_got = picked_buddies[idx]
            st.warning("เอ็งสุ่มไปแล้วไม่ใช่เรอะ!")
            st.info(f"บัดดี้คือ: **{already_got}**")
        else:
            # ตัดชื่อตัวเองออก
            possible_choices = [name for name in available_buddies if name != your_name]

            if len(possible_choices) == 0:
                st.error("เกิดข้อผิดพลาดในการสุ่ม (คนสุดท้ายเหลือแค่ชื่อตัวเอง) แคปไปบอกหมิวที")
            else:
                if st.button("🎲 กดสุ่มบัดดี้"):
                    picked = random.choice(possible_choices)

                    # ส่งผลสุ่มเข้า Google Form ทันทีเพื่อบันทึกลง Sheets
                    form_url = f"https://docs.google.com/forms/d/e/{FORM_ID}/formResponse"
                    form_data = {
                        ENTRY_YOUR_NAME: your_name,
                        ENTRY_PICKED: picked
                    }
                    requests.post(form_url, data=form_data)

                    st.success("สำเร็จ!")
                    st.markdown(f"### 🎉 บัดดี้คือ: **{picked}**")
                    st.markdown("แคปไว้อย่าบอกใครนะ")
                    st.balloons()
except Exception as e:
    st.error("ไม่สามารถโหลดข้อมูลรายชื่อได้ กรุณาตรวจสอบการแชร์ Google Sheets")
