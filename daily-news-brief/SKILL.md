---
name: daily-news-brief
description: "Use for news briefs. Dated citations, categories, Bloomberg."
version: 1.1.0
author: Greggy (Hermes Agent)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [news, briefing, citations, Bloomberg, Obsidian]
---

# Daily News Brief

## When to Use
Requests for a "news brief", "top news summary", "AI brief", or daily digest — especially variants adding "by category", "with citations", "and dates", "Bloomberg", or "save to notetaker/News".

Greg repeatedly asks for top-news summaries by category (sometimes AI-only), from leading publications **with Bloomberg explicitly included**, with **citations AND article dates on every item**.

## Standing format spec
- Category sections with emoji headers: 🌍 Geopolitics & War · 🇺🇸 US Politics · 📈 Markets & Economy · 💻 Technology & AI · 🏢 Business · 🌐 Disasters · 🏅 Sport & Other. Drop empty categories; add others only if the day demands.
- Each item: **bold headline**, 1–3 sentence summary, inline citation `(Publication — Mon DD, YYYY)`. Publication name + article date on every item is mandatory, not optional. When the brief is saved (Obsidian) or delivered where markdown renders, make the publication name a clickable markdown link to the article: `([Bloomberg](https://bloomberg.com/news/articles/...) — Oct 13, 2026)` — keep the date outside the link; plain-text citations only when the channel can't render markdown.
- Publication mix: Bloomberg, Reuters, FT, BBC, Al Jazeera, AP, Euronews, Axios, TechCrunch, NBC, AFP, Democracy Now. Bold key figures/names.
- AI-only variant: same spec, Technology & AI section expanded with a head-to-head angle where sources conflict.

## Scripted collection layer (v1.1.0)
`scripts/daily_news_brief.py` (installed at `~/.hermes/scripts/daily_news_brief.py`) does the deterministic half: generates for now() so nothing is date-stale, fetches 10 outlets in parallel (Bloomberg + Reuters via Bing News RSS with apiclick-URL unwrapping to direct article links; BBC, Guardian, Al Jazeera, Euronews, NPR, CNBC, Verge, TechCrunch direct RSS), filters to a 36h window, dedupes near-identical titles, keyword-categorizes into the standing sections, and prints a markdown CANDIDATE POOL — every line already has **headline** — outlet summary — ([Publication](direct-url) — Mon DD, YYYY). The cron job (id efd0a62bb2aa) runs it via `script=` so stdout injects into the agent prompt; the agent then only curates, verifies, summarizes, saves, delivers. If the pool is missing/stale or its SOURCE FAILURES line names outlets, fall back to pure search below.

## Procedure
1. **Run `date` first.** "Today" may have rolled past midnight since the session started; re-search for the current day rather than reusing earlier brief data. Earlier briefs in the same conversation are stale the moment the date advances. Confirm the candidate pool header date matches.
2. If no candidate pool is present, run the script (`python3 ~/.hermes/scripts/daily_news_brief.py`); if it fails, batch parallel web_search in ONE response (independent queries):
   - `top world news <Month DD YYYY>`
   - `site:bloomberg.com <YYYY-MM-DD> news` (or `site:bloomberg.com <topic> <YYYY>`)
   - `markets stocks today <date> Reuters` — the Reuters Global Markets Data page carries live index levels and % changes worth quoting numerically
   - topic-specific queries when the user scopes narrower (AI, economy, etc.).
3. web_extract aggregator pages the search surfaces (Bloomberg homepage, `euronews.com/YYYY/MM/DD` day archives, Reuters section pages) to fill category gaps.
4. Dedupe across sources, rank by impact, write the brief. Date each citation from the URL slug (`/2026-10-12/`) or page byline — the slug is the most reliable signal; never date an item from vibes.
5. Major stories span days (e.g. a ceasefire announced Sunday and breaking Monday): keep both dates in the citation chain rather than flattening to one date.
6. **Always save the brief to the vault** (`~/Greggy-AI/News/YYYY-MM-DD.md`, spec below) — saving is the default, not opt-in; deliver the brief in chat AND write the note in the same run. Only skip if the user explicitly says not to save.

## Save-to-Obsidian spec (always runs)
When saving the brief to the Obsidian "News" folder with a date title (the default every run):
- Path: `~/Greggy-AI/News/YYYY-MM-DD.md` (folder may need creating; write_file auto-creates).
- Title line: `# Top News — <Weekday>, <Month DD, YYYY>`.
- Add a one-line source note under the title and a footer wikilink `[[YYYY-MM-DD]]` so the note joins the daily graph.
- Citations in the saved note MUST be clickable markdown links (see standing format spec): the URL comes from the web_search result that surfaced the story — never invent or guess article URLs; if no URL was captured during research, capture it with a targeted follow-up search before saving, else fall back to plain-text citation for that item. Copy URLs verbatim from the search result rather than retyping from memory, and after saving re-read the note to spot-check every link against the result set — patch truncated or mistyped URLs immediately; a broken link is a broken citation.
- Vault rules (path resolution, write conventions) governed by the obsidian skill.

## Pitfalls
## Pitfalls
- Cron variant (verified 2026-10-23): `deliver='all'` fails with "no delivery target resolved" when no messaging home channel is connected — use `deliver='local'`; the run still completes research + vault save, output also archived under `~/.hermes/cron/output/<job_id>/`. Verify after a test fire with cronjob list (`last_status`, `last_delivery_error`) + vault note mtime.
- Cross-check casualty figures, sports scores, and any hard number sourced ONLY from sketchy aggregators or propaganda mirror sites with one batched verification search restricted to majors (Reuters/AP/BBC/Al Jazeera/Guardian) before finalizing; when verified sources disagree on a toll, present it as a range with both sources cited rather than picking one.
- Resolve "today" with a live `date` call before the first search — a brief assembled from yesterday's searches reads fresh but is wrong, and Greg checks dates.
- Search snippets mix in stale articles (week-old market wraps appear under "today" queries); filter by URL-slug date and label genuinely continuing stories with their original date instead of dropping them.
- Publication prose often disagrees on which weekday an event fell (game days, announcement days); prefer raw dates over weekday labels, defer to the primary schedule/issuer source (league site, official press office) over article text, and when sources still conflict cite a raw-date range ("Oct 13–14") rather than asserting a weekday you cannot verify.
- When a Bloomberg/Reuters extract returns only navigation chrome, pivot to another aggregator — re-requesting the same URL wastes a turn.
- Verifying citation links with curl: use a FULL browser UA string (`Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)`), not bare `Mozilla/5.0` — aljazeera.com and euronews.com answer short/bot UAs with 404/406 while the URLs are fine in a real browser; reuters.com 401, nytimes.com 403, abs-cbn 403 are bot walls, not broken links. Only treat a link as broken when it 404s under a full UA. Search backends also display dates in URLs inconsistently (dashes vs slashes) — when a dated URL 404s under a full UA, toggle `/YYYY-MM-DD/` ↔ `/YYYY/MM/DD/` and retest before calling it broken; the slash variant usually recovers to 200 (verified on aljazeera.com, cnbc.com).
- Quote index levels (% and points) only from a dated market-data snapshot, not from memory of an earlier turn.
- When fixing a citation URL in a saved note, the `patch` tool's fuzzy matcher can report success with a no-change diff if old and new differ only in punctuation (dash vs slash). Verify the exact replacement string is on disk after any URL patch; if it no-oped, redo with exact string replacement in code (read file, `str.replace`, write back).
