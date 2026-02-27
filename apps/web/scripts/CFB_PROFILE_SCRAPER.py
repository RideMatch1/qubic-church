#!/usr/bin/env python3
"""
CFB Profile Posts Scraper - Direct from Profile Pages
======================================================

Profil: https://bitcointalk.org/index.php?action=profile;u=46556;sa=showPosts

Usage:
    python CFB_PROFILE_SCRAPER.py
    python CFB_PROFILE_SCRAPER.py --limit 50
"""

import os
import json
import time
import re
import csv
from pathlib import Path
from typing import Optional, List

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    os.system("pip3 install requests beautifulsoup4 lxml")
    import requests
    from bs4 import BeautifulSoup

CFB_USER_ID = 46556
CFB_USERNAME = "Come-from-Beyond"
BASE_URL = "https://bitcointalk.org"
PROFILE_POSTS_URL = f"{BASE_URL}/index.php?action=profile;u={CFB_USER_ID};sa=showPosts"
OUTPUT_DIR = Path(__file__).parent / "cfb_profile_posts"
POSTS_PER_PAGE = 20


class CFBProfileScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        })
        self.last_request = 0

    def _wait(self):
        elapsed = time.time() - self.last_request
        if elapsed < 2.5:
            time.sleep(2.5 - elapsed)
        self.last_request = time.time()

    def _get(self, url: str) -> Optional[str]:
        self._wait()
        try:
            resp = self.session.get(url, timeout=30)
            resp.encoding = 'ISO-8859-1'
            if resp.status_code == 200:
                return resp.text
        except Exception as e:
            print(f"  Error: {e}")
        return None

    def get_total_posts(self) -> int:
        """Get total posts from profile page"""
        html = self._get(f"{BASE_URL}/index.php?action=profile;u={CFB_USER_ID}")
        if not html:
            return 16216  # Known value for CFB
        match = re.search(r"Posts:\s*([\d,]+)", html)
        return int(match.group(1).replace(",", "")) if match else 16216

    def scrape_profile_page(self, start: int = 0) -> List[dict]:
        """Scrape posts from profile page using titlebg2 rows as headers"""
        url = f"{PROFILE_POSTS_URL};start={start}"
        html = self._get(url)
        if not html:
            return []

        soup = BeautifulSoup(html, 'lxml')
        posts = []

        # Each post header is in a tr.titlebg2
        title_rows = soup.find_all("tr", class_="titlebg2")

        for title_row in title_rows:
            post = {"author": CFB_USERNAME}

            # Extract info from header row
            for link in title_row.find_all("a"):
                href = link.get("href", "")
                text = link.get_text(strip=True)

                if "board=" in href:
                    post["board"] = text
                elif "topic=" in href and "#msg" in href:
                    # This is the link to CFB's actual post
                    post["post_url"] = href
                    post["topic_title"] = text
                    msg_match = re.search(r"msg(\d+)", href)
                    if msg_match:
                        post["message_id"] = int(msg_match.group(1))
                    topic_match = re.search(r"topic=(\d+)", href)
                    if topic_match:
                        post["topic_id"] = int(topic_match.group(1))

            # Extract date
            for td in title_row.find_all("td"):
                text = td.get_text()
                if "on:" in text:
                    date_match = re.search(r"on:\s*(.+)", text.strip())
                    if date_match:
                        post["timestamp"] = date_match.group(1).strip()
                        break

            # Find the content div.post - it's in the next sibling table structure
            # Navigate to find the associated content
            parent_table = title_row.find_parent("table")
            if parent_table:
                # The content table is a sibling
                next_table = parent_table.find_next_sibling("table")
                if next_table:
                    post_div = next_table.find("div", class_="post")
                    if post_div:
                        # Extract quote info
                        quote_header = post_div.find("div", class_="quoteheader")
                        if quote_header:
                            quote_link = quote_header.find("a")
                            if quote_link:
                                post["replied_to"] = quote_link.get_text(strip=True)

                        # Get clean content
                        post_copy = BeautifulSoup(str(post_div), 'lxml')
                        for q in post_copy.find_all("div", class_="quote"):
                            q.decompose()
                        for q in post_copy.find_all("div", class_="quoteheader"):
                            q.decompose()

                        content = post_copy.get_text(separator="\n", strip=True)
                        post["content"] = content
                        post["content_length"] = len(content)

            # Include posts even if content is empty (image-only posts)
            if post.get("message_id"):
                if not post.get("content"):
                    post["content"] = "[IMAGE ONLY]"
                    post["content_length"] = 0
                posts.append(post)

        return posts

    def scrape_first_100(self, limit: int = 100) -> List[dict]:
        """Scrape CFB's first posts as shown on profile (newest first)"""
        print(f"\n{'='*60}")
        print(f"CFB PROFILE POSTS SCRAPER")
        print(f"{'='*60}")
        print(f"Profile: {PROFILE_POSTS_URL}")
        print(f"Target: First {limit} posts (as shown on profile)")
        print(f"{'='*60}\n")

        total_posts = self.get_total_posts()
        print(f"Total CFB posts: {total_posts:,}")

        # Start from offset 0 (newest posts, as shown on profile page 1)
        print(f"Starting from offset 0 (newest posts)...\n")

        all_posts = []
        current_offset = 0

        while len(all_posts) < limit:
            print(f"  Offset {current_offset}...", end=" ", flush=True)
            page_posts = self.scrape_profile_page(current_offset)

            if page_posts:
                print(f"{len(page_posts)} posts")
                all_posts.extend(page_posts)
            else:
                print("empty")
                break

            current_offset += POSTS_PER_PAGE

        # Deduplicate by message_id (keep order)
        seen = set()
        unique_posts = []
        for p in all_posts:
            mid = p.get("message_id")
            if mid and mid not in seen:
                seen.add(mid)
                unique_posts.append(p)

        # Take first N (already in profile order - newest first)
        final_posts = unique_posts[:limit]

        for i, p in enumerate(final_posts):
            p["post_number"] = i + 1

        print(f"\nCollected {len(final_posts)} unique posts")
        return final_posts

    def save(self, posts: List[dict], limit: int):
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        csv_path = OUTPUT_DIR / f"cfb_first_{limit}_posts.csv"
        fields = ["post_number", "message_id", "timestamp", "board", "topic_title",
                  "topic_id", "replied_to", "content", "content_length", "post_url"]
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            w.writerows(posts)
        print(f"\nCSV: {csv_path}")

        json_path = OUTPUT_DIR / f"cfb_first_{limit}_posts.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(posts, f, indent=2, ensure_ascii=False)
        print(f"JSON: {json_path}")


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", "-l", type=int, default=100)
    args = parser.parse_args()

    scraper = CFBProfileScraper()
    posts = scraper.scrape_first_100(args.limit)

    if posts:
        scraper.save(posts, args.limit)

        print(f"\n{'='*60}")
        print(f"DONE - {len(posts)} CFB posts")
        print(f"{'='*60}")

        print(f"\nOldest: #{posts[0]['post_number']} msg{posts[0]['message_id']}")
        print(f"        {posts[0].get('timestamp', '?')}")
        print(f"Newest: #{posts[-1]['post_number']} msg{posts[-1]['message_id']}")
        print(f"        {posts[-1].get('timestamp', '?')}")

        print(f"\n=== FIRST 5 POSTS ===")
        for p in posts[:5]:
            print(f"\n#{p['post_number']} - msg{p['message_id']}")
            print(f"  {p.get('timestamp', '?')}")
            print(f"  {p.get('board', '?')} / {p.get('topic_title', '?')[:50]}")
            print(f"  {p.get('content', '')[:120]}...")


if __name__ == "__main__":
    main()
