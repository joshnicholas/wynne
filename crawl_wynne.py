import csv
from pathlib import Path

import scrapy
from scrapy.crawler import CrawlerProcess


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
IMAGES_DIR = DATA_DIR / "images"
CSV_PATH = DATA_DIR / "wynne_finalists.csv"

YEARS = list(range(2011, 2026))

CSV_FIELDS = [
    "year",
    "artist",
    "title",
    "medium",
    "description",
    "winner",
    "image_path",
    "image_stem",
    "url",
]


class WynneSpider(scrapy.Spider):
    name = "wynne"
    custom_settings = {
        "DOWNLOAD_DELAY": 1,
        "CONCURRENT_REQUESTS": 1,
        "ROBOTSTXT_OBEY": True,
        "USER_AGENT": "WynneResearchBot/1.0 (+educational research)",
        "LOG_LEVEL": "INFO",
        "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        # Write CSV header if file doesn't exist or is empty
        if not CSV_PATH.exists() or CSV_PATH.stat().st_size == 0:
            with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
                writer.writeheader()

    def start_requests(self):
        for year in YEARS:
            url = f"https://www.artgallery.nsw.gov.au/prizes/wynne/{year}/"
            yield scrapy.Request(url, callback=self.parse_year, meta={"year": year})

    def parse_year(self, response):
        year = response.meta["year"]
        # Each finalist is a card-artwork-link
        links = response.css("a.card-artwork-link::attr(href)").getall()
        if not links:
            # Fallback: try any link matching the pattern /prizes/wynne/YEAR/ID/
            links = response.css(
                f'a[href*="/prizes/wynne/{year}/"]::attr(href)'
            ).getall()
            # Filter to only detail pages (have a numeric ID segment)
            links = [
                l
                for l in links
                if l.rstrip("/").split("/")[-1].isdigit()
            ]

        # Deduplicate while preserving order
        seen = set()
        unique_links = []
        for link in links:
            if link not in seen:
                seen.add(link)
                unique_links.append(link)

        self.logger.info(f"Year {year}: found {len(unique_links)} finalists")
        for link in unique_links:
            url = response.urljoin(link)
            yield scrapy.Request(
                url, callback=self.parse_finalist, meta={"year": year}
            )

    def parse_finalist(self, response):
        year = response.meta["year"]

        # Artist and title from the heading
        # Format: "Artist Name <span>Title</span>"
        heading = response.css("h2.articleHeader-titleArtistWork")
        if not heading:
            self.logger.warning(f"No heading found on {response.url}")
            return

        # Artist name is the text node before the span
        full_text = heading.css("::text").getall()
        artist = full_text[0].strip() if full_text else ""

        # Title is in the subtitle span
        title = heading.css("span.articleHeader-subtitle::text").get("")
        title = title.strip()

        # Medium
        medium = response.css("p.articleHeader-medium::text").get("")
        medium = medium.strip()

        # Winner status
        winner_text = response.css("p.articleHeader-winnerText::text").get("")
        winner = bool(winner_text and winner_text.strip())

        # Description from the text module
        desc_selector = response.css("div.textModule div.grid.text p ::text").getall()
        description = " ".join(t.strip() for t in desc_selector if t.strip())

        # Image URL - prefer og:image for full resolution
        image_url = response.css('meta[property="og:image"]::attr(content)').get("")
        if not image_url:
            # Fallback to the article header image
            image_url = response.css("img.articleHeader-image::attr(src)").get("")

        if image_url:
            image_url = response.urljoin(image_url)

        meta = {
            "year": year,
            "artist": artist,
            "title": title,
            "medium": medium,
            "description": description,
            "winner": winner,
            "url": response.url,
        }

        if image_url:
            yield scrapy.Request(
                image_url,
                callback=self.save_image,
                meta=meta,
                dont_filter=True,
            )
        else:
            self.logger.warning(f"No image found for {artist} - {title}")
            self._write_row(meta, image_path="", image_stem="")

    def save_image(self, response):
        meta = response.meta
        # Build a filename from year, artist, and title
        safe_artist = "".join(
            c if c.isalnum() or c in " -" else "_" for c in meta["artist"]
        )
        safe_title = "".join(
            c if c.isalnum() or c in " -" else "_" for c in meta["title"]
        )
        stem = f"{meta['year']}_{safe_artist}_{safe_title}"[:120]

        # Determine extension from URL or content type
        url_path = response.url.split("?")[0]
        ext = Path(url_path).suffix or ".jpg"
        if ext not in (".jpg", ".jpeg", ".png", ".gif", ".webp"):
            ext = ".jpg"

        filename = f"{stem}{ext}"
        filepath = IMAGES_DIR / filename

        filepath.write_bytes(response.body)
        self.logger.info(f"Saved image: {filename}")

        rel_path = str(filepath.relative_to(BASE_DIR))
        self._write_row(meta, image_path=rel_path, image_stem=stem)

    def _write_row(self, meta, image_path, image_stem):
        row = {
            "year": meta["year"],
            "artist": meta["artist"],
            "title": meta["title"],
            "medium": meta["medium"],
            "description": meta["description"],
            "winner": meta["winner"],
            "image_path": image_path,
            "image_stem": image_stem,
            "url": meta["url"],
        }
        with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            writer.writerow(row)
        self.logger.info(
            f"Wrote CSV row: {meta['year']} - {meta['artist']} - {meta['title']}"
        )


if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(WynneSpider)
    process.start()
