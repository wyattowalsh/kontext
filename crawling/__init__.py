"""
Web Crawling package for Kontext.

This package handles web crawling functionality using Crawlee
with domain restrictions, robots.txt compliance, and sitemap discovery.
"""

from .crawler import WebCrawler

__all__ = ['WebCrawler']