import os
import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
import pytz

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

FEEDS = {
    "breaking": [
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://news.google.com/rss/headlines/section/topic/WORLD"
    ],
    "india": [
        "https://www.thehindu.com/news/national/feeder/default.rss",
        "https://indianexpress.com/section/india/feed/"
    ],
    "finance": [
        "https://search.cnbc.com/rs/search/view.html?partnerId=2000&keywords=markets&sort=date",
        "https://feeds.bloomberg.com/markets/news.rss"
    ],
    "crypto": [
        "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "https://cointelegraph.com/rss"
    ],
    "viral": [
        "https://trends.google.com/trends/trendingsearches/daily/rss?geo=IN",
        "https://trends.google.com/trends/trendingsearches/daily/rss?geo=US"
    ]
}

def fetch_rss_titles(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            root = ET.fromstring(resp.read())
            items = []
            for item in root.findall('.//item')[:12]:
                title = item.find('title')
                if title is not None and title.text:
                    items.append(title.text.strip())
            return items
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

raw_data = {}
for category, urls in FEEDS.items():
    collected = []
    for u in urls:
        collected.extend(fetch_rss_titles(u))
    raw_data[category] = list(set(collected))[:20]

ist = pytz.timezone('Asia/Kolkata')
now = datetime.now(ist)
edition = "morning" if now.hour < 12 else "evening"

system_prompt = f"""
You are the intelligence engine of 'News Crux'. Synthesize these raw news items into a strictly verified, dual-language briefing.
Enforce these point constraints:
- breaking: exactly 10 points
- india: exactly 5 points
- finance: exactly 10 points
- crypto: exactly 10 points
- viral: exactly 10 points

Generate BOTH English ('en') and Hindi ('hi') versions.
Hindi points must be formal, journalistic (शुद्ध और स्पष्ट समाचार भाषा).
Each bullet must begin with its number (e.g., '1. ', '2. ').

Output ONLY valid JSON matching this exact structure:
{{
  "edition": "{edition}",
  "timestamp": "{now.isoformat()}",
  "en": {{
    "breaking": ["1. ...", "2. ..."],
    "india": ["1. ..."],
    "finance": ["1. ..."],
    "crypto": ["1. ..."],
    "viral": ["1. ..."]
  }},
  "hi": {{
    "breaking": ["1. ...", "2. ..."],
    "india": ["1. ..."],
    "finance": ["1. ..."],
    "crypto": ["1. ..."],
    "viral": ["1. ..."]
  }}
}}
"""

gemini_payload = {
    "contents": [{
        "parts": [
            {"text": system_prompt},
            {"text": f"Raw News Feeds:\n{json.dumps(raw_data)}"}
        ]
    }],
    "generationConfig": {
        "response_mime_type": "application/json",
        "temperature": 0.2
    }
}

req = urllib.request.Request(
    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}",
    data=json.dumps(gemini_payload).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)

with urllib.request.urlopen(req) as resp:
    result = json.loads(resp.read().decode('utf-8'))
    raw_json_text = result['candidates'][0]['content']['parts'][0]['text']
    parsed_briefing = json.loads(raw_json_text)

os.makedirs("data", exist_ok=True)
with open("data/news-crux.json", "w", encoding="utf-8") as f:
    json.dump(parsed_briefing, f, ensure_ascii=False, indent=2)

print("Briefing generated successfully.")
