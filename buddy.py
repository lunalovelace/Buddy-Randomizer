import random
import gspread
import pandas as pd
import streamlit as st
from google.oauth2.service_account import Credentials

st.set_page_config(page_title="สุ่มบัดดี้", page_icon="🎁")
st.title("🎁 สุ่มบัดดี้")

# --- 1. เชื่อมต่อ Google Sheets ผ่าน Service Account ---
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# ดึง Credentials จาก Streamlit Secrets
creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scope
)
client = gspread.authorize(creds)

# เปิดไฟล์ Google Sheets ด้วยชื่อไฟล์
SHEET_NAME = "https://docs.google.com/spreadsheets/d/1L6bnrkkhh-mLhFEVsDkeKQBB0iGsCcxkLTLMCBKzDxg/edit?usp=sharing" 
spreadsheet = client.open(SHEET_NAME)

sheet_members = spreadsheet.worksheet("Members")
sheet_history = spreadsheet.worksheet("History")

# --- 2. ดึงข้อมูลแบบ Realtime ---
# อ่านรายชื่อทั้งหมด
all_members = [item for item in sheet_members.col_values(1) if item.strip()]

# อ่านประวัติคนที่สุ่มไปแล้ว และบัดดี้ที่ถูกจับไปแล้ว
history_records = sheet_history.get_all_values()

# ตัด Header ออกถ้ามี
if len(history_records) > 0 and history_records[0][0] == "User":
    history_records = history_records[1:]

done_users = [row[0] for row in history_records if len(row) > 0]
picked_buddies = [row[1] for row in history_records if len(row) > 1]

# --- 3. ส่วนการทำงานของเว็บ ---
if not all_members:
    st.error("ไม่พบรายชื่อเพื่อนใน Google Sheets")
else:
    # กฎข้อ 2: บัดดี้ที่โดนสุ่มไปแล้ว จะถูกตัดออก
    available_buddies = [m for m in all_members if m not in picked_buddies]

    your_name = st.selectbox("เลือกชื่อของตัวเอง:", ["-- เลือกชื่อของตัวเอง --"] + all_members)

    if st.button("กดสุ่มบัดดี้!", type="primary"):
        if your_name == "-- เลือกชื่อของตัวเอง --":
            st.warning("กรุณาเลือกชื่อของตัวเองก่อน")
            
        # กฎล็อก: ถ้าชื่อนี้เคยสุ่มแล้ว ห้ามสุ่มซ้ำ
        elif your_name in done_users:
            st.error(f"คุณ {your_name} เคยสุ่มไปแล้ว ไม่สามารถสุ่มซ้ำได้!")
            
        else:
            # กฎข้อ 1: ตัดชื่อตัวเองออกจากบัดดี้ที่มีให้สุ่ม
            possible_targets = [b for b in available_buddies if b != your_name]

            if not possible_targets:
                st.error("ไม่เหลือบัดดี้ให้สุ่มแล้ว หรือเหลือแค่ชื่อตัวเอง กรุณาติดต่อคนดูแลระบบ")
            else:
                # สุ่มบัดดี้
                picked = random.choice(possible_targets)

                # บันทึกเข้า Google Sheets ตรงๆ
                sheet_history.append_row([your_name, picked])

                # แสดงผล
                st.success("สุ่มสำเร็จ!")
                st.markdown(f"🎉 **{your_name}** สุ่มได้บัดดี้คือ: **{picked}**")
                st.info("อย่าลืมแคปหน้าจอไว้เป็นความลับนะ!")
                st.balloons()

