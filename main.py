from flask import Flask, render_template, jsonify, request
import requests
from bs4 import BeautifulSoup
import json
from flask_cors import CORS  # Allow JavaScript requests

app = Flask(__name__)
CORS(app)  # Enables frontend to fetch from backend

def scrape_data(query, max_results=10):
    search_results = []
    base_url = "https://www.bing.com/search"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(base_url, params={"q": query}, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    for item in soup.find_all('li', class_='b_algo'):
        title = item.find('h2').get_text() if item.find('h2') else 'No Title'
        link = item.find('a')['href'] if item.find('a') else '#'
        description = item.find('p').text if item.find('p') else 'No description available.'
        logo = f"https://www.google.com/s2/favicons?domain={link}"  

        search_results.append({
            'title': title,
            'link': link,
            'logo': logo,
            'description': description
        })

        if len(search_results) >= max_results:
            break

    return search_results

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '').strip()
    if query:
        search_results = scrape_data(query)
        return jsonify(search_results)
    return jsonify({"error": "No query provided"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)