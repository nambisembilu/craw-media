import streamlit as st
import pandas as pd
from io import BytesIO
from web_scraper import scrape_search_results  # pastikan file ini ada
import time

st.set_page_config(page_title="⛏️ Scraptic", layout="wide")
st.title("🌏 Web Scrap & Article Extractor")

uploaded_file = st.file_uploader("📥 Upload CSV berisi daftar URL (kolom: url)", type="csv")
keyword = st.text_input("📝 Masukkan kata kunci pencarian", value="makan bergizi gratis")

if uploaded_file and keyword:
    if st.button("🔍 Proses Pencarian"):
        df_input = pd.read_csv(uploaded_file)
        all_results = []

        progress = st.progress(0)
        total = len(df_input)

        for i, row in df_input.iterrows():
            url = row['url']
            st.write(f"🔗 Memproses: {url}")
            result = scrape_search_results(url, keyword, max_pages=3)
            for r in result:
                all_results.append({'sumber': url, **r})
            progress.progress((i + 1) / total)

        df_out = pd.DataFrame(all_results)
        st.success(f"✅ Ditemukan {len(df_out)} hasil dari {total} URL")
        st.dataframe(df_out)

        # Export ke Excel
        towrite = BytesIO()
        with pd.ExcelWriter(towrite, engine='xlsxwriter') as writer:
            df_out.to_excel(writer, index=False, sheet_name='Hasil')
        towrite.seek(0)

        st.download_button(
            label="📤 Download hasil sebagai Excel",
            data=towrite,
            file_name="hasil_pencarian.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
