import streamlit as st
from PIL import Image
import google.generativeai as genai

# SET API KEY
genai.configure(api_key="AIzaSyCpPSgC2RBk3rxS-P4R4FXYJI2pXQcuhCA")

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
