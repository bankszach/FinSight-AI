import os
import openai
import re
import backoff
import unicodedata
import string
from . import cache
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

CATS = ["Groceries", "Dining", "Fuel", "Utilities", "Subscriptions", "Insurance",
        "Shopping", "Entertainment", "Medical", "Transportation", "Services",
        "Credit Card", "Rent", "Car Payment", "Income", "Refund"]

def clean_vendor(v: str) -> str:
    """Normalize vendor name to ASCII, uppercase, and remove punctuation."""
    v = unicodedata.normalize("NFKD", v).encode("ascii","ignore").decode()
    v = v.upper().translate(str.maketrans("","", string.punctuation))
    v = re.sub(r"\s{2,}", " ", v)
    return v.strip()[:30]

# Validate API key format (supports both old and new project-scoped keys)
api_key = os.getenv("OPENAI_API_KEY")
if not api_key or not re.match(r'^sk(-proj)?-[A-Za-z0-9_-]{20,}$', api_key):
    raise ValueError("Invalid OPENAI_API_KEY format")

openai.api_key = api_key
openai.base_url = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

PROMPT = """You are a personal finance assistant.
Return ONE category from this list:
{cats}
and a concise vendor name (≤30 chars), separated by " | ".
If unsure, pick "Services".
Description: "{desc}"
""".format(cats=", ".join(CATS), desc="{desc}")

@backoff.on_exception(backoff.expo,
                     (openai.RateLimitError, openai.APIError),
                     max_time=60)
def _chat(messages: list[dict]) -> str:
    # Safety check for token limit
    if len(messages[0]["content"].split()) > 9000:
        return "Services | " + messages[0]["content"][:30]
        
    resp = openai.chat.completions.create(
        model=MODEL,
        temperature=0,
        max_tokens=8,
        response_format={"type": "text"},
        messages=messages)
    return resp.choices[0].message.content.strip()

def classify(description: str) -> tuple[str, str]:
    # 1️⃣ cache lookup
    hit = cache.get(description)
    if hit:
        return hit
    
    # 2️⃣ call OpenAI with backoff retry
    msg = PROMPT.format(desc=description.replace('"', ''))
    text = _chat([{"role": "user", "content": msg}])
    
    # Expected format: Category | Vendor
    m = re.match(r"([^|]+)\|\s*(.+)", text)
    category, vendor = (m.group(1).strip(), m.group(2).strip()) if m else ("Services", description[:30])
    
    # Normalize vendor name before caching
    vendor = clean_vendor(vendor)
    
    # 3️⃣ write cache
    cache.put(description, category, vendor)
    return category, vendor

def batch_classify(descriptions: list[str]) -> list[tuple[str, str]]:
    """Classify multiple descriptions in batches of 50."""
    results = []
    for i in range(0, len(descriptions), 50):
        batch = descriptions[i:i+50]
        for desc in batch:
            results.append(classify(desc))
    return results 