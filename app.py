from flask import Flask, render_template, request, jsonify
import re
import emoji
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from googleapiclient.discovery import build
from collections import Counter

app = Flask(__name__)

# Set up YouTube Data API key
API_KEY = "AIzaSyCX-uXhUicGES1H6WEn9ZL11jUGs0QvxGI"
youtube = build("youtube", "v3", developerKey=API_KEY)


# Function to fetch all comments from a YouTube video
def fetch_all_comments(video_id):
    comments = []
    nextPageToken = None
    while True:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,  # Fetch up to 100 comments per request
            pageToken=nextPageToken,
        )
        response = request.execute()
        for item in response["items"]:
            comment = item["snippet"]["topLevelComment"]["snippet"]
            comments.append(comment["textDisplay"])
        nextPageToken = response.get("nextPageToken")
        if not nextPageToken:
            break
    return comments


# Function to preprocess comments and filter relevant ones
def preprocess_comments(comments):
    relevant_comments = []
    hyperlink_pattern = re.compile(
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
    )
    threshold_ratio = 0.65
    for comment_text in comments:
        comment_text = comment_text.lower().strip()
        emojis = emoji.emoji_count(comment_text)
        text_characters = len(re.sub(r"\s", "", comment_text))
        if (
            any(char.isalnum() for char in comment_text)
        ) and not hyperlink_pattern.search(comment_text):
            if (
                emojis == 0
                or (text_characters / (text_characters + emojis)) > threshold_ratio
            ):
                relevant_comments.append(comment_text)
    return relevant_comments


# Function to perform sentiment analysis
def analyze_sentiment(comments):
    analyzer = SentimentIntensityAnalyzer()
    positive_comments = []
    negative_comments = []
    neutral_comments = []
    for comment in comments:
        sentiment_scores = analyzer.polarity_scores(comment)
        if sentiment_scores["compound"] > 0.05:
            positive_comments.append(comment)
        elif sentiment_scores["compound"] < -0.05:
            negative_comments.append(comment)
        else:
            neutral_comments.append(comment)
    return positive_comments, negative_comments, neutral_comments


# Function to find comments containing suggestions
def find_suggestions(comments):
    suggestion_phrases = [
        r"should",
        r"would be better if",
        r"could try",
        r"might consider",
        r"why dont you",
        r"if I were you",
        r"have you thought about",
        r"perhaps you could",
        r"I suggest",
        r"my suggestion is",
        r"it would be great if",
    ]
    suggestion_pattern = "|".join(suggestion_phrases)
    suggestion_comments = [
        comment
        for comment in comments
        if re.search(suggestion_pattern, comment, re.IGNORECASE)
    ]
    return suggestion_comments


# Function to find comments containing suggestion keywords
def find_suggestion_comments(comments):
    suggestion_keywords = [
        "suggest",
        "recommend",
        "should",
        "would be better if",
        "could try",
        "might consider",
    ]
    suggestion_comments = [
        comment
        for comment in comments
        if any(keyword in comment.lower() for keyword in suggestion_keywords)
    ]
    return suggestion_comments


# Function to find the most frequently discussed words in comments
def find_most_frequent_words(comments):
    comments = [comment.lower() for comment in comments]
    words = []
    for comment in comments:
        words.extend(re.findall(r"\b[a-z]+\b", comment))
    word_counts = Counter(words)
    most_common_words = word_counts.most_common(10)
    return most_common_words


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/sentiment_analysis", methods=["POST"])
def sentiment_analysis():
    # Handle AJAX request for sentiment analysis
    video_url = request.form["video_id"]
    pattern = r"(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(pattern, video_url)
    video_id = match.group(1)
    comments = fetch_all_comments(video_id)
    relevant_comments = preprocess_comments(comments)
    positive_comments, negative_comments, neutral_comments = analyze_sentiment(
        relevant_comments
    )

    # Find comments with suggestions
    suggestion_comments = find_suggestions(relevant_comments)

    # Find suggestion comments using keywords
    keyword_suggestion_comments = find_suggestion_comments(relevant_comments)

    # Find most frequent words
    frequent_words = find_most_frequent_words(relevant_comments)

    # Count the number of positive, negative, and neutral comments
    positive_count = len(positive_comments)
    negative_count = len(negative_comments)
    neutral_count = len(neutral_comments)

    # Calculate overall sentiment score
    overall_sentiment_score = (
        (positive_count - negative_count) / len(relevant_comments)
        if relevant_comments
        else 0
    )

    sentiment_data = {
        "video_id": video_id,
        "positive_count": positive_count,
        "positive_comments": positive_comments,
        "negative_count": negative_count,
        "negative_comments": negative_comments,
        "neutral_count": neutral_count,
        "neutral_comments": neutral_comments,
        "overall_sentiment_score": overall_sentiment_score,
        "suggestion_comments": suggestion_comments,
        "keyword_suggestion_comments": keyword_suggestion_comments,
        "frequent_words": frequent_words,
    }
    return jsonify(sentiment_data)


if __name__ == "__main__":
    app.run(debug=True)
