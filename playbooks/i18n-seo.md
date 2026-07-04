# International SEO & hreflang methodology

For multi-language / multi-region sites (e.g. a remittance brand: en + ne, selective Hindi, across diaspora
corridors). `hreflang-i18n` audits and generates the setup; this is the methodology.

## hreflang in one paragraph
`hreflang` tells Google which language/region version of a URL to serve. It is a **bidirectional
contract**: if page A points to B as the `ne` version, B must point back to A. A broken return
tag voids the whole cluster. Every URL in a set must also reference **itself**.

## The full-mesh rules (what the audit checks)
1. **Self-reference** — each page includes an hreflang tag pointing to itself.
2. **Return tags** — every annotation is reciprocal (A↔B↔C all reference each other).
3. **x-default** — a fallback for unmatched languages/regions (usually the language selector or primary market).
4. **Valid codes** — language = ISO 639-1 (`en`, `ne`, `hi`); optional region = ISO 3166-1 alpha-2 (`en-US`, `en-GB`). Region without language is invalid.
5. **Canonical alignment** — each page's canonical points to itself, never to another language (a cross-language canonical collapses the cluster).
6. **Protocol/host consistency** — all absolute URLs, same scheme/host pattern.
7. **Cross-domain correctness** — if languages live on different domains/ccTLDs, annotations span domains correctly.
8. **Content parity** — the alternates are genuine translations, not near-duplicates or partial machine output.

## Implementation methods (pick one, be consistent)
- **HTML `<link rel="alternate" hreflang>`** in `<head>` — simplest; best for HTML pages.
- **HTTP `Link:` header** — for non-HTML (PDF) or when you can't edit `<head>`.
- **XML sitemap `xhtml:link`** — best at scale (hundreds of programmatic pages); keeps tags out of the HTML.

## URL structure trade-offs
| Structure | Geo signal | Cost | Best when |
|---|---|---|---|
| ccTLD (`brand.com.np`) | strongest | high (separate domains/authority) | strong per-country presence |
| subfolder (`brand.com/ne/`) | good | low (shared authority) | **default for most** — esp. language-first sites |
| subdomain (`ne.brand.com`) | medium | medium | infra constraints |

## Content & cultural adaptation (not just translation)
Localize currency, examples, idioms, regulatory/compliance notes, and intent — Nepali senders
search differently than US rate-shoppers. Machine translation alone fails the parity check and
the GEO citability bar; have a native speaker review money/YMYL pages.

## Common failure modes
Wrong language ranking in a market → missing/broken return tags or no x-default. "Duplicate
content across languages" → missing hreflang + cross-language canonical. Region code without
language → ignored.

## Validation (falsifiable)
Each fix gets: the check it satisfies, the method (HTML/header/sitemap), and a test — e.g.
"GSC International Targeting shows 0 'no return tags' errors within 2 crawls" or "the `ne` URL
ranks for Nepali queries in NP within 30 days."
