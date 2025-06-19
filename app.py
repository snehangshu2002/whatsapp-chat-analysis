import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import seaborn as sns
from matplotlib import rcParams
import plotly.express as px
import json
import helper
import Preprocessor
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from urlextract import URLExtract
from collections import Counter
import nltk
nltk.download('stopwords')
from nltk.tokenize import word_tokenize

# Download required NLTK data
nltk.download('punkt', quiet=True)

rcParams['font.family'] = 'Segoe UI Emoji'
analyzer = SentimentIntensityAnalyzer()

def get_sentiment(text):
    if not isinstance(text, str) or not text.strip():
        return 0.0
    return analyzer.polarity_scores(text)['compound']

def sentiment_label(score):
    if score > 0.05:
        return "Positive"
    elif score < -0.05:
        return "Negative"
    else:
        return "Neutral"

def get_file_type_counts(df):
    video = df['message'].str.contains("video", case=False, na=False).sum()
    photo = df['message'].str.contains("photo|image|picture|jpg|jpeg|png", case=False, na=False).sum()
    audio = df['message'].str.contains("audio|voice|mp3|ogg", case=False, na=False).sum()
    return video, photo, audio

def preprocess_input(user_input):
    """Preprocess user input to improve AI understanding."""
    # Tokenize and clean input
    tokens = word_tokenize(user_input.lower())
    cleaned_tokens = [token for token in tokens if token.isalnum()]
    return ' '.join(cleaned_tokens)

# Sidebar Title
st.sidebar.title("📁 WhatsApp Chat Analyzer")


uploaded_file = st.sidebar.file_uploader("Choose a chat file (.txt)", type=["txt"])

if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = Preprocessor.preprocess(data)
    st.session_state.df = df

    if 'sentiment' not in df.columns:
        df['sentiment'] = df['message'].apply(get_sentiment)
    df['sentiment_label'] = df['sentiment'].apply(sentiment_label)
    df['date_only'] = df['date'].dt.date

    user_list = df["user"].unique().tolist()
    if "group_notification" in user_list:
        user_list.remove("group_notification")
    user_list.sort()
    user_list.insert(0, "Overall")

    st.sidebar.title("👤 Select User")
    selected_user = st.sidebar.selectbox("Select a user", user_list)

    if st.sidebar.button("Show Analysis"):
        st.title("📊 Chat Analysis Dashboard")

        # Stats
        num_messages, words, num_media, num_urls = helper.fetch_stats(selected_user, df)
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Messages", num_messages)
        col2.metric("Total Words", words)
        col3.metric("Media Shared", num_media)
        col4.metric("URLs Shared", num_urls)

        # Monthly Timeline
        st.subheader("📅 Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline['time'], timeline['message'], color='green')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # Daily Timeline
        st.subheader("🗓️ Daily Timeline")
        timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline['only_date'], timeline['message'], color='yellow')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # Activity Map
        st.subheader('🕒 Activity Map')
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Most Busy Day**")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color='purple')
            plt.xticks(rotation=90)
            st.pyplot(fig)
        with col2:
            st.markdown("**Most Busy Month**")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        st.subheader("📈 Weekly Activity Heatmap")
        user_heatmap = helper.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots()
        sns.heatmap(user_heatmap, ax=ax)
        st.pyplot(fig)

        if selected_user == "Overall":
            st.subheader("👥 Most Active Users")
            x, new_df = helper.most_busy_user(df)
            col1, col2 = st.columns(2)
            with col1:
                fig, ax = plt.subplots()
                ax.bar(x.index, x.values, color="red")
                plt.xticks(rotation=90)
                st.pyplot(fig)
            with col2:
                st.dataframe(new_df)

        st.subheader("☁️ WordCloud")
        df_wc = helper.count_wordcloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc, interpolation='bilinear')
        ax.axis("off")
        st.pyplot(fig)

        # Most Common Words
        st.title("Top 20 Most Common Words")
        bengali_font_path = "nirmala-ui.ttf"
        bengali_font = fm.FontProperties(fname=bengali_font_path)

        most_common_df = helper.most_common_user(selected_user, df)
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(most_common_df["Common words"], most_common_df["count"], color='skyblue')

        # Set Bengali font for all text elements
        ax.set_title("Most Common Words in Chat", fontproperties=bengali_font)
        ax.set_xlabel("Count", fontproperties=bengali_font)
        ax.set_ylabel("Words", fontproperties=bengali_font)

        # Manually set yticks with Bengali font
        ax.set_yticks(range(len(most_common_df)))
        ax.set_yticklabels(most_common_df["Common words"], fontproperties=bengali_font)

        plt.tight_layout()
        st.pyplot(fig)


        st.subheader("😄 Emoji Analysis")
        emoji_df = helper.emoji_helper(selected_user, df)
        col1, col2 = st.columns(2)
        with col1:
            st.dataframe(emoji_df)
        with col2:
            top_emojis = emoji_df.head(10)
            fig = px.pie(values=top_emojis.iloc[:, 1], names=top_emojis.iloc[:, 0], title="Top Emojis", hole=0.3)
            st.plotly_chart(fig)

        st.subheader("😊 Sentiment Timeline")
        sentiment_timeline = df.groupby('date_only')['sentiment'].mean()
        fig, ax = plt.subplots()
        sentiment_timeline.plot(ax=ax, marker='o')
        ax.set_ylabel("Average Sentiment")
        ax.set_title("Sentiment Over Time")
        st.pyplot(fig)

        st.subheader("😃 Sentiment Distribution")
        sentiment_counts = df['sentiment_label'].value_counts()
        fig = px.pie(values=sentiment_counts.values, names=sentiment_counts.index, title="Overall Sentiment Distribution")
        st.plotly_chart(fig)

