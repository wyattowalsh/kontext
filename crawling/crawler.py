"""
Web Crawling Module for Kontext.

Advanced web crawler using Crawlee with domain restrictions, robots.txt compliance,
sitemap discovery, and configurable crawling strategies.
"""

import asyncio
import aiohttp
from pathlib import Path
from typing import List, Dict, Any, Optional, Set, Union
from urllib.parse import urljoin, urlparse, robots
from urllib.robotparser import RobotFileParser
import polars as pl
from datetime import datetime
import xml.etree.ElementTree as ET
from collections import deque
import re

# Crawlee and async libraries
from crawlee.playwright_crawler import PlaywrightCrawler, PlaywrightCrawlingContext
from crawlee.router import Router
from crawlee import Request
import streamlit as st

# Progress and logging
from tqdm.asyncio import tqdm
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from loguru import logger

# Local imports
from config.settings import AppConfig
from utils.validators import validate_url, is_same_domain

console = Console()

class WebCrawler:
    """
    Advanced web crawler with Crawlee integration and comprehensive configuration.
    
    Features:
    - Domain restriction and robots.txt compliance
    - Sitemap discovery and parsing
    - Configurable crawling strategies (BFS/DFS)
    - URL filtering and validation
    - Live progress tracking
    """
    
    def __init__(self, config: AppConfig):
        """
        Initialize the web crawler.
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.crawl_config = config.web_crawling
        
        # Crawler state
        self.visited_urls: Set[str] = set()
        self.failed_urls: Set[str] = set()
        self.robots_cache: Dict[str, RobotFileParser] = {}
        self.sitemap_urls: Set[str] = set()
        
        # Results storage
        self.crawl_results: List[Dict[str, Any]] = []
        
        # Initialize router for Crawlee
        self.router = Router[PlaywrightCrawlingContext]()
        self._setup_crawler_routes()
        
        logger.info("WebCrawler initialized with Crawlee")
    
    def _setup_crawler_routes(self) -> None:
        """Setup Crawlee router with request handlers."""
        
        @self.router.default_handler
        async def default_handler(context: PlaywrightCrawlingContext) -> None:
            """Default handler for crawled pages."""
            try:
                # Extract page content
                page_content = await self._extract_page_content(context)
                
                # Store result
                self.crawl_results.append(page_content)
                
                # Find and enqueue new URLs
                if len(self.visited_urls) < self.current_max_urls:
                    await self._enqueue_new_urls(context)
                    
            except Exception as e:
                logger.error(f"Error processing {context.request.url}: {e}")
                self.failed_urls.add(context.request.url)
    
    async def crawl_urls_async(
        self,
        start_urls: List[str],
        options: Dict[str, Any],
        progress_placeholder: Optional[Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Crawl URLs asynchronously with progress tracking.
        
        Args:
            start_urls: List of starting URLs
            options: Crawling options
            progress_placeholder: Streamlit placeholder for progress updates
            
        Returns:
            List of crawled page data
        """
        logger.info(f"Starting crawl of {len(start_urls)} URLs")
        
        # Store current options for use in handlers
        self.current_max_urls = options.get('max_urls', 100)
        self.current_max_depth = options.get('max_depth', 3)
        self.domain_restriction = options.get('domain_restriction', True)
        self.respect_robots = options.get('respect_robots', True)
        
        # Reset state
        self.visited_urls.clear()
        self.failed_urls.clear()
        self.crawl_results.clear()
        
        # Discover sitemaps if enabled
        if options.get('discover_sitemaps', True):
            await self._discover_sitemaps(start_urls)
        
        # Initialize Crawlee crawler
        crawler = PlaywrightCrawler(
            router=self.router,
            max_requests_per_crawl=self.current_max_urls,
            request_handler_timeout=self.crawl_config.timeout_seconds * 1000,  # Convert to ms
            headless=True,
            browser_type='chromium'
        )
        
        # Create initial requests
        initial_requests = []
        for url in start_urls:
            if await self._should_crawl_url(url, 0):
                initial_requests.append(Request.from_url(url, user_data={'depth': 0}))
        
        # Add sitemap URLs if discovered
        for sitemap_url in list(self.sitemap_urls)[:50]:  # Limit sitemap URLs
            if await self._should_crawl_url(sitemap_url, 0):
                initial_requests.append(Request.from_url(sitemap_url, user_data={'depth': 0}))
        
        try:
            # Run the crawler
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console
            ) as progress:
                
                task = progress.add_task("Crawling websites...", total=len(initial_requests))
                
                # Start crawling
                await crawler.run(initial_requests)
                
                # Update progress
                if progress_placeholder:
                    progress_placeholder.progress(1.0)
        
        except Exception as e:
            logger.error(f"Crawling error: {e}")
            raise
        
        finally:
            await crawler.tear_down()
        
        logger.info(f"Crawling completed. Processed {len(self.crawl_results)} pages")
        return self.crawl_results
    
    async def _extract_page_content(self, context: PlaywrightCrawlingContext) -> Dict[str, Any]:
        """Extract content from a crawled page."""
        page = context.page
        request = context.request
        
        try:
            # Basic page information
            title = await page.title()
            url = request.url
            
            # Extract text content
            text_content = await page.evaluate("""
                () => {
                    // Remove script and style elements
                    const scripts = document.querySelectorAll('script, style');
                    scripts.forEach(el => el.remove());
                    
                    // Get text content
                    return document.body.innerText || document.body.textContent || '';
                }
            """)
            
            # Extract metadata
            meta_description = await page.evaluate("""
                () => {
                    const meta = document.querySelector('meta[name="description"]');
                    return meta ? meta.getAttribute('content') : '';
                }
            """)
            
            # Extract headings
            headings = await page.evaluate("""
                () => {
                    const headings = [];
                    const elements = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
                    elements.forEach(el => {
                        headings.push({
                            level: parseInt(el.tagName.substring(1)),
                            text: el.textContent.trim()
                        });
                    });
                    return headings;
                }
            """)
            
            # Extract links
            links = await page.evaluate("""
                () => {
                    const links = [];
                    const elements = document.querySelectorAll('a[href]');
                    elements.forEach(el => {
                        const href = el.getAttribute('href');
                        const text = el.textContent.trim();
                        if (href && text) {
                            links.push({
                                url: href,
                                text: text,
                                title: el.getAttribute('title') || ''
                            });
                        }
                    });
                    return links;
                }
            """)
            
            # Get response status
            response = await page.evaluate("() => ({ status: window.performance?.navigation?.type || 0 })")
            
            # Calculate content metrics
            word_count = len(text_content.split())
            char_count = len(text_content)
            
            return {
                'url': url,
                'title': title,
                'meta_description': meta_description,
                'text_content': text_content,
                'headings': headings,
                'links': links,
                'word_count': word_count,
                'char_count': char_count,
                'status_code': 200,  # Playwright successful load
                'crawled_at': datetime.now().isoformat(),
                'depth': request.user_data.get('depth', 0)
            }
            
        except Exception as e:
            logger.error(f"Content extraction error for {request.url}: {e}")
            return {
                'url': request.url,
                'title': '',
                'meta_description': '',
                'text_content': '',
                'headings': [],
                'links': [],
                'word_count': 0,
                'char_count': 0,
                'status_code': 0,
                'error': str(e),
                'crawled_at': datetime.now().isoformat(),
                'depth': request.user_data.get('depth', 0)
            }
    
    async def _enqueue_new_urls(self, context: PlaywrightCrawlingContext) -> None:
        """Find and enqueue new URLs from the current page."""
        current_depth = context.request.user_data.get('depth', 0)
        
        if current_depth >= self.current_max_depth:
            return
        
        # Extract all links from the page
        links = await context.page.evaluate("""
            () => {
                const links = [];
                const elements = document.querySelectorAll('a[href]');
                elements.forEach(el => {
                    const href = el.getAttribute('href');
                    if (href) {
                        links.push(href);
                    }
                });
                return links;
            }
        """)
        
        # Process and filter links
        base_url = context.request.url
        new_requests = []
        
        for link in links:
            try:
                # Resolve relative URLs
                absolute_url = urljoin(base_url, link)
                
                # Check if we should crawl this URL
                if await self._should_crawl_url(absolute_url, current_depth + 1):
                    new_requests.append(
                        Request.from_url(absolute_url, user_data={'depth': current_depth + 1})
                    )
                    
                    # Limit the number of new requests
                    if len(new_requests) >= 10:
                        break
                        
            except Exception as e:
                logger.debug(f"Error processing link {link}: {e}")
                continue
        
        # Enqueue new requests
        if new_requests:
            await context.add_requests(new_requests)
    
    async def _should_crawl_url(self, url: str, depth: int) -> bool:
        """
        Determine if a URL should be crawled based on various criteria.
        
        Args:
            url: URL to check
            depth: Current crawl depth
            
        Returns:
            True if URL should be crawled
        """
        # Basic validation
        if not validate_url(url):
            return False
        
        # Check if already visited
        if url in self.visited_urls or url in self.failed_urls:
            return False
        
        # Check depth limit
        if depth > self.current_max_depth:
            return False
        
        # Check URL count limit
        if len(self.visited_urls) >= self.current_max_urls:
            return False
        
        # Parse URL
        parsed_url = urlparse(url)
        
        # Domain restriction check
        if self.domain_restriction and hasattr(self, '_start_domains'):
            if not any(is_same_domain(url, domain) for domain in self._start_domains):
                return False
        
        # Robots.txt check
        if self.respect_robots:
            if not await self._check_robots_txt(url):
                return False
        
        # File extension filtering (skip binary files)
        skip_extensions = {'.pdf', '.jpg', '.jpeg', '.png', '.gif', '.zip', '.exe', '.dmg'}
        if any(parsed_url.path.lower().endswith(ext) for ext in skip_extensions):
            return False
        
        # Mark as visited
        self.visited_urls.add(url)
        return True
    
    async def _check_robots_txt(self, url: str) -> bool:
        """
        Check if URL is allowed by robots.txt.
        
        Args:
            url: URL to check
            
        Returns:
            True if URL is allowed
        """
        try:
            parsed_url = urlparse(url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            # Check cache first
            if base_url in self.robots_cache:
                rp = self.robots_cache[base_url]
            else:
                # Fetch and parse robots.txt
                robots_url = urljoin(base_url, '/robots.txt')
                rp = RobotFileParser()
                rp.set_url(robots_url)
                
                try:
                    rp.read()
                    self.robots_cache[base_url] = rp
                except Exception as e:
                    logger.debug(f"Could not fetch robots.txt for {base_url}: {e}")
                    # If robots.txt is not accessible, allow crawling
                    return True
            
            # Check if URL is allowed
            user_agent = self.crawl_config.user_agent
            return rp.can_fetch(user_agent, url)
            
        except Exception as e:
            logger.debug(f"Robots.txt check error for {url}: {e}")
            # If there's an error, allow crawling
            return True
    
    async def _discover_sitemaps(self, start_urls: List[str]) -> None:
        """
        Discover and parse sitemaps from starting URLs.
        
        Args:
            start_urls: List of starting URLs
        """
        logger.info("Discovering sitemaps...")
        
        # Store start domains for domain restriction
        self._start_domains = [urlparse(url).netloc for url in start_urls]
        
        for url in start_urls:
            try:
                parsed_url = urlparse(url)
                base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                
                # Try common sitemap locations
                sitemap_urls = [
                    urljoin(base_url, '/sitemap.xml'),
                    urljoin(base_url, '/sitemap_index.xml'),
                    urljoin(base_url, '/sitemaps.xml')
                ]
                
                for sitemap_url in sitemap_urls:
                    await self._parse_sitemap(sitemap_url)
                    
            except Exception as e:
                logger.debug(f"Sitemap discovery error for {url}: {e}")
        
        logger.info(f"Discovered {len(self.sitemap_urls)} URLs from sitemaps")
    
    async def _parse_sitemap(self, sitemap_url: str) -> None:
        """
        Parse a sitemap XML file.
        
        Args:
            sitemap_url: URL of the sitemap
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(sitemap_url, timeout=10) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Parse XML
                        root = ET.fromstring(content)
                        
                        # Handle sitemap index
                        if 'sitemapindex' in root.tag:
                            for sitemap in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap'):
                                loc = sitemap.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                                if loc is not None:
                                    await self._parse_sitemap(loc.text)
                        
                        # Handle regular sitemap
                        elif 'urlset' in root.tag:
                            for url in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
                                loc = url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                                if loc is not None:
                                    self.sitemap_urls.add(loc.text)
                                    
                                    # Limit sitemap URLs
                                    if len(self.sitemap_urls) >= 1000:
                                        return
                        
        except Exception as e:
            logger.debug(f"Sitemap parsing error for {sitemap_url}: {e}")
    
    def export_results(
        self,
        results: List[Dict[str, Any]],
        format: str = 'json',
        output_path: Optional[str] = None
    ) -> str:
        """
        Export crawling results to specified format.
        
        Args:
            results: Crawling results to export
            format: Export format ('json', 'csv', 'parquet')
            output_path: Output file path
            
        Returns:
            Path to exported file
        """
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"kontext_crawl_results_{timestamp}.{format}"
        
        # Convert to Polars DataFrame for consistent export
        df = pl.DataFrame(results)
        
        if format == 'json':
            df.write_json(output_path)
        elif format == 'csv':
            df.write_csv(output_path)
        elif format == 'parquet':
            df.write_parquet(output_path)
        else:
            raise ValueError(f"Unsupported export format: {format}")
        
        logger.info(f"Crawl results exported to {output_path}")
        return output_path