import os
from flask import Flask, send_from_directory, jsonify, request
import requests
from bs4 import BeautifulSoup
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/search": {"origins": ["https://pfmcodes.sytes.net", "https://pfmcodes.tiiny.site", "https://localhost:8000"]}})

def scrape_data(query, max_results=10):
    """Scrape search results from Bing."""
    search_results = []
    base_url = "https://www.bing.com/search"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(base_url, params={"q": query}, headers=headers, timeout=5)
        response.raise_for_status()
    except requests.RequestException as e:
        return {"error": f"Failed to fetch search results: {str(e)}"}

    soup = BeautifulSoup(response.text, 'html.parser')

    for item in soup.find_all('li', class_='b_algo'):
        title_tag = item.find('h2')
        link_tag = item.find('a')
        desc_tag = item.find('p')

        title = title_tag.get_text(strip=True) if title_tag else "No Title"
        link = link_tag['href'] if link_tag and link_tag.has_attr('href') else "#"
        description = desc_tag.get_text(strip=True) if desc_tag else "No description available."

        # Generate favicon URL (ensure valid domain)
        domain = link.split('/')[2] if link.startswith('http') else ''
        logo = f"https://www.google.com/s2/favicons?domain={domain}" if domain else ""

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
    return send_from_directory('.', 'index.html')  # Serve frontend

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '').strip()
    if query:
        search_results = scrape_data(query)
        return jsonify(search_results)
    return jsonify({"error": "No query provided"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # Render assigns a dynamic port
    app.run(host='0.0.0.0', port=port, debug=True)
