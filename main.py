import streamlit as st
from PIL import Image
import google.generativeai as genai
from streamlit_option_menu import option_menu
import numpy as np
import matplotlib.pyplot as plt
import uuid
import os
import json


# API CONFIG

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


# LOAD & SAVE USER (JSON)

def load_users():
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f)

USERS = load_users()


# SESSION STATE

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

if "hasil_analisis" not in st.session_state:
    st.session_state.hasil_analisis = None

if "tema" not in st.session_state:
    st.session_state.tema = "Light"


# LOGIN & REGISTER

if not st.session_state.logged_in:
    st.title("Masuk / Daftar")

    menu_auth = st.radio("Pilih Menu", ["Masuk", "Daftar"])

    # LOGIN
    if menu_auth == "Masuk":
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Masuk"):
            if username in USERS and USERS[username] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Login berhasil")
                st.rerun()
            else:
                st.error("Username atau password salah")

    # REGISTER
    elif menu_auth == "Daftar":
        new_user = st.text_input("Username Baru")
        new_pass = st.text_input("Password Baru", type="password")
        confirm_pass = st.text_input("Konfirmasi Password", type="password")

        if st.button("Daftar"):
            if new_user in USERS:
                st.warning("Username sudah digunakan")
            elif new_pass != confirm_pass:
                st.warning("Password tidak sama")
            elif new_user == "" or new_pass == "":
                st.warning("Tidak boleh kosong")
            else:
                USERS[new_user] = new_pass
                save_users(USERS)
                st.success("Registrasi berhasil! Silakan login.")

    st.stop()


# TEMA

if st.session_state.tema == "Dark":
    st.markdown("""
        <style>
        body {background-color: #0E1117; color: white;}
        </style>
    """, unsafe_allow_html=True)


# SIDEBAR

with st.sidebar:
    st.write(f"Login sebagai: {st.session_state.username}")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    selected = option_menu(
        "Menu",
        ["Beranda", "Analisis Grafik", "Kalkulator", "Materi", "Pengaturan"],
        icons=["house", "graph-up", "calculator", "book", "gear"],
        menu_icon="cast",
        default_index=0,
    )


# BERANDA

if selected == "Beranda":
    st.title("Aplikasi Analisis Grafik Fungsi Kuadrat")
    st.write("Gunakan menu di kiri untuk mulai.")


# ANALISIS GRAFIK

elif selected == "Analisis Grafik":
    st.title("Analisis Grafik")

    camera_image = st.camera_input("Ambil foto grafik")

    if st.button("Analisis") and camera_image is not None:
        image = Image.open(camera_image)

        with st.spinner("Memproses..."):
            try:
                model = genai.GenerativeModel("gemini-flash-latest")

                response = model.generate_content([
                    "Jelaskan kesalahan matematika dalam poin dan beri solusi",
                    image
                ])

                poin = model.generate_content([
                    "Nilai 1-100 untuk kebenaran, angka saja",
                    image
                ])

                st.session_state.hasil_analisis = {
                    "teks": response.text,
                    "poin": poin.text
                }

            except Exception as e:
                st.error(f"Error: {e}")

    if st.session_state.hasil_analisis:
        st.subheader("Hasil:")
        st.write(st.session_state.hasil_analisis["teks"])
        st.write("Nilai:", st.session_state.hasil_analisis["poin"])


# KALKULATOR

elif selected == "Kalkulator":
    st.title("Kalkulator Fungsi Kuadrat")

    a = st.number_input("Koefisien x²", value=1)
    b = st.number_input("Koefisien x", value=0)
    c = st.number_input("Konstanta", value=0)

    st.write(f"f(x) = {a}x² + {b}x + {c}")

    if st.button("Buat Grafik"):
        x = np.linspace(-10, 10, 400)
        y = a*x**2 + b*x + c

        fig, ax = plt.subplots()
        ax.plot(x, y)
        ax.axhline(0, linestyle='--')
        ax.axvline(0, linestyle='--')
        ax.set_title("Grafik Fungsi Kuadrat")
        ax.grid()

        st.pyplot(fig)


# MATERI

elif selected == "Materi":
    st.title("Materi")
    st.write("Materi akan ditambahkan.")


# PENGATURAN

elif selected == "Pengaturan":
    st.title("Pengaturan")

    tema = st.selectbox("Pilih Tema", ["Light", "Dark"])
    st.session_state.tema = tema

    st.success(f"Tema aktif: {tema}")