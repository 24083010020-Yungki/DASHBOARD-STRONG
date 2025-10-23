# ============================================================
# 🌟 DASHBOARD SURVEI FASILITAS KANTIN KAMPUS (Versi Final Otomatis)
# ============================================================

import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# -----------------------------------
# 🔹 Konfigurasi Halaman
# -----------------------------------
st.set_page_config(
    page_title="DASHBOARD ANALISIS FASILITAS KANTIN UPN VETERAN JAWA TIMUR",
    page_icon="🍽️",
    layout="wide"
)

# -----------------------------------
# 🔹 CSS Kustom (Tema Biru Elegan)
# -----------------------------------
st.markdown("""
<style>
    .main-title {
        background: linear-gradient(to right, #0a3d62, #3c6382);
        color: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        font-size: 28px;
        font-weight: bold;
        letter-spacing: 0.5px;
    }
    .stat-card {
        background-color: #f0f4f8;
        padding: 15px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.1);
    }
    .stat-number {
        font-size: 28px;
        font-weight: bold;
        color: #0a3d62;
    }
    .stat-label {
        font-size: 14px;
        color: #3c6382;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------
# 🔹 Header Formal
# -----------------------------------
st.markdown('<div class="main-title">🍽️ DASHBOARD ANALISIS FASILITAS KANTIN KAMPUS</div>', unsafe_allow_html=True)

# -----------------------------------
# 🔹 Load Data
# -----------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("Responden_EDA_Kel1_Rapi.csv", sep=";", engine="python")
    df.columns = df.columns.str.strip()
    return df

data = load_data()

# -----------------------------------
# 🔹 Bersihkan Kolom Fakultas & Prodi
# -----------------------------------
data.columns = data.columns.str.strip()
if "Fakultas" in data.columns:
    data["Fakultas"] = data["Fakultas"].astype(str).str.strip().str.title()
if "Prodi" in data.columns:
    data["Prodi"] = data["Prodi"].astype(str).str.strip().str.title()

# -----------------------------------
# 🔹 Sidebar Filter
# -----------------------------------
st.sidebar.header("🎚️ Filter Data")

Fakultas_opt = ["Semua"] + sorted(data["Fakultas"].dropna().unique().tolist())
Fakultas = st.sidebar.selectbox("Pilih Fakultas", Fakultas_opt)

if Fakultas != "Semua":
    prodi_opt = ["Semua"] + sorted(data[data["Fakultas"] == Fakultas]["Prodi"].dropna().unique().tolist())
else:
    prodi_opt = ["Semua"] + sorted(data["Prodi"].dropna().unique().tolist())
Prodi = st.sidebar.selectbox("Pilih Prodi", prodi_opt)

filtered = data.copy()
if Fakultas != "Semua":
    filtered = filtered[filtered["Fakultas"] == Fakultas]
if Prodi != "Semua":
    filtered = filtered[filtered["Prodi"] == Prodi]

# -----------------------------------
# 🔹 Identifikasi Kolom Numerik & Teks Secara Otomatis
# -----------------------------------
numeric_cols = []
text_cols = []

for col in filtered.columns:
    if col in ["Fakultas", "Prodi"]:
        continue
    # Coba ubah ke numerik, kalau banyak berhasil, anggap numerik
    converted = pd.to_numeric(filtered[col], errors="coerce")
    ratio_numeric = converted.notna().mean()
    if ratio_numeric > 0.8:
        numeric_cols.append(col)
        filtered[col] = converted
    else:
        text_cols.append(col)

# -----------------------------------
# 🔹 Sidebar Navigasi
# -----------------------------------
menu = st.sidebar.radio(
    "📂 Pilih Halaman",
    ["📊 Ringkasan Statistik", "🔵 Analisis Korelasi", "📈 Visualisasi", "🗣️ Analisis Teks"]
)

# -----------------------------------
# 🧾 CARD RINGKAS
# -----------------------------------
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"<div class='stat-card'><div class='stat-number'>{len(filtered)}</div><div class='stat-label'>Total Responden</div></div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='stat-card'><div class='stat-number'>{filtered['Fakultas'].nunique()}</div><div class='stat-label'>Fakultas Terlibat</div></div>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<div class='stat-card'><div class='stat-number'>{filtered['Prodi'].nunique()}</div><div class='stat-label'>Program Studi</div></div>", unsafe_allow_html=True)

st.markdown("---")

# -----------------------------------
# 📊 RINGKASAN STATISTIK
# -----------------------------------
if menu == "📊 Ringkasan Statistik":
    st.subheader("📊 Ringkasan Statistik Tiap Pertanyaan Skala (1–5)")
    if numeric_cols:
        st.dataframe(
            filtered[numeric_cols].describe().T.style.background_gradient(cmap="Blues"),
            use_container_width=True
        )
    else:
        st.info("Tidak ada kolom numerik yang dapat ditampilkan.")

# -----------------------------------
# 🔵 ANALISIS KORELASI
# -----------------------------------
elif menu == "🔵 Analisis Korelasi":
    st.subheader("🔵 Korelasi Pearson Antar Variabel Skala 1–5")
    if len(numeric_cols) > 1:
        corr = filtered[numeric_cols].corr(method="pearson")
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(corr, annot=True, cmap="coolwarm", linewidths=0.5)
        st.pyplot(fig)
    else:
        st.warning("Data numerik tidak cukup untuk analisis korelasi.")

# -----------------------------------
# 📈 VISUALISASI
# -----------------------------------
elif menu == "📈 Visualisasi":
    st.subheader("📈 Visualisasi Skala & Frekuensi Penggunaan Kantin")

    if numeric_cols:
        mean_scores = filtered[numeric_cols].mean().sort_values(ascending=False)
        st.markdown("#### 🔹 Rata-Rata Skor Tiap Pertanyaan")
        st.bar_chart(mean_scores)

    st.markdown("#### 🥧 Frekuensi Penggunaan Kantin")
    col_name = "Seberapa sering menggunakan fasilitas kantin"
    if col_name in filtered.columns:
        pie_data = filtered[col_name].value_counts()
        if not pie_data.empty:
            fig, ax = plt.subplots()
            ax.pie(pie_data.values, labels=pie_data.index, autopct="%1.1f%%", startangle=90)
            ax.axis("equal")
            st.pyplot(fig)

    # Rata-rata skor per fakultas
    if "Fakultas" in filtered.columns and numeric_cols:
        st.markdown("#### 📈 Rata-Rata Skor Keseluruhan per Fakultas")
        mean_by_faculty = filtered.groupby("Fakultas")[numeric_cols].mean().mean(axis=1).sort_values(ascending=False)
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.barplot(x=mean_by_faculty.values, y=mean_by_faculty.index, palette="Blues_r", ax=ax)
        ax.set_xlabel("Rata-rata Skor Keseluruhan")
        ax.set_ylabel("Fakultas")
        st.pyplot(fig)

# -----------------------------------
# 🗣️ ANALISIS TEKS
# -----------------------------------
elif menu == "🗣️ Analisis Teks":
    st.subheader("🗣️ Analisis Jawaban Teks Responden")

    if text_cols:
        for col in text_cols:
            st.markdown(f"#### 📝 {col}")
            vc = filtered[col].value_counts().head(10)
            if not vc.empty:
                st.bar_chart(vc)
            else:
                st.info("Tidak ada data teks untuk kolom ini.")
    else:
        st.info("Tidak ada kolom teks yang dapat ditampilkan.")

# -----------------------------------
# ⚙️ FOOTER FORMAL
# -----------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#666; font-size:13px; padding-top:10px;">
© 2025 UPN "Veteran" Jawa Timur<br>
Dashboard Analisis Fasilitas Kantin Kampus<br>
Dibuat oleh <b>Kelompok STRONG</b>
</div>
""", unsafe_allow_html=True)

