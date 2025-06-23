import streamlit as st
import sqlite3
import pandas as pd
import hashlib

# --- Database Setup ---
conn = sqlite3.connect('crm.db', check_same_thread=False)
c = conn.cursor()

# Create tables for users and customers
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL
)
''')

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

# Password hashing
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed

# User management
def register_user(username, password):
    c.execute('SELECT * FROM users WHERE username=?', (username,))
    if c.fetchone():
        return False  # User exists
    c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hash_password(password)))
    conn.commit()
    return True

def login_user(username, password):
    c.execute('SELECT * FROM users WHERE username=?', (username,))
    user = c.fetchone()
    if user and verify_password(password, user[1]):
        return True
    return False

# Customer management
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

# --- Streamlit App ---

st.set_page_config(page_title="CRM with Login", page_icon="🔐", layout="centered")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# --- Login/Register ---
def login_register():
    st.title("🔐 CRM Login")

    menu = ["Login", "Register"]
    choice = st.selectbox("Choose an option", menu)

    if choice == "Login":
        st.subheader("Login to CRM")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if login_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success(f"Welcome {username}!")
            else:
                st.error("Invalid username or password")

    elif choice == "Register":
        st.subheader("Register New Account")
        username = st.text_input("Username", key="reg_user")
        password = st.text_input("Password", type="password", key="reg_pass")
        if st.button("Register"):
            if username and password:
                if register_user(username, password):
                    st.success("Account created successfully! Please login.")
                else:
                    st.warning("Username already exists.")
            else:
                st.warning("Please enter both username and password.")

# --- CRM Main App ---
def crm_app():
    st.sidebar.title(f"Welcome, {st.session_state.username} 👋")
    menu = ["Add Customer", "View Customers", "Search Customer", "Logout"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Add Customer":
        st.subheader("➕ Add New Customer")
        with st.form("add_form"):
            name = st.text_input("Full Name")
            email = st.text_input("Email Address")
            phone = st.text_input("Phone Number")
            notes = st.text_area("Notes")
            submit = st.form_submit_button("Add Customer")
            if submit:
                if name and email:
                    add_customer(name, email, phone, notes)
                    st.success(f"Customer '{name}' added successfully!")
                else:
                    st.warning("Name and Email are required.")

    elif choice == "View Customers":
        st.subheader("📄 Customer List")
        data = get_all_customers()
        if not data:
            st.info("No customers in the database.")
        else:
            df = pd.DataFrame(data, columns=["ID", "Name", "Email", "Phone", "Notes"])
            st.dataframe(df)

    elif choice == "Search Customer":
        st.subheader("🔍 Search Customer")
        term = st.text_input("Enter Name, Email, or Phone")
        if term:
            results = search_customer(term)
            if results:
                df = pd.DataFrame(results, columns=["ID", "Name", "Email", "Phone", "Notes"])
                st.success(f"Found {len(results)} matching customer(s).")
                st.dataframe(df)
            else:
                st.warning("No matching customer found.")

    elif choice == "Logout":
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.success("Logged out successfully.")

# --- App Controller ---
if st.session_state.logged_in:
    crm_app()
else:
    login_register()
