import streamlit as st
import datetime
import urllib.request
import json
import pandas as pd
import altair as alt

# Konfigurasi Halaman
st.set_page_config(page_title="Digital Logbook IPAL", layout="wide")

st.title("🎛️ Digital Logbook & EWS IPAL")
st.subheader("RSUD Tanjung Priok - Instalasi Kesehatan Lingkungan (Versi 4.0 - Real-Time SCADA)")
st.markdown("---")

# ========================================== #
# KONEKSI DATABASE (WEBHOOK & CSV PULL)
# ========================================== #
# 1. URL untuk MENGIRIM Data (Push)
WEBHOOK_URL = "https://script.google.com/macros/s/AKfycbzS9HDRvge_k8AA6TWIla-m6D-RWUZXG-uMEuwsND78UYXxFzUMLQpzTK0XFjafa2Y/exec"

# 2. URL untuk MENARIK Riwayat Data (Pull)
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTQ6T05NwCYzCYA9qgeYjt-gzPc73Ym8pY_IfNqJ3t_YpU4g7Tul-S_H-REz3tDmFldgP2_XiItcg6b/pub?output=csv"

@st.cache_data(ttl=10) # Refresh penarikan data tiap 10 detik
def ambil_data_riwayat():
    try:
        df = pd.read_csv(CSV_URL)
        return df
    except Exception as e:
        return pd.DataFrame()

df_history = ambil_data_riwayat()

# Ekstraksi Data Riwayat Aktual (7 Data Terakhir)
riwayat_ph_aktual = []
riwayat_do_aktual = []
riwayat_klorin_aktual = []
tanggal_riwayat = []

if not df_history.empty:
    try:
        # Menarik data 7 baris terakhir dari Google Sheets
        df_last = df_history.tail(7)
        riwayat_ph_aktual = pd.to_numeric(df_last['pH Efluen'], errors='coerce').dropna().tolist()
        riwayat_do_aktual = pd.to_numeric(df_last['DO Aerasi (mg/L)'], errors='coerce').dropna().tolist()
        riwayat_klorin_aktual = pd.to_numeric(df_last['Sisa Klorin (ppm)'], errors='coerce').dropna().tolist()
        tanggal_riwayat = pd.to_datetime(df_last['Tanggal Inspeksi'], errors='coerce').dt.date.tolist()
    except:
        pass

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
            st.success(f"✅ Berhasil! Laporan atas nama {operator} telah tersimpan di Database!")
            st.cache_data.clear() # Paksa sistem memuat ulang data terbaru setelah submit
        except Exception as e:
            st.error(f"⚠️ Gagal mengirim data. Error: {e}")

st.markdown("---")

# ========================================== #
# GRAFIK ANALITIK (REAL-TIME TRENDLINES)
# ========================================== #
st.header("📈 Analitika Tren Parameter Utama")
st.markdown("*Grafik menampilkan riwayat **Aktual dari Database** digabungkan dengan input Anda saat ini. Area hijau adalah Batas Aman.*")

def buat_grafik(nilai_sekarang, riwayat_y, tgl_riwayat, judul, nama_y, min_aman, max_aman):
    # Gabungkan riwayat aktual dengan data di layar saat ini
    tgl_semua = tgl_riwayat + [tanggal]
    nilai_semua = riwayat_y + [nilai_sekarang]
    
    # Pencegahan error jika database baru berisi 1 baris
    if len(tgl_semua) <= 1:
        tgl_semua = [tanggal - datetime.timedelta(days=1), tanggal]
        nilai_semua = [nilai_sekarang, nilai_sekarang]
        
    df = pd.DataFrame({"Tanggal": tgl_semua, nama_y: nilai_semua})
    df['Tanggal'] = pd.to_datetime(df['Tanggal'])
    
    area_aman = alt.Chart(pd.DataFrame({'min': [min_aman], 'max': [max_aman]})).mark_rect(opacity=0.15, color='green').encode(y='min:Q', y2='max:Q')
    garis_bawah = alt.Chart(pd.DataFrame({'min': [min_aman]})).mark_rule(color='red', strokeDash=[5,5]).encode(y='min:Q')
    garis_atas = alt.Chart(pd.DataFrame({'max': [max_aman]})).mark_rule(color='red', strokeDash=[5,5]).encode(y='max:Q')
    
    garis_data = alt.Chart(df).mark_line(point=alt.OverlayMarkDef(color='blue', size=100), strokeWidth=3).encode(
        x=alt.X('Tanggal:T', title='Tanggal Inspeksi', axis=alt.Axis(format='%d %b')),
        y=alt.Y(f'{nama_y}:Q', title=nama_y, scale=alt.Scale(domain=[max(0, min_aman - (max_aman-min_aman)*0.5), max_aman + (max_aman-min_aman)*0.5])),
        tooltip=[alt.Tooltip('Tanggal:T', format='%d %b %Y'), alt.Tooltip(f'{nama_y}:Q')]
    ).properties(title=judul, height=300)
    
    return area_aman + garis_bawah + garis_atas + garis_data

col_g1, col_g2, col_g3 = st.columns(3)
with col_g1:
    st.altair_chart(buat_grafik(ph_effluent, riwayat_ph_aktual, tanggal_riwayat, "pH Effluent (Rentang: 6 - 8)", "pH", 6.0, 8.0), use_container_width=True)
with col_g2:
    st.altair_chart(buat_grafik(do_aerasi, riwayat_do_aktual, tanggal_riwayat, "DO Aerasi (Rentang: 1.5 - 3.0)", "DO (mg/L)", 1.5, 3.0), use_container_width=True)
with col_g3:
    st.altair_chart(buat_grafik(sisa_klorin, riwayat_klorin_aktual, tanggal_riwayat, "Sisa Klorin (Rentang: 0.1 - 0.5)", "Klorin (ppm)", 0.1, 0.5), use_container_width=True)

st.markdown("---")

# ========================================== #
# TAMPILAN UTAMA DASHBOARD (EWS PANEL)
# ========================================== #
st.header("🚨 Panel Status Peringatan Dini (EWS)")

status_inlet = ("🟢 AMAN", "Limbah masuk stabil.") if 6.0 <= ph_inlet <= 8.0 else ("🔴 BAHAYA", "ALARM! pH Inlet Ekstrem!")
status_ph_out = ("🟢 AMAN", "Sesuai baku mutu.") if 6.0 <= ph_effluent <= 8.0 else ("🔴 BAHAYA", "Melanggar baku mutu.")
status_tss = ("🟢 AMAN", "Flok sehat.") if kekeruhan == "Bening Jernih" else ("🔴 BAHAYA", "Indikasi Wash-out.")

if 1.5 <= do_aerasi <= 3.0: status_do = ("🟢 AMAN", "Oksigen ideal.")
elif do_aerasi < 1.5: status_do = ("🔴 BAHAYA", "Oksigen DROP! Bakteri lemas.")
else: status_do = ("🟡 WASPADA", "Over-aerasi. Boros Blower.")

if 2000 <= mlss <= 4000: status_mlss = ("🟢 AMAN", "Bakteri optimal.")
elif mlss < 2000: status_mlss = ("🔴 BAHAYA", "Populasi kurang.")
else: status_mlss = ("🟡 WASPADA", "Lumpur padat (Butuh Desludging).")

status_klorin = ("🟢 AMAN", "Patogen mati.") if 0.1 <= sisa_klorin <= 0.5 else ("🔴 BAHAYA", "Dosis tidak standar.")
status_blower = ("🟢 AMAN", "Blower ON.") if uptime_blower == 24 else ("🔴 BAHAYA", "Blower Trip/Mati!")

col_d1, col_d2, col_d3 = st.columns(3)
with col_d1:
    st.subheader("💧 Fisik & Kimia")
    st.warning(f"**pH Inlet:** {ph_inlet} | {status_inlet[0]}\n\n*{status_inlet[1]}*")
    st.info(f"**pH Effluent:** {ph_effluent} | {status_ph_out[0]}\n\n*{status_ph_out[1]}*")
    st.info(f"**Kekeruhan:** {kekeruhan} | {status_tss[0]}")
with col_d2:
    st.subheader("🦠 Bioreaktor")
    st.warning(f"**DO Aerasi:** {do_aerasi} | {status_do[0]}\n\n*{status_do[1]}*")
    st.warning(f"**MLSS:** {mlss} | {status_mlss[0]}\n\n*{status_mlss[1]}*")
    st.success(f"**Jam Blower:** {uptime_blower} Jam | {status_blower[0]}")
with col_d3:
    st.subheader("🏥 PPI & Sosial")
    st.warning(f"**Klorin:** {sisa_klorin} ppm | {status_klorin[0]}")
    if keluhan_warga == 0: st.success(f"**Komplain Bau:** {keluhan_warga} | 🟢 AMAN")
    else: st.error(f"**Komplain Bau:** {keluhan_warga} | 🔴 BAHAYA")
