import os
import json
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime
import pytz

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

FEEDS = {
    "breaking": [
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "https://rss.nytimes.com/services/xml/rss/World.xml"
    ],
    "india": [
        "https://www.thehindu.com/news/national/feeder/default.rss",
        "https://timesofindia.indiatimes.com/rssfeeds/-2128936835.cms"
    ],
    "finance": [
        "https://www.cnbc.com/id/10000664/device/rss/rss.html",
        "https://finance.yahoo.com/news/rssindex"
    ],
    "crypto": [
        "https://www.coindesk.com/arc/outboundfeeds/rss/",
        "https://cointelegraph.com/rss"
    ],
    "viral": [
        "https://techcrunch.com/feed/",
        "https://www.theverge.com/rss/index.xml"
    ]
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}

def fetch_rss_titles(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=12) as resp:
            content = resp.read()
            root = ET.fromstring(content)
            items = []
            for item in root.findall('.//item')[:15]:
                title = item.find('title')
                if title is not None and title.text:
                    clean_title = title.text.strip().replace('\n', ' ')
                    if clean_title:
                        items.append(clean_title)
            return items
    except Exception as e:
        print(f"Skipping feed {url}: {e}")
        return []

raw_data = {}
for category, urls in FEEDS.items():
    collected = []
    for u in urls:
        collected.extend(fetch_rss_titles(u))
    # Deduplicate while preserving order
    seen = set()
    unique = []
    for item in collected:
        if item not in seen:
            seen.add(item)
            unique.append(item)
    raw_data[category] = unique[:15]
    print(f"Loaded {len(raw_data[category])} items for {category}")

ist = pytz.timezone('Asia/Kolkata')
now = datetime.now(ist)
edition = "morning" if now.hour < 12 else "evening"

system_prompt = f"""
You are the intelligence engine of 'News Crux'. Synthesize these raw news items into a strictly verified, dual-language briefing.
Enforce these exact point counts:
- breaking: exactly 10 points
- india: exactly 5 points
- finance: exactly 10 points
- crypto: exactly 10 points
- viral: exactly 10 points

Generate BOTH English ('en') and Hindi ('hi') versions.
Hindi points must be formal and journalistic (शुद्ध और स्पष्ट समाचार भाषा).
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
            {"text": f"Raw News Feeds:\n{json.dumps(raw_data, ensure_ascii=False)}"}
        ]
    }],
    "generationConfig": {
        "response_mime_type": "application/json",
        "temperature": 0.2
    }
}

# Try modern Gemini models with automated fallback
CANDIDATE_MODELS = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest"
]

parsed_briefing = None
payload_bytes = json.dumps(gemini_payload).encode('utf-8')

for model_name in CANDIDATE_MODELS:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={GEMINI_API_KEY}"
    print(f"Attempting model: {model_name}...")
    req = urllib.request.Request(
        url,
        data=payload_bytes,
        headers={'Content-Type': 'application/json'}
    )
    try:
        with urllib.request.urlopen(req, timeout=40) as resp:
            result = json.loads(resp.read().decode('utf-8'))
            raw_json_text = result['candidates'][0]['content']['parts'][0]['text']
            # Clean possible markdown wrap
            raw_json_text = raw_json_text.strip()
            if raw_json_text.startswith("```json"):
                raw_json_text = raw_json_text[7:]
            if raw_json_text.startswith("```"):
                raw_json_text = raw_json_text[3:]
            if raw_json_text.endswith("```"):
                raw_json_text = raw_json_text[:-3]
            parsed_briefing = json.loads(raw_json_text.strip())
            print(f"Success with {model_name}!")
            break
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode('utf-8', errors='ignore')
        print(f"Model {model_name} failed with HTTP {e.code}: {err_msg[:200]}")
    except Exception as e:
        print(f"Error querying {model_name}: {e}")

# If API fails, provide emergency synthesis so workflow never crashes
if not parsed_briefing:
    print("Warning: Falling back to feed passthrough mode.")
    parsed_briefing = {
        "edition": edition,
        "timestamp": now.isoformat(),
        "en": {
            "breaking": [f"{i+1}. {t}" for i, t in enumerate(raw_data.get("breaking", [])[:10])],
            "india": [f"{i+1}. {t}" for i, t in enumerate(raw_data.get("india", [])[:5])],
            "finance": [f"{i+1}. {t}" for i, t in enumerate(raw_data.get("finance", [])[:10])],
            "crypto": [f"{i+1}. {t}" for i, t in enumerate(raw_data.get("crypto", [])[:10])],
            "viral": [f"{i+1}. {t}" for i, t in enumerate(raw_data.get("viral", [])[:10])]
        },
        "hi": {
            "breaking": [f"{i+1}. {t}" for i, t in enumerate(raw_data.get("breaking", [])[:10])],
            "india": [f"{i+1}. {t}" for i, t in enumerate(raw_data.get("india", [])[:5])],
            "finance": [f"{i+1}. {t}" for i, t in enumerate(raw_data.get("finance", [])[:10])],
            "crypto": [f"{i+1}. {t}" for i, t in enumerate(raw_data.get("crypto", [])[:10])],
            "viral": [f"{i+1}. {t}" for i, t in enumerate(raw_data.get("viral", [])[:10])]
        }
    }

os.makedirs("data", exist_ok=True)
with open("data/news-crux.json", "w", encoding="utf-8") as f:
    json.dump(parsed_briefing, f, ensure_ascii=False, indent=2)

print("News Crux briefing written successfully.")
