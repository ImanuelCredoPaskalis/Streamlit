from urllib import response
from xml.parsers.expat import model
import streamlit as st
from PIL import Image
from streamlit_option_menu import option_menu
import numpy as np
import matplotlib.pyplot as plt
import uuid
import os
import json
import random
import pandas as pd
import base64
import io
import hashlib
import requests

# API CONFIG

API_URL = "https://interseaboard-multimedial-lavera.ngrok-free.dev/v1/chat/completions"
MODEL_NAME = "gemma-4-e4b-uncensored-hauhaucs-aggressive"
def encode_image(image):
    from io import BytesIO

    buffer = BytesIO()
    image.save(buffer, format="PNG")  # bisa ganti JPEG kalau mau
    return base64.b64encode(buffer.getvalue()).decode("utf-8")
def kirim_ke_model(prompt, image=None):
    try:
        if image:
            img_base64 = encode_image(image)

            payload = {
                "model": MODEL_NAME,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{img_base64}"
                                }
                            }
                        ]
                    }
                ]
            }
        else:
            payload = {
                "model": MODEL_NAME,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }

        response = requests.post(API_URL, json=payload)

        if response.status_code != 200:
            return f"Server error: {response.text}"

        data = response.json()
        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"Error: {str(e)}"

# USER DATABASE

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


# SCORE DATABASE

def load_scores():
    try:
        with open("scores.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_scores(data):
    with open("scores.json", "w") as f:
        json.dump(data, f)

SCORES = load_scores()


# SESSION STATE

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "user_id" not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())

if "hasil_analisis" not in st.session_state:
    st.session_state.hasil_analisis = None


# LOGIN / REGISTER

if not st.session_state.logged_in:
    st.title("Masuk / Daftar")

    menu_auth = st.radio("Pilih Menu", ["Masuk", "Daftar"])

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

    else:
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


# SIDEBAR

with st.sidebar:
    st.write(f"Masuk sebagai: {st.session_state.username}")
    
    if st.button("Keluar"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    selected = option_menu(
        "Menu",
        ["Beranda", "Analisis Grafik", "Kalkulator", "Materi", "Latihan Soal", "Pengaturan"],
        icons=["house", "graph-up", "calculator", "book", "pen", "gear"],
        menu_icon="cast",
        default_index=0,
    )
    st.sidebar.markdown("Oleh: Imanuel Credo Paskalis")
    st.sidebar.markdown("Versi: 1.0.0")
    st.sidebar.markdown(
    "<p style='text-align: center; color: grey; opacity: 0.5;'>© 2026 Pendidikan Matematika USD</p>", 
    unsafe_allow_html=True
    )

# BERANDA

if selected == "Beranda":
    st.title("GrafKu")
    st.write("Selamat datang di GrafKu! Aplikasi pembelajaran matematika yang memanfaatkan kecerdasan buatan untuk membantu kamu memahami konsep matematika dengan lebih mudah. Pilih menu di sidebar untuk mulai belajar!")
    st.success("Tujuan Pembelajaran"
               "\n1. Memahami konsep dasar fungsi kuadrat"
               "\n2. Menganalisis grafik fungsi kuadrat")


# ANALISIS GRAFIK (AI)

elif selected == "Analisis Grafik":
    st.title("Analisis Grafik")

    camera_image = st.camera_input("Ambil foto grafik")

    if st.button("Analisis") and camera_image is not None:
        try:
            image = Image.open(camera_image)

            with st.spinner("Memproses..."):
                response = kirim_ke_model(
                    "Jelaskan kesalahan matematika dalam poin dan beri solusi",
                    image
                )
                poin = kirim_ke_model(
                    "Nilai 1-100 untuk kebenaran, angka saja",
                    image
                )
                st.session_state.hasil_analisis = {
                    "teks": str(response),
                    "poin": str(poin)
                }

        except Exception as e:
            st.error(f"Error: {e}")

    # Aman dari None / belum ada data
    if "hasil_analisis" in st.session_state and st.session_state.hasil_analisis:
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


# LATIHAN SOAL (UPGRADE)

elif selected == "Latihan Soal":
    st.title("Latihan Soal")

    bank_soal = [
        {"q": "2 + 3 =", "a": "5"},
        {"q": "5 x 2 =", "a": "10"},
        {"q": "10 - 4 =", "a": "6"},
        {"q": "8 / 2 =", "a": "4"},
        {"q": "3² =", "a": "9"},
        {"q": "√16 =", "a": "4"},
        {"q": "7 + 8 =", "a": "15"},
        {"q": "6 x 6 =", "a": "36"},
    ]

    if "soal_aktif" not in st.session_state:
        st.session_state.soal_aktif = random.sample(bank_soal, 5)

    soal = st.session_state.soal_aktif
    jawaban_user = []

    st.subheader("Jawab soal berikut:")

    for i, s in enumerate(soal):
        jawab = st.text_input(f"Soal {i+1}: {s['q']}", key=f"soal_{i}")
        jawaban_user.append(jawab)

    if st.button("Kumpulkan Jawaban"):
        skor = 0
        hasil = []
        for i, s in enumerate(soal):
            if jawaban_user[i] == s["a"]:
                skor += 20
                hasil.append(1)
            else:
                hasil.append(0)

        st.success(f"Skor kamu: {skor}")

        st.session_state.detail = hasil
        st.session_state.skor = skor

        user = st.session_state.username

        if user not in SCORES:
            SCORES[user] = []

        SCORES[user].append(skor)
        save_scores(SCORES)
        st.session_state.soal_aktif = random.sample(bank_soal, 5)
        st.rerun()

    # Pemberitauan detail jawaban
    if "detail" in st.session_state:
        st.subheader("Hasil Jawaban")
        for i, hasil in enumerate(st.session_state.detail):
            if hasil == 1:
                st.success(f"Soal {i+1}: Jawaban Benar")
            else:
                st.error(f"Soal {i+1}: Jawaban Salah")

    # Uji coba skor
    if st.session_state.username in SCORES:
        st.subheader("Riwayat Nilai")
        data = SCORES[st.session_state.username]
        percobaan = list(range(1, len(data)+1))
        df = pd.DataFrame({"Percobaan ke-": percobaan, "Skor": data})
        st.dataframe(df, hide_index=True)
    if st.button("Reset Riwayat Nilai"):
        if st.session_state.username in SCORES:
            del SCORES[st.session_state.username]
            save_scores(SCORES)
            st.success("Riwayat nilai berhasil direset")
            st.rerun()
elif selected == "Pengaturan":
    st.title("Pengaturan")
    if st.button("Hapus Akun"):
        if st.session_state.username in USERS:
            del USERS[st.session_state.username]
            save_users(USERS)
        if st.session_state.username in SCORES:
            del SCORES[st.session_state.username]
            save_scores(SCORES)
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.success("Akun berhasil dihapus")
        st.rerun()