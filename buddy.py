import random
import requests
import pandas as pd
import streamlit as st

st.set_page_config(page_title="สุ่มบัดดี้", page_icon="🎁")
st.title("🎁 สุ่มบัดดี้")

# --- ดึงรายชื่อจาก Google Sheets ---
URL_MEMBERS = "https://docs.google.com/spreadsheets/d/1qM5rLtF_vLmBsjewqYPvAOL-grvVtQwU3dx77SVvwJY/export?format=csv"
URL_RESPONSES = "https://docs.google.com/spreadsheets/d/1yHczRQc9Y95KzIsSF14it2d4-NrwijT7D1wuos3BgAc/export?format=csv"

FORM_URL = "https://docs.google.com/forms/d/1vxw15K7QooU69Og16CrvbPS3kap9w_lXv3c3dbN313w/formResponse"
ENTRY_YOUR_NAME = "entry.822914815"
ENTRY_PICKED = "entry.880874775"

# ตัวแปรจำผลการสุ่มชั่วคราวใน session เพื่อให้เตือนทันทีโดยไม่ต้องรอ Google
if "local_done" not in st.session_state:
    st.session_state.local_done = {}

try:
    # 1. ดึงรายชื่อสมาชิกทั้งหมด
    ALL_MEMBERS = pd.read_csv(URL_MEMBERS).iloc[:, 0].dropna().astype(str).str.strip().tolist()

    # 2. ดึงประวัติจาก Google Sheets
    done_users = []
    picked_buddies = []
    try:
        df_r = pd.read_csv(URL_RESPONSES)
        if df_r.shape[1] >= 2:
            done_users = df_r.iloc[:, 1].dropna().astype(str).str.strip().tolist()
        if df_r.shape[1] >= 3:
            picked_buddies = df_r.iloc[:, 2].dropna().astype(str).str.strip().tolist()
    except Exception:
        pass

    # รวมประวัติจาก Google Sheets และคนที่เพิ่งกดสุ่มในหน้าเว็บตอนนี้
    all_done_users = set(done_users + list(st.session_state.local_done.keys()))
    all_picked_buddies = set(picked_buddies + list(st.session_state.local_done.values()))

    # เลือกชื่อตัวเอง
    your_name = st.selectbox("เลือกชื่อของตัวเอง:", ["-- เลือกชื่อ --"] + ALL_MEMBERS)

    if your_name != "-- เลือกชื่อ --":
        # เช็คว่าเคยสุ่มไปหรือยัง (เช็กทั้งจาก Sheets และ Session ตอนนี้)
        if your_name in all_done_users:
            st.warning("เอ็งสุ่มไปแล้วไม่ใช่เหรอะ!")
            
            # ถ้ามีประวัติการสุ่มอยู่ ให้โชว์บัดดี้ที่เคยสุ่มได้ด้วย
            if your_name in st.session_state.local_done:
                st.info(f"บัดดี้ของคุณคือ: **{st.session_state.local_done[your_name]}**")
        else:
            # ตัดคนที่โดนสุ่มไปแล้ว และตัดชื่อตัวเอง ออกจากตัวเลือก
            available_buddies = [m for m in ALL_MEMBERS if m not in all_picked_buddies]
            possible_choices = [name for name in available_buddies if name != your_name]

            if len(possible_choices) == 0:
                st.error("เกิดข้อผิดพลาดในการสุ่ม (ไม่เหลือคนให้สุ่มแล้ว หรือเหลือแค่ชื่อตัวเอง) แคปไปบอกหมิวที")
            else:
                if st.button("🎲 กดสุ่มบัดดี้", type="primary"):
                    picked = random.choice(possible_choices)

                    # 1. บันทึกลง Session ทันที (ทำให้ปุ่มล็อก + ขึ้น warning ทันที)
                    st.session_state.local_done[your_name] = picked

                    # 2. ส่งข้อมูลไปเก็บใน Google Sheets หลังบ้าน
                    payload = {
                        ENTRY_YOUR_NAME: your_name,
                        ENTRY_PICKED: picked
                    }
                    headers = {"User-Agent": "Mozilla/5.0"}
                    try:
                        requests.post(FORM_URL, data=payload, headers=headers, timeout=5)
                    except Exception:
                        pass

                    st.success("สำเร็จ")
                    st.markdown(f"### 🎉 จับได้: **{picked}**")
                    st.balloons()
                    st.rerun()  # รีเฟรชหน้าจอทันทีเพื่อตัดสิทธิ์การกดซ้ำ

except Exception as e:
    st.error("เกิดข้อผิดพลาดในการดึงข้อมูลจาก Google Sheets")
