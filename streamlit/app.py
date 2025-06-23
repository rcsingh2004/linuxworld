import streamlit as st
import sqlite3
import pandas as pd
import hashlib

# --- Database Setup ---
conn = sqlite3.connect('crm.db', check_same_thread=False)
c = conn.cursor()

# Create users table
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL
)
''')

# Create customers table
c.execute('''
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    notes TEXT
)
''')
conn.commit()

# --- Helper Functions ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed

def register_user(username, password):
    c.execute('SELECT * FROM users WHERE username=?', (username,))
    if c.fetchone():
        return False
    c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hash_password(password)))
    conn.commit()
    return True

def login_user(username, password):
    c.execute('SELECT * FROM users WHERE username=?', (username,))
    user = c.fetchone()
    if user and verify_password(password, user[1]):
        return True
    return False

def add_customer(name, email, phone, notes):
    c.execute('INSERT INTO customers (name, email, phone, notes) VALUES (?, ?, ?, ?)',
              (name, email, phone, notes))
    conn.commit()

def get_all_customers():
    c.execute('SELECT * FROM customers')
    return c.fetchall()

def search_customer(term):
    c.execute('''
        SELECT * FROM customers 
        WHERE name LIKE ? OR email LIKE ? OR phone LIKE ?
    ''', (f'%{term}%', f'%{term}%', f'%{term}%'))
    return c.fetchall()

# --- Streamlit App Config ---
st.set_page_config(page_title="CRM System", page_icon="🗂️", layout="centered")

# Session State Initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# --- UI Styling ---
st.markdown("""
    <style>
        .main-title {
            text-align: center;
            color: #4CAF50;
            font-size: 36px;
            margin-bottom: 20px;
        }
        .sub-header {
            color: #FF5722;
            margin-top: 10px;
            margin-bottom: 20px;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border-radius: 8px;
            padding: 10px 20px;
            margin-top: 10px;
        }
        .stTextInput>div>input, .stTextArea>div>textarea {
            border-radius: 6px;
        }
    </style>
""", unsafe_allow_html=True)

# --- Login/Register Screens ---
def login_register_ui():
    st.markdown('<div class="main-title">🗂️ Business CRM Login</div>', unsafe_allow_html=True)
    menu = st.selectbox("Choose an option", ["Login", "Register"])

    if menu == "Login":
        st.markdown('<h4 class="sub-header">🔑 Login to your CRM account</h4>', unsafe_allow_html=True)
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if login_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome, {username}!")
            else:
                st.error("Invalid username or password.")

    elif menu == "Register":
        st.markdown('<h4 class="sub-header">📝 Register New Account</h4>', unsafe_allow_html=True)
        username = st.text_input("Create Username")
        password = st.text_input("Create Password", type="password")
        if st.button("Register"):
            if username and password:
                if register_user(username, password):
                    st.success("Account created successfully! You can now login.")
                else:
                    st.warning("Username already exists. Try another.")
            else:
                st.warning("Please fill in both fields.")

# --- CRM Main Application ---
def crm_dashboard_ui():
    st.sidebar.title(f"👋 Hello, {st.session_state.username}")
    menu = st.sidebar.radio("Navigate", ["Add Customer", "View Customers", "Search Customer", "Logout"])

    if menu == "Add Customer":
        st.markdown('<div class="main-title">➕ Add New Customer</div>', unsafe_allow_html=True)
        with st.form("customer_form"):
            name = st.text_input("Full Name")
            email = st.text_input("Email Address")
            phone = st.text_input("Phone Number")
            notes = st.text_area("Additional Notes")

            submitted = st.form_submit_button("Add Customer")
            if submitted:
                if name and email:
                    add_customer(name, email, phone, notes)
                    st.success(f"✅ Customer '{name}' added successfully.")
                else:
                    st.warning("Name and Email are required.")

    elif menu == "View Customers":
        st.markdown('<div class="main-title">📋 Customer List</div>', unsafe_allow_html=True)
        data = get_all_customers()
        if not data:
            st.info("No customers found.")
        else:
            df = pd.DataFrame(data, columns=["ID", "Name", "Email", "Phone", "Notes"])
            st.dataframe(df, use_container_width=True)

    elif menu == "Search Customer":
        st.markdown('<div class="main-title">🔍 Search Customer</div>', unsafe_allow_html=True)
        term = st.text_input("Search by Name, Email, or Phone")
        if term:
            results = search_customer(term)
            if results:
                df = pd.DataFrame(results, columns=["ID", "Name", "Email", "Phone", "Notes"])
                st.success(f"Found {len(results)} matching customer(s).")
                st.dataframe(df, use_container_width=True)
            else:
                st.warning("No matching customer found.")

    elif menu == "Logout":
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.success("Successfully logged out.")

# --- Main Controller ---
if st.session_state.logged_in:
    crm_dashboard_ui()
else:
    login_register_ui()
