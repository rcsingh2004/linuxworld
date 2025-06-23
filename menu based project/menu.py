import streamlit as st
import webbrowser
import datetime
import calendar
import subprocess
import os
import sys

# Function to open WhatsApp (web version)
def open_whatsapp():
    webbrowser.open("https://web.whatsapp.com/")

# Function to show current date
def show_date():
    today = datetime.date.today()
    st.write(f"Today's date is: {today}")

# Function to show calendar for current month
def show_calendar():
    now = datetime.datetime.now()
    cal = calendar.month(now.year, now.month)
    st.text(cal)

# Function to open camera (platform dependent)
def open_camera():
    import cv2
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.error("Cannot access camera")
        return
    st.write("Press 'q' to close the camera window.")
    while True:
        ret, frame = cap.read()
        if not ret:
            st.error("Failed to grab frame")
            break
        cv2.imshow('Camera', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

# Function to open a website in default browser
def open_website(url):
    webbrowser.open(url)

# Streamlit app layout
st.title("Basic Commands Menu")

menu = ["Open WhatsApp", "Show Date", "Show Calendar", "Open Camera", "Open Browser", "Open YouTube"]
choice = st.selectbox("Select an action:", menu)

if choice == "Open WhatsApp":
    st.button("Open WhatsApp Web", on_click=open_whatsapp)

elif choice == "Show Date":
    if st.button("Show Date"):
        show_date()

elif choice == "Show Calendar":
    if st.button("Show Calendar"):
        show_calendar()

elif choice == "Open Camera":
    st.write("Click the button below to open your camera.")
    if st.button("Open Camera"):
        open_camera()

elif choice == "Open Browser":
    url = st.text_input("Enter URL to open:", value="https://")
    if st.button("Open Website"):
        open_website(url)

elif choice == "Open YouTube":
    if st.button("Open YouTube"):
        open_website("https://www.youtube.com")