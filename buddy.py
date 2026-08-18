import random
import requests
import pandas as pd
import streamlit as st

st.set_page_config(page_title="สุ่มบัดดี้", page_icon="🎁")
st.title("🎁 สุ่มบัดดี้")

# 1. เอา Web App URL ที่ได้จาก Apps Script ขั้นที่ 1 มาวางตรงนี้
API_URL = "https://script.google.com/u/0/home/projects/1rppUlPrspeCJVobIpkZqxPvq0tFpKpCZ_8-DsASHudST224zZt0MZVCo/edit"

# 2. ลิงก์รายชื่อเพื่อน (คอลัมน์ A)
URL_MEMBERS = "https://docs.google.com/spreadsheets/d/1qM5rLtF_vLmBsjewqYPvAOL-grvVtQwU3dx77SVvwJY/export?format=csv"

# ดึงข้อมูลสมาชิกและประวัติการสุ่ม
def load_data():
    members = []
    done_users = []
    picked_buddies = []

    # ดึงรายชื่อสมาชิกทั้งหมด
    try:
        df_m = pd.read_csv(URL_MEMBERS)
        members = df_m.iloc[:, 0].dropna().astype(str).str.strip().tolist()
    except Exception:
        pass

    # ดึงประวัติการสุ่มจาก API Google Sheets
    try:
        res = requests.get(API_URL, timeout=5)
        if res.status_code == 200:
            rows = res.json()
            # ข้าม Header row (แถวแรก)
            for row in rows[1:]:
                if len(row) >= 2 and row[1]:
                    done_users.append(str(row[1]).strip())
                if len(row) >= 3 and row[2]:
                    picked_buddies.append(str(row[2]).strip())
    except Exception:
        pass

    return members, done_users, picked_buddies

ALL_MEMBERS, done_users, picked_buddies = load_data()

if not ALL_MEMBERS:
    st.error("ไม่สามารถดึงรายชื่อได้ กรุณาตรวจสอบลิงก์รายชื่อสมาชิก")
else:
    # เงื่อนไข 2: ใครโดนสุ่มได้ไปแล้ว ตัดออกจากรายชื่อบัดดี้ที่เหลือ
    available_buddies = [name for name in ALL_MEMBERS if name not in picked_buddies]

    your_name = st.selectbox("เลือกชื่อของตัวเอง:", ["-- เลือกชื่อของตัวเอง --"] + ALL_MEMBERS)

    if st.button("กดสุ่มบัดดี้!", type="primary"):
        if your_name == "-- เลือกชื่อของตัวเอง --":
            st.warning("กรุณาเลือกชื่อของตัวเองก่อน")
            
        # ล็อก: ถ้าเคยสุ่มไปแล้ว ห้ามสุ่มซ้ำ
        elif your_name in done_users:
            st.error(f"คุณ {your_name} เคยสุ่มไปแล้ว ไม่สามารถสุ่มซ้ำได้!")
            
        else:
            # เงื่อนไข 1: ตัดชื่อตัวเองออก สุ่มไม่ได้ชื่อตัวเอง
            possible_targets = [b for b in available_buddies if b != your_name]

            if not possible_targets:
                st.error("เกิดข้อผิดพลาด: ไม่เหลือบัดดี้ให้สุ่มแล้ว หรือเหลือแค่ชื่อตัวเอง กรุณาติดต่อคนดูแลระบบ")
            else:
                picked = random.choice(possible_targets)

                # ส่งผลการสุ่มไปบันทึกลง Google Sheets โดยตรง
                payload = {
                    "your_name": your_name,
                    "picked": picked
                }
                
                try:
                    res = requests.post(API_URL, json=payload, timeout=10)
                    if res.status_code == 200:
                        st.success("สุ่มสำเร็จ!")
                        st.markdown(f"🎉 **{your_name}** สุ่มได้บัดดี้คือ: **{picked}**")
                        st.info("แคปหน้าจอเก็บไว้เป็นความลับด้วยนะ!")
                        st.balloons()
                    else:
                        st.error("บันทึกข้อมูลไม่สำเร็จ กรุณาลองใหม่อีกครั้ง")
                except Exception:
                    st.error("เกิดข้อผิดพลาดในการเชื่อมต่อระบบบันทึกข้อมูล")
