---
name: skill-catalog-sync
description: "Keep runtime skills and GitHub skill catalog in sync."
version: 1.2.0
author: Greg (Greggy-Eng), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [skills, sync, github, catalog, maintenance]
    related_skills: [hermes-agent-skill-authoring]
---

# Skill Catalog Sync

Greg's skill library has two homes that must carry identical content. Editing one and leaving the other behind causes silent drift — it has already happened once (local copies picked up mid-task edits the repo never saw).

## When to Use
- Creating, editing, or version-bumping any skill in `~/.hermes/skills/` or the `hermes-skills` repo
- User asks to "save/push the skill", "clone the skills repo", or asks where a skill lives
- Before patching a skill, to check whether runtime and repo copies have drifted
- Don't use for: authoring standards for upstream PRs to the Nous hermes-agent repo → hermes-agent-skill-authoring.

## The two homes
- **Runtime (what actually loads):** `~/.hermes/skills/<skill-name>/` — skills may sit under a category subfolder (`~/.hermes/skills/<category>/<skill-name>/`, e.g. `note-taking/`, `productivity/`); the repo is always flat `<skill-name>/`. Resolve the real runtime path with a glob (`ls -d ~/.hermes/skills/*<skill-name>/ ~/.hermes/skills/<skill-name>/ 2>/dev/null`) before copying or diffing, and strip the category segment when placing into the repo.
- **Canonical catalog (source of record):** GitHub `Greggy-Eng/hermes-skills`, cloned at `~/Greggy-Eng/hermes-skills`, branch `main`, layout `<skill-name>/SKILL.md` (+ `references/`, `templates/`, `scripts/` subdirs).

## Procedure — every skill edit
1. **Check drift first** in both copies before patching: `git fetch` + `git status -sb` in the repo, and read the runtime copy. The runtime copy is often *ahead* (skills get amended mid-task in live sessions); the repo may be ahead too. Diff them and merge the richer content forward before layering the new change.
2. Apply the change to the runtime copy (`skill_manage patch`) or the repo copy, whichever the task started in.
3. Bump the semver `version:` in frontmatter (patch = wording fix, minor = new step/mode/pitfall, major = redesign).
4. **Copy the whole skill folder to the other home** so both trees are byte-identical (`cp -R`), then `find <repo-copy> -name .DS_Store -delete` before `git add`.
5. Commit on `main` and push: message pattern `<skill-name> vX.Y.Z: <what changed>`. In-repo skills are source — an uncommitted skill edit is not durable.

## Rules & pitfalls
- `skill_manage(action='create')` writes to the runtime tree only — after creating, immediately copy into the repo clone and commit; a skill that exists in just one home is half-done.
- The skill loader caches per session: new or renamed skills won't appear in `skills_list`/`skill_view` until a fresh chat. Expected, not a bug — don't re-verify or duplicate the skill.
- `gh` CLI auth (keychain PAT) covers push to Greggy-Eng repos; no extra setup needed.
- macOS cruft: `.DS_Store` must never be committed (repo already has a `.gitignore` for it) — check `git status` staged list before committing.
- This repo is Greg's personal catalog, NOT the upstream Nous hermes-agent repo: no tests/docs-generator gates from `hermes-agent-skill-authoring` apply here; match the existing skills' frontmatter style (name, quoted description ≤60 chars ending in period, version, author, license, platforms, `metadata.hermes.tags`).

## Reporting
- When asked to "show the diffs": per-commit plain-language summary (sha + version + what changed). Raw patches only on explicit follow-up.
- When asked to "show the skill": attach the SKILL.md as a file plus a short structural map — don't paste multi-KB text into chat.
- Quote commit hashes only from fresh tool output (`git log -1`), never from memory — an unverified hash in a report is a false claim.

## Verification
- `git status -sb` clean and level with `origin/main`.
- `diff -r ~/Greggy-Eng/hermes-skills/<skill> <resolved-runtime-path>` reports no differences (resolve the runtime path first — category subfolders make a naive `~/.hermes/skills/<skill>` path miss).
- Frontmatter `version:` bumped and identical in both copies.
