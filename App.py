import streamlit as st
from groq import Groq
import json
import os
import datetime
import streamlit.components.v1 as components

# Config Halaman
st.set_page_config(page_title="RSI System - Coach Aldi", layout="wide")

# Sidebar Pengaturan Key
st.sidebar.title("🔐 Pengaturan System")

secrets_key = st.secrets.get("GROQ_API_KEY", "")
user_api_key = st.sidebar.text_input("Groq API Key (gsk_...):", value=secrets_key, type="password")

client = None
clean_key = user_api_key.strip() if user_api_key else ""

if clean_key:
    try:
        client = Groq(api_key=clean_key)
        st.sidebar.success("✅ API Key Terhubung")
    except Exception as e:
        st.sidebar.error(f"Gagal Inisialisasi: {str(e)}")
else:
    st.sidebar.warning("Masukkan Groq API Key di atas.")

# Fungsi Panggilan AI dengan Multi-Model Fallback
def query_groq_ai(client_obj, prompt_text):
    # Urutan kandidat model aktif di Groq saat ini
    candidate_models = [
        "llama-3.3-70b-versatile",
        "llama3-70b-8192",
        "llama-3.1-70b-versatile",
        "mixtral-8x7b-32768",
        "llama3-8b-8192"
    ]
    
    last_error = None
    for model_name in candidate_models:
        try:
            response = client_obj.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt_text}]
            )
            return response.choices[0].message.content
        except Exception as e:
            last_error = e
            continue
            
    raise Exception(f"Semua model gagal diakses. Error terakhir: {str(last_error)}")

# Safe JSON Loader & Saver
DB_PATIENTS = "database_pasien.json"
DB_INVENTORY = "database_stok.json"
DB_TRANSACTIONS = "database_transaksi.json"

def safe_load_json(filename, default_val):
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default_val
    return default_val

def safe_save_json(filename, data):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception:
        pass

# Session State Initialization
if "patients_db" not in st.session_state:
    st.session_state.patients_db = safe_load_json(DB_PATIENTS, [])

if "inventory_db" not in st.session_state:
    default_inv = [
        {"nama": "Jahe Merah (gram)", "hpp": 150, "stok": 5000},
        {"nama": "Kunyit (gram)", "hpp": 100, "stok": 5000},
        {"nama": "Temulawak (gram)", "hpp": 120, "stok": 3000},
        {"nama": "Kayu Manis (gram)", "hpp": 200, "stok": 2000},
        {"nama": "Bangle (gram)", "hpp": 180, "stok": 1500},
        {"nama": "Cengkih (gram)", "hpp": 300, "stok": 1000}
    ]
    st.session_state.inventory_db = safe_load_json(DB_INVENTORY, default_inv)

if "transactions_db" not in st.session_state:
    st.session_state.transactions_db = safe_load_json(DB_TRANSACTIONS, [])

if "calculated_herbal_price" not in st.session_state:
    st.session_state.calculated_herbal_price = 0

if "current_patient" not in st.session_state:
    st.session_state.current_patient = "Klien Umum"

if "selected_herbal_items" not in st.session_state:
    st.session_state.selected_herbal_items = []

# Header Utama
st.title("🏥 System Operasional Klinik RSI (Rumah Sehat Insani)")
st.caption("Aplikasi Rekam Medis, Diagnosa TCM (AI), Stok Herbal, Kasir & Akuntansi")

tabs = st.tabs([
    "📋 Data Pasien & Diagnosa TCM", 
    "🌿 Peresepan & Stok Herbal", 
    "🧾 Kasir & Struk Bluetooth", 
    "📊 Laporan Keuangan (.txt)"
])

# ---------------------------------------------------------
# TAB 1: DIAGNOSA & REKAM MEDIS PASIEN
# ---------------------------------------------------------
with tabs[0]:
    st.header("1. Data Pasien & Empat Pemeriksaan (Si Zhen)")
    col1, col2 = st.columns(2)
    
    with col1:
        nama = st.text_input("Nama Pasien:", key="input_nama")
        usia = st.number_input("Usia (Tahun):", min_value=1, max_value=120, value=35)
        gender = st.selectbox("Jenis Kelamin:", ["Laki-laki", "Perempuan"])
        keluhan_utama = st.text_area("Keluhan Utama & Hasil Pemeriksaan (Wang, Wen, Wen, Qie):", 
                                     placeholder="Contoh: Sakit kepala berdenyut, leher kaku, lidah merah selaput kuning, nadi cepat...")
        
    with col2:
        td = st.text_input("Tekanan Darah (S/D):", "120/80")
        nadi_bpm = st.number_input("Frekuensi Nadi (BPM):", value=75)

    if st.button("🔮 Analisis Diagnosa & Formulasi TCM (AI)"):
        if not client or not clean_key:
            st.error("Masukkan Groq API Key di sidebar sebelah kiri terlebih dahulu.")
        elif not nama or not keluhan_utama:
            st.warning("Harap isi Nama Pasien dan Keluhan Utama terlebih dahulu.")
        else:
            with st.spinner("AI sedang menganalisis Sindrom, Titik Akupuntur, Food Terapi & Resep Herbal..."):
                try:
                    stok_list_str = ", ".join([f"{item['nama']} (Stok: {item['stok']}g, HPP: Rp{item['hpp']}/g)" for item in st.session_state.inventory_db])

                    prompt = f"""
                    Posisikan Anda sebagai Coach Healing Profesional dan Praktisi Pengobatan TCM Profesional.
                    Analisis data rekam medis pasien berikut:
                    - Nama Pasien: {nama}, Usia: {usia}, Gender: {gender}
                    - Vital Sign: TD {td}, Nadi {nadi_bpm} bpm
                    - Keluhan Utama & Empat Pemeriksaan (Si Zhen): {keluhan_utama}
                    - Daftar Stok Herbal Tersedia: {stok_list_str}

                    Berikan hasil analisis terstruktur berformat teks rapi (.txt) mencakup:
                    1. DIAGNOSA SINDROM TCM (Diferensiasi Zang-Fu, Ba Gang, Organ & Penyebab Utama).
                    2. REKOMENDASI TERAPI AKUPUNTUR & AKUPRESUR (Sebutkan kode titik misal ST36, SP6, LR3, lokasi posisi titik, dan indikasinya).
                    3. REKOMENDASI TITIK MOKSA (Jika diindikasikan, beserta alasannya).
                    4. RESEP FOOD TERAPI (Anjuran makanan & pantangan makanan sesuai sindrom).
                    5. FORMULA HERBAL IDEAL (Formula Klasik Standar TCM).
                    6. FORMULA HERBAL SESUAI STOK TERSEDIA (Pilih dari daftar stok herbal lokal di atas beserta takaran gramnya).
                    """
                    
                    ai_result = query_groq_ai(client, prompt)
                    
                    st.session_state.current_patient = nama
                    st.session_state.patients_db.append({
                        "tanggal": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "nama": nama, "usia": usia, "keluhan": keluhan_utama, "diagnosa_ai": ai_result
                    })
                    safe_save_json(DB_PATIENTS, st.session_state.patients_db)
                    
                    st.success("✅ Analisis AI Berhasil Disimpan!")
                    st.text_area("Hasil Analisis Complete (TCM & Terapi):", ai_result, height=350)
                except Exception as e:
                    st.error(f"Gagal memproses AI: {str(e)}")

# ---------------------------------------------------------
# TAB 2: STOK & KALKULATOR MARKUP 250%
# ---------------------------------------------------------
with tabs[1]:
    st.header("2. Management Stok & Kalkulator Herbal (Markup 250%)")
    
    selected_items = []
    total_hpp = 0
    
    col_inv1, col_inv2 = st.columns(2)
    with col_inv1:
        st.subheader("Pilih Racikan Herbal dari Stok:")
        for idx, item in enumerate(st.session_state.inventory_db):
            qty = st.number_input(f"Jumlah {item['nama']} (gram):", min_value=0, max_value=int(item['stok']), value=0, key=f"inv_input_{idx}")
            if qty > 0:
                sub_hpp = int(qty * item['hpp'])
                total_hpp += sub_hpp
                selected_items.append({"nama": item['nama'], "qty": qty, "hpp": item['hpp'], "sub_hpp": sub_hpp})
    
    with col_inv2:
        st.subheader("Kalkulasi Biaya & Harga Jual:")
        st.metric("Total HPP Herbal", f"Rp {total_hpp:,.0f}")
        
        harga_jual_herbal = int(total_hpp * 3.5)
        st.metric("Harga Jual Herbal (Markup 250%)", f"Rp {harga_jual_herbal:,.0f}")
        
        st.session_state.calculated_herbal_price = harga_jual_herbal
        st.session_state.selected_herbal_items = selected_items

# ---------------------------------------------------------
# TAB 3: KASIR & CETAK STRUK BLUETOOTH
# ---------------------------------------------------------
with tabs[2]:
    st.header("3. Kasir & Pembayaran Struk Thermal Bluetooth")
    
    col_k1, col_k2 = st.columns(2)
    with col_k1:
        patient_name = st.text_input("Nama Pasien / Klien:", value=st.session_state.current_patient)
        biaya_jasa = st.number_input("Biaya Jasa Konsultasi / Akupuntur (Rp):", value=100000, step=10000)
        
        herbal_price_int = int(st.session_state.calculated_herbal_price)
        biaya_herbal = st.number_input("Biaya Racikan Herbal (Rp):", value=herbal_price_int, step=5000)
        
        total_transaksi = int(biaya_jasa + biaya_herbal)
        
        st.write(f"### Total Tagihan: **Rp {total_transaksi:,.0f}**")
        
        if st.button("Simpan Transaksi & Potong Stok"):
            for s_item in st.session_state.selected_herbal_items:
                for inv_item in st.session_state.inventory_db:
                    if inv_item['nama'] == s_item['nama']:
                        inv_item['stok'] -= s_item['qty']
            safe_save_json(DB_INVENTORY, st.session_state.inventory_db)
            
            trans_record = {
                "tgl": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "pasien": patient_name,
                "jasa": biaya_jasa,
                "herbal": biaya_herbal,
                "total": total_transaksi
            }
            st.session_state.transactions_db.append(trans_record)
            safe_save_json(DB_TRANSACTIONS, st.session_state.transactions_db)
            st.success("✅ Transaksi Berhasil Disimpan & Stok Diperbarui!")

    with col_k2:
        st.subheader("Pratinjau Struk Thermal (58mm)")
        tgl_sekarang = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        
        struk_html = f"""
        <div id="receipt-area" style="font-family: monospace; width: 250px; padding: 10px; border: 1px solid #000; font-size: 12px; background: #fff; color: #000;">
            <div style="text-align:center; font-weight:bold;">
                RUMAH SEHAT INSANI (RSI)<br>
                Holistic Health & TCM Center
            </div>
            <div>--------------------------------</div>
            <div>Tgl   : {tgl_sekarang}</div>
            <div>Pasien: {patient_name}</div>
            <div>--------------------------------</div>
            <div>Jasa Terapi  : Rp {biaya_jasa:,.0f}</div>
            <div>Herbal Custom: Rp {biaya_herbal:,.0f}</div>
            <div>--------------------------------</div>
            <div style="font-weight:bold; font-size: 13px;">TOTAL : Rp {total_transaksi:,.0f}</div>
            <div>--------------------------------</div>
            <div style="text-align:center; margin-top:8px;">
                Semoga Lekas Sembuh & Sehat Selalu<br>
                *** Terima Kasih ***
            </div>
        </div>
        """
        st.markdown(struk_html, unsafe_allow_html=True)
        
        print_script = """
        <script>
        function printReceipt() {
            var printContents = document.getElementById('receipt-area').outerHTML;
            var originalContents = document.body.innerHTML;
            document.body.innerHTML = printContents;
            window.print();
            document.body.innerHTML = originalContents;
            window.location.reload();
        }
        </script>
        <button onclick="printReceipt()" style="margin-top:15px; padding: 10px 20px; background-color: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer; font-weight: bold;">
            Cetak Struk Bluetooth (RawBT)
        </button>
        """
        components.html(print_script, height=90)

# ---------------------------------------------------------
# TAB 4: AKUNTANSI
# ---------------------------------------------------------
with tabs[3]:
    st.header("4. Laporan Keuangan Standar Akuntansi (.txt)")
    
    if st.button("📈 Susun Laporan Keuangan Akuntansi"):
        if not client or not clean_key:
            st.error("Groq API Key belum terpasang di sidebar.")
        elif not st.session_state.transactions_db:
            st.warning("Belum ada data transaksi tersimpan.")
        else:
            with st.spinner("AI menyusun Laporan Jurnal & Laba Rugi..."):
                try:
                    trans_summary = json.dumps(st.session_state.transactions_db, indent=2)
                    
                    prompt_acc = f"""
                    Bertindaklah sebagai Akuntan Publik Profesional.
                    Berdasarkan data transaksi berikut:
                    {trans_summary}

                    Buatkan Laporan Keuangan Standar Akuntansi lengkap berformat Teks (.txt) rapi meliputi:
                    1. JURNAL UMUM (Double-Entry: Debit vs Kredit untuk Pendapatan Jasa, Pendapatan Herbal, Kas, dll).
                    2. LAPORAN LABA RUGI (Total Revenue, HPP Estimasi, Gross Profit, Net Income).
                    3. NERACA SEDERHANA (Aset Kas vs Ekuitas).
                    4. CATATAN MANAJEMEN KEUANGAN KLINIK.
                    """
                    
                    report_acc_text = query_groq_ai(client, prompt_acc)
                    
                    st.text_area("Pratinjau Laporan Keuangan (.txt):", report_acc_text, height=300)
                    
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
                    st.download_button(
                        label="📄 Download Laporan Keuangan (.txt)",
                        data=report_acc_text,
                        file_name=f"Laporan_Keuangan_RSI_{timestamp}.txt",
                        mime="text/plain"
                    )
                except Exception as e:
                    st.error(f"Gagal menyusun laporan keuangan: {str(e)}")
