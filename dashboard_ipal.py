import streamlit as st
import datetime
import urllib.request
import json
import pandas as pd
import altair as alt

# Konfigurasi Halaman
st.set_page_config(page_title="Digital Logbook IPAL", layout="wide")

st.title("🎛️ Digital Logbook & EWS IPAL")
st.subheader("RSUD Tanjung Priok - Instalasi Kesehatan Lingkungan (Versi 3.2 - Analytics)")
st.markdown("---")

# ========================================== #
# FORMULIR INPUT OPERATOR
# ========================================== #
st.header("📝 Form Entry Harian")

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
    ph_inlet = st.number_input("pH Inlet (Air Masuk)", min_value=0.0, max_value=14.0, value=7.0, step=0.1)
    ph_effluent = st.number_input("pH Effluent (Air Keluar)", min_value=0.0, max_value=14.0, value=7.0, step=0.1)

col_bio1, col_bio2 = st.columns(2)
with col_bio1:
    do_aerasi = st.number_input("DO Aerasi (mg/L)", min_value=0.0, max_value=10.0, value=2.0, step=0.1)
    mlss = st.number_input("MLSS Bakteri (mg/L)", min_value=0, value=3000, step=100)
    uptime_blower = st.number_input("Uptime Blower (Jam)", min_value=0, max_value=24, value=24)
with col_bio2:
    listrik = st.number_input("Meteran Listrik IPAL (kWh)", min_value=0.0, value=120.0, step=1.0)
    sisa_klorin = st.number_input("Sisa Klorin Bebas (ppm)", min_value=0.0, max_value=5.0, value=0.2, step=0.1)
    keluhan_warga = st.number_input("Keluhan Warga", min_value=0, value=0)

WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbzS9HDRvge_k8AA6TWIla-m6D-RWUZXG-uMEuwsND78UYXxFzUMLQpzTK0XFjafa2Y/exec"

tombol_submit = st.button("💾 SUBMIT DATA LOGBOOK")

if tombol_submit:
    if operator == "":
        st.error("⚠️ Nama Operator wajib diisi sebelum Submit!")
    else:
        data_to_send = {
            "operator": operator, "shift": shift, "tanggal": tanggal.strftime("%Y-%m-%d"),
            "waktu": waktu.strftime("%H:%M"), "debit": debit, "kekeruhan": kekeruhan,
            "ph_inlet": ph_inlet, "ph_effluent": ph_effluent, "listrik": listrik,
            "uptime_blower": uptime_blower, "sisa_klorin": sisa_klorin,
            "keluhan_warga": keluhan_warga, "do_aerasi": do_aerasi, "mlss": mlss
        }
        try:
            req = urllib.request.Request(WEBHOOK_URL, method="POST")
            req.add_header('Content-Type', 'application/json')
            jsondata = json.dumps(data_to_send).encode('utf-8')
            response = urllib.request.urlopen(req, jsondata)
            st.success(f"✅ Berhasil! Laporan atas nama {operator} telah tersimpan di Google Sheets!")
        except Exception as e:
            st.error(f"⚠️ Gagal mengirim data. Error: {e}")

st.markdown("---")

# ========================================== #
# GRAFIK ANALITIK (TRENDLINES)
# ========================================== #
st.header("📈 Analitika Tren Parameter Utama")
st.markdown("*Grafik menampilkan simulasi riwayat 7 hari terakhir digabungkan dengan **input real-time Anda hari ini**. Area hijau adalah Batas Aman (Baku Mutu).*")

# Fungsi pembuat grafik dengan batas aman
def buat_grafik(nilai_sekarang, riwayat, judul, nama_y, min_aman, max_aman):
    tanggal_list = [tanggal - datetime.timedelta(days=i) for i in range(7, 0, -1)] + [tanggal]
    data_lengkap = riwayat + [nilai_sekarang]
    
    df = pd.DataFrame({"Tanggal": tanggal_list, nama_y: data_lengkap})
    
    # Area Hijau (Aman)
    area_aman = alt.Chart(pd.DataFrame({'min': [min_aman], 'max': [max_aman]})).mark_rect(opacity=0.15, color='green').encode(y='min:Q', y2='max:Q')
    
    # Garis Batas (Merah Putus-putus)
    garis_bawah = alt.Chart(pd.DataFrame({'min': [min_aman]})).mark_rule(color='red', strokeDash=[5,5]).encode(y='min:Q')
    garis_atas = alt.Chart(pd.DataFrame({'max': [max_aman]})).mark_rule(color='red', strokeDash=[5,5]).encode(y='max:Q')
    
    # Grafik Garis Utama
    garis_data = alt.Chart(df).mark_line(point=alt.OverlayMarkDef(color='blue', size=100), strokeWidth=3).encode(
        x=alt.X('Tanggal:T', title='Tanggal Inspeksi', axis=alt.Axis(format='%d %b')),
        y=alt.Y(f'{nama_y}:Q', title=nama_y, scale=alt.Scale(domain=[max(0, min_aman - (max_aman-min_aman)*0.5), max_aman + (max_aman-min_aman)*0.5])),
        tooltip=[alt.Tooltip('Tanggal:T', format='%d %b %Y'), alt.Tooltip(f'{nama_y}:Q')]
    ).properties(title=judul, height=300)
    
    return area_aman + garis_bawah + garis_atas + garis_data

# Data riwayat dummy (7 hari terakhir)
riwayat_ph = [7.1, 7.3, 6.8, 7.5, 7.2, 6.9, 7.1]
riwayat_do = [2.1, 2.0, 2.3, 1.8, 1.9, 2.1, 2.2]
riwayat_klorin = [0.2, 0.3, 0.2, 0.4, 0.3, 0.2, 0.3]

# Menampilkan Grafik Berjejer
col_g1, col_g2, col_g3 = st.columns(3)
with col_g1:
    st.altair_chart(buat_grafik(ph_effluent, riwayat_ph, "pH Effluent (Rentang: 6 - 8)", "pH", 6.0, 8.0), use_container_width=True)
with col_g2:
    st.altair_chart(buat_grafik(do_aerasi, riwayat_do, "DO Aerasi (Rentang: 1.5 - 3.0)", "DO (mg/L)", 1.5, 3.0), use_container_width=True)
with col_g3:
    st.altair_chart(buat_grafik(sisa_klorin, riwayat_klorin, "Sisa Klorin (Rentang: 0.1 - 0.5)", "Klorin (ppm)", 0.1, 0
