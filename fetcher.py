import asyncio
import feedparser
from datetime import datetime
from asyncio import Semaphore
from sqlalchemy.dialects.postgresql import insert
from models import Paper
from sqlalchemy.ext.asyncio import AsyncSession
import logging


async def fetch_papers(http_session, task, db_session: AsyncSession, semaphore: Semaphore, retries=3):
    start = task["start"]
    query = f"search_query=all&start={start}&max_results=100&sortBy=lastUpdatedDate&sortOrder=descending"
    url = f"http://export.arxiv.org/api/query?{query}"

    for attempt in range(retries):
        try:
            async with semaphore:
                async with http_session.get(url, timeout=10) as response:
                    if response.status != 200:
                        raise Exception(f"HTTP Error {response.status}")

                    text = await response.text()
                    parsed = feedparser.parse(text)

                    rows = []
                    for entry in parsed.entries:
                        arxiv_id = entry.id
                        authors = ", ".join([a.name for a in entry.authors]) if hasattr(entry, "authors") else ""
                        abstract = entry.summary.replace("\n", " ").strip()
                        published_date = datetime.strptime(entry.published, "%Y-%m-%dT%H:%M:%SZ")
                        for link in entry.links:
                            if link.type == "application/pdf":
                                pdf_url = link.href
                        categories = ", ".join(tag['term'] for tag in entry.tags) if hasattr(entry, "tags") else ""

                        rows.append({
                            "arxiv_id": arxiv_id,
                            "authors": authors,
                            "category": categories,
                            "abstract": abstract,
                            "published_date": published_date,
                            "pdf_url": pdf_url
                        })

                    if rows:
                        stmt = insert(Paper).values(rows).on_conflict_do_nothing(index_elements=["arxiv_id"])
                        await db_session.execute(stmt)
                        await db_session.commit()

                    logging.info(f"Request URL: {url} | Number of response papers: {len(parsed.entries)}")
                    logging.info(f"Success: start-index={start} | length of rows: {len(rows)}")
                    return True

        except Exception as e:
            logging.info(f"Attempt {attempt + 1} failed: {e} | {url}")
            await asyncio.sleep(2)

    logging.info(f"Final failure: start={start}")
    return False
