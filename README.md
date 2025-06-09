# Website Spell Checker Tool

This tool scans a given website URL for potential spelling errors in visible text, highlights the typos in a saved HTML version of the page, and supports domain-specific whitelisting of terms.

## Features

- Spell-checks visible text from a webpage
- Highlights potential typos in the saved HTML
- Embeds external stylesheets so the output retains original page styling
- Supports per-domain whitelist to ignore known valid terms
- Stores whitelist decisions in a local JSON file (`whitelists.json`)

## How It Works

1. Enter a URL when prompted.
2. The tool fetches visible content from the page using Selenium and BeautifulSoup.
3. Words are filtered and spell-checked using the `pyspellchecker` library.
4. For each potential typo, you are prompted whether to add it to the domain-specific whitelist.
5. Remaining typos are visually highlighted in a saved HTML file (`highlighted_output.html`), with CSS preserved.

## Requirements

Install required dependencies using:

```bash
pip install -r requirements.txt
