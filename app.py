import streamlit as st
import pandas as pd
from web_scraper import scrape_search_results
from io import BytesIO

st.set_page_config(page_title="Crawl Search Tool", layout="wide")
st.title("🔍 Web Search Extractor")

# Upload CSV dan input kata kunci
uploaded_file = st.file_uploader("📥 Upload CSV berisi daftar URL (kolom: url)", type="csv")
keyword = st.text_input("📝 Masukkan kata kunci pencarian", value="makan bergizi gratis")

# Tambahkan tombol proses
if uploaded_file and keyword:
    if st.button("🔍 Proses Pencarian"):
        df_input = pd.read_csv(uploaded_file)
        all_results = []

        with st.spinner("⏳ Sedang memproses URL..."):
            for i, row in df_input.iterrows():
                url = row['url']
                result = scrape_search_results(url, keyword)
                for r in result:
                    all_results.append({'sumber': url, **r})

        df_out = pd.DataFrame(all_results)
        st.success(f"✅ Ditemukan {len(df_out)} hasil")
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
