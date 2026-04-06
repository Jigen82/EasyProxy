import asyncio
import logging
import re
import random
from urllib.parse import urlparse, urljoin
from typing import Dict, Any
import aiohttp
from aiohttp import ClientSession, ClientTimeout, TCPConnector
from aiohttp_socks import ProxyConnector

logger = logging.getLogger(__name__)

class ExtractorError(Exception):
    """Custom exception for extraction errors."""
    pass

class DLStreamsExtractor:
    """Extractor for dlstreams.top streams."""

    def __init__(self, request_headers: dict = None, proxies: list = None):
        self.request_headers = request_headers or {}
        self.base_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        }
        self.session = None
        self.mediaflow_endpoint = "hls_manifest_proxy"
        self.proxies = proxies or []

    def _get_random_proxy(self):
        return random.choice(self.proxies) if self.proxies else None

    async def _get_session(self):
        if self.session is None or self.session.closed:
            proxy = self._get_random_proxy()
            if proxy:
                connector = ProxyConnector.from_url(proxy)
            else:
                connector = TCPConnector(limit=0, limit_per_host=0)
            
            timeout = ClientTimeout(total=30, connect=10)
            self.session = ClientSession(
                timeout=timeout,
                connector=connector,
                headers=self.base_headers
            )
        return self.session

    async def extract(self, url: str, **kwargs) -> Dict[str, Any]:
        """Extracts the M3U8 URL and headers bypassing dlstreams.top."""
        try:
            # Extract ID from URL or use as is if numeric
            match_id = re.search(r"id=(\d+)", url)
            channel_id = match_id.group(1) if match_id else url
            
            if not channel_id.isdigit():
                # Remove 'premium' prefix if user passed 'premium854'
                channel_id = channel_id.replace("premium", "")

            channel_key = f"premium{channel_id}"
            session = await self._get_session()

            # --- SPEED BYPASS ---
            # Current iframe host (user can update this manually here)
            iframe_host = "embedkclx.sbs"
            iframe_origin = f"https://{iframe_host}"

            # 1. SERVER LOOKUP: Fetch dynamic server_key
            lookup_url = f"https://sec.ai-hls.site/server_lookup?channel_id={channel_key}"
            logger.info(f"Looking up server key for: {channel_key} (Bypassing dlstreams.top)")
            
            lookup_headers = {
                "Referer": f"{iframe_origin}/",
                "User-Agent": self.base_headers["User-Agent"]
            }
            
            try:
                async with session.get(lookup_url, headers=lookup_headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        server_key = data.get("server_key", "wind")
                        logger.info(f"Found server_key: {server_key}")
                    else:
                        logger.warning(f"Lookup failed (HTTP {resp.status}), using default key.")
                        server_key = "wind"
            except Exception as e:
                logger.warning(f"Error during lookup: {e}, using default key.")
                server_key = "wind"

            # 2. Construct M3U8 URL
            m3u8_url = f"https://sec.ai-hls.site/proxy/{server_key}/{channel_key}/mono.css"

            # 3. Setup headers for playback/proxying
            playback_headers = {
                "Referer": f"{iframe_origin}/",
                "Origin": iframe_origin,
                "User-Agent": self.base_headers["User-Agent"],
                "Accept": "*/*",
            }

            logger.info(f"Extracted M3U8: {m3u8_url}")

            return {
                "destination_url": m3u8_url,
                "request_headers": playback_headers,
                "mediaflow_endpoint": self.mediaflow_endpoint,
            }

        except Exception as e:
            logger.exception(f"DLStreams extraction failed for {url}")
            raise ExtractorError(f"Extraction failed: {str(e)}")

    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None
