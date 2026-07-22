# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

Scrapes [Personvārdi DB](https://personvardi.pmlp.gov.lv) (Latvian population register) to retrieve the registered count and, when available, the explanation for each Latvian first name. Input is a `namedays.json` file produced by the sibling [vardadiena-parser](https://github.com/DeveloperMaris/vardadiena-parser) project; output is `output/personvardi.json`.

## Commands

Setup (Python version pinned in `.python-version`):

```console
python -m venv env
source env/bin/activate
python -m pip install -r requirements/base.txt
```

Run the parser (input path is a required positional argument):

```console
python parse.py "input/namedays.json"
```

There is no test suite, linter, or build step configured.

## Architecture

Two-file pipeline:

- `parse.py` — entry point. Loads the input JSON (one record per name: `{month, day, name, is_additional_calendar_name, removed}`), fans every record's `item["name"]` out to a `ThreadPoolExecutor` (no filtering on `removed` or `is_additional_calendar_name` — every record is looked up), collects results into a dict keyed by lowercase name, sorts it, and writes `output/personvardi.json`. Each worker constructs a fresh `Personvardi` instance, so HTTP sessions are not shared across threads.
- `Personvardi.py` — single-class scraper. `search_by_name` hits `/index.php?name=<NAME>` and parses the result table with BeautifulSoup. The listing page may include a link to a detail page (`./index.php?name=<id>`); when present, the scraper follows it and merges in the detail-page data (which adds `explanation`). The detail page is parsed via a `match` on Latvian column headers: `Vārds` → name, `Sastopams` → count, `Skaidrojums` → explanation. Requests use `urllib3` retry (`connect=3, backoff_factor=0.5`) and a 10s timeout.

Disambiguation matters in `__process_name_list`: the listing endpoint substring-matches the full name field, so searching "Dans" also returns unrelated single-word names like "Bogdans" (skipped — "dans" is only a substring, not a whole-word match) as well as double names like "Nimmija Una" (whose count *is* added into "nimmija"'s total, since "nimmija" is a whole word within it). Matching splits both the search term and each row's name on whitespace and requires the search term's word sequence to appear as a contiguous subsequence of the row's words — this merges compound registrations into their component names without an extra HTTP request per compound row.

## Operational notes

- The README warns that frequent runs can get the source IP blocked by the host. Do not loop the script for testing without throttling.
- Attribution to *Pilsonības un migrācijas lietu pārvalde* is required when redistributing the output data.
