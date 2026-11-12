import streamlit as st

st.set_page_config(page_title="Profile Peserta", page_icon="🧑‍💼", layout="centered")

st.title("Profile Peserta")

nama = st.text_input("Siapa nama Anda?")
if nama:
    st.success(f"Selamat datang di pelatihan dashboard, {nama}!")

divisi = st.selectbox("Divisi", ["HR", "IT", "Finance", "Marketing", "Operasional"])
tahun_pengalaman = st.slider("Tahun pengalaman", min_value=0, max_value=40, value=1, step=1)

if nama:
    st.info(f"**{nama}** — Divisi {divisi}, pengalaman {tahun_pengalaman} tahun")
else:
    st.caption("Isi nama Anda untuk melihat ringkasan profil.")
