from urlextract import URLExtract
import matplotlib.pyplot as plt
import pandas as pd
import emoji
from wordcloud import WordCloud
from nltk.corpus import stopwords
from collections import Counter
from matplotlib import font_manager as fm

import os

# Load stopwords
english_stopwords = set(stopwords.words('english'))
with open("stop_hinglish.txt", "r", encoding="utf-8") as english:
    stopwords_eng = english.read()

bengali_stopwords = set("""
অতএব অথচ অথবা অনুসায়ী অনেক অনেকে অনেকেই অন্তত অন্য অবধি অবশ্য অর্থাত আই আগামী আগে আগেই আছে আজ আদ্যভাগে আপনার আপনি আবার আমরা আমাকে আমাদের আমার আমি আর আরও ই ইত্যাদি ইহা উচিত উত্তর উনি উপর উপরে এ এঁদের এঁরা এই একই একটি একবার একে এক্ এখন এখনও এখানে এখানেই এটা এটই এটি এত এতটাই এতে এদের এব এবং এবার এমন এমনকী এমনি এর এরা এল এস এসে ঐ ও ওঁদের ওঁর ওঁরা ওই ওকে ওখানে ওদের ওর ওরা কখনও কত কবে কমনে কয়েক কয়েকটি করছে করছেন করতে করবে করবেন করলে করলেন করা করাই করায় করার করি করিতে করিয়া করিয়ে করে করেই করেছিলেন করেছে করেছেন করেন কাউকে কাছ কাছে কাজ কাজে কারও কারণ কি কিংবা কিছু কিছুই কিন্তু কী কে কেউ কেউই কেখা কেন কোটি কোন কোনও কোনো ক্ষেত্রে কয়েক খুব গিয়ে গিয়েছে গিয়ে গুলি গেছে গেল গেলে গোটা চলে চান চায় চার চালু চেয়ে চেষ্টা ছাড়া ছাড়াও ছিল ছিলেন জন জনকে জনের জন্য জন্যওজে জানতে জানা জানানো জানায় জানিয়ে জানিয়েছে জে জ্নজন টি ঠিক তখন তত তথা তবু তবে তা তাঁকে তাঁদের তাঁর তাঁরা তাঁাহারা তাই তাও তাকে তাতে তাদের তার তারপর তারা তারৈ তাহলে তাহা তাহাতে তাহার তিনঐ তিনি তিনিও তুমি তুলে তেমন তো তোমার থাকবে থাকবেন থাকা থাকায় থাকে থাকেন থেকে থেকেই থেকেও দিকে দিতে দিন দিয়ে দিয়েছে দিয়েছেন দিলেন দু দুই দুটি দুটো দেওয়া দেওয়ার দেওয়া দেখতে দেখা দেখে দেন দেয় দ্বারা ধরা ধরে ধামার নতুন নয় না নাই নাকি নাগাদ নানা নিজে নিজেই নিজেদের নিজের নিতে নিয়ে নিয়ে নেই নেওয়া নেওয়ার নেওয়া নয় পক্ষে পর পরে পরেই পরেও পর্যন্ত পাওয়া পাচ পারি পারে পারেন পি পেয়ে পেয়্র্ প্রতি প্রথম প্রভৃতি প্রযন্ত প্রাথমিক প্রায় প্রায় ফলে ফিরে ফের বক্তব্য বদলে বন বরং বলতে বলল বললেন বলা বলে বলেছেন বলেন বসে বহু বা বাদে বার বি বিনা বিভিন্ন বিশেষ বিষয়টি বেশ বেশি ব্যবহার ব্যাপারে ভাবে ভাবেই মতো মতোই মধ্যভাগে মধ্যে মধ্যেই মধ্যেও মনে মাত্র মাধ্যমে মোট মোটেই যখন যত যতটা যথেষ্ট যদি যদিও যা যাঁর যাঁরা যাওয়া যাওয়ার যাওয়া যাকে যাচ্ছে যাতে যাদের যান যাবে যায় যার যারা তিনি যে যেখানে যেতে যেন যেমন র রকম রয়েছে রাখা রেখে লক্ষ শুধু শুরু সঙ্গে সঙ্গেও সব সবার সমস্ত সম্প্রতি সহ সহিত সাধারণ সামনে সি সুতরাং সে সেই সেখান সেখানে সেটা সেটাই সেটাও এটি স্পষ্ট স্বয়ং হইতে হইবে হইয়া হওয়া হওয়ায় হওয়ার হচ্ছে হত হতে হতই হন হবে হবেন হয় হয়তো হয়নি হয়ে হয়েই হয়েছিল হয়েছে হয়েছেন হল হলে হলেই হলেও হলো হাজার হিসেবে হৈলে হোক হয়
""".split())

extractor = URLExtract()

# Fetch basic statistics
def fetch_stats(selected_user, df):
    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    num_messages = df.shape[0]
    words = [word for msg in df["message"] for word in msg.split()]
    num_media = df[df["message"] == "<Media omitted>\n"].shape[0]
    num_urls = sum(len(extractor.find_urls(msg)) for msg in df["message"])

    return num_messages, len(words), num_media, num_urls

# Most busy users
def most_busy_user(df):
    user_counts = df[df["user"] != "group_notification"]["user"].value_counts()
    percent = (user_counts / user_counts.sum() * 100).round(2).reset_index()
    percent.columns = ["Name", "Percent"]
    return user_counts, percent

# Word cloud generator
def count_wordcloud(selected_user, df):
    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    df = df[(df["user"] != "group_notification") & (df["message"] != "<Media omitted>\n")]
    stopwords_set = english_stopwords | set(stopwords_eng.split()) | bengali_stopwords

    def clean_text(text):
        return " ".join([word.lower() for word in text.split() if word not in stopwords_set])

    df["cleaned"] = df["message"].apply(clean_text)
    text = " ".join(df["cleaned"])

    wc = WordCloud(width=500, height=500, background_color='white', font_path='NotoSansBengali-VariableFont_wdth,wght.ttf', min_font_size=10)
    return wc.generate(text)

# Most common words
def most_common_user(selected_user, df):
    if selected_user != "Overall":
        df = df[df["user"] == selected_user]

    temp = df[(df["user"] != "group_notification") & (df["message"] != "<Media omitted>\n")]
    stopwords_set = english_stopwords | set(stopwords_eng.split()) | bengali_stopwords

    words = [word for message in temp["message"] for word in message.lower().split() if word not in stopwords_set]
    common_df = pd.DataFrame(Counter(words).most_common(20), columns=["Common words", "count"])
    return common_df

# Emoji analysis
def emoji_helper(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = [c for msg in df["message"] for c in msg if c in emoji.EMOJI_DATA]
    return pd.DataFrame(Counter(emojis).most_common())

# Monthly timeline
def monthly_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = df.groupby(["year", "month_num", "month"])['message'].count().reset_index()
    timeline["time"] = timeline["month"] + "-" + timeline["year"].astype(str)
    return timeline

# Daily timeline
def daily_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df.groupby("only_date")["message"].count().reset_index()

# Activity maps
def week_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df["day_name"].value_counts()

def month_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df["month"].value_counts()

def activity_heatmap(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

