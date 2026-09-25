import streamlit as st
import google.generativeai as genai
from PIL import Image
import json
import os
import datetime
import streamlit.components.v1 as components

st.set_page_config(page_title="RSI Holistic System - Coach Aldi", layout="wide")

API_KEY_RSI = "AQ.Ab8RN6IXMnvIVSDSNPntNcbDvDdL7NFnK7iPyx1Bcpxc0DbcCg"
genai.configure(api_key=API_KEY_RSI)
model = genai.GenerativeModel('gemini-1.5-flash')

DB_PATIENTS = "database_pasien.json"
DB_INVENTORY = "database_stok.json"
DB_TRANSACTIONS = "database_transaksi.json"

def load_data(filepath, default):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except:
            return default
    return default

def save_data(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)

patients_db = load_data(DB_PATIENTS, [])
inventory_db = load_data(DB_INVENTORY, [
    {"nama": "Jahe Merah (gram)", "hpp": 150, "stok": 5000},
    {"nama": "Kunyit (gram)", "hpp": 100, "stok": 5000},
    {"nama": "Temulawak (gram)", "hpp": 120, "stok": 3000},
    {"nama": "Kayu Manis (gram)", "hpp": 200, "stok": 2000},
    {"nama": "Bangle (gram)", "hpp": 180, "stok": 1500},
    {"nama": "Cengkih (gram)", "hpp": 300, "stok": 1000}
])
transactions_db = load_data(DB_TRANSACTIONS, [])

st.title("🏥 System Operasional Klinik RSI (Rumah Sehat Insani)")
st.caption("Aplikasi Rekam Medis, Diagnosa TCM (AI), Stok Herbal, Kasir & Akuntansi")

tabs = st.tabs([
    "📋 Data Pasien & Diagnosa TCM", 
    "🌿 Peresepan & Stok Herbal", 
    "🧾 Kasir & Struk Bluetooth", 
    "📊 Laporan Keuangan (.txt)"
])

with tabs[0]:
    st.header("1. Data Pasien & Empat Pemeriksaan (Si Zhen)")
    col1, col2 = st.columns(2)
    
    with col1:
        nama = st.text_input("Nama Pasien:")
        usia = st.number_input("Usia (Tahun):", min_value=1, max_value=120, value=35)
        gender = st.selectbox("Jenis Kelamin:", ["Laki-laki", "Perempuan"])
        keluhan_utama = st.text_area("Keluhan Utama & Hasil Pemeriksaan (Wang, Wen, Wen, Qie):", 
                                     placeholder="Contoh: Sakit kepala berdenyut, leher kaku, lidah merah selaput kuning, nadi cepat...")
        
    with col2:
        td = st.text_input("Tekanan Darah (S/D):", "120/80")
        nadi_bpm = st.number_input("Frekuensi Nadi (BPM):", value=75)
        foto_lidah = st.file_uploader("Upload Foto Lidah Pasien (Opsional):", type=["jpg", "png", "jpeg"])

    if st.button("🔮 Analisis Diagnosa & Formulasi TCM (AI)"):
        if not nama or not keluhan_utama:
            st.warning("Harap isi Nama Pasien dan Keluhan Utama terlebih dahulu.")
        else:
            with st.spinner("Gemini AI sedang menganalisis Sindrom, Titik Akupuntur, Food Terapi & Resep Herbal..."):
                stok_list_str = ", ".join([f"{item['nama']} (Stok: {item['stok']}g, HPP: Rp{item['hpp']}/g)" for item in inventory_db])
                
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
                
                contents = [prompt]
                if foto_lidah:
                    contents.append(Image.open(foto_lidah))
                
                response = model.generate_content(contents)
                ai_result = response.text
                
                st.session_state['current_diagnosis'] = ai_result
                st.session_state['current_patient'] = nama
                
                patients_db.append({
                    "tanggal": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "nama": nama, "usia": usia, "keluhan": keluhan_utama, "diagnosa_ai": ai_result
                })
                save_data(DB_PATIENTS, patients_db)
                
                st.success("Analisis AI Berhasil Disimpan!")
                st.text_area("Hasil Analisis Complete (TCM & Terapi):", ai_result, height=400)

with tabs[1]:
    st.header("2. Management Stok & Kalkulator Herbal (Markup 250%)")
    
    selected_items = []
    total_hpp = 0
    
    col_inv1, col_inv2 = st.columns(2)
    with col_inv1:
        st.subheader("Pilih Racikan Herbal dari Stok:")
        for idx, item in enumerate(inventory_db):
            qty = st.number_input(f"Jumlah {item['nama']} (gram):", min_value=0, max_value=item['stok'], value=0, key=f"inv_{idx}")
            if qty > 0:
                sub_hpp = qty * item['hpp']
                total_hpp += sub_hpp
                selected_items.append({"nama": item['nama'], "qty": qty, "hpp": item['hpp'], "sub_hpp": sub_hpp})
    
    with col_inv2:
        st.subheader("Kalkulasi Biaya & Harga Jual:")
        st.metric("Total HPP Herbal", f"Rp {total_hpp:,.0f}")
        
        harga_jual_herbal = total_hpp * 3.5
        st.metric("Harga Jual Herbal (Markup 250%)", f"Rp {harga_jual_herbal:,.0f}")
        
        st.session_state['calculated_herbal_price'] = harga_jual_herbal
        st.session_state['selected_herbal_items'] = selected_items

with tabs[2]:
    st.header("3. Kasir & Pembayaran Struk Thermal Bluetooth")
    
    col_k1, col_k2 = st.columns(2)
    with col_k1:
        patient_name = st.text_input("Nama Pasien / Klien:", st.session_state.get('current_patient', 'Klien Umum'))
        biaya_jasa = st.number_input("Biaya Jasa Konsultasi / Akupuntur (Rp):", value=100000)
        biaya_herbal = st.number_input("Biaya Racikan Herbal (Rp):", value=float(st.session_state.get('calculated_herbal_price', 0)))
        total_transaksi = biaya_jasa + biaya_herbal
        
        st.write(f"### Total Tagihan: **Rp {total_transaksi:,.0f}**")
        
        if st.button("Simpan Transaksi & Potong Stok"):
            selected_herbs = st.session_state.get('selected_herbal_items', [])
            for s_item in selected_herbs:
                for inv_item in inventory_db:
                    if inv_item['nama'] == s_item['nama']:
                        inv_item['stok'] -= s_item['qty']
            save_data(DB_INVENTORY, inventory_db)
            
            trans_record = {
                "tgl": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "pasien": patient_name,
                "jasa": biaya_jasa,
                "herbal": biaya_herbal,
                "total": total_transaksi
            }
            transactions_db.append(trans_record)
            save_data(DB_TRANSACTIONS, transactions_db)
            st.success("Transaksi Berhasil Disimpan & Stok Berhasil Diperbarui!")

    with col_k2:
        st.subheader("Pratinjau Struk Thermal (58mm)")
        tgl_sekarang = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        
        struk_html = f"""
        <div id="receipt-area" style="font-family: 'Courier New', monospace; width: 260px; padding: 10px; border: 1px solid #000; font-size: 12px; background: #fff; color: #000;">
            <div style="text-align:center; font-weight:bold;">
                RUMAH SEHAT INSANI (RSI)<br>
                Holistic Health & TCM Center
            </div>
            <div>--------------------------------</div>
            <div>Tgl   : {tgl_sekarang}</div>
            <div>Pasien: {patient_name}</div>
            <div>--------------------------------</div>
            <div>Jasa Terapi/Konsultasi : Rp {biaya_jasa:,.0f}</div>
            <div>Formula Herbal Custom  : Rp {biaya_herbal:,.0f}</div>
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
            🖨️ Cetak Struk via Bluetooth Printer (RawBT)
        </button>
        """
        components.html(print_script, height=100)

with tabs[3]:
    st.header("4. Laporan Keuangan Standar Akuntansi (.txt)")
    
    if st.button("📈 Susun Laporan Keuangan Akuntansi"):
        with st.spinner("AI menyusun Laporan Jurnal & Laba Rugi..."):
            trans_summary = json.dumps(transactions_db, indent=2)
            
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
            
            response_acc = model.generate_content([prompt_acc])
            report_acc_text = response_acc.text
            
            st.text_area("Pratinjau Laporan Keuangan (.txt):", report_acc_text, height=350)
            
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button(
                label="📄 Download Laporan Keuangan (.txt)",
                data=report_acc_text,
                file_name=f"Laporan_Keuangan_RSI_{timestamp}.txt",
                mime="text/plain"
            )
