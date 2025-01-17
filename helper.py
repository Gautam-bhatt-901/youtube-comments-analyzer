from datetime import datetime
from googleapiclient.discovery import build
from collections import Counter
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import emoji
from textblob import TextBlob
import streamlit as st
stop_words = stopwords.words('english')

youtube = build('youtube', 'v3', developerKey=st.secrets['api_key'])

def get_video_id(url):
    """Extract video ID from the YouTube URL."""
    if "v=" in url:
        return url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in url:
        return url.split("youtu.be/")[1]
    else:
        raise ValueError("Invalid YouTube URL")
    
def fetch_comments(video_url, max_comments=10000):
    video_id = get_video_id(video_url)
    comments_data = []
    next_page_token = None

    while len(comments_data) < max_comments:
        request = youtube.commentThreads().list(
            part='snippet',
            videoId=video_id,
            pageToken=next_page_token,
            maxResults=min(10000, max_comments - len(comments_data))
        )
        response = request.execute()
        for item in response.get('items', []):
            snippet = item['snippet']['topLevelComment']['snippet']
            comment = snippet['textDisplay']
            date = snippet['publishedAt']
            likes = snippet['likeCount']
            comments_data.append({'Comment': comment, 'Date': date, 'Likes': likes})

        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break

    return comments_data

def format_date(date):
    date_object = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
    return date_object.strftime("%d/%m/%Y")

def convert_month_year(date_str):
    # convert the input date string to a datetime object 
    date_obj = datetime.strptime(date_str, "%d/%m/%Y")
    # get the current date
    present_date = datetime.now()

    # Calculate total months and years relative to the present date
    total_months = (present_date.year - date_obj.year) * 12 + (present_date.month - date_obj.month)
    total_years = total_months // 12
    return total_months, total_years

def length_of_comments(comment):
    return len(comment.split())

def tokenize_data(text):
    # convert to lowercase
    text = text.lower()
    # remove special characters and numbers
    text = re.sub(r'[^a-z\s]', '', text)
    # word token
    text_tokenize = word_tokenize(text)
    # removing stopwords
    clean_text = [w for w in text_tokenize if not w in stop_words]
    return clean_text

def clean_text(text):
    # Remove emojis, special characters, and make lowercase
    text = re.sub(r"[^\w\s]", "", text)  # Remove punctuation
    text = re.sub(r"\d+", "", text)      # Remove numbers
    return text.lower()

def extract_emojis(text):
    return [char for char in text if char in emoji.EMOJI_DATA]

def analyze_sentiment(text):
    blob = TextBlob(text)
    # Polarity: -1 (negative) to 1 (positive)
    # Subjectivity: 0 (objective) to 1 (subjective)
    polarity = blob.sentiment.polarity

    if polarity > 0:
        return "Positive", polarity
    elif polarity == 0:
        return "Neutral", polarity
    else:
        return "Negative", polarity