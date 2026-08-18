import random
import requests
import pandas as pd
import streamlit as st

st.set_page_config(page_title="สุ่มบัดดี้", page_icon="🎁")
st.title("🎁 สุ่มบัดดี้")

# --- 1. ข้อมูล Google Form ---
FORM_URL = "https://docs.google.com/forms/d/1vxw15K7QooU69Og16CrvbPS3kap9w_lXv3c3dbN313w/formResponse"

ENTRY_YOUR_NAME = "entry.822914815"
ENTRY_PICKED = "entry.880874775"

# --- 2. ลิงก์ดึง CSV จากทั้ง 2 ชีท ---
url_members = "https://docs.google.com/spreadsheets/d/1qM5rLtF_vLmBsjewqYPvAOL-grvVtQwU3dx77SVvwJY/gviz/tq?tqx=out:csv"
url_responses = "https://docs.google.com/spreadsheets/d/1yHczRQc9Y95KzIsSF14it2d4-NrwijT7D1wuos3BgAc/gviz/tq?tqx=out:csv"

def load_data():
    members = []
    done = []
    picked = []

    # 1. ดึงรายชื่อสมาชิกทั้งหมด
    try:
        df_m = pd.read_csv(url_members)
        members = df_m.iloc[:, 0].dropna().astype(str).str.strip().tolist()
    except Exception as e:
        st.write("Error ดึงรายชื่อ:", e)

    # 2. ดึงประวัติคนที่เคยสุ่มไปแล้ว
    try:
        df_r = pd.read_csv(url_responses)
        
        # คอลัมน์ B (Index 1) = คนที่เคยกดสุ่มไปแล้ว
        if df_r.shape[1] >= 2:
            done = df_r.iloc[:, 1].dropna().astype(str).str.strip().tolist()
            
        # คอลัมน์ C (Index 2) = บัดดี้ที่ถูกสุ่มออกไปแล้ว
        if df_r.shape[1] >= 3:
            picked = df_r.iloc[:, 2].dropna().astype(str).str.strip().tolist()
    except Exception as e:
        st.write("Error ดึงประวัติ:", e)

    return members, done, picked

ALL_MEMBERS, done_users, picked_buddies = load_data()

if not ALL_MEMBERS:
    st.error("ไม่สามารถดึงรายชื่อได้ กรุณาตรวจสอบการตั้งค่าแชร์ไฟล์รายชื่อเป็น 'Anyone with the link'")
else:
    # ตัดคนที่โดนสุ่มได้ไปแล้ว ออกจากตัวเลือกบัดดี้
    available_buddies = [name for name in ALL_MEMBERS if name not in picked_buddies]

    your_name = st.selectbox("เลือกชื่อของตัวเอง:", ["-- เลือกชื่อของตัวเอง --"] + ALL_MEMBERS)

    if st.button("กดสุ่มบัดดี้!", type="primary"):
        if your_name == "-- เลือกชื่อของตัวเอง --":
            st.warning("กรุณาเลือกชื่อของตัวเองก่อน")
        elif your_name in done_users:
            st.error(f"คุณ {your_name} เคยสุ่มไปแล้ว ไม่สามารถสุ่มซ้ำได้ครับ!")
        else:
            # ตัดชื่อตัวเองออก
            possible_targets = [b for b in available_buddies if b != your_name]

            if not possible_targets:
                st.error("เกิดข้อผิดพลาด: ไม่เหลือบัดดี้ให้สุ่มแล้ว หรือเหลือแค่ชื่อตัวเอง กรุณาติดต่อหมิว")
            else:
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
                        st.error(f"บันทึกไม่สำเร็จ (Status Code: {res.status_code})")
                except Exception as err:
                    st.error(f"เกิดข้อผิดพลาดในการส่งข้อมูล: {err}")
