import re
from spellchecker import SpellChecker
import json
import os
from utils import get_text_from_url, inline_external_stylesheets
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

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


def inject_highlighting_css(driver):
    HIGHLIGHT_CSS = """
    var style = document.createElement('style');
    style.innerHTML = `.spellcheck-highlight {
        background-color: yellow;
        color: black;
        font-weight: bold;
    }`;
    document.head.appendChild(style);
    """
    driver.execute_script(HIGHLIGHT_CSS)


def inject_typos_highlight(driver, typos):
    for typo in typos:
        escaped_typo = typo.replace("'", "\\'")
        script = f"""
        var bodyText = document.body.innerHTML;
        var regex = new RegExp('\\\\b({escaped_typo})\\\\b', 'gi');
        document.body.innerHTML = bodyText.replace(regex, '<span class="spellcheck-highlight">$1</span>');
        """
        driver.execute_script(script)


def main():
    options = Options()
    options.add_experimental_option("detach", True)
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    url = input("Enter a URL: ").strip()
    driver.get(url)

    text = get_text_from_url(url)
    if not text:
        return

    whitelists = load_whitelist()
    domain = url.split("/")[2]
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

    inject_highlighting_css(driver)
    inject_typos_highlight(driver, final_typos)


if __name__ == "__main__":
    main()
