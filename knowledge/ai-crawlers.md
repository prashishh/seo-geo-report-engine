# AI crawler reference — user-agents, purpose, allow/block

Reference for `geo-audit` and `technical-seo-audit`. Two kinds of AI bot:

- **Answer / search crawlers** — fetch pages at query time to *cite* them in AI answers. **ALLOW these** —
  blocking them removes you from AI-search visibility (the whole point of GEO).
- **Training-only crawlers** — collect data to train future models; no direct citation benefit.
  **Optional BLOCK** if the client wants their content kept out of model training. Blocking has little
  downside for *visibility* but also little upside; make it the client's call.

Many vendors run separate UAs for each purpose so you can allow answers while blocking training.

## Crawler table

| User-agent | Company | Purpose | Recommendation |
|---|---|---|---|
| `GPTBot` | OpenAI | Training data collection | Optional BLOCK (training-only) |
| `OAI-SearchBot` | OpenAI | Indexing for ChatGPT Search results | **ALLOW** (search) |
| `ChatGPT-User` | OpenAI | Live fetch when a user/plugin asks | **ALLOW** (live answers) |
| `ClaudeBot` | Anthropic | Training data collection | Optional BLOCK (training-only) |
| `anthropic-ai` | Anthropic | Legacy training crawler | Optional BLOCK (training-only) |
| `Claude-Web` | Anthropic | Legacy web crawler | Optional BLOCK (legacy) |
| `Claude-User` / `Claude-SearchBot` | Anthropic | Live fetch / search for Claude answers | **ALLOW** (live answers/search) |
| `PerplexityBot` | Perplexity | Indexing for Perplexity answers + citations | **ALLOW** (search) |
| `Perplexity-User` | Perplexity | Live fetch for a user query | **ALLOW** (live answers) |
| `Google-Extended` | Google | Gemini / Vertex training & grounding opt-in | Optional BLOCK (does NOT affect Search/AI Overviews indexing) |
| `GoogleOther` | Google | Misc Google crawls (R&D, non-Search) | Optional ALLOW |
| `Googlebot` | Google | Search index — also powers AI Overviews / AI Mode | **ALLOW** (never block) |
| `Applebot-Extended` | Apple | Apple Intelligence training opt-in | Optional BLOCK (training-only) |
| `Amazonbot` | Amazon | Alexa / answers indexing | **ALLOW** (answers) |
| `Bytespider` | ByteDance (TikTok) | Training data collection | Optional BLOCK (aggressive; training-only) |
| `CCBot` | Common Crawl | Open dataset used to train many models | Optional BLOCK (training-only) |
| `Meta-ExternalAgent` | Meta | AI training / product data collection | Optional BLOCK (training-only) |
| `FacebookBot` | Meta | Indexing + AI uses | Optional ALLOW |
| `Bingbot` | Microsoft | Bing index — powers Copilot answers | **ALLOW** (never block) |
| `msnbot` | Microsoft | Legacy Bing crawler | **ALLOW** |

> Note: `Google-Extended` and `Applebot-Extended` are **opt-out tokens**, not standalone crawlers —
> disallowing them blocks *training/grounding use*, not Search/AI-Overview indexing (which stays with
> `Googlebot` / `Applebot`). So a client can keep AI-search visibility while opting out of training.

## robots.txt — allow answer/search crawlers (ready to paste)

This explicitly welcomes the citation-driving bots and (optionally) opts out of training-only ones.
Adjust the training block to the client's preference. Keep `Googlebot`/`Bingbot` allowed.

```text
# --- AI answer & search crawlers: ALLOW (drives AI-search visibility) ---
User-agent: OAI-SearchBot
User-agent: ChatGPT-User
User-agent: Claude-User
User-agent: Claude-SearchBot
User-agent: PerplexityBot
User-agent: Perplexity-User
User-agent: Amazonbot
Allow: /

# --- Training-only crawlers: opt out below if the client wants (optional) ---
User-agent: GPTBot
User-agent: ClaudeBot
User-agent: anthropic-ai
User-agent: Google-Extended
User-agent: Applebot-Extended
User-agent: Bytespider
User-agent: CCBot
User-agent: Meta-ExternalAgent
Disallow: /

# --- Search engines that power AI answers: never block ---
User-agent: Googlebot
User-agent: Bingbot
Allow: /

# Point AI systems at your canonical resource list
Sitemap: https://example.com/sitemap.xml
```

To **keep training enabled** too, drop the training block (or set its `Disallow:` to empty).

## /llms.txt header (example)

Markdown at the domain root pointing models to canonical content. Transparency aid; **no current
citation weight** (see `playbooks/geo-playbook.md`). Header shape:

```markdown
# Example Corp
> One-line description of what Example does and who it serves.

## Docs
- [Getting started](https://example.com/docs/start): how to begin
- [Reference](https://example.com/docs/reference): full API / spec

## Key pages
- [How it works](https://example.com/how-it-works): the plain-English explainer
```

**Verify crawler access for real** before reporting: fetch the live `robots.txt` and `/llms.txt`,
and confirm Ahrefs' own crawler reach with `public-crawler-ips` / `public-crawler-ip-ranges` when
diagnosing IP-level blocks. Data priority: Ahrefs MCP > CLI connectors > web.
