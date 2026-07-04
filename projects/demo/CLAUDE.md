# Demo project — Acme Roastworks (fictional)

This is the demo client that ships with the repo. **Every company, domain (`.example`), and
number in this folder is invented** so you can render the full first-scan report and dashboard
without any API keys:

```bash
python3 tools/report/first_scan.py --project demo --date "sample data" --render
./bin/mkt dashboard serve        # then open http://localhost:8787
```

To run against a real prospect, copy the shape of `client.yml` into `projects/<your-slug>/`
and follow `commands/client-report.md`. Real projects are gitignored; only this demo ships.
