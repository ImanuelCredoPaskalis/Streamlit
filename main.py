import streamlit as st
from io import BytesIO
from streamlit_option_menu import option_menu
import numpy as np
import matplotlib.pyplot as plt
import uuid
import json
import random
import pandas as pd
import base64
import requests
from PIL import Image, ImageEnhance, ImageFilter
# PROMPT ANALISIS GRAFIK
PROMPT = """
Lihat gambar dengan teliti.
1. Baca angka dan persamaan yang terlihat.
2. Tentukan titik puncak grafik.
3. Tentukan arah buka parabola.
4. Cocokkan grafik dengan persamaan.
5. Sebutkan kesalahan utama dan kesalahan detil mulai dari tata cara penggambaran grafik.
Jawaban singkat.
Format:
Analisis: ...
Poin: .../100
"""
API_URL = "http://127.0.0.1:1234/v1/chat/completions"
MODEL_NAME = "qwen/qwen3-vl-8b"

def preprocess(img):
    img = img.convert("L")  # grayscale
    img = ImageEnhance.Contrast(img).enhance(2.0)
    img = img.filter(ImageFilter.SHARPEN)
    img.thumbnail((1024,1024))
    return img
def encode_image(image):
    buffer = BytesIO()
    image.save(buffer, format="PNG") 
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
        msg = data.get("choices", [{}])[0].get("message", {})
        content = msg.get("content")
        return str(content)
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
    menu_auth = st.radio("Pilih Menu", ["Masuk", "Daftar"], horizontal=True)
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
        ["Beranda", "Analisis Grafik", "Kalkulator Grafik", "Materi", "Latihan Soal", "Pengaturan"],
        icons=["house", "graph-up", "calculator", "book", "pen", "gear"],
        menu_icon="cast",
        default_index=0,
    )
    st.sidebar.markdown("Oleh: Imanuel Credo Paskalis")
    st.sidebar.markdown(f"Model AI: qwen3")
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
    st.title("Analisis Grafik Fungsi Kuadrat")

    # state
    if "proses_analisis" not in st.session_state:
        st.session_state.proses_analisis = False
    if "hasil_analisis" not in st.session_state:
        st.session_state.hasil_analisis = None
    if "gambar_cache" not in st.session_state:
        st.session_state.gambar_cache = None
    pilihan = st.radio(
        "Pilih sumber gambar:",
        ["Upload Gambar", "Gunakan Kamera"], horizontal=True, label_visibility="collapsed"
    )
    camera_image = None
    if pilihan == "Upload Gambar":
        camera_image = st.file_uploader(
        "Upload foto grafik",
        type=["png", "jpg", "jpeg"]
    )
    if camera_image is not None:
        st.image(
            camera_image,
            caption="Preview",
            use_container_width=True
        )
    elif pilihan == "Gunakan Kamera":
        camera_image = st.camera_input("Ambil foto grafik")

    if st.button("Analisis Grafik"):
        if camera_image is None:
            st.warning("Masukkan gambar dulu")
        else:
            st.session_state.gambar_cache = camera_image
            st.session_state.proses_analisis = True
            st.session_state.hasil_analisis = None
            st.rerun()
    # proses analisis
    if st.session_state.proses_analisis:
        try:
            image = Image.open(st.session_state.gambar_cache)
            image = preprocess(image)

            with st.spinner("Memproses gambar..."):
                response = kirim_ke_model(PROMPT, image)

            st.session_state.hasil_analisis = response
            st.session_state.proses_analisis = False
            st.rerun()

        except Exception as e:
            st.session_state.proses_analisis = False
            st.error(f"Error: {e}")
    # tampilkan hasil
    if st.session_state.hasil_analisis:
        st.subheader("Hasil Analisis")
        st.write(st.session_state.hasil_analisis)
    # tombol reset
    if st.button("Reset Hasil"):
        st.session_state.hasil_analisis = None
        st.session_state.gambar_cache = None
        st.session_state.proses_analisis = False
        st.rerun()
# KALKULATOR

elif selected == "Kalkulator Grafik":
    st.title("Kalkulator Fungsi Kuadrat")
    a = st.number_input("Koefisien x²", value=1)
    b = st.number_input("Koefisien x", value=0)
    c = st.number_input("Konstanta", value=0)
    fungsi = f"f(x) = {a}x² + {b}x + {c}"
    if st.button("Buat Grafik"):
        if a == 0:
            x = np.linspace(-10, 10, 400)
            y = a*x**2 + b*x + c
            fig, ax = plt.subplots()
            ax.plot(x, y)
            ax.set_xlim(-10,10)
            ax.set_ylim(-10,10)
            ax.set_xticks(np.arange(-10, 11, 1))
            ax.set_yticks(np.arange(-10, 11, 1))
            ax.axhline(0, linestyle='--')
            ax.axvline(0, linestyle='--')
            ax.set_title(f"Grafik {fungsi}")
            ax.grid()
            st.pyplot(fig)
        else:
            x = np.linspace(-10, 10, 400)
            y = a*x**2 + b*x + c
            xp = -b/(2*a)
            yp = c - b**2/(4*a)
            fig, ax = plt.subplots()
            ax.scatter(xp, yp, color="black", s=100, marker=".", zorder=5)
            ax.text(xp, yp-2, f"Titik Puncak\n({xp:.2f}, {yp:.2f})", ha='center', va='bottom', fontsize=9, color='black')
            ax.plot(x, y)
            ax.set_xlim(-10,10)
            ax.set_ylim(-10,10)
            ax.set_xticks(np.arange(-10, 11, 1))
            ax.set_yticks(np.arange(-10, 11, 1))
            ax.axhline(0, linestyle='--')
            ax.axvline(0, linestyle='--')
            ax.set_title(f"Grafik {fungsi}")
            ax.grid()
            st.pyplot(fig)
            st.success(f"Arah buka parabola: {'ke atas' if a > 0 else 'ke bawah'}")
# MATERI
elif selected == "Materi":
    st.title("Materi")
    st.write("Pilih materi yang ingin dipelajari")
    # simpan halaman aktif
    if "halaman_materi" not in st.session_state:
        st.session_state.halaman_materi = "home"
    if st.session_state.halaman_materi == "home":
        materi = [
            ("Menggambar Grafik Fungsi Kuadrat", "Cara menggambar grafik fungsi kuadrat dengan mudah.", "kuadrat"),
            ("Menganalisis Grafik Fungsi Kuadrat", "Cara menganalisis grafik fungsi kuadrat untuk memahami sifat-sifatnya.", "analisis"),
            ("Operasi Bentuk Aljabar", "Cara melakukan operasi aljabar pada fungsi kuadrat untuk menyelesaikan masalah.", "operasi")
        ]
        cols = st.columns(3)
        for i, item in enumerate(materi):
            judul, desc, key_page = item
            with cols[i % 3]:
                with st.container(border=True):
                    st.subheader(judul)
                    st.write(desc)
                    for _ in range(2):
                        st.write("")
                    if st.button(
                        "Buka Materi",
                        key=f"btn_{key_page}",
                        use_container_width=True
                    ):
                        st.session_state.halaman_materi = key_page
                        st.rerun()

    else:

        if st.button("Kembali", use_container_width=True):
            st.session_state.halaman_materi = "home"
            st.rerun()

        page = st.session_state.halaman_materi

        if page == "kuadrat":
            st.header("Menggambar Grafik Fungsi Kuadrat")


        elif page == "analisis":
            st.header("Menganalisis Grafik Fungsi Kuadrat")


        elif page == "operasi":
            st.header("Operasi Bentuk Aljabar")


# LATIHAN SOAL (contoh soal sederhana, bisa dikembangkan lagi)

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