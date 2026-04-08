import streamlit as st
import datetime

# Konfigurasi Halaman
st.set_page_config(page_title="Digital Logbook IPAL", layout="wide")

st.title("🎛️ Digital Logbook & EWS IPAL")
st.subheader("RSUD Tanjung Priok - Instalasi Kesehatan Lingkungan (Versi 2.0)")
st.markdown("---")

# ========================================== #
# SIDEBAR: FORMULIR INPUT OPERATOR (KIRI)
# ========================================== #
st.sidebar.header("📝 Form Entry Harian")

# Blok 1: Identitas
st.sidebar.markdown("**1. Identitas & Waktu**")
operator = st.sidebar.text_input("Nama Operator Pengecek")
tanggal = st.sidebar.date_input("Tanggal Inspeksi", datetime.date.today())
waktu = st.sidebar.time_input("Waktu (Jam:Menit)", datetime.datetime.now().time())
shift = st.sidebar.selectbox("Shift Kerja", ["Pagi", "Siang", "Malam"])

st.sidebar.markdown("---")

# Blok 2: Kualitas Air
st.sidebar.markdown("**2. Kualitas Air & Proses**")
debit = st.sidebar.number_input("Debit Flowmeter (m³)", min_value=0.0, value=15.0, step=0.5)
ph_inlet = st.sidebar.number_input("pH Inlet (Air Masuk Ekualisasi)", min_value=0.0, max_value=14.0, value=7.0, step=0.1)
ph_effluent = st.sidebar.number_input("pH Effluent (Air Keluar)", min_value=0.0, max_value=14.0, value=7.0, step=0.1)
kekeruhan = st.sidebar.selectbox("Kekeruhan/TSS (Visual)", ["Bening Jernih", "Sedikit Keruh", "Keruh Pekat / Pin Floc"])

st.sidebar.markdown("---")

# Blok 3: Utilitas
st.sidebar.markdown("**3. Utilitas & Sosial**")
listrik = st.sidebar.number_input("Meteran Listrik IPAL (kWh)", min_value=0.0, value=120.0, step=1.0)
sisa_klorin = st.sidebar.number_input("Sisa Klorin Bebas (ppm)", min_value=0.0, max_value=5.0, value=0.2, step=0.1)
uptime_blower = st.sidebar.number_input("Uptime Blower (Jam Beroperasi)", min_value=0, max_value=24, value=24)
keluhan_warga = st.sidebar.number_input("Keluhan Warga (Jumlah)", min_value=0, value=0)

st.sidebar.markdown("---")
# Tombol Submit (Persiapan untuk integrasi Google Sheets di Versi 3.0)
tombol_submit = st.sidebar.button("💾 SUBMIT DATA LOGBOOK")

if tombol_submit:
    if operator == "":
        st.sidebar.error("⚠️ Nama Operator wajib diisi sebelum Submit!")
    else:
        st.sidebar.success(f"Data milik {operator} siap dikirim! (Integrasi Database segera hadir)")

# ========================================== #
# LOGIC: TRAFFIC LIGHT SYSTEM (MESIN ANALISA)
# ========================================== #

# Logic Hulu (Peringatan Dini Ekualisasi)
if 6.0 <= ph_inlet <= 8.0:
    status_inlet = ("🟢 AMAN", "Limbah masuk stabil. Tidak ada indikasi tumpahan kimia berat.")
else:
    status_inlet = ("🔴 BAHAYA", "ALARM! pH Inlet Ekstrem! Bypass aliran sekarang untuk selamatkan bakteri!")

# Logic Hilir (Efluen)
if 6.0 <= ph_effluent <= 8.0:
    status_ph_out = ("🟢 AMAN", "pH buangan sesuai baku mutu.")
else:
    status_ph_out = ("🔴 BAHAYA", "pH buangan melanggar baku mutu.")

if kekeruhan == "Bening Jernih":
    status_tss = ("🟢 AMAN", "Flok bakteri sehat, pengendapan sempurna.")
else:
    status_tss = ("🔴 BAHAYA", "Indikasi bakteri mati (Wash-out). Periksa MLSS!")

# Logic PPI & Utilitas
if 0.1 <= sisa_klorin <= 0.5:
    status_klorin = ("🟢 AMAN", "Dosis disinfektan pas. Patogen mati.")
else:
    status_klorin = ("🔴 BAHAYA", "Dosis Klorin tidak standar (Berisiko E.coli lolos / Meracuni sungai).")

if uptime_blower == 24:
    status_blower = ("🟢 AMAN", "Suplai oksigen bakteri maksimal.")
else:
    status_blower = ("🔴 BAHAYA", "Blower Trip! Bakteri berisiko mati septik.")


# ========================================== #
# TAMPILAN UTAMA DASHBOARD (KEPALA KESLING)
# ========================================== #

st.info(f"📌 **Laporan Aktif:** Shift {shift} | **Operator:** {operator if operator else 'Belum diisi'} | **Waktu:** {waktu.strftime('%H:%M')} WIB")

col1, col2, col3 = st.columns(3)

with col1:
    st.header("🌍 Kualitas Air")
    st.warning(f"**pH Masuk (Inlet):** {ph_inlet}\n\n**Status:** {status_inlet[0]}\n\n*{status_inlet[1]}*")
    st.info(f"**pH Keluar (Efluen):** {ph_effluent}\n\n**Status:** {status_ph_out[0]}\n\n*{status_ph_out[1]}*")
    st.info(f"**Kekeruhan:** {kekeruhan}\n\n**Status:** {status_tss[0]}\n\n*{status_tss[1]}*")

with col2:
    st.header("⚙️ Utilitas & Kinerja")
    st.success(f"**Debit Olahan:** {debit} m³")
    st.success(f"**Pemakaian Listrik:** {listrik} kWh")
    st.success(f"**Jam Blower:** {uptime_blower} Jam\n\n**Status:** {status_blower[0]}")

with col3:
    st.header("🦠 Indikator PPI & Sosial")
    st.warning(f"**Residu Klorin:** {sisa_klorin} ppm\n\n**Status:** {status_klorin[0]}\n\n*{status_klorin[1]}*")
    if keluhan_warga == 0:
         st.success(f"**Komplain (Bau):** {keluhan_warga}\n\n**Status:** 🟢 AMAN")
    else:
         st.error(f"**Komplain (Bau):** {keluhan_warga}\n\n**Status:** 🔴 BAHAYA")
