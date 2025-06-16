import snscrape.modules.twitter as sntwitter
import pandas as pd
import openai

openai.api_key = "YOUR_OPENAI_KEY"

def analyze_with_ai(text, prompt="Buat ringkasan dan analisis topik ini."):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": f"{prompt}\n\n{text}"}]
    )
    return response.choices[0].message['content']

def crawl_tweets(query, max_tweets=50, use_ai=False, prompt="Analisis isi tweet berikut:"):
    tweets = []
    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
        if i >= max_tweets:
            break
        row = {
            "date": tweet.date,
            "username": tweet.user.username,
            "content": tweet.content,
            "url": tweet.url,
            "likes": tweet.likeCount,
            "retweets": tweet.retweetCount
        }
        if use_ai:
            try:
                row["analisis_ai"] = analyze_with_ai(tweet.content, prompt)
            except:
                row["analisis_ai"] = "Gagal menganalisis"
        tweets.append(row)
    return pd.DataFrame(tweets)