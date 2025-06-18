import requests
import pickle
from bs4 import BeautifulSoup
import json

def load_cookies():
    with open('discourse_cookies.pkl', 'rb') as f:
        return pickle.load(f)

def get_topics():
    cookies = load_cookies()
    cookies_dict = {c['name']: c['value'] for c in cookies}
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml'
    })
    
    # Fetch category page
    url = "https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb/34"
    response = session.get(url, cookies=cookies_dict)
    
    if response.status_code != 200:
        print(f"Failed to fetch topics. Status: {response.status_code}")
        return []
    
    # Parse HTML for topics
    soup = BeautifulSoup(response.text, 'html.parser')
    topics = []
    
    # Find all topic rows
    topic_rows = soup.find_all('tr', class_=lambda x: x and 'topic-list-item' in x and 'category-courses-tds-kb' in x)
    
    for row in topic_rows:
        try:
            # Get topic ID from tr attribute
            topic_id = row.get('data-topic-id')
            if not topic_id:
                continue
                
            # Find title link
            title_link = row.find('a', class_='title raw-link raw-topic-link')
            if not title_link:
                continue
                
            # Extract title text and href
            title = title_link.text.strip()
            relative_url = title_link.get('href')
            if not relative_url:
                continue
                
            topics.append({
                'id': topic_id,
                'title': title,
                'url': f"https://discourse.onlinedegree.iitm.ac.in{relative_url}"
            })
        except Exception as e:
            print(f"Error processing topic row: {e}")
            continue
    
    # Save to JSON
    with open('topics.json', 'w', encoding='utf-8') as f:
        json.dump(topics, f, indent=2, ensure_ascii=False)
    
    print(f"Found {len(topics)} topics. Saved to topics.json")
    return topics

if __name__ == "__main__":
    get_topics()