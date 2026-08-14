# fedya.ai

Personal site. Astro, fully static, zero client-side JavaScript, deliberately
unstyled (browser defaults plus a readable measure), deployed as a Cloudflare
Worker with static assets.

Routes: `/` (home), `/work`, `/about`, `/blog`, `/now`, `/contact`, `/misc`.

## Commands

```sh
npm run dev      # local dev at localhost:4321
npm run build    # static build → dist/
npm run deploy   # build + wrangler deploy
```

First deploy: `npx wrangler login` once, then `npm run deploy`. Attach the
custom domain under the Worker's **Settings → Domains & Routes** (or push the
repo to GitHub and connect it via Workers Builds for deploy-on-push).

## Where things live

| What | Where |
| --- | --- |
| Identity (name, role, bio line, profiles) | `src/config.ts` — propagates to meta, JSON-LD, footer |
| Pages | `src/pages/` |
| Projects | `src/content/projects/*.md` (frontmatter: title, description, year, url, repo, order) |
| Posts | `src/content/blog/*.md` (frontmatter: title, description, date, updated, draft) |
| CSS (minimal, ~20 lines) | `src/styles/global.css` |
| robots.txt / llms.txt / favicon | `public/` |
| Cloudflare config | `wrangler.jsonc` |

## Launch checklist

- [ ] Replace every `TODO` (grep for it): bio, role, profile URLs, project copy
- [ ] Rewrite or delete the placeholder post in `src/content/blog/`
- [ ] Keep `/now` dated and current — cheap freshness signal
- [ ] Update `public/llms.txt` if the one-liner in `src/config.ts` changes
- [ ] Deploy, then verify `robots.txt`, `sitemap-index.xml`, `rss.xml`, `llms.txt` resolve
- [ ] Validate JSON-LD with https://validator.schema.org

## The GEO/AIO layer (what's wired in and why)

- **Person + WebSite JSON-LD on every page, Article on posts** — machine-readable
  identity; `sameAs` links this domain to your profiles so AI systems connect
  the entity.
- **Answer-shaped copy** — hero and About sections open with a sentence that can
  be quoted standalone by an answer engine. Keep that shape when editing.
- **Zero-JS static HTML** — AI crawlers largely don't execute JavaScript; all
  content is in the initial response.
- **Sitemap + RSS + canonical URLs + OG meta** — table-stakes discovery surface.
- **robots.txt explicitly allows AI crawlers** (GPTBot, ClaudeBot,
  PerplexityBot, Google-Extended, CCBot…). For a portfolio, ingestion is the goal.
- **`updated` frontmatter on posts** — surfaces `dateModified` in Article
  schema; freshness measurably increases AI citations. Bump it when you revise.
- **llms.txt** — low-cost nicety for AI dev tools; not a ranking lever.
