from flask import Flask, request, render_template, jsonify
import requests
import os
from dotenv import load_dotenv
from transformers import pipeline
import openai

# Load environment variables
load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

app = Flask(__name__)

# Load summarization model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def get_top_headlines(query=None):
    base_url = "https://newsapi.org/v2/top-headlines" if not query else "https://newsapi.org/v2/everything"
    params = {
        "apiKey": NEWS_API_KEY,
    }
    if not query:
        params["country"] = "in"
    else:
        params["q"] = query
     # Fetch top 15 headlines for breaking news

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        articles = data.get('articles', [])
        return articles[:15] 
    except requests.exceptions.RequestException as e:
        return str(e)

def summarize_text(text):
    try:
        # Use the Hugging Face summarizer
        summaries = summarizer(text, max_length=450, min_length=100, do_sample=False)
        summary = summaries[0]['summary_text']
        return summary
    except Exception as e:
        return str(e)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        name = request.form.get('name')
        query = request.form.get('query')
        news_articles = get_top_headlines(query)

        if isinstance(news_articles, str):
            return render_template('index.html', error=news_articles, name=name, query=query)

        return render_template('index.html', name=name, query=query, articles=news_articles)
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    text = request.json.get('text')
    summary = summarize_text(text)
    return jsonify({'summary': summary})

@app.route('/breaking-news')
def breaking_news():
    articles = get_top_headlines()
    return jsonify({'articles': articles})

if __name__ == '__main__':
    app.run(debug=True)
