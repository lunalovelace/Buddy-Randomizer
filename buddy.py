# ตั้งค่าหน้าเว็บ
st.title("🎁 สุ่มบัดดี้")

# รายชื่อเพื่อนทั้งหมดในกลุ่ม
ALL_MEMBERS = ["หมิว","เชง","พิม","มน","เอก","พลอย","ซิม"]

if "available_buddies" not in st.session_state:
    st.session_state.available_buddies = ALL_MEMBERS.copy()

if "assigned_pairs" not in st.session_state:
    st.session_state.assigned_pairs = {}

# 1. ให้เพื่อนเลือกชื่อตัวเอง
your_name = st.selectbox("เลือกชื่อของตัวเอง:", ["-- เลือกชื่อ --"] + ALL_MEMBERS)

if your_name != "-- เลือกชื่อ --":
    # เช็คว่าเคยสุ่มไปหรือยัง
    if your_name in st.session_state.assigned_pairs:
        st.warning("เอ็งสุ่มไปแล้วไม่ใช่เรอะ!")
        st.info(f"บัดดี้คือ: **{st.session_state.assigned_pairs[your_name]}**")
    else:
        # หา รายชื่อที่สุ่มได้ (ตัดชื่อตัวเอง ออกจากตัวเลือก)
        possible_choices = [name for name in st.session_state.available_buddies if name != your_name]
        
        # กรณีเหลือคนสุดท้ายแล้วเจอชื่อตัวเองพอดี (Edge Case)
        if len(possible_choices) == 0:
            st.error("เกิดข้อผิดพลาดในการสุ่ม (คนสุดท้ายเหลือแค่ชื่อตัวเอง) แคปไปบอกหมิวที")
        else:
            if st.button("🎲 จับสุ่มบัดดี้"):
                # สุ่ม 1 คนจากรายชื่อที่เหลืออยู่
                chosen_buddy = random.choice(possible_choices)
                
                # บันทึกผล
                st.session_state.assigned_pairs[your_name] = chosen_buddy
                
                # ตัดรายชื่อคนที่ถูกจับได้แล้วออกจากโถสุ่ม
                st.session_state.available_buddies.remove(chosen_buddy)
                
                # แสดงผลให้เห็นเฉพาะคนที่กด
                st.success("จับสุ่มสำเร็จ!")
                st.markdown(f"### 🎉 จับได้: **{chosen_buddy}**")
                st.caption("อย่าลืมแคปหน้าจอไว้เป็นความลับนะ!")
