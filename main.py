import re
from spellchecker import SpellChecker
import json
import os
from utils import get_text_from_url, highlight_typos_in_html, inline_external_stylesheets
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

WHITELIST_FILE = "whitelists.json"

def load_whitelist():
    if os.path.exists(WHITELIST_FILE):
        with open(WHITELIST_FILE, "r") as f:
            return json.load(f)
    return {}

def save_whitelist(whitelists):
    with open(WHITELIST_FILE, "w") as f:
        json.dump(whitelists, f, indent=2)

def filter_words(text, url_whitelist):
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text)
    return [w for w in words if w.lower() not in url_whitelist]

def check_spelling(text, url_whitelist):
    spell = SpellChecker()
    filtered_words = filter_words(text, url_whitelist)
    return spell.unknown(filtered_words)

def main():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    url = input("Enter a URL: ").strip()
    text = get_text_from_url(url)
    if not text:
        return

    whitelists = load_whitelist()
    domain = url.split("/")[2]  # simple way to extract domain
    url_whitelist = set(whitelists.get(domain, []))

    misspelled = check_spelling(text, url_whitelist)

    new_words = []
    for word in sorted(misspelled):
        print(f"Potential typo: {word}")
        decision = input(f"Add '{word}' to whitelist for {domain}? (y/n): ").strip().lower()
        if decision == 'y':
            url_whitelist.add(word.lower())
            new_words.append(word.lower())

    if new_words:
        whitelists[domain] = sorted(url_whitelist)
        save_whitelist(whitelists)
        print(f"Updated whitelist for {domain}")
        
    final_typos = check_spelling(text, url_whitelist)
    
    driver.get(url)
    html = driver.page_source
    text = get_text_from_url(url)
    driver.quit()

    highlighted_html = highlight_typos_in_html(html, final_typos)
    
    # Fix CSS links
    soup = BeautifulSoup(highlighted_html, 'html.parser')
    inline_external_stylesheets(soup, url)
    
    with open("highlighted_output.html", "w", encoding="utf-8") as f:
        f.write(highlighted_html)

if __name__ == "__main__":
    main()
