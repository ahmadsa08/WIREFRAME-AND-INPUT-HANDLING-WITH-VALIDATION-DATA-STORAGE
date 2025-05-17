import streamlit as st
import pandas as pd
import sqlite3
import re
from contextlib import closing

CSV_FILE = 'registrations.csv'
DB_FILE = 'registrations.db'

def create_database_table():
    """Creates the registrations table in the database if it doesn't exist."""
    try:
        with closing(sqlite3.connect(DB_FILE)) as conn:
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS registrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT,
                    email TEXT,
                    student_id TEXT,
                    phone TEXT,
                    year_of_study TEXT,
                    faculty TEXT
                )
            ''')
            conn.commit()
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")

def save_to_csv(data):
    """Saves registration data to a CSV file."""
    try:
        df = pd.DataFrame([data])
        df.to_csv(CSV_FILE, mode='a', header=not pd.io.common.file_exists(CSV_FILE), index=False)
    except Exception as e:
        st.error(f"Error saving to CSV: {e}")

def save_to_db(data):
    """Saves registration data to the database."""
    try:
        with closing(sqlite3.connect(DB_FILE)) as conn:
            c = conn.cursor()
            c.execute('''
                INSERT INTO registrations (full_name, email, student_id, phone, year_of_study, faculty)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                data['Full Name'],
                data['Email'],
                data['Student ID'],
                data['Phone Number'],
                data['Year of Study'],
                data['Faculty']
            ))
            conn.commit()
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")

def is_valid_email(email):
    """Validates email format."""
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def is_valid_phone(phone):
    """Validates phone number format."""
    return re.match(r"^\d{10,12}$", phone)

def is_database_populated():
    """Checks if the database table contains any data."""
    try:
        with closing(sqlite3.connect(DB_FILE)) as conn:
            c = conn.cursor()
            c.execute('SELECT COUNT(*) FROM registrations')
            count = c.fetchone()[0]
            return count > 0
    except sqlite3.Error as e:
        st.error(f"Database error: {e}")
        return False  # Return False on error to prevent app from crashing

# Custom CSS for better style
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        font-size: 2.5rem;
        font-weight: 700;
        color: #304FFE;
        margin-bottom: 20px;
    }
    .footer {
        font-size: 0.8rem;
        color: gray;
        text-align: center;
        margin-top: 50px;
    }
    .nav-text {
        font-size: 1rem;
        font-weight: 600;
        color: #FFFFFF;
        margin-right: 1rem;
        display: inline-block;
        vertical-align: middle;
    }
    .stRadio > div {
        flex-direction: row;
        justify-content: center;
        gap: 2rem;
    }
    .stButton>button {
        background-color: #304FFE;
        color: white;
        border-radius: 8px;
        font-size: 16px;
        padding: 8px 25px;
        margin-top: 15px;
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

def show_home():
    left_col, right_col = st.columns([0.6, 0.4])
    with left_col:
        st.markdown("<h2 style='color:#304FFE; font-weight: bold;'>Shape the Future with AI & Innovation</h2>", unsafe_allow_html=True)
        st.markdown("<h4>Join leading experts and passionate minds at FutureTech2025 to explore the transformative power of Artificial Intelligence and emerging technologies.</h4>", unsafe_allow_html=True)
        st.markdown("""
            -   **Discover** the latest breakthroughs in AI and their real-world applications.
            -   **Engage** in interactive sessions and gain practical insights.
            -   **Network** with fellow innovators, researchers, and industry leaders.
            -   **Be inspired** by visionary talks and future-forward discussions.
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Register Now!", key="register_button_home"):
            st.session_state.page = "Registration"
            st.rerun()
    with right_col:
        st.image("FutureTech 2025.jpg", caption="Immerse yourself in the world of Future Tech")
        st.markdown("<small>Welcome to the FutureTech 2025 registration portal.</small>", unsafe_allow_html=True)
        st.markdown("<small>Click 'Register Now!' or use the navigation tabs above to secure your spot.</small>", unsafe_allow_html=True)

def show_registration_form():
    st.markdown("### Event Registration Form")
    # Define the list of faculties
    faculties = [
        "Faculty of Chemical and Process Engineering Technology",
        "Faculty of Civil Engineering Technology",
        "Faculty of Electrical and Electronics Engineering Technology",
        "Faculty of Manufacturing and Mechatronic Engineering Technology",
        "Faculty of Mechanical and Automotive Engineering Technology",
        "Faculty of Computing"
    ]
    with st.form("register_form"):
        full_name = st.text_input("Full Name")
        email = st.text_input("Email")
        student_id = st.text_input("Student ID")
        phone = st.text_input("Phone Number")
        year = st.text_input("Year of Study")
        # Use st.selectbox() for faculty selection
        faculty = st.selectbox("Faculty", options=faculties)
        submitted = st.form_submit_button("Submit")

        if submitted:
            errors = []
            if not full_name:
                errors.append("Full Name is required.")
            if not is_valid_email(email):
                errors.append("Invalid email format.")
            if not student_id:
                errors.append("Student ID is required.")
            if not is_valid_phone(phone):
                errors.append("Phone must be 10–12 digits.")
            if not year:
                errors.append("Year of Study is required.")
            if not faculty:
                errors.append("Faculty is required.")

            if errors:
                for err in errors:
                    st.error(err)
            else:
                data = {
                    "Full Name": full_name,
                    "Email": email,
                    "Student ID": student_id,
                    "Phone Number": phone,
                    "Year of Study": year,
                    "Faculty": faculty  # Use the selected faculty
                }
                save_to_csv(data)
                save_to_db(data)
                st.session_state["registration_data"] = data
                st.success("🎉 Registration submitted successfully!")
                st.session_state.page = "Confirmation"
                st.rerun()

def show_confirmation():
    st.markdown("### Confirmation Details")
    if "registration_data" in st.session_state:
        data = st.session_state["registration_data"]
        st.success("Thank you for registering! Here's your information:")
        df = pd.DataFrame.from_dict(data, orient='index', columns=["Your Info"])
        st.table(df)
        st.markdown("<br><br>")
        if st.button("Register Another Participant"):
            st.session_state.page = "Registration"
            st.rerun()
    else:
        st.info("No registration data found. Please complete your registration.")

def main():
    create_database_table()

    st.markdown('<div class="main-header">FutureTech2025: Innovation & AI Workshop</div>', unsafe_allow_html=True)

    if "page" not in st.session_state:
        st.session_state.page = "Home"

    st.markdown("""
        <style>
        .stRadio {
            display: flex;
            justify-content: center;
            align-items: center;
        }
        </style>
    """, unsafe_allow_html=True)
    
    cols = st.columns([0.15, 0.85])
    with cols[0]:
        st.markdown('<span class="nav-text">Navigate:</span>', unsafe_allow_html=True)
    with cols[1]:
        page = st.radio("", ["Home", "Registration", "Confirmation"], horizontal=True,
                        index=["Home", "Registration", "Confirmation"].index(st.session_state.page))

    if page == "Home":
        show_home()
    elif page == "Registration":
        show_registration_form()
    elif page == "Confirmation":
        show_confirmation()

    if page != st.session_state.page:
        st.session_state.page = page

    st.markdown('<div class="footer">© 2025 FutureTech Workshop | Developed by Your Name</div>', unsafe_allow_html=True)

if __name__ == '__main__':
    main()
