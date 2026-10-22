---
name: notion-meeting-transcripts
description: "Read Notion meeting pages/transcripts; find pages by title."
version: 1.4.0
author: Greggy (Hermes Agent)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [notion, meetings, transcripts, connector]
---

# Notion Meeting Transcripts

## When to Use
Greg shares a Notion page link to a recorded meeting (e.g. "RFSmart Meeting") — or asks to FIND a meeting page by name — and wants its summary/transcript read, summarized, or copied to the vault. Web extraction hits a login wall — always use the Notion connector tools instead.

## Procedure
1. Extract the 32-hex page ID from the URL (`/p/<Title>-<ID>`).
2. `connectors__notion__FETCH_BLOCK_CONTENTS` on the page ID (parameter name is `block_id`, not `page_id`) → look for a block of `type: "transcription"`. Its `transcription.children` gives `summary_block_id`, `notes_block_id`, `transcript_block_id`; `transcription.recording.start_time` is the meeting start.
3. Fetch the **summary** block for the structured recap (headings, to-dos with owners, bullets, quotes). Fetch the **transcript** block only if raw dialogue is needed — it paginates at 100 blocks (pass `start_cursor`/`page_size`).
4. Large transcript fetches spill to a file — parse the JSON with code, don't re-request.
5. Deliver the summary in chat. Loomstate meeting summaries are filed routinely into the vault (obsidian skill routing: WMS/shipping meetings → `Companies/Loomstate/WMS Project/Shipping/` — Greg consolidated all meeting summaries into the Shipping subfolder), matching sibling naming `Title_Summary_YYYY-MM-DD.md`; file directly and state the path, don't ask whether to save.
6. Verbatim vs restructured: when Greg asks for the summary itself ("the exact version that is in Notion, not the one you summarized"), copy the summary block verbatim into a SEPARATE dated file (e.g. `Title_Notion_Summary_YYYY-MM-DD.md`) alongside the restructured note — don't replace it. Preserve Notion's block order, bold/italic marks, to-do checkboxes, and dividers; fetch children of nested bullets (they're omitted from top-level fetches); flag inline when the API returns empty table cells (Notion tables often don't serialize — the rows are only visible on the page).

## Images/slides in the page
- Images appear as `image` blocks (they can be added AFTER the meeting — re-fetch if Greg references a newly inserted slide).
- `image.file.url` is a signed S3 URL expiring ~1 hour — curl it immediately, save into the note's sibling `attachments/` folder, verify PNG magic bytes + vault-unique name, embed with a vault-root wikilink `![[Companies/.../attachments/file.png]]`.
- Caption/outline the slide via vision_analyze (the model cannot see images inline in the note).

## Finding a page when Greg gives only a name (no URL)
1. `connectors__notion__SEARCH_NOTION_PAGE` with the exact title, then progressively looser single tokens ("RFSmart_Meeting_Summary" → "RFSmart" → "RF Smart"). Notion's title search tokenizes — compound/underscore-joined queries often return zero hits even when generic tokens ("meeting", "summary") match fine, so a zero-result query proves nothing.
2. If token searches miss, enumerate everything accessible: empty `query` with `page_size: 100`, follow `next_cursor` to exhaustion (one tool call per page).
3. Each enumeration page spills to a spillover file (~100 KB+) — parse all spillover JSONs with code, extracting titles from `properties.title.title[].plain_text` OR `properties.Name.title[].plain_text` (database rows use `Name`), and regex-filter client-side. Do not eyeball the previews.
4. If exhaustive enumeration still finds no match, the page simply isn't shared with the integration — tell Greg and ask him to share it (••• → Connections) and/or send the link; do not keep re-searching variants.

## Enumerating workspace structure ("what folders/pages are under X?")
1. Confirm authorization first: `manage_connections` action=status → the notion account must be `active`.
2. The connector has no block-children call for hierarchy navigation: enumerate with `FETCH_DATA` (`fetch_type: pages`, `page_size: 100`, follow `next_cursor` to exhaustion), then derive structure client-side — children of page X are entries whose `parent.page_id` equals X's page ID; `parent.type: workspace` marks top-level pages; entries whose parent is a `database_id` are database rows (filter out unless asked for).
3. Union ALL spillover files (this session + prior ones — large pages responses land in the spillover dir automatically) and dedupe by page ID before reporting; older files can re-cover the same pagination, and pages moved between pulls show stale parents — state that caveat when presenting structure.
4. Label the result the way the user framed it: Notion "folders" = pages-with-children; report titles + emoji icons, and distinguish top-level pages from children of the named hub page.

## Pitfalls
- 404 `object_not_found` = page not shared with integration "Hermes Capabilities" — ask Greg to share it (••• → Connections) rather than guessing content; he can do it in seconds.
- Title/date/user/page references come through as `mention` rich_text items — render their `plain_text`.
- Connector title-search may miss pages even when block fetch works after sharing (indexing lag), and pages not yet shared with the integration never appear in ANY search query. When a keyword hunt returns nothing, do not conclude the meeting page doesn't exist: crawl hub pages (recently-edited top-level pages, per the notion skill's workspace-survey workflow) with FETCH_BLOCK_CONTENTS and harvest hyperlinks from rich_text — meeting summaries often sit as href'd list items whose `/p/<Title>-<32hex>` URL yields the page ID; a fetch of that ID then distinguishes "needs sharing" (404 → ask Greg) from readable.
