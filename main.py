import streamlit as st
from PIL import Image
import google.generativeai as genai
from streamlit_option_menu import option_menu

# SET API KEY
genai.configure(api_key="AIzaSyBkIp9tsKzmGcTzSwky_f7IX19FnYID_is")

# Menu Utama
with st.sidebar:
    selected = option_menu(
        "Menu", ["Beranda", "Analisis Grafik","Kalkulator", "Materi", "Pengaturan"],
        icons=["house", "graph-up", "calculator", "book", "gear"],
        menu_icon="cast", default_index=0,
    )

# Submenu berdasarkan pilihan menu utama
if selected == "Analisis Grafik":
    st.title("Analisis Grafik Fungsi Kuadrat")
    camera_image = st.camera_input("Ambil foto grafik fungsi kuadrat yang ingin dianalisis")
    if camera_image is not None and st.button("Analisis"):
        image = Image.open(camera_image)
        st.subheader("Hasil Analisis:")
        with st.spinner("Analisis sedang berlangsung..."):
            try:
                model = genai.GenerativeModel("gemini-flash-latest")

                response = model.generate_content([
                "jelaskan kesalahan matematika dalam bentuk poin-poin dari foto ini, serta berikan solusi yang benar",
                image
            ])
                poin = model.generate_content(["Berikan Poin 1 sampai 100 untuk tingkat kebenaran dalam analisis foto ini, berikan poin angka saja tanpa deskripsi", image])
                st.write(response.text)
                st.write("Tingkat Kebenaran:", poin.text)
                st.success("Analisis selesai! Semoga membantu.")
            except Exception as e:
                st.error(f"Error: {e}")

elif selected == "Beranda":
    st.title("Selamat Datang di Aplikasi Analisis Grafik Fungsi Kuadrat")
    st.write("Gunakan menu di sebelah kiri untuk mulai menganalisis grafik fungsi kuadrat Anda.")

elif selected == "Pengaturan":
    st.title("Pengaturan")
    st.write("Pengaturan aplikasi akan ditampilkan di sini.")

elif selected == "Kalkulator":
    st.title("Kalkulator Fungsi Kuadrat")
    st.write("Fitur kalkulator akan ditampilkan di sini.")

elif selected == "Materi":
    st.title("Materi Pembelajaran")
    st.write("Materi pembelajaran akan ditampilkan di sini.")