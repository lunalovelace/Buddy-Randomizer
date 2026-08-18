import random
import pandas as pd
import streamlit as st

st.title("🎁 สุ่มบัดดี้")

# --- ดึงรายชื่อจาก Google Sheets ---
sheet_url = "https://docs.google.com/spreadsheets/d/1qM5rLtF_vLmBsjewqYPvAOL-grvVtQwU3dx77SVvwJY/export?format=csv"

try:
    # ดึงรายชื่อจากคอลัมน์แรกใน Sheets
    ALL_MEMBERS = pd.read_csv(sheet_url).iloc[:, 0].dropna().tolist()

    if "available_buddies" not in st.session_state:
        st.session_state.available_buddies = ALL_MEMBERS.copy()

    if "assigned_pairs" not in st.session_state:
        st.session_state.assigned_pairs = {}

    # 1. ให้เพื่อนเลือกชื่อตัวเอง
    your_name = st.selectbox(
        "เลือกชื่อของตัวเอง:", ["-- เลือกชื่อ --"] + ALL_MEMBERS
    )

    if your_name != "-- เลือกชื่อ --":
        # เช็คว่าเคยสุ่มไปหรือยัง
        if your_name in st.session_state.assigned_pairs:
            st.warning("เอ็งสุ่มไปแล้วไม่ใช่เหรอะ!")
            st.info(
                f"บัดดี้คือ: **{st.session_state.assigned_pairs[your_name]}**"
            )
        else:
            # หา รายชื่อที่สุ่มได้ (ตัดชื่อตัวเอง ออกจากตัวเลือก)
            possible_choices = [
                name
                for name in st.session_state.available_buddies
                if name != your_name
            ]

            # กรณีเหลือคนสุดท้ายแล้วเจอชื่อตัวเองพอดี (Edge Case)
            if len(possible_choices) == 0:
                st.error(
                    "เกิดข้อผิดพลาดในการสุ่ม (คนสุดท้ายเหลือแค่ชื่อตัวเอง) แคปไปบอกหมิวที"
                )
            else:
                if st.button("🎲 กดสุ่มบัดดี้"):
                    picked = random.choice(possible_choices)

                    # บันทึกผล
                    st.session_state.assigned_pairs[your_name] = picked
                    st.session_state.available_buddies.remove(picked)

                    st.success("สำเร็จ")
                    st.markdown(f"### 🎉 จับได้: **{picked}**")
                    st.balloons()

except Exception as e:
    st.error("เกิดข้อผิดพลาดในการโหลดรายชื่อจาก Google Sheets")

