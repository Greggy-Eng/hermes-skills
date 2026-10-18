---
name: omlx-admin
description: "Use to inspect/administer local oMLX: health, models, disk."
version: 1.1.0
author: Greggy (Hermes Agent)
license: MIT
platforms: [macos]
metadata:
  hermes:
    tags: [MLX, omlx, disk-usage, models, maintenance]
    related_skills: [local-mlx-benchmarking, desktop-plugins]
---

# oMLX Server Admin

## When to Use
Questions about the oMLX dashboard (Active Models card, Status/Settings/Models tabs), server health, which models are loaded/pinned, or "what's using disk in ~/.omlx". For speed tests/model comparisons → `local-mlx-benchmarking` (it owns the live-test procedure and vault save-to step).

## Server facts
- Server: `http://localhost:8000`; admin dashboard `/admin` (session auth) — Status tab = Active Models card + stats, Settings = global + per-model config (`is_pinned`, TTL), Models = load/unload/download/quantize (jundot/omlx).
- `GET /health` (no auth) returns `status`, `default_model`, and `engine_pool{model_count, loaded_count, final_ceiling, current_model_memory}` — ground truth for "what's warm in RAM" without the dashboard. OpenAI API key lives in the macOS keychain: `security find-generic-password -s omlx -a api-key -w`.
- Active-model semantics: models load on demand; eviction is TTL/LRU against the memory ceiling unless a model is pinned. "Active" = resident in RAM, not downloaded.

## Disk layout (`~/.omlx`)
- `models/<vendor>/<model>/` — safetensors weights (the real footprint).
- `cache/_gdn_sidecars/<sha256>/` — gated-delta-net layer sidecars auto-derived for Qwen3-Next-hybrid models; content-hash keyed, NOT mappable to model dirs by name, and often the single largest item.
- `cache/<hex-bucket 0-f>/` — download/quant blob cache backing the model copies.
- `stats.json` — `per_model` all-time request/token totals (usage ranking); `usage.sqlite3` table `model_usage_hourly` for time-sliced usage.
- `model_settings.json` — shape `{"models": {"<ModelName>": {"is_pinned": bool, …}}}` (top-level `models` key, model names are refs not paths).

## SSD/GDN cache maintenance ("clean the cache")
- `~/.omlx/cache` = live paged-SSD KV cache (hex buckets `0`-`f`, per-file block-hash names, LRU) + `_gdn_sidecars/` (fp32 GDN checkpoints, dir = sha256 of JSON cache_signature {model_name,num_layers,block_size,layer_cache_types,...}). These are NOT weight copies — they are derived warm-cache data, safe to wipe wholesale; cost is slower first prefills while they rebuild.
- `cache.ssd_cache_max_size = "auto"` reserves HALF of available cache space — huge on big volumes; set an explicit cap (e.g. "64GB") to bound growth.
- Native clear: `POST /admin/api/ssd-cache/clear` (admin prefix `/admin` required) with `Authorization: Bearer <keychain api-key>` (`security find-generic-password -s omlx -a api-key -w`). Deletes KV blocks + all sidecar sets, works while loaded.
- Global settings API is FLAT: `POST /admin/api/global-settings` with flat fields (`{"ssd_cache_max_size":"64GB"}`) — NOT the nested section shape that GET returns. Echoing the GET body back validates as all-null and silently no-ops (says "saved" anyway). Verify by grepping `settings.json`; `runtime_applied:["cache"]` = live without restart.
- Server shutdown rewrites settings.json from memory: any direct file edit while the server runs gets clobbered at quit. Always persist via the POST endpoint while running (or edit the file while fully stopped).
- Server.log lines `SSD cache scan complete: skipped_incompatible=N (X GB)` quantify signature-invalidated garbage (e.g. after GDN numerics revisions) that the engine never reuses — dead weight until cleared.
- Don't hand-delete individual sidecar hash dirs hoping to hit orphans — attribution needs signature reconstruction; prefer the native clear + cap.

## Disk audit procedure ("what's using space?")
1. `du -sh ~/<dir>/* | sort -rh` at the level the user asked about, then drill one level deeper per hot dir (`models/*/*`, `cache/_gdn_sidecars/*`).
2. Rank usage: parse `stats.json` `per_model` by `requests` descending.
3. Join size × usage × pin state into one table: big + few requests = top cleanup candidate; `stats.json` names with no matching `models/` dir = orphaned (their blobs/sidecars are likely dead weight).
4. Report: table (size | requests | pinned) + prioritized removal candidates. Say plainly that nothing pinned-only-in-RAM means disk is the only cost — eviction frees RAM, deletion frees disk.
5. Prune via the dashboard/API cache management or targeted deletes of whole orphaned model dirs. Do NOT delete individual `_gdn_sidecars` hash dirs to reclaim space — they back live hybrid models and get recomputed at cost; only remove a whole model (weights) and let its cache age out, unless orphanhood is proven.

## Stop / restart lifecycle
- The :8000 server is owned by the menu-bar GUI app `/Applications/oMLX.app` (launchd label `application.app.omlx.*`), NOT the CLI. `omlx stop` prints "oMLX stopped" but leaves the app-managed `omlx-server` child running and /health green — verify with pgrep + curl, never trust the CLI verdict.
- `osascript quit app "oMLX"` fails -128 "User canceled" — the app raises a quit-confirmation dialog an agent cannot dismiss.
- Working stop: `kill -TERM <app-pid> <omlx-server-pid>`; the server may linger ~5s releasing model memory — then `kill -KILL` any surviving `omlx-server`. The app typically AUTO-RELASES within a minute (launchd keepalive) unless Greg wants it durably down (`launchctl bootout gui/$UID/<label>`).
- Reopen after kill: `open -a oMLX`; confirm /health + `/v1/models` (model list refreshes at server start — deleted models linger in the cached list until restart).
- `omlx restart` (CLI) may print "Failed to control oMLX.app" yet still cycle the server successfully — again, verify by health + new server PID, not the message.
- IMPORTANT: Hermes chat may itself be served by oMLX (custom provider, default_model). Stopping oMLX interrupts the live session with provider-recovery cycles — warn Greg before stopping and ask whether the app should stay down.

## Pitfalls
- `du` over a home dir can take minutes — foreground with a generous timeout is fine; never pipe through `head` (auto-truncation already applies).
- Refuse to guess dashboard internals: jundot/omlx docs on DeepWiki (`jundot/omlx` — Admin Dashboard + Real-Time Monitoring pages) are the reliable citation source for UI feature questions.
- Report engine-pool memory in human units (GiB) derived from the byte fields — don't paste raw ints.
