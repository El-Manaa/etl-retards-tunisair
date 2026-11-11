import asyncio
import httpx
from elementpath.xpath3 import XPath31Parser
from elementpath import select as xpath_select
from lxml import html


XPATH = "(//table)[2]//tr[td/text()!='' and td/text() != 'Heure Locale']"

QUERY = f"""
    for $r in {XPATH}
    return map {{
        'heure_locale': string($r/td[1]),
        'origine': string(if ($r/../tr[1]/td[2] = 'Origine') then string($r/td[2]) else ''),
        'dest': string(if ($r/../tr[1]/td[2] = 'Destination') then string($r/td[2]) else ''),
        'num_vol': string($r/td[4]),
        'statut': string($r/td[5])
    }}
"""

def extract_html_tables(content: str) -> list[dict[str, [str]]]:
    tabs = []
    for tab in xpath_select(html.fromstring(content), QUERY, parser=XPath31Parser):
        tabs.append(tab._map)
    return tabs


TIMEOUT = 20
async def async_fetch(client, sem, url):
    async with sem:
        while True:
            try:
                r = await client.get(url, timeout=TIMEOUT)
                r.raise_for_status()
                return extract_html_tables(r.text)
            except Exception as e:
                continue


CONCURRENCY = 100
BATCH_SIZE = 1000
async def async_scrape(urls):
    sem = asyncio.Semaphore(CONCURRENCY)
    limits = httpx.Limits(max_connections=CONCURRENCY+10)
    async with httpx.AsyncClient(
        limits=limits,
        headers={"User-Agent": "Mozilla/5.0 (compatible; research/1.0)"},
        follow_redirects=True,
        http2=False
    ) as client:
        tasks = (async_fetch(client, sem, url) for url in urls)
        raws = await asyncio.gather(*tasks)
        return raws

    
