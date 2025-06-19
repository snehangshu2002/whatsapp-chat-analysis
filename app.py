import streamlit as st
import pandas as pd
import Preprocessor, helper
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import seaborn as sns
from matplotlib import rcParams
import plotly.express as px



# Set emoji-compatible font
rcParams['font.family'] = 'Segoe UI Emoji'

# Sidebar UI
st.sidebar.title("WhatsApp Chat Analyzer")
uploaded_file = st.sidebar.file_uploader("Choose a file", type=["txt"])

if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = Preprocessor.preprocess(data)

    user_list = df["user"].unique().tolist()
    user_list.remove("group_notification")
    user_list.sort()
    user_list.insert(0, "Overall")

    st.sidebar.title("Select User")
    selected_user = st.sidebar.selectbox("Select a user", user_list)

    if st.sidebar.button("Show Analysis"):
        # Top stats
        st.title("Top Statistics")
        num_messages, words, num_media, num_urls = helper.fetch_stats(selected_user, df)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Messages", num_messages)
        col2.metric("Total Words", words)
        col3.metric("Media Shared", num_media)
        col4.metric("URLs Shared", num_urls)

        # Monthly Timeline
        st.title("Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline['time'], timeline['message'], color='green')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # Daily Timeline
        st.title("Daily Timeline")
        timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline['only_date'], timeline['message'], color='yellow')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # Activity Map
        st.title('Activity Map')
        col1, col2 = st.columns(2)

        with col1:
            st.header("Most Busy Day")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color='purple')
            plt.xticks(rotation=90)
            st.pyplot(fig)

        with col2:
            st.header("Most Busy Month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        # Weekly Heatmap
        st.title("Weekly Activity Map")
        user_heatmap = helper.activity_heatmap(selected_user, df)
        fig, ax = plt.subplots()
        ax = sns.heatmap(user_heatmap)
        st.pyplot(fig)

        # Group Level - Most Busy User
        if selected_user == "Overall":
            st.title("Most Busy Users")
            x, new_df = helper.most_busy_user(df)

            col1, col2 = st.columns(2)
            with col1:
                fig, ax = plt.subplots()
                ax.bar(x.index, x.values, color="red")
                plt.xticks(rotation=90)
                st.pyplot(fig)

            with col2:
                st.dataframe(new_df)

        # WordCloud
        st.title("WordCloud")
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


        # Emoji Analysis
        st.title("Emoji Analysis")
        emoji_df = helper.emoji_helper(selected_user, df)

        col1, col2 = st.columns(2)

        with col1:
            st.dataframe(emoji_df)

        with col2:
            top_emojis = emoji_df.head(10)
            fig = px.pie(
                values=top_emojis[1],
                names=top_emojis[0],
                title="Top Emojis",
                hole=0.3  # for a donut chart, remove this for a regular pie
            )
            st.plotly_chart(fig)

        st.title("Ask Chatbot About the Chat 📩")

        # Initialize chat history and question
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        user_input = st.text_input("Type your question here...", key="chat_input")

        if st.button("Ask"):
            if user_input:
                # Combine some message context for the chatbot
                context = "\n".join(df["message"].tolist()[:3000])  # Limit context for API
                prompt = f"The following is a WhatsApp chat log:\n\n{context}\n\nAnswer this question based only on the chat:\n\n{user_input}"

                import requests
                import json

                headers = {
                    "Authorization": "Bearer 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",
                    "Content-Type": "application/json",
                }

                payload = {
                    "model": "google/gemma-1.1-7b-it:free",  # Choose your preferred model
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                }

                with st.spinner("🤖 Thinking..."):
                    response = requests.post(
                        url="https://openrouter.ai/api/v1/chat/completions",
                        headers=headers,
                        data=json.dumps(payload)
                    )

                    try:
                        data = response.json()
                        reply = data["choices"][0]["message"]["content"]
                        st.session_state.chat_history.append((user_input, reply))
                    except Exception as e:
                        reply = "⚠️ Failed to get a valid response."
                        st.session_state.chat_history.append((user_input, reply))

        # Show chat history
        if st.session_state.chat_history:
            for i, (q, a) in enumerate(reversed(st.session_state.chat_history)):
                st.markdown(f"**You:** {q}")
                st.markdown(f"**Bot:** {a}")
                st.markdown("---")
