from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup, NavigableString, Tag
from urllib.parse import urljoin
import time
import requests
import re


def inline_external_stylesheets(soup, base_url):
    for link_tag in soup.find_all("link", rel="stylesheet"):
        href = link_tag.get("href")
        if not href:
            continue

        full_url = urljoin(base_url, href)
        try:
            response = requests.get(full_url, timeout=10)
            response.raise_for_status()
            css_content = response.text

            style_tag = soup.new_tag("style")
            style_tag.string = css_content
            link_tag.replace_with(style_tag)

        except requests.RequestException as e:
            print(f"Failed to fetch stylesheet: {full_url} — {e}")

def get_text_from_url(url):
    try:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)

        time.sleep(2)

        html = driver.page_source
        driver.quit()

        soup = BeautifulSoup(html, 'html.parser')

        for tag in soup(['script', 'style', 'noscript']):
            tag.decompose()

        return soup.get_text(separator=' ', strip=True)

    except Exception as e:
        print(f"Error loading page with Selenium: {e}")
        return ""
    
def highlight_typos_in_html(html, typos):
    soup = BeautifulSoup(html, 'html.parser')

    for element in soup.find_all(text=True):
        parent = element.parent

        # Skip non-visible tags
        if parent.name in ['style', 'script', 'noscript']:
            continue

        if isinstance(element, NavigableString):
            new_text = str(element)
            for typo in sorted(typos, key=len, reverse=True):
                pattern = re.compile(rf'\b({re.escape(typo)})\b', re.IGNORECASE)
                new_text = pattern.sub(r'<span class="spellcheck-highlight">\1</span>', new_text)

            if new_text != str(element):
                new_fragment = BeautifulSoup(new_text, 'html.parser')
                element.replace_with(new_fragment)

    # Add a CSS style block at the top
    style_tag = soup.new_tag("style")
    style_tag.string = """
    .spellcheck-highlight {
        background-color: yellow;
        color: black;
        font-weight: bold;
    }
    """
    if soup.head:
        soup.head.append(style_tag)
    else:
        soup.insert(0, style_tag)

    return str(soup)