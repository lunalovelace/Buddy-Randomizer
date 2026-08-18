import random
import requests
import pandas as pd
import streamlit as st

st.set_page_config(page_title="สุ่มบัดดี้", page_icon="🎁")
st.title("🎁 สุ่มบัดดี้")

# --- 1. ข้อมูล Google Form (ใส่ URL เต็มเพื่อป้องกันปัญหา 404) ---
FORM_RESPONSE_URL = "https://docs.google.com/forms/u/0/d/e/1FAIpQLSc-PLACEHOLDER/formResponse" 
# หมายเหตุ: หาก URL ลิงก์ฟอร์มเดิมคือ 1vxw15K7QooU69Og16CrvbPS3kap9w_lXv3c3dbN313w
# เราจะใช้ URL มาตรฐานของ Google Form Response โดยตรงตามด้านล่างนี้ครับ:

FORM_URL = "https://docs.google.com/forms/d/1vxw15K7QooU69Og16CrvbPS3kap9w_lXv3c3dbN313w/formResponse"

ENTRY_YOUR_NAME = "entry.822914815"
ENTRY_PICKED = "entry.1201390400"

# --- 2. ลิงก์ตรงสำหรับดึง CSV จากทั้ง 2 ชีท ---
url_members = "https://docs.google.com/spreadsheets/d/1qM5rLtF_vLmBsjewqYPvAOL-grvVtQwU3dx77SVvwJY/gviz/tq?tqx=out:csv"
url_responses = "https://docs.google.com/spreadsheets/d/1yHczRQc9Y95KzIsSF14it2d4-NrwijT7D1wuos3BgAc/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=2)
def load_data():
    # 1. อ่านรายชื่อเพื่อนจากไฟล์ที่ 1
    try:
        df_m = pd.read_csv(url_members)
        members = df_m.iloc[:, 0].dropna().astype(str).str.strip().tolist()
    except Exception:
        members = []

    # 2. อ่านผลการสุ่มจากไฟล์ที่ 2 (Google Form Responses)
    done = []
    picked = []
    try:
        df_r = pd.read_csv(url_responses)
        if df_r.shape[1] >= 3:
            done = df_r.iloc[:, 1].dropna().astype(str).str.strip().tolist()
            picked = df_r.iloc[:, 2].dropna().astype(str).str.strip().tolist()
    except Exception:
        pass

    return members, done, picked

try:
    ALL_MEMBERS, done_users, picked_buddies = load_data()

    if not ALL_MEMBERS:
        st.error("ไม่สามารถดึงรายชื่อได้ กรุณาตรวจสอบการตั้งค่าแชร์ไฟล์รายชื่อเป็น 'Anyone with the link'")
    else:
        available_buddies = [name for name in ALL_MEMBERS if name not in picked_buddies]

        your_name = st.selectbox("เลือกชื่อของตัวเอง:", ["-- เลือกชื่อของตัวเอง --"] + ALL_MEMBERS)

        if st.button("กดสุ่มบัดดี้!", type="primary"):
            if your_name == "-- เลือกชื่อของตัวเอง --":
                st.warning("กรุณาเลือกชื่อของตัวเองก่อน")
            elif your_name in done_users:
                st.error(f"{your_name} เอ็งสุ่มไปแล้วไม่ใช่เรอะ!")
            else:
                possible_targets = [b for b in available_buddies if b != your_name]

                if not possible_targets:
                    st.error("เกิดข้อผิดพลาดในการสุ่ม (คนสุดท้ายเหลือแค่ชื่อตัวเอง) แคปไปบอกหมิวที")
                else:
                    picked = random.choice(possible_targets)

                    payload = {
                        ENTRY_YOUR_NAME: your_name,
                        ENTRY_PICKED: picked
                    }
                    
                    headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                        "Content-Type": "application/x-www-form-urlencoded"
                    }
                    
                    # ส่งแบบไม่ follow redirect เพื่อตรวจรับ status 200 หรือ 302 (ซึ่ง Google Form ถือว่าบันทึกสำเร็จทั้งคู่)
                    res = requests.post(FORM_URL, data=payload, headers=headers, allow_redirects=False)

                    if res.status_code in [200, 302]:
                        st.success("สำเร็จ!")
                        st.markdown(f"🎉 **{your_name}** สุ่มได้บัดดี้คือ: **{picked}**")
                        st.markdown("แคปไปเป็นความลับด้วยนะ")
                        st.balloons()
                        st.cache_data.clear()
                    else:
                        st.error(f"เกิดข้อผิดพลาดในการบันทึกข้อมูล (Status: {res.status_code})")

except Exception as e:
    st.error("เกิดข้อผิดพลาดในการเชื่อมต่อระบบ")
