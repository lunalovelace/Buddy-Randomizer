import random
import requests
import pandas as pd
import streamlit as st

st.set_page_config(page_title="สุ่มบัดดี้", page_icon="🎁")
st.title("🎁 สุ่มบัดดี้")

# --- 1. ข้อมูล Google Form ---
FORM_ID = "1vxw15K7QooU69Og16CrvbPS3kap9w_lXv3c3dbN313w"
ENTRY_YOUR_NAME = "entry.822914815"
ENTRY_PICKED = "entry.1201390400"

# --- 2. ลิงก์ Google Sheets (ปรับรูปแบบเป็น /gviz/tq?tqx=out:csv&gid=...) ---
# *** อย่าลืมเปลี่ยน เลขgidของคุณ เป็นเลข gid ของแท็บที่มีรายชื่อเพื่อนนะครับ ***
SHEET_ID = "1yHczRQc9Y95KzISsF14it2d4-NrwijT7D1wuos3BgAc"
GID = "1385562614" 

sheet_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&gid={GID}"

# ฟังก์ชันดึงข้อมูลแบบไม่ค้างแคช
@st.cache_data(ttl=5)
def load_data(url):
    return pd.read_csv(url)

try:
    df = load_data(sheet_url)

    # ดึงรายชื่อจากคอลัมน์ A
    ALL_MEMBERS = df.iloc[:, 0].dropna().astype(str).str.strip().tolist()

    if not ALL_MEMBERS:
        st.error("ไม่พบรายชื่อ กรุณาเขียนชื่อให้ถูกต้อง")
    else:
        # ดึงรายชื่อคนที่เคยสุ่มไปแล้วจากคอลัมน์ B และ C (ถ้ามี)
        done_users = []
        picked_buddies = []

        if df.shape[1] >= 3:
            done_users = df.iloc[:, 1].dropna().astype(str).str.strip().tolist()
            picked_buddies = df.iloc[:, 2].dropna().astype(str).str.strip().tolist()

        # รายชื่อบัดดี้ที่ยังเหลือให้สุ่ม
        available_buddies = [name for name in ALL_MEMBERS if name not in picked_buddies]

        your_name = st.selectbox("เลือกชื่อของตัวเอง:", ["-- เลือกชื่อของตัวเอง --"] + ALL_MEMBERS)

        if st.button("กดสุ่มบัดดี้!", type="primary"):
            if your_name == "-- เลือกชื่อของตัวเอง --":
                st.warning("กรุณาเลือกชื่อของตัวเองก่อนนะ")
            elif your_name in done_users:
                st.error(f"คุณ {your_name} เอ็งสุ่มไปแล้วไม่ใช่เรอะ!")
            else:
                possible_targets = [b for b in available_buddies if b != your_name]

                if not possible_targets:
                    st.error("เกิดข้อผิดพลาดในการสุ่ม (คนสุดท้ายเหลือแค่ชื่อตัวเอง) แคปไปบอกหมิวที")
                else:
                    picked = random.choice(possible_targets)

                    # ส่งผลสุ่มเข้า Google Form
                    form_url = f"https://docs.google.com/forms/d/e/{339007925}/formResponse"
                    payload = {
                        ENTRY_YOUR_NAME: your_name,
                        ENTRY_PICKED: picked
                    }
                    
                    res = requests.post(form_url, data=payload)

                    if res.status_code == 200:
                        st.success(f"🎉  **{your_name}** สุ่มได้บัดดี้คือ: **{picked}**")
                        st.balloons()
                        st.cache_data.clear()  # เคลียร์แคชเพื่อให้ข้อมูลอัปเดตทันที
                    else:
                        st.error("เกิดข้อผิดพลาดในการบันทึกข้อมูล กรุณาลองใหม่อีกครั้ง")

except Exception as e:
    st.error("ไม่สามารถโหลดข้อมูลรายชื่อได้ กรุณาตรวจสอบสิทธิ์การแชร์ Google Sheets (ต้องตั้งเป็น Anyone with the link)")
