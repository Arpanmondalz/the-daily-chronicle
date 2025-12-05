import feedparser
import json
import requests
import time
from bs4 import BeautifulSoup

API_KEY = os.environ.get("GEMINI_API_KEY") 

if not API_KEY:
    raise ValueError("No API Key found in environment variables!")

MODEL_ID = "gemini-2.5-flash" 
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_ID}:generateContent?key={API_KEY}"

# RSS Feeds 
RSS_FEEDS = [
    "https://www.sciencedaily.com/rss/top/science.xml",     # Science -> Alchemy/Magic
    "https://www.theverge.com/rss/index.xml",               # Tech -> Gadgets/Artifacts
    "http://feeds.bbci.co.uk/news/world/rss.xml",           # World -> Kingdoms/Empires
    "https://www.cnbc.com/id/100003114/device/rss/rss.html" # Business -> Merchants/Gold
]

OUTPUT_FILE = "news.json"

# --- 1. HELPER FUNCTIONS ---

def clean_html(html_text):
    """Basic cleanup to remove HTML tags from RSS descriptions."""
    if not html_text: return ""
    try:
        soup = BeautifulSoup(html_text, "html.parser")
        return soup.get_text()
    except:
        return html_text

def fetch_news_candidates(limit=5):
    """Fetches and deduplicates news items from RSS."""
    print(f"[CRON] Fetching news from {len(RSS_FEEDS)} feeds...")
    candidates = []
    
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            # Take top 2 from each feed
            for entry in feed.entries[:2]:
                summary = entry.get('description', '') or entry.get('summary', '')
                candidates.append({
                    "id": entry.link,
                    "headline": entry.title,
                    "summary": clean_html(summary)[:300] # Truncate for token saving
                })
        except Exception as e:
            print(f"[ERROR] Failed to fetch {url}: {e}")

    # Deduplicate by headline
    unique = []
    seen = set()
    for item in candidates:
        if item['headline'] not in seen:
            unique.append(item)
            seen.add(item['headline'])
            
    print(f"[CRON] Found {len(unique)} unique items. Keeping top {limit}.")
    return unique[:limit]

# --- 2. GEMINI API CALL (REST) ---

def generate_fantasy_news(news_items):
    print("[CRON] Preparing payload for Gemini...")
    
    # System Instructions (The "Grand Chronicler" Persona)
    system_instruction = """
    You are the Grand Chronicler. 
    Task: Rewrite real news into medieval fantasy.
    Safety: SKIP items about death, violence, hate, tragedy, or sensitive politics.
    
    STYLE RULES FOR SAFE ITEMS:
    - Tone: Accessible fantasy (like Harry Potter or Studio Ghibli), not Shakespearean.
    - Language: Use simple, modern English but keep the fantasy concepts. 
      - BAD: "Hark! The alchemists hath concocted a draught..."
      - GOOD: "The Alchemists' Guild has brewed a new potion..."
    - Map concepts:
      - Scientists -> Alchemists, Wizards
      - Companies -> Guilds, Clans
      - Tech -> Magic, Artifacts, Enchantments
      - Money -> Gold Coins
    - Constraints:
      - FANTASY_HEADLINE: max 12 words, catchy.
      - FANTASY_STORY: 2-4 sentences, max 80 words.

    
    OUTPUT FORMAT:
    - Valid JSON only. NO Markdown.
    - Schema: 
    { 
      "stories": [ 
        { 
          "id": "...", 
          "status": "published"|"skipped", 
          "reason": "...", 
          "original_headline": "...", 
          "original_summary": "...", 
          "fantasy_headline": "...", 
          "fantasy_story": "...", 
          "tag": "magic"|"kingdom"|"merchants"|"nature" 
        } 
      ] 
    }
    """

    # Prepare Payload
    user_content = json.dumps({"items": news_items})
    
    payload = {
        "contents": [{
            "parts": [
                {"text": system_instruction},
                {"text": f"Here are the news items to process:\n{user_content}"}
            ]
        }],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }

    try:
        # Execute HTTP Request
        response = requests.post(
            API_URL, 
            headers={"Content-Type": "application/json"}, 
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"[ERROR] Gemini API returned {response.status_code}: {response.text}")
            return None
            
        # Parse Response
        result = response.json()
        text_response = result['candidates'][0]['content']['parts'][0]['text']
        return json.loads(text_response)

    except Exception as e:
        print(f"[ERROR] API Request failed: {e}")
        return None

# --- 3. MAIN EXECUTION ---

def main():
    print(f"--- Starting Job at {time.strftime('%Y-%m-%d %H:%M:%S')} ---")
    
    # A. Fetch
    items = fetch_news_candidates(limit=5)
    if not items:
        print("[CRON] No items found. Exiting.")
        return

    # B. Process
    fantasy_data = generate_fantasy_news(items)
    
    if fantasy_data:
        # C. Filter & Save
        published_stories = [
            s for s in fantasy_data.get("stories", []) 
            if s.get("status") == "published"
        ]
        
        final_output = {
            "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
            "stories": published_stories
        }

        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(final_output, f, indent=2, ensure_ascii=False)
            
        print(f"[CRON] Success! Saved {len(published_stories)} stories to {OUTPUT_FILE}")
        
    else:
        print("[ERROR] Failed to generate content.")

if __name__ == "__main__":
    main()
