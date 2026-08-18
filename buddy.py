import random
import requests
import pandas as pd
import streamlit as st

st.set_page_config(page_title="สุ่มบัดดี้", page_icon="🎁")
st.title("🎁 สุ่มบัดดี้")

# --- 1. ข้อมูล Google Form ---
# URL สำหรับส่งข้อมูลคำตอบตรงๆ เข้า Google Form
FORM_URL = "https://docs.google.com/forms/d/1vxw15K7QooU69Og16CrvbPS3kap9w_lXv3c3dbN313w/formResponse"

ENTRY_YOUR_NAME = "entry.822914815"
ENTRY_PICKED = "entry.1201390400"

# --- 2. ลิงก์ดึง CSV จากทั้ง 2 ชีท ---
url_members = "https://docs.google.com/spreadsheets/d/1qM5rLtF_vLmBsjewqYPvAOL-grvVtQwU3dx77SVvwJY/edit?gid=0#gid=0"
url_responses = "https://docs.google.com/spreadsheets/d/1L6bnrkkhh-mLhFEVsDkeKQBB0iGsCcxkLTLMCBKzDxg/edit?resourcekey=&gid=1823141371#gid=1823141371"

# อ่านข้อมูลแบบปิด Cache ชั่วคราวเพื่อดึงข้อมูลล่าสุดจาก Google Sheets ตลอดเวลา
def load_data():
    members = []
    done = []
    picked = []

    # 1. ดึงรายชื่อสมาชิกทั้งหมด
    try:
        df_m = pd.read_csv(f"{url_members}&_={pd.Timestamp.now().timestamp()}")
        members = df_m.iloc[:, 0].dropna().astype(str).str.strip().tolist()
    except Exception:
        pass

    # 2. ดึงประวัติคนที่เคยสุ่มไปแล้ว และบัดดี้ที่ถูกสุ่มออกไปแล้ว
    try:
        df_r = pd.read_csv(f"{url_responses}&_={pd.Timestamp.now().timestamp()}")
        # คอลัมน์ที่ 2 (Index 1) = ชื่อคนที่เคยสุ่มแล้ว
        if df_r.shape[1] >= 2:
            done = df_r.iloc[:, 1].dropna().astype(str).str.strip().tolist()
        # คอลัมน์ที่ 3 (Index 2) = บัดดี้ที่ถูกสุ่มออกไปแล้ว
        if df_r.shape[1] >= 3:
            picked = df_r.iloc[:, 2].dropna().astype(str).str.strip().tolist()
    except Exception:
        pass

    return members, done, picked

ALL_MEMBERS, done_users, picked_buddies = load_data()

if not ALL_MEMBERS:
    st.error("ไม่สามารถดึงรายชื่อได้ กรุณาตรวจสอบการตั้งค่าแชร์ไฟล์รายชื่อเป็น 'Anyone with the link'")
else:
    # เงื่อนไข 2: ตัดคนที่โดนสุ่มได้ไปแล้ว ออกจากตัวเลือกบัดดี้ที่เหลือ
    available_buddies = [name for name in ALL_MEMBERS if name not in picked_buddies]

    your_name = st.selectbox("เลือกชื่อของตัวเอง:", ["-- เลือกชื่อของตัวเอง --"] + ALL_MEMBERS)

    if st.button("กดสุ่มบัดดี้!", type="primary"):
        if your_name == "-- เลือกชื่อของตัวเอง --":
            st.warning("กรุณาเลือกชื่อของตัวเองก่อน")
        # ล็อก: ถ้าสุ่มไปแล้ว จะสุ่มซ้ำไม่ได้อีก
        elif your_name in done_users:
            st.error(f"คุณ {your_name} เคยสุ่มไปแล้ว ไม่สามารถสุ่มซ้ำได้!")
        else:
            # เงื่อนไข 1: ตัดชื่อตัวเองออก ไม่ให้สุ่มได้ชื่อตัวเอง
            possible_targets = [b for b in available_buddies if b != your_name]

            if not possible_targets:
                st.error("เกิดข้อผิดพลาด: ไม่เหลือบัดดี้ให้สุ่มแล้ว หรือเหลือแค่ชื่อตัวเอง กรุณาติดต่อหมิว")
            else:
                # สุ่มบัดดี้
                picked = random.choice(possible_targets)

                payload = {
                    ENTRY_YOUR_NAME: your_name,
                    ENTRY_PICKED: picked
                }
                
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                }
                
                try:
                    res = requests.post(FORM_URL, data=payload, headers=headers, timeout=10)
                    
                    if res.status_code in [200, 302]:
                        st.success("สุ่มสำเร็จ!")
                        st.markdown(f"🎉 **{your_name}** สุ่มได้บัดดี้คือ: **{picked}**")
                        st.info("แคปหน้าจอเก็บไว้เป็นความลับด้วยนะ!")
                        st.balloons()
                    else:
                        st.error(f"ส่งข้อมูลไม่ผ่าน (Status: {res.status_code})")
                except Exception:
                    st.error("เกิดข้อผิดพลาดในการเชื่อมต่อส่งข้อมูล")
