"""
Configuration management for Kontext application.

Handles loading and validation of application settings from YAML files
and environment variables with Pydantic models.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DocumentProcessingConfig(BaseModel):
    """Configuration for document processing module."""
    
    supported_formats: List[str] = Field(
        default=['pdf', 'docx', 'txt', 'html', 'md'],
        description="Supported document formats"
    )
    max_file_size_mb: int = Field(
        default=50,
        description="Maximum file size in MB"
    )
    default_chunk_size: int = Field(
        default=512,
        description="Default chunk size for text splitting"
    )
    extract_tables: bool = Field(
        default=True,
        description="Extract tables by default"
    )
    extract_images: bool = Field(
        default=False,
        description="Extract image descriptions by default"
    )
    parallel_processing: bool = Field(
        default=True,
        description="Enable parallel processing"
    )
    max_workers: int = Field(
        default=4,
        description="Maximum number of worker threads"
    )

class WebCrawlingConfig(BaseModel):
    """Configuration for web crawling module."""
    
    default_max_urls: int = Field(
        default=100,
        description="Default maximum URLs to crawl"
    )
    default_max_depth: int = Field(
        default=3,
        description="Default maximum crawl depth"
    )
    default_concurrent_requests: int = Field(
        default=5,
        description="Default number of concurrent requests"
    )
    default_delay_ms: int = Field(
        default=1000,
        description="Default delay between requests in milliseconds"
    )
    respect_robots_txt: bool = Field(
        default=True,
        description="Respect robots.txt by default"
    )
    user_agent: str = Field(
        default="Kontext-Crawler/1.0 (+https://github.com/your-repo/kontext)",
        description="User agent string for crawling"
    )
    timeout_seconds: int = Field(
        default=30,
        description="Request timeout in seconds"
    )
    max_retries: int = Field(
        default=3,
        description="Maximum number of retries for failed requests"
    )

class LoggingConfig(BaseModel):
    """Configuration for logging."""
    
    level: str = Field(
        default="INFO",
        description="Logging level"
    )
    format: str = Field(
        default="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}",
        description="Log format string"
    )
    rotation: str = Field(
        default="10 MB",
        description="Log rotation size"
    )
    retention: str = Field(
        default="7 days",
        description="Log retention period"
    )
    log_dir: str = Field(
        default="logs",
        description="Directory for log files"
    )

class UIConfig(BaseModel):
    """Configuration for UI settings."""
    
    theme: str = Field(
        default="light",
        description="UI theme (light/dark)"
    )
    sidebar_expanded: bool = Field(
        default=True,
        description="Sidebar expanded by default"
    )
    show_progress_bars: bool = Field(
        default=True,
        description="Show progress bars during processing"
    )
    results_per_page: int = Field(
        default=50,
        description="Number of results to show per page"
    )

class AppConfig(BaseModel):
    """Main application configuration."""
    
    app_name: str = Field(
        default="Kontext",
        description="Application name"
    )
    version: str = Field(
        default="1.0.0",
        description="Application version"
    )
    debug: bool = Field(
        default=False,
        description="Debug mode"
    )
    
    # Module configurations
    document_processing: DocumentProcessingConfig = Field(
        default_factory=DocumentProcessingConfig
    )
    web_crawling: WebCrawlingConfig = Field(
        default_factory=WebCrawlingConfig
    )
    logging: LoggingConfig = Field(
        default_factory=LoggingConfig
    )
    ui: UIConfig = Field(
        default_factory=UIConfig
    )
    
    @validator('debug', pre=True)
    def parse_debug(cls, v):
        """Parse debug flag from environment variable."""
        if isinstance(v, str):
            return v.lower() in ('true', '1', 'yes', 'on')
        return v

def load_config(config_path: Optional[str] = None) -> AppConfig:
    """
    Load application configuration from YAML file and environment variables.
    
    Args:
        config_path: Path to configuration file. Defaults to config/config.yaml
        
    Returns:
        AppConfig: Loaded and validated configuration
    """
    if config_path is None:
        config_path = Path(__file__).parent / "config.yaml"
    
    # Load base configuration from YAML
    config_data = {}
    if Path(config_path).exists():
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f) or {}
    
    # Override with environment variables
    env_overrides = {
        'debug': os.getenv('KONTEXT_DEBUG', config_data.get('debug', False)),
        'app_name': os.getenv('KONTEXT_APP_NAME', config_data.get('app_name', 'Kontext')),
        'version': os.getenv('KONTEXT_VERSION', config_data.get('version', '1.0.0')),
    }
    
    # Merge configurations
    config_data.update({k: v for k, v in env_overrides.items() if v is not None})
    
    # Create and validate configuration
    return AppConfig(**config_data)

def save_config(config: AppConfig, config_path: Optional[str] = None) -> None:
    """
    Save configuration to YAML file.
    
    Args:
        config: Configuration to save
        config_path: Path to save configuration file
    """
    if config_path is None:
        config_path = Path(__file__).parent / "config.yaml"
    
    # Ensure directory exists
    Path(config_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Save configuration
    with open(config_path, 'w') as f:
        yaml.dump(config.dict(), f, default_flow_style=False, indent=2)