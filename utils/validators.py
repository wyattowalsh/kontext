"""
Validation Utilities for Kontext.

Provides comprehensive validation functions for URLs, files, and user inputs
with proper error handling and security considerations.
"""

import re
import validators
from urllib.parse import urlparse, urljoin
from pathlib import Path
from typing import List, Optional, Any, Union
import mimetypes
from loguru import logger

# File size constants
MB = 1024 * 1024
GB = 1024 * MB

def validate_url(url: str) -> bool:
    """
    Validate if a URL is properly formatted and accessible.
    
    Args:
        url: URL to validate
        
    Returns:
        True if URL is valid
    """
    if not url or not isinstance(url, str):
        return False
    
    # Basic URL validation using validators library
    if not validators.url(url):
        return False
    
    # Parse URL for additional checks
    try:
        parsed = urlparse(url)
        
        # Check for required components
        if not parsed.scheme or not parsed.netloc:
            return False
        
        # Only allow HTTP/HTTPS
        if parsed.scheme not in ['http', 'https']:
            return False
        
        # Check for suspicious patterns
        suspicious_patterns = [
            r'localhost',
            r'127\.0\.0\.1',
            r'0\.0\.0\.0',
            r'192\.168\.',
            r'10\.',
            r'172\.(1[6-9]|2[0-9]|3[0-1])\.'
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, parsed.netloc, re.IGNORECASE):
                logger.warning(f"Potentially unsafe URL detected: {url}")
                # Don't reject, but log for security awareness
                break
        
        return True
        
    except Exception as e:
        logger.debug(f"URL validation error for {url}: {e}")
        return False

def validate_urls(urls: List[str]) -> List[str]:
    """
    Validate a list of URLs and return only valid ones.
    
    Args:
        urls: List of URLs to validate
        
    Returns:
        List of valid URLs
    """
    valid_urls = []
    
    for url in urls:
        if validate_url(url):
            valid_urls.append(url.strip())
        else:
            logger.warning(f"Invalid URL skipped: {url}")
    
    return valid_urls

def is_same_domain(url1: str, url2: str) -> bool:
    """
    Check if two URLs belong to the same domain.
    
    Args:
        url1: First URL
        url2: Second URL
        
    Returns:
        True if URLs are from the same domain
    """
    try:
        domain1 = urlparse(url1).netloc.lower()
        domain2 = urlparse(url2).netloc.lower()
        
        # Remove www. prefix for comparison
        domain1 = domain1.replace('www.', '')
        domain2 = domain2.replace('www.', '')
        
        return domain1 == domain2
        
    except Exception:
        return False

def validate_file_type(filename: str, allowed_types: List[str]) -> bool:
    """
    Validate if a file type is allowed.
    
    Args:
        filename: Name of the file
        allowed_types: List of allowed file extensions (without dots)
        
    Returns:
        True if file type is allowed
    """
    if not filename or not isinstance(filename, str):
        return False
    
    # Get file extension
    file_extension = Path(filename).suffix.lower().lstrip('.')
    
    # Check against allowed types
    allowed_types_lower = [ext.lower() for ext in allowed_types]
    
    return file_extension in allowed_types_lower

def validate_file_size(file_obj: Any, max_size_mb: int) -> bool:
    """
    Validate if a file size is within limits.
    
    Args:
        file_obj: File object (Streamlit uploaded file)
        max_size_mb: Maximum allowed size in MB
        
    Returns:
        True if file size is acceptable
    """
    try:
        # Get file size
        if hasattr(file_obj, 'size'):
            file_size = file_obj.size
        elif hasattr(file_obj, 'getvalue'):
            file_size = len(file_obj.getvalue())
        else:
            # Try to read and get size
            current_pos = file_obj.tell() if hasattr(file_obj, 'tell') else 0
            file_obj.seek(0, 2)  # Seek to end
            file_size = file_obj.tell()
            file_obj.seek(current_pos)  # Restore position
        
        max_size_bytes = max_size_mb * MB
        return file_size <= max_size_bytes
        
    except Exception as e:
        logger.error(f"File size validation error: {e}")
        return False

def validate_file_content(file_obj: Any, filename: str) -> bool:
    """
    Validate file content for security and integrity.
    
    Args:
        file_obj: File object
        filename: Original filename
        
    Returns:
        True if file content is safe
    """
    try:
        # Get file extension
        file_extension = Path(filename).suffix.lower()
        
        # Read first few bytes for magic number validation
        current_pos = file_obj.tell() if hasattr(file_obj, 'tell') else 0
        file_obj.seek(0)
        header = file_obj.read(1024)  # Read first 1KB
        file_obj.seek(current_pos)  # Restore position
        
        # Basic magic number checks
        magic_numbers = {
            '.pdf': [b'%PDF'],
            '.docx': [b'PK\x03\x04'],  # ZIP-based format
            '.zip': [b'PK\x03\x04'],
            '.png': [b'\x89PNG'],
            '.jpg': [b'\xff\xd8\xff'],
            '.jpeg': [b'\xff\xd8\xff'],
            '.gif': [b'GIF87a', b'GIF89a']
        }
        
        if file_extension in magic_numbers:
            expected_headers = magic_numbers[file_extension]
            if not any(header.startswith(magic) for magic in expected_headers):
                logger.warning(f"File header mismatch for {filename}")
                # Don't reject, but log for awareness
        
        # Check for suspicious content patterns
        suspicious_patterns = [
            b'<script',
            b'javascript:',
            b'vbscript:',
            b'onload=',
            b'onerror='
        ]
        
        header_lower = header.lower()
        for pattern in suspicious_patterns:
            if pattern in header_lower:
                logger.warning(f"Suspicious content detected in {filename}")
                return False
        
        return True
        
    except Exception as e:
        logger.error(f"File content validation error for {filename}: {e}")
        return False

def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename for safe storage.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    if not filename:
        return "unnamed_file"
    
    # Remove or replace dangerous characters
    dangerous_chars = r'[<>:"/\\|?*\x00-\x1f]'
    sanitized = re.sub(dangerous_chars, '_', filename)
    
    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip('. ')
    
    # Ensure filename is not empty
    if not sanitized:
        sanitized = "unnamed_file"
    
    # Limit length
    if len(sanitized) > 255:
        name, ext = Path(sanitized).stem, Path(sanitized).suffix
        max_name_length = 255 - len(ext)
        sanitized = name[:max_name_length] + ext
    
    return sanitized

def validate_crawl_options(options: dict) -> dict:
    """
    Validate and sanitize crawling options.
    
    Args:
        options: Crawling options dictionary
        
    Returns:
        Validated and sanitized options
    """
    validated = {}
    
    # Max URLs validation
    max_urls = options.get('max_urls', 100)
    validated['max_urls'] = max(1, min(max_urls, 10000))
    
    # Max depth validation
    max_depth = options.get('max_depth', 3)
    validated['max_depth'] = max(1, min(max_depth, 10))
    
    # Concurrent requests validation
    concurrent_requests = options.get('concurrent_requests', 5)
    validated['concurrent_requests'] = max(1, min(concurrent_requests, 20))
    
    # Delay validation
    delay = options.get('delay_between_requests', 1000)
    validated['delay_between_requests'] = max(0, min(delay, 10000))
    
    # Boolean options
    validated['respect_robots'] = bool(options.get('respect_robots', True))
    validated['domain_restriction'] = bool(options.get('domain_restriction', True))
    
    # Strategy validation
    strategy = options.get('crawl_strategy', 'BFS')
    validated['crawl_strategy'] = strategy if strategy in ['BFS', 'DFS'] else 'BFS'
    
    return validated

def validate_processing_options(options: dict) -> dict:
    """
    Validate and sanitize document processing options.
    
    Args:
        options: Processing options dictionary
        
    Returns:
        Validated and sanitized options
    """
    validated = {}
    
    # Chunk size validation
    chunk_size = options.get('chunk_size', 512)
    validated['chunk_size'] = max(50, min(chunk_size, 4000))
    
    # Boolean options
    validated['extract_tables'] = bool(options.get('extract_tables', True))
    validated['extract_images'] = bool(options.get('extract_images', False))
    
    return validated

def validate_export_format(format_str: str) -> str:
    """
    Validate export format.
    
    Args:
        format_str: Export format string
        
    Returns:
        Validated format string
    """
    allowed_formats = ['json', 'csv', 'parquet', 'xlsx']
    format_lower = format_str.lower().strip()
    
    if format_lower in allowed_formats:
        return format_lower
    else:
        logger.warning(f"Invalid export format: {format_str}, defaulting to json")
        return 'json'

def validate_user_input(input_str: str, max_length: int = 1000) -> str:
    """
    Validate and sanitize user text input.
    
    Args:
        input_str: User input string
        max_length: Maximum allowed length
        
    Returns:
        Sanitized input string
    """
    if not input_str or not isinstance(input_str, str):
        return ""
    
    # Remove control characters
    sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', input_str)
    
    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    # Strip whitespace
    sanitized = sanitized.strip()
    
    return sanitized

def validate_regex_pattern(pattern: str) -> bool:
    """
    Validate if a string is a valid regex pattern.
    
    Args:
        pattern: Regex pattern string
        
    Returns:
        True if pattern is valid
    """
    try:
        re.compile(pattern)
        return True
    except re.error:
        return False

def validate_json_structure(data: Any, required_keys: Optional[List[str]] = None) -> bool:
    """
    Validate JSON data structure.
    
    Args:
        data: Data to validate
        required_keys: List of required keys (for dict validation)
        
    Returns:
        True if structure is valid
    """
    try:
        if required_keys and isinstance(data, dict):
            return all(key in data for key in required_keys)
        return True
    except Exception:
        return False

def get_safe_path(base_path: str, filename: str) -> Path:
    """
    Get a safe file path preventing directory traversal.
    
    Args:
        base_path: Base directory path
        filename: Filename to join
        
    Returns:
        Safe Path object
    """
    # Sanitize filename
    safe_filename = sanitize_filename(filename)
    
    # Create path
    base = Path(base_path).resolve()
    full_path = (base / safe_filename).resolve()
    
    # Ensure the path is within the base directory
    try:
        full_path.relative_to(base)
        return full_path
    except ValueError:
        # Path traversal attempt detected
        logger.warning(f"Path traversal attempt detected: {filename}")
        return base / "safe_filename.txt"

# Security validation functions
def is_safe_url_for_crawling(url: str) -> bool:
    """
    Check if URL is safe for crawling (not internal/private networks).
    
    Args:
        url: URL to check
        
    Returns:
        True if URL is safe for crawling
    """
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        
        if not hostname:
            return False
        
        # Check for private/internal networks
        import ipaddress
        
        try:
            ip = ipaddress.ip_address(hostname)
            # Reject private networks
            if ip.is_private or ip.is_loopback or ip.is_link_local:
                return False
        except ValueError:
            # Not an IP address, check hostname patterns
            private_patterns = [
                r'^localhost$',
                r'^.*\.local$',
                r'^.*\.internal$',
                r'^.*\.corp$'
            ]
            
            for pattern in private_patterns:
                if re.match(pattern, hostname, re.IGNORECASE):
                    return False
        
        return True
        
    except Exception:
        return False