import streamlit as st
import datetime
import urllib.request
import json

# Konfigurasi Halaman
st.set_page_config(page_title="Digital Logbook IPAL", layout="wide")

st.title("🎛️ Digital Logbook & EWS IPAL")
st.subheader("RSUD Tanjung Priok - Instalasi Kesehatan Lingkungan (Versi 3.0 Final)")
st.markdown("---")

# ========================================== #
# FORMULIR INPUT OPERATOR (HALAMAN UTAMA)
# ========================================== #
st.header("📝 Form Entry Harian")
st.markdown("Silakan isi data inspeksi lapangan di bawah ini:")

# Menggunakan kolom agar rapi di PC, dan otomatis ke bawah di HP
col_id1, col_id2 = st.columns(2)
with col_id1:
    operator = st.text_input("Nama Operator Pengecek")
    shift = st.selectbox("Shift Kerja", ["Pagi", "Siang", "Malam"])
with col_id2:
    tanggal = st.date_input("Tanggal Inspeksi", datetime.date.today())
    waktu = st.time_input("Waktu (Jam:Menit)", datetime.datetime.now().time())

col_air1, col_air2 = st.columns(2)
with col_air1:
    debit = st.number_input("Debit Flowmeter (m³)", min_value=0.0, value=15.0, step=0.5)
    kekeruhan = st.selectbox("Kekeruhan/TSS (Visual)", ["Bening Jernih", "Sedikit Keruh", "Keruh Pekat / Pin Floc"])
with col_air2:
    ph_inlet = st.number_input("pH Inlet (Air Masuk Ekualisasi)", min_value=0.0, max_value=14.0, value=7.0, step=0.1)
    ph_effluent = st.number_input("pH Effluent (Air Keluar)", min_value=0.0, max_value=14.0, value=7.0, step=0.1)

col_ut1, col_ut2 = st.columns(2)
with col_ut1:
    listrik = st.number_input("Meteran Listrik IPAL (kWh)", min_value=0.0, value=120.0, step=1.0)
    uptime_blower = st.number_input("Uptime Blower (Jam Beroperasi)", min_value=0, max_value=24, value=24)
with col_ut2:
    sisa_klorin = st.number_input("Sisa Klorin Bebas (ppm)", min_value=0.0, max_value=5.0, value=0.2, step=0.1)
    keluhan_warga = st.number_input("Keluhan Warga (Jumlah)", min_value=0, value=0)

# URL Webhook Google Sheets milik Anda
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbx2R3umzNLcD8TmZjiXoUvpYcIWmB4rc6rI0TgzSbFbLoIM7svJ_8lrTryEWOQjtrbR/exec"

# Tombol Submit 
tombol_submit = st.button("💾 SUBMIT DATA LOGBOOK")

if tombol_submit:
    if operator == "":
        st.error("⚠️ Nama Operator wajib diisi sebelum Submit!")
    else:
        # Menyiapkan paket data untuk dikirim ke Google Sheets
        data_to_send = {
            "operator": operator,
            "shift": shift,
            "tanggal": tanggal.strftime("%Y-%m-%d"),
            "waktu": waktu.strftime("%H:%M"),
            "debit": debit,
            "kekeruhan": kekeruhan,
            "ph_inlet": ph_inlet,
            "ph_effluent": ph_effluent,
            "listrik": listrik,
            "uptime_blower": uptime_blower,
            "sisa_klorin": sisa_klorin,
            "keluhan_warga": keluhan_warga
        }
        
        # Proses Pengiriman Data
        try:
            req = urllib.request.Request(WEBHOOK_URL, method="POST")
            req.add_header('Content-Type', 'application/json')
            jsondata = json.dumps(data_to_send).encode('utf-8')
            response = urllib.request.urlopen(req, jsondata)
            
            st.success(f"✅ Berhasil! Laporan atas nama {operator} telah tersimpan permanen di Google Sheets!")
        except Exception as e:
            st.error(f"⚠️ Gagal mengirim data. Error: {e}")

st.markdown("---")

# ========================================== #
# LOGIC: TRAFFIC LIGHT SYSTEM (MESIN ANALISA)
# ========================================== #

# Logic Hulu (Peringatan Dini Ekualisasi)
if 6.0 <= ph_inlet <= 8.0:
    status_inlet = ("🟢 AMAN", "Limbah masuk stabil. Tidak ada indikasi tumpahan B3.")
else:
    status_inlet = ("🔴 BAHAYA", "ALARM! pH Inlet Ekstrem! Bypass aliran sekarang!")

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
    status_klorin = ("🔴 BAHAYA", "Dosis Klorin tidak standar (Berisiko E.coli lolos).")

if uptime_blower == 24:
    status_blower = ("🟢 AMAN", "Suplai oksigen bakteri maksimal.")
else:
    status_blower = ("🔴 BAHAYA", "Blower Trip! Bakteri berisiko mati septik.")

# ========================================== #
# TAMPILAN UTAMA DASHBOARD (KEPALA KESLING)
# ========================================== #
st.header("📊 Dashboard Status EWS")

# Banner Info Update dengan Tanggal
st.info(f"📌 **Laporan Aktif:** Tanggal {tanggal.strftime('%d/%m/%Y')} | Shift {shift} | **Operator:** {operator if operator else 'Belum diisi'} | **Waktu:** {waktu.strftime('%H:%M')} WIB")

col_dash1, col_dash2, col_dash3 = st.columns(3)

with col_dash1:
    st.subheader("🌍 Kualitas Air")
    st.warning(f"**pH Masuk (Inlet):** {ph_inlet}\n\n**Status:** {status_inlet[0]}\n\n*{status_inlet[1]}*")
    st.info(f"**pH Keluar (Efluen):** {ph_effluent}\n\n**Status:** {status_ph_out[0]}\n\n*{status_ph_out[1]}*")
    st.info(f"**Kekeruhan:** {kekeruhan}\n\n**Status:** {status_tss[0]}\n\n*{status_tss[1]}*")

with col_dash2:
    st.subheader("⚙️ Utilitas & Kinerja")
    st.success(f"**Debit Olahan:** {debit} m³")
    st.success(f"**Pemakaian Listrik:** {listrik} kWh")
    st.success(f"**Jam Blower:** {uptime_blower} Jam\n\n**Status:** {status_blower[0]}")

with col_dash3:
    st.subheader("🦠 Indikator PPI & Sosial")
    st.warning(f"**Residu Klorin:** {sisa_klorin} ppm\n\n**Status:** {status_klorin[0]}\n\n*{status_klorin[1]}*")
    if keluhan_warga == 0:
         st.success(f"**Komplain (Bau):** {keluhan_warga}\n\n**Status:** 🟢 AMAN")
    else:
         st.error(f"**Komplain (Bau):** {keluhan_warga}\n\n**Status:** 🔴 BAHAYA")
