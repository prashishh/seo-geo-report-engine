# Positioning & messaging methodology

The brand-language spine. `positioning-messaging` produces the Pack; everything downstream
(content-brief, comparison-pages, programmatic-seo, proposal-builder) inherits its canonical
one-liner, pillars, and "say this / not that" via the `messaging:` block in `client.yml`.
Ground it in real customer language from [[customer-research]] (`research/voc.md`) — positioning
asserted without VOC is a guess.

## 1. Positioning — April Dunford's 5 components
Positioning is **context**: the frame that makes your strengths obvious. Work it in order.
1. **Competitive alternatives** — what the customer would do if you didn't exist (often a spreadsheet, a rival, or nothing). This sets the frame.
2. **Unique attributes** — what you have that the alternatives don't (features, model, data, distribution).
3. **Value** — the benefit those attributes enable, that customers care about. Attribute → value.
4. **Target segment** — the customers who care *most* about that value. Niche down.
5. **Market category** — the frame you compete in; it sets expectations. Choose the category that makes your value obvious.

> Test: if you swapped your logo for a competitor's, would the positioning still read true? If yes, it's not differentiated.

## 2. Positioning statement — Geoffrey Moore template
> For **[target]** who **[need]**, **[product]** is a **[category]** that **[key benefit]**.
> Unlike **[primary alternative]**, we **[primary differentiation]**.

## 3. Messaging House
- **Roof — the one-liner / value prop:** a single sentence a stranger repeats correctly.
- **3 pillars — the differentiators:** the three things you want remembered. Each maps to a customer pain.
- **Foundation — proof:** evidence under each pillar (data, customers, mechanism, credentials).

## 4. StoryBrand SB7 (narrative spine for site/landing copy)
Customer = hero with a problem → brand = guide with a plan → call to action → stakes (success vs failure). The brand is the guide, never the hero.

## 5. Copy primitives (generate 3 variants each, then pick)
One-liner · tagline · elevator pitch (30s) · hero headline + subhead · boilerplate. All must
trace to a pillar; none may introduce a claim not in the foundation.

## 6. "Say this / not that"
A consistency table: the on-brand phrasing for each concept vs the off-brand/competitor phrasing
to avoid. This is what keeps 500 programmatic pages and 20 posts/week on-voice.

## 7. Validation (falsifiable)
- **Sales-pitch test:** can you pitch it in one breath and have the listener restate it?
- **Customer-echo test:** do the words appear in `voc.md` quotes? If not, you're using insider language.
- **Differentiation test:** does a competitor's homepage already say the same thing? If yes, sharpen.
- **Leading indicator:** message-match lift — CTR/scroll-depth/conversion on pages using the new language vs old.

## Output contract
Write `deliverables/positioning-messaging-pack.md` AND the canonical fields back into
`client.yml: messaging:` (`one_liner`, `pillars[]`, `say_this_not_that[]`) so every skill reads one source of truth.
