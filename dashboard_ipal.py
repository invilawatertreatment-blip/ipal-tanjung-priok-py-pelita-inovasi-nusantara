import streamlit as st
from datetime import date

# Konfigurasi Halaman
st.set_page_config(page_title="Dashboard IPAL RSUD Tanjung Priok", layout="wide")

# Judul Utama
st.title("🎛️ EWS & Dashboard Monitoring IPAL")
st.subheader("RSUD Tanjung Priok - Instalasi Kesehatan Lingkungan")
st.markdown("---")

# ========================================== #
# SIDEBAR: FORMULIR INPUT OPERATOR (KIRI)
# ========================================== #
st.sidebar.header("📝 Form Entry Harian (Operator)")
st.sidebar.markdown("Masukkan data dari logsheet lapangan ke sini:")

tanggal = st.sidebar.date_input("Tanggal Pengecekan", date.today())
ph_effluent = st.sidebar.number_input("pH Effluent (Air Keluar)", min_value=0.0, max_value=14.0, value=7.0, step=0.1)
kekeruhan = st.sidebar.selectbox("Kekeruhan/TSS (Visual)", ["Bening Jernih", "Sedikit Keruh", "Keruh Pekat / Pin Floc"])
sisa_klorin = st.sidebar.number_input("Sisa Klorin Bebas (ppm)", min_value=0.0, max_value=5.0, value=0.2, step=0.1)
uptime_blower = st.sidebar.number_input("Uptime Blower (Jam Beroperasi)", min_value=0, max_value=24, value=24)
keluhan_warga = st.sidebar.number_input("Keluhan Warga (Jumlah)", min_value=0, value=0)

# ========================================== #
# LOGIC: TRAFFIC LIGHT SYSTEM (MESIN ANALISA)
# ========================================== #

# 1. Logic Mutu Lingkungan
if 6.0 <= ph_effluent <= 8.0:
    status_ph = ("🟢 AMAN", "pH dalam rentang baku mutu (6-8).")
else:
    status_ph = ("🔴 BAHAYA", "pH EKSTREM! Periksa kebocoran B3 di Lab/Farmasi.")

if kekeruhan == "Bening Jernih":
    status_tss = ("🟢 AMAN", "Flok bakteri sehat, pengendapan sempurna.")
else:
    status_tss = ("🔴 BAHAYA", "Indikasi bakteri mati (Wash-out). Hentikan pembuangan!")

# 2. Logic Pencegahan & Pengendalian Infeksi (PPI)
if 0.1 <= sisa_klorin <= 0.5:
    status_klorin = ("🟢 AMAN", "Dosis disinfektan pas. Patogen mati, sungai aman.")
elif sisa_klorin < 0.1:
    status_klorin = ("🟡 WASPADA", "Dosis terlalu rendah! E.coli berisiko lolos.")
else:
    status_klorin = ("🔴 BAHAYA", "Overdosis Klorin! Meracuni ekosistem buangan.")

# 3. Logic Efisiensi & Utilitas
if uptime_blower == 24:
    status_blower = ("🟢 AMAN", "Suplai oksigen bakteri maksimal.")
else:
    status_blower = ("🔴 BAHAYA", "Blower Trip! Bakteri berisiko mati septik.")

if keluhan_warga == 0:
    status_sosial = ("🟢 AMAN", "Nihil komplain bau H2S/Amonia.")
else:
    status_sosial = ("🔴 BAHAYA", f"Ada {keluhan_warga} komplain! Potensi sidak DLH.")


# ========================================== #
# TAMPILAN UTAMA DASHBOARD (KEPALA KESLING)
# ========================================== #

col1, col2, col3 = st.columns(3)

with col1:
    st.header("🌍 Blok 1: Mutu Lingkungan")
    st.info(f"**pH Efluen Akhir:** {ph_effluent}\n\n**Status:** {status_ph[0]}\n\n*Analisa: {status_ph[1]}*")
    st.info(f"**Visual Kekeruhan:** {kekeruhan}\n\n**Status:** {status_tss[0]}\n\n*Analisa: {status_tss[1]}*")

with col2:
    st.header("🦠 Blok 2: Indikator PPI")
    st.warning(f"**Residu Klorin:** {sisa_klorin} ppm\n\n**Status:** {status_klorin[0]}\n\n*Analisa: {status_klorin[1]}*")

with col3:
    st.header("⚙️ Blok 3: Utilitas & Sosial")
    st.success(f"**Jam Operasional Blower:** {uptime_blower} Jam\n\n**Status:** {status_blower[0]}\n\n*Analisa: {status_blower[1]}*")
    st.error(f"**Komplain Warga (Bau):** {keluhan_warga}\n\n**Status:** {status_sosial[0]}\n\n*Analisa: {status_sosial[1]}*")
