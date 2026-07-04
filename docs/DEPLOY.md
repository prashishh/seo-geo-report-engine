# Publishing the homepage

The homepage is static files in this folder. No build step, no tracking, no external assets.
The contact path is a plain mailto link to namaste@prashish.xyz, so there is nothing to deploy
beyond the page itself.

## 1. GitHub Pages

Repo -> Settings -> Pages -> Source "Deploy from a branch" -> Branch `main`, folder `/docs` -> Save.

## 2. Custom subdomain

The page is set to serve at `geoseo-visibility.prashish.xyz` (the `docs/CNAME` file holds it).
To make it live:

1. At your DNS host for prashish.xyz, add a CNAME record:
   `geoseo-visibility` -> `prashishh.github.io`
2. In repo Settings -> Pages, the custom domain should read `geoseo-visibility.prashish.xyz`
   (GitHub picks it up from the CNAME file). Enable Enforce HTTPS once the certificate is issued,
   usually within a few minutes.

Until DNS propagates, the site also serves at `https://prashishh.github.io/seo-geo-report-engine/`.

## 3. Update the GitHub links

`index.html`, `capabilities.html`, `llms.txt` and `README.md` point at
`github.com/prashishh/seo-geo-report-engine`. If the repo name differs, search-replace after
you create it.
