#!/usr/bin/env python3
"""daily_news_brief.py — deterministic collection layer for the daily-news-brief skill.

Collects, filters, dedupes, categorizes, and formats a candidate news brief from
curated publications (direct RSS + Bing News RSS for Bloomberg/Reuters), with a
clickable markdown citation + article date on every item. The agent layer then:
curates/ranks the candidates, polishes summaries, cross-verifies single-source
hard numbers (casualties etc.), saves to the vault, and delivers.

Output: markdown candidate brief on stdout (cron `script` injects it into the
agent prompt verbatim). Exit 0 unless ALL sources fail. Stdlib only (py3.9+).
"""

import html
import re
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
TIMEOUT = 20
AGE_HOURS = 36          # keep items newer than this
DESC_LIMIT = 320        # max summary chars carried from RSS

# (publisher, priority, feed_url) — priority decides which outlet "owns" a deduped story
FEEDS = [
    ("Bloomberg",  0, "https://www.bing.com/news/search?format=rss&q=site:bloomberg.com"),
    ("Reuters",    1, "https://www.bing.com/news/search?format=rss&q=source:reuters.com"),
    ("BBC",        2, "https://feeds.bbci.co.uk/news/world/rss.xml"),
    ("The Guardian", 3, "https://www.theguardian.com/world/rss"),
    ("Al Jazeera", 4, "https://www.aljazeera.com/xml/rss/all.xml"),
    ("Euronews",   5, "https://www.euronews.com/rss?level=theme&name=news"),
    ("NPR",        6, "https://feeds.npr.org/1001/rss.xml"),
    ("CNBC",       7, "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114"),
    ("The Verge",  8, "https://www.theverge.com/rss/index.xml"),
    ("TechCrunch", 9, "https://techcrunch.com/feed/"),
]

# Category sections in skill order; most keyword hits win. Unmatched -> Sport & Other.
CATEGORIES = [
    ("🌍 Geopolitics & War", [
        "war", "missile", "airstrike", "air strike", "strike", "bomb", "ceasefire",
        "troops", "israel", "gaza", "hamas", "ukraine", "russia", "putin",
        "kyiv", "iran", "tehran", "nato", "sanction", "hezbollah", "houthi", "west bank",
        "hebron", "idf", "diplomat", "peace talk", "border", "conflict", "hostage",
    ]),
    ("🌐 Disasters", [
        "earthquake", "typhoon", "hurricane", "cyclone", "flood", "storm", "wildfire",
        " tsunami", "landslide", "eruption", "power outage", "blackout", "rescu",
    ]),
    ("🇺🇸 US Politics", [
        "trump", "white house", "congress", "senate", "house republicans", "democrat",
        "supreme court", "election", "midterm", "voter", "washington", "governor",
        "pentagon", "ice raid", "immigration", "natasha", "musk", "senate race",
    ]),
    ("📈 Markets & Economy", [
        "stock", "s&p", "nasdaq", "dow", "yield", "inflation", "fed ", "federal reserve",
        "rate cut", "rate hike", "oil", "crude", "brent", "gold", "dollar", "bond",
        "economy", "gdp", "tariff", "recession", "treasury", "pmi", "earnings season",
    ]),
    ("💻 Technology & AI", [
        " ai", "ai ", "openai", "anthropic", "artificial intelligence", "chatbot",
        "model", "nvidia", "chip", "semiconductor", "data center", "microsoft",
        "google", "meta", "apple", "android", "software", "cyber", "hack",
        "vulnerability", "robot", "autonomous", "spacex", "tesla", "quantum",
    ]),
    ("🏢 Business", [
        "merger", "acquisition", "acquire", "ipo", "earnings", "revenue", "profit",
        "ceo", "layoff", "startup", "funding", "raises", "billion", "valuation",
        "investment", "company", "industry", "union strike", "labor",
    ]),
]
OTHER = "🏅 Sport & Other"


def fetch(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA, "Accept": "application/rss+xml, application/xml, text/xml, */*",
        "Accept-Encoding": "identity",
    })
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        data = r.read()
    return data.decode("utf-8", "replace")


def clean(text):
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", html.unescape(text))
    text = re.sub(r"\s+", " ", text).strip()
    for junk in ("Read more", "Sign in", "Subscribe"):
        text = re.split(rf"\b{junk}\b", text)[0].strip()
    if len(text) > DESC_LIMIT:
        cut = text.rfind(".", 0, DESC_LIMIT)
        text = (text[: cut + 1] if cut > 120 else text[:DESC_LIMIT].rsplit(" ", 1)[0] + "…")
    return text


def unwrap_bing(link):
    """Bing News RSS wraps items in apiclick.aspx?...&url=<encoded original>&..."""
    if "apiclick.aspx" in link and "url=" in link:
        q = urllib.parse.parse_qs(urllib.parse.urlsplit(link).query)
        if q.get("url"):
            return q["url"][0]
    return link


ATOM = "{http://www.w3.org/2005/Atom}"


def parse_feed(raw, publisher, priority, now):
    items = []
    root = ET.fromstring(raw)
    nodes = root.findall(".//item")
    if nodes:
        for it in nodes:
            title = (it.findtext("title") or "").strip()
            link = (it.findtext("link") or "").strip()
            desc = clean(it.findtext("description") or "")
            date = None
            for tag in ("pubDate", "dc:date", "date"):
                v = it.findtext(tag)
                if v:
                    try:
                        date = parsedate_to_datetime(v.strip())
                        break
                    except (ValueError, TypeError):
                        pass
            if title and link:
                items.append((publisher, priority, title, link, desc, date))
    else:  # Atom
        for it in root.findall(f".//{ATOM}entry"):
            title = (it.findtext(f"{ATOM}title") or "").strip()
            link = ""
            for l in it.findall(f"{ATOM}link"):
                if l.get("rel") in (None, "alternate"):
                    link = l.get("href", "")
                    break
            desc = clean(it.findtext(f"{ATOM}summary") or it.findtext(f"{ATOM}content") or "")
            date = None
            v = it.findtext(f"{ATOM}updated") or it.findtext(f"{ATOM}published")
            if v:
                try:
                    date = datetime.fromisoformat(v.strip().replace("Z", "+00:00"))
                except ValueError:
                    pass
            if title and link:
                items.append((publisher, priority, title, link, desc, date))
    # filter age + tidy
    cutoff = now - timedelta(hours=AGE_HOURS)
    out = []
    for pub, pri, title, link, desc, date in items:
        link = html.unescape(unwrap_bing(link))
        if "news.google.com" in link:      # opaque redirect, not a real citation
            continue
        if date and date.tzinfo and date < cutoff:
            continue
        out.append({
            "publisher": pub, "priority": pri,
            "title": re.sub(r"\s+", " ", html.unescape(title)).strip(),
            "url": link, "desc": desc,
            "date": date.astimezone() if date else None,
            "key": re.sub(r"[^a-z0-9]", "", title.lower())[:60],
        })
    return out


def categorize(item):
    hay = (" " + item["title"] + " " + item["desc"]).lower()
    best, score = OTHER, 0
    for name, kws in CATEGORIES:
        hits = sum(1 for k in kws if k in hay)
        if hits > score:
            best, score = name, hits
    return best


def fmt_date(dt):
    return dt.strftime("%b %-d, %Y") if dt else "date unverified"


def main():
    now = datetime.now(timezone.utc)
    local = datetime.now()
    results, failures = [], []
    prio = {p: pr for p, pr, _ in FEEDS}

    with ThreadPoolExecutor(max_workers=6) as pool:
        fut = {pool.submit(fetch, url): pub for pub, pri, url in FEEDS}
        for f in as_completed(fut):
            pub = fut[f]
            try:
                results.extend(parse_feed(f.result(), pub, prio[pub], now))
            except Exception as e:  # noqa: BLE001 — report, keep going
                failures.append(f"{pub}: {type(e).__name__} {e}")

    # dedupe by title key; keep highest-priority outlet, record co-reporters
    by_key = {}
    for it in sorted(results, key=lambda x: x["priority"]):
        k = it["key"]
        if k in by_key:
            ex = by_key[k]
            if it["publisher"] not in ex["also"]:
                ex["also"].append(it["publisher"])
        else:
            it["also"] = []
            by_key[k] = it
    items = list(by_key.values())
    for it in items:
        it["category"] = categorize(it)

    sections = {}
    for it in items:
        sections.setdefault(it["category"], []).append(it)
    ordered_names = [n for n, _ in CATEGORIES] + [OTHER]

    lines = []
    lines.append(f"# Daily News Brief — candidate pool — {local.strftime('%A, %B %-d, %Y')}")
    lines.append("")
    lines.append(f"Generated {local.strftime('%-I:%M %p %Z')} · window {AGE_HOURS}h · "
                 f"{len(items)} unique stories from {len(FEEDS) - len(failures)}/{len(FEEDS)} sources. "
                 "Summaries are outlet RSS text; AGENT: verify single-source hard numbers "
                 "(casualties, index levels) against Reuters/AP/BBC/Al Jazeera before saving, "
                 "rank by impact, keep the final format identical to the skill spec.")
    lines.append("")
    if failures:
        lines.append("SOURCE FAILURES: " + "; ".join(failures))
        lines.append("")
    for name in ordered_names:
        bucket = sections.get(name)
        if not bucket:
            continue
        bucket.sort(key=lambda x: (-len(x["also"]), -(x["date"].timestamp() if x["date"] else 0)))
        lines.append(f"## {name}  ({len(bucket)})")
        for it in bucket[:12]:
            cited = f"([{it['publisher']}]({it['url']}) — {fmt_date(it['date'])})"
            extra = f" [+{len(it['also'])}: {', '.join(it['also'])}]" if it["also"] else ""
            desc = f" — {it['desc']}" if it["desc"] else ""
            lines.append(f"- **{it['title']}**{desc} {cited}{extra}")
        lines.append("")
    lines.append(f"[spec: skill daily-news-brief v{version()} · deterministic collection layer]")
    print("\n".join(lines))
    if failures and len(failures) == len(FEEDS):
        sys.exit(2)  # total outage -> surface as script error


def version():
    return "1.1.0"


if __name__ == "__main__":
    main()
