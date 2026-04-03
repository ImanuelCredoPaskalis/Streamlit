import streamlit as st
from PIL import Image
import google.generativeai as genai

# SET API KEY
genai.configure(api_key="AIzaSyA32kG6VNkHJPJSiHqVszROEQlDV-KHqMo")

st.title("📸 AI Camera Analyzer (Gemini Version, Lebih Hemat)")

camera_image = st.camera_input("Ambil foto")

if camera_image is not None:
    image = Image.open(camera_image)
    st.image(image, caption="📷 Hasil Foto", use_column_width=True)

    st.subheader("🧠 Analisis AI (Gemini)")

    with st.spinner("AI lagi mikir... santai dia, gratis soalnya"):
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
