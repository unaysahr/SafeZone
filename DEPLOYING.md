# Deploying and editing SafeZone

## Required: set a session secret

The app refuses to start without `SESSION_SECRET`. Generate one:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

On Replit, add it in the **Secrets** pane (lock icon) as `SESSION_SECRET`.
Never commit it.

## Run it

```bash
pip install flask gunicorn          # or: uv pip install -e .
export SESSION_SECRET=<your-secret>
gunicorn --bind 0.0.0.0:5000 main:app
```

For local editing with auto-reload:

```bash
FLASK_DEBUG=1 SESSION_SECRET=dev python main.py
```

Run the tests with `python -m pytest tests/ -q`.

## Verify the registry data source after deploying

Registry endpoints cannot be reached from a sandboxed dev environment, so the
first thing to do on a real deployment is check that the provider works:

```
https://<your-app>/health/providers
```

- `200` with `"ok": true` - the source is live and returning records.
- `503` - the endpoint is unreachable or its URL has changed. The app stays
  safe in this state: it reports the outage and links users to the official
  registry rather than showing anything invented.

If DC's ArcGIS layer id has rotated, find the current one on
[Open Data DC](https://opendata.dc.gov/datasets/sex-offender-registry) and set
`SAFEZONE_DC_LAYER_URL` to the new `.../query` URL. No code change needed.

## Data sources and coverage

There is **no free national API**. NSOPW is a federated search portal with no
public programmatic interface - the `api.nsopw.gov` endpoint that used to
appear in the code comments does not exist.

Built in:

| Provider | Coverage | Cost | Env |
|---|---|---|---|
| Open Data DC | Washington DC | free, no key | `SAFEZONE_ENABLE_DC=0` to disable, `SAFEZONE_DC_LAYER_URL` to override |
| National aggregator | nationwide | paid subscription | `SAFEZONE_NATIONAL_API_URL`, `SAFEZONE_NATIONAL_API_KEY` |

Everywhere else, the app tells the user it has no verified source for that
area and links to the official registry search. That is the intended
behaviour, not a gap to paper over.

### Adding national coverage

Vendors that resell aggregated registry data include
[offenders.io](https://offenders.io/), [OffenderList](https://offenderlist.us/)
and [Zyla](https://zylalabs.com/). All require a paid key. Once you have one:

```
SAFEZONE_NATIONAL_API_URL=https://api.vendor.com/v1/offenders
SAFEZONE_NATIONAL_API_KEY=<key>
SAFEZONE_NATIONAL_ZIP_PARAM=zip          # optional, defaults shown
SAFEZONE_NATIONAL_AUTH_HEADER=X-Api-Key
SAFEZONE_NATIONAL_RESULTS_KEY=offenders
```

The provider normalises common field spellings (`name`/`full_name`,
`lng`/`longitude`, etc.), so most vendors work without code changes. Check
`/health/providers` after setting it, and read the vendor's terms - several
prohibit redistribution or caching.

### Adding a state provider

Write a class with `covers(zip_code, state)` and `lookup(zip_code, state)`
returning `OffenderRecord`s (see `safezone/providers/dc.py`), then register it
in `build_providers()`. Two rules:

- Raise `ProviderError` on any failure. Never return a placeholder record.
- Leave unknown fields as `None`. A missing address must stay missing.

## Official registry links

Uncovered areas link to the authoritative registry via
`safezone/registries.py`. States with a verified entry link straight to their
own registry; everything else falls back to a state-scoped NSOPW search, which
covers every US jurisdiction and is always correct.

Only add a URL you have actually opened and confirmed. A plausible-looking
guess is worse than the fallback, because it sends someone looking for safety
information to the wrong place.

An entry can carry a `note` for a caveat that changes how a result should be
read. California has one: state law lets some registrants be excluded from
public disclosure, so an empty California result does **not** mean no
registered offenders live in the area. The UI shows a note on every result for
that state, including the reassuring ones.

## Why California has no data provider

California publishes no API and no bulk download - meganslaw.ca.gov is a
search-only UI. It is also the most legally restricted state we surveyed:
under [Penal Code 290.46](https://codes.findlaw.com/ca/penal-code/pen-sect-290-46/),
authorised use is limited to protecting a person at risk, misuse carries civil
penalties up to $25,000 plus damages and fees, and the state expressly
disclaims responsibility for "secondary dissemination" - republication on a
site like this one, where liability for errors moves to the operator.

Linking out is the deliberate choice for California, not a gap to fill.

## Legal and safety notes

Registry data is public record, but publishing it carries obligations:

- **Most state registries restrict reuse.** Many prohibit bulk scraping,
  commercial use, or republication. Read the terms for each source you add.
- **Attribution is often mandatory.** Each provider carries an `attribution`
  string that the UI displays with every result.
- **Accuracy matters legally.** Associating a real address with a sex offence
  incorrectly is defamatory. This is why the app fails closed everywhere.
- The UI carries the standard notice that using registry information to
  harass or harm anyone is a crime. Keep it.
