import streamlit as st
from twitter_pipeline import crawl_tweets

st.set_page_config(page_title="Crawl4AI X-Tweet Analyzer", layout="wide")
st.title("🐦 Crawl & AI Analysis dari Platform X (Twitter)")

with st.form("crawl_form"):
    topic = st.text_input("Masukkan topik pencarian", value="makan bergizi gratis")
    jumlah = st.slider("Jumlah tweet", 10, 100, 20)
    use_ai = st.checkbox("Gunakan analisis AI GPT-4?")
    prompt = st.text_area("Prompt untuk analisis AI", value="Apa topik utama dan konteks tweet ini?")
    submitted = st.form_submit_button("Jalankan Crawling")

if submitted:
    with st.spinner("⏳ Sedang mengambil data tweet..."):
        df = crawl_tweets(query=f'"{topic}" lang:id', max_tweets=jumlah, use_ai=use_ai, prompt=prompt)

    st.success(f"✅ Ditemukan {len(df)} tweet!")
    st.dataframe(df)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Unduh sebagai CSV", csv, "hasil_crawling.csv", "text/csv")

    if use_ai:
        st.markdown("### 🔍 Ringkasan Analisis AI")
        for i, row in df.iterrows():
            st.subheader(f"Tweet dari @{row['username']}")
            st.write(row["content"])
            st.info(row["analisis_ai"])