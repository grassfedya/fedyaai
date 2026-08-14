---
# TODO: placeholder post — rewrite in your own voice or delete before launch
title: Rebuilding my site for the AI-readable web
description: 'Why I rebuilt fedya.ai as a zero-JavaScript, answer-shaped site — and what SEO, GEO, and AIO actually mean for a personal site in 2026.'
date: 2026-08-05
---

Every page on the web now has two readers: people, and the AI systems that
answer questions on their behalf. Rebuilding this site, I optimized for both —
and it turns out they mostly want the same thing.

## What changed

Search didn't die; it got re-weighted. Classic ranking still matters — pages at
the top of Google get cited by AI assistants at several times the rate of pages
below them — but the unit of consumption shrank from the page to the passage.
An answer engine lifts two sentences, not a layout.

So the rules for 2026 are old rules with new stakes:

- Server-rendered HTML, because most AI crawlers don't execute JavaScript
- Semantic structure — one h1, honest headings, real lists
- Answer-shaped sections that open with a sentence that survives being quoted alone
- JSON-LD identity: a `Person` schema linking this domain to my profiles
- Freshness — recently updated pages measurably earn more citations

## What I built

This site is Astro compiled to static HTML, served from Cloudflare's edge, and
ships zero client-side JavaScript. Dark mode is a media query. The animations
are CSS. The "identity layer" — Person and Article schema, sitemap, RSS,
llms.txt — is generated at build time from one config file.

---

The web that's easy for machines to read turns out to be the web that was
always good: fast, plain, structured, and written by someone with something to
say.
