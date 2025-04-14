import requests
import os
from bs4 import BeautifulSoup
from datetime import datetime

WORDPRESS_URL = "https://isperia.rip"
OUTPUT_DIR = "./lore/wordpress"

def sanitize_filename(title):
    return "".join(c for c in title if c.isalnum() or c in (" ", "_", "-")).rstrip().replace(" ", "_")

def fetch_wp_content(content_type):
    print(f"[SCRAPER] Fetching {content_type} from WordPress...")
    url = f"{WORDPRESS_URL}/wp-json/wp/v2/{content_type}?per_page=100"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def html_to_markdown(html_content):
    soup = BeautifulSoup(html_content, "html.parser")

    # Convert <blockquote> to markdown-style quotes
    for block in soup.find_all("blockquote"):
        quote_lines = [f"> {line}" for line in block.get_text().splitlines()]
        block.replace_with("\n".join(quote_lines))

    # Convert <strong> and <em> tags
    for tag in soup.find_all("strong"):
        tag.replace_with(f"**{tag.get_text()}**")
    for tag in soup.find_all("em"):
        tag.replace_with(f"*{tag.get_text()}*")

    # Convert <h1>-<h6> tags
    for i in range(6, 0, -1):
        for tag in soup.find_all(f"h{i}"):
            tag.replace_with(f"{'#' * i} {tag.get_text()}")

    return soup.get_text().strip()

def save_markdown_file(title, content, content_type, slug):
    folder = os.path.join(OUTPUT_DIR, content_type)
    os.makedirs(folder, exist_ok=True)
    filename = sanitize_filename(slug or title) + ".md"
    filepath = os.path.join(folder, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n{content}")
    print(f"[SCRAPER] Saved: {filepath}")

def scrape_wordpress():
    print("[SCRAPER] Starting WordPress scrape...")
    for content_type in ["posts", "pages"]:
        try:
            items = fetch_wp_content(content_type)
            for item in items:
                title = item["title"]["rendered"]
                raw_html = item["content"]["rendered"]
                slug = item.get("slug", "")
                markdown = html_to_markdown(raw_html)
                save_markdown_file(title, markdown, content_type, slug)
        except Exception as e:
            print(f"[SCRAPER] Error fetching {content_type}: {e}")
    print("[SCRAPER] WordPress scraping complete.")