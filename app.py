import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import streamlit as st
import plotly.express as px
from wordcloud import WordCloud
import helper

# Title
st.title("YouTube Comments Analyzer")
# get video url from user input
video_url = st.text_input("Enter video's link here : ")
if(st.button('Analyze')):
    if('watch' in video_url):
        # fetch the comments from youtube
        comments_data = helper.fetch_comments(video_url)
        df = pd.DataFrame(comments_data)

        # convert the object to datetime 
        df['date'] = df['Date'].apply(helper.format_date)
        # create total months and years of the comment 
        df[['total_months', 'total_years']] = df['date'].apply(lambda x : pd.Series(helper.convert_month_year(x)))

        # get longest comment from the video
        longest_comment_len = max(df['Comment'].apply(helper.length_of_comments))

        # Get most common comments from the video
        # combine all comments and tokenize
        all_words = []
        df['Comment'].apply(lambda x : all_words.extend(helper.tokenize_data(x)))
        # count word frequency
        word_counts = Counter(all_words)
        common_words_df = pd.DataFrame(word_counts.items(), columns = ['words', 'count']).sort_values(by = 'count', ascending = False)

        # Get the most common emojis from the video
        all_emoji = []
        df['Comment'].apply(lambda x : all_emoji.extend(helper.extract_emojis(x)))
        # count emoji fequencies
        emoji_counts = Counter(all_emoji)
        # get most common emojis
        common_emoji_df = emoji_df = pd.DataFrame(emoji_counts.items(), columns = ['emoji', 'count']).sort_values(by = 'count', ascending = False)

        # Apply sentiment analysis in the comments
        df['sentiment'], df['polarity'] = zip(*df['Comment'].apply(helper.analyze_sentiment))

        # Sentiment Analysis Section
        st.header("Sentiment Analysis")
        col1, col2 = st.columns(2)
        with col1:
            fig, ax = plt.subplots()
            sns.histplot(df['sentiment'], ax = ax)
            st.pyplot(fig)
        with col2:
            sentiment_counts = df['sentiment'].value_counts()
            fig, ax = plt.subplots()
            sentiment_counts.plot.pie(autopct = "%1.1f%%", colors = ["skyblue", "lightgreen", "salmon"], ax = ax)
            ax.set_title("Sentiment Distribution")
            ax.set_ylabel("")  # Remove y-axis label
            st.pyplot(fig)

        # Time frame segment
        st.header("Time Frame")
        col3, col4 = st.columns(2)
        with col3:
            fig, ax = plt.subplots()
            sns.histplot(df['total_months'], kde = True, ax = ax)
            ax.set_title("Distribution of Total Months")
            ax.set_xlabel("Months")
            ax.set_ylabel("Frequency")
            st.pyplot(fig)
            fig, ax = plt.subplots()
        with col4:
            fig, ax = plt.subplots()
            sns.histplot(df['total_years'], kde = True, ax = ax)
            ax.set_title("Distribution of Total Years")
            ax.set_xlabel("Years")
            ax.set_ylabel("Frequency")
            st.pyplot(fig)

        # Most Common Emojis segment
        st.header("Most Common Emojis")
        top_emojis = emoji_df.head()
        col5, col6 = st.columns(2)
        with col5:
            fig = px.bar(
                    top_emojis,
                    x="emoji",
                    y="count",
                    text="count",
                    title="Top 5 Most Common Emojis",
                    labels={"emoji": "emoji", "count": "frequency"},
                    color="count",
                    color_continuous_scale="Viridis",
                )
            fig.update_traces(textposition="outside", marker_line_width=1.5, marker_line_color="black")
            st.plotly_chart(fig)
        with col6:
            fig = px.pie(
                    top_emojis,
                    values = 'count',
                    names = 'emoji',
                    title = "Top 5 most common Emojis",
                    color_discrete_sequence=px.colors.qualitative.Set2,
                )
            st.plotly_chart(fig)

        # Most Common Words segment
        st.header("Most Common Words")
        col7, col8 = st.columns(2)
        with col7:
            st.dataframe(common_words_df.head(8))
        with col8:
            df['cleaned'] = df['Comment'].apply(helper.clean_text)
            joined_words = " ".join(df['cleaned'])
            wordcloud = WordCloud(width=1100, height=950, background_color="white", colormap="viridis").generate(joined_words)
            # Display the word cloud
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wordcloud, interpolation="bilinear")
            ax.axis("off")  # Remove axes
            st.pyplot(fig)
            

    else:
        st.header("Please Enter a valid URL")
