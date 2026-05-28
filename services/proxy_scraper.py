"""
Fetch free SOCKS5 proxy lists from GitHub repos and append to GLOBAL_PROXIES.
Per-domain proxy cache: remembers working proxies per domain, removes on failure.
"""

import asyncio
import logging
from urllib.parse import urlparse

import aiohttp

from config import GLOBAL_PROXIES

logger = logging.getLogger(__name__)

# Raw URLs from popular GitHub proxy lists (SOCKS5 only)
PROXY_SOURCES = [
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
    "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5.txt",
    "https://raw.githubusercontent.com/proxifly/free-proxy-list/refs/heads/main/proxies/protocols/socks5/data.txt",
]

# Per-domain proxy cache: {domain: [proxy_url, ...]}
_domain_proxies: dict[str, list[str]] = {}


def _extract_domain(url: str) -> str:
    return urlparse(url).hostname or url


def mark_proxy_success(url: str, proxy: str | None):
    if not proxy:
        return
    domain = _extract_domain(url)
    lst = _domain_proxies.setdefault(domain, [])
    # Move to front if already present
    if proxy in lst:
        lst.remove(proxy)
    lst.insert(0, proxy)
    logger.debug("Proxy cache: %s <- %s (pos 0, total %d)", domain, proxy.split("@")[0] if "@" in proxy else proxy[:40], len(lst))


def mark_proxy_failure(url: str, proxy: str | None):
    if not proxy:
        return
    domain = _extract_domain(url)
    lst = _domain_proxies.get(domain)
    if lst and proxy in lst:
        lst.remove(proxy)
        logger.debug("Proxy cache: %s removed %s (%d left)", domain, proxy.split("@")[0] if "@" in proxy else proxy[:40], len(lst))


def get_cached_proxies(url: str) -> list[str]:
    domain = _extract_domain(url)
    return list(_domain_proxies.get(domain, []))


async def fetch_proxies(sources: list[str] | None = None) -> list[str]:
    proxies: list[str] = []
    sources = sources or PROXY_SOURCES
    async with aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=10)
    ) as sess:
        for src in sources:
            try:
                async with sess.get(src) as resp:
                    if resp.status == 200:
                        text = await resp.text()
                        for line in text.splitlines():
                            line = line.strip()
                            if line and ":" in line and not line.startswith("#"):
                                if not line.startswith("socks5://"):
                                    line = f"socks5://{line}"
                                proxies.append(line)
                        logger.info(
                            "Fetched %d proxies from %s",
                            len(proxies),
                            src.rsplit("/", 1)[-1],
                        )
            except Exception as e:
                logger.warning("Failed to fetch %s: %s", src, e)
    return proxies


async def refresh_proxies_loop(interval: int = 600):
    while True:
        proxies = await fetch_proxies()
        if proxies:
            # Merge into GLOBAL_PROXIES, avoiding duplicates
            seen = set(GLOBAL_PROXIES)
            added = 0
            for p in proxies:
                if p not in seen:
                    GLOBAL_PROXIES.append(p)
                    seen.add(p)
                    added += 1
            logger.info(
                "Proxy pool: %d new / %d total from %d sources",
                added,
                len(GLOBAL_PROXIES),
                len(PROXY_SOURCES),
            )
        await asyncio.sleep(interval)
