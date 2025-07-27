"""
Kontext - Document Processing & Web Crawling Application
========================================================

A production-ready Streamlit application for processing documents and crawling websites
with modern async architecture and responsive UI design.

Author: Senior Full-Stack Python Developer
"""

import streamlit as st
import asyncio
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List
import polars as pl
from datetime import datetime

# Local imports
from config.settings import AppConfig, load_config
from processing.document_processor import DocumentProcessor
from crawling.crawler import WebCrawler
from utils.session_manager import SessionManager
from utils.ui_helpers import apply_custom_css, create_sidebar_navigation
from utils.validators import validate_urls, validate_file_types

# Configure logging
from loguru import logger
logger.add("logs/kontext_{time}.log", rotation="10 MB", retention="7 days")

class KontextApp:
    """
    Main Streamlit application class for Kontext.
    
    Handles the overall application flow, session management, and UI coordination
    between document processing and web crawling modules.
    """
    
    def __init__(self):
        """Initialize the Kontext application with configuration and session management."""
        self.config = load_config()
        self.session_manager = SessionManager()
        self.document_processor = DocumentProcessor(self.config)
        self.web_crawler = WebCrawler(self.config)
        
        # Initialize session state
        self._initialize_session_state()
        
    def _initialize_session_state(self) -> None:
        """Initialize Streamlit session state variables."""
        if 'processing_results' not in st.session_state:
            st.session_state.processing_results = []
        if 'crawl_results' not in st.session_state:
            st.session_state.crawl_results = []
        if 'current_job' not in st.session_state:
            st.session_state.current_job = None
        if 'job_progress' not in st.session_state:
            st.session_state.job_progress = 0
            
    def run(self) -> None:
        """Main application entry point."""
        # Apply custom styling
        apply_custom_css()
        
        # Set page configuration
        st.set_page_config(
            page_title="Kontext - Document Processing & Web Crawling",
            page_icon="🌐",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Create main header
        st.title("🌐 Kontext")
        st.markdown("*Professional Document Processing & Web Crawling Platform*")
        
        # Create sidebar navigation
        selected_tab = create_sidebar_navigation()
        
        # Route to appropriate module
        if selected_tab == "Document Processing":
            self._render_document_processing()
        elif selected_tab == "Web Crawling":
            self._render_web_crawling()
        elif selected_tab == "Results & Export":
            self._render_results_export()
        elif selected_tab == "Settings":
            self._render_settings()
            
    def _render_document_processing(self) -> None:
        """Render the document processing interface."""
        st.header("📄 Document Processing")
        st.markdown("Upload and process documents for LLM-ready context extraction.")
        
        # File upload section
        col1, col2 = st.columns([2, 1])
        
        with col1:
            uploaded_files = st.file_uploader(
                "Choose files to process",
                type=['pdf', 'docx', 'txt', 'html', 'md'],
                accept_multiple_files=True,
                help="Supported formats: PDF, DOCX, TXT, HTML, Markdown"
            )
            
        with col2:
            st.markdown("### Processing Options")
            extract_tables = st.checkbox("Extract tables", value=True)
            extract_images = st.checkbox("Extract image descriptions", value=False)
            chunk_size = st.slider("Chunk size (tokens)", 100, 2000, 512)
            
        # Processing controls
        if uploaded_files:
            st.markdown(f"**{len(uploaded_files)} files selected**")
            
            if st.button("🚀 Start Processing", type="primary"):
                self._process_documents(uploaded_files, {
                    'extract_tables': extract_tables,
                    'extract_images': extract_images,
                    'chunk_size': chunk_size
                })
                
        # Show current processing status
        if st.session_state.current_job == 'document_processing':
            self._show_processing_progress()
            
    def _render_web_crawling(self) -> None:
        """Render the web crawling interface."""
        st.header("🕷️ Web Crawling")
        st.markdown("Crawl websites with advanced configuration and compliance features.")
        
        # URL input section
        col1, col2 = st.columns([2, 1])
        
        with col1:
            start_urls = st.text_area(
                "Starting URLs (one per line)",
                height=100,
                placeholder="https://example.com\nhttps://another-site.com",
                help="Enter the URLs you want to start crawling from"
            )
            
        with col2:
            st.markdown("### Crawling Options")
            max_urls = st.number_input("Max URLs to crawl", 1, 10000, 100)
            max_depth = st.number_input("Max crawl depth", 1, 10, 3)
            respect_robots = st.checkbox("Respect robots.txt", value=True)
            domain_restriction = st.checkbox("Restrict to same domain", value=True)
            
        # Advanced settings
        with st.expander("🔧 Advanced Settings"):
            crawl_strategy = st.selectbox("Crawl Strategy", ["BFS", "DFS"], index=0)
            concurrent_requests = st.slider("Concurrent requests", 1, 20, 5)
            delay_between_requests = st.slider("Delay between requests (ms)", 0, 5000, 1000)
            
        # Crawling controls
        if start_urls.strip():
            urls = [url.strip() for url in start_urls.strip().split('\n') if url.strip()]
            valid_urls = validate_urls(urls)
            
            if valid_urls:
                st.success(f"✅ {len(valid_urls)} valid URLs ready for crawling")
                
                if st.button("🕸️ Start Crawling", type="primary"):
                    self._start_crawling(valid_urls, {
                        'max_urls': max_urls,
                        'max_depth': max_depth,
                        'respect_robots': respect_robots,
                        'domain_restriction': domain_restriction,
                        'crawl_strategy': crawl_strategy,
                        'concurrent_requests': concurrent_requests,
                        'delay_between_requests': delay_between_requests
                    })
            else:
                st.error("❌ No valid URLs found. Please check your input.")
                
        # Show current crawling status
        if st.session_state.current_job == 'web_crawling':
            self._show_crawling_progress()
            
    def _render_results_export(self) -> None:
        """Render the results and export interface."""
        st.header("📊 Results & Export")
        
        # Processing results
        if st.session_state.processing_results:
            st.subheader("📄 Document Processing Results")
            
            # Create results dataframe
            results_df = pl.DataFrame(st.session_state.processing_results)
            st.dataframe(results_df, use_container_width=True)
            
            # Export options
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📥 Export as CSV"):
                    self._export_results(results_df, 'csv')
            with col2:
                if st.button("📥 Export as JSON"):
                    self._export_results(results_df, 'json')
            with col3:
                if st.button("📥 Export as Parquet"):
                    self._export_results(results_df, 'parquet')
                    
        # Crawling results
        if st.session_state.crawl_results:
            st.subheader("🕷️ Web Crawling Results")
            
            crawl_df = pl.DataFrame(st.session_state.crawl_results)
            st.dataframe(crawl_df, use_container_width=True)
            
            # Export options for crawl results
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📥 Export Crawl CSV"):
                    self._export_results(crawl_df, 'csv', prefix='crawl_')
            with col2:
                if st.button("📥 Export Crawl JSON"):
                    self._export_results(crawl_df, 'json', prefix='crawl_')
            with col3:
                if st.button("📥 Export Crawl Parquet"):
                    self._export_results(crawl_df, 'parquet', prefix='crawl_')
                    
        if not st.session_state.processing_results and not st.session_state.crawl_results:
            st.info("🔍 No results available yet. Process some documents or crawl websites first!")
            
    def _render_settings(self) -> None:
        """Render the application settings interface."""
        st.header("⚙️ Settings")
        
        # Configuration display
        st.subheader("Current Configuration")
        st.json(self.config.dict())
        
        # Log level setting
        st.subheader("Logging Configuration")
        log_level = st.selectbox(
            "Log Level",
            ["DEBUG", "INFO", "WARNING", "ERROR"],
            index=1
        )
        
        if st.button("Update Log Level"):
            logger.remove()
            logger.add("logs/kontext_{time}.log", level=log_level, rotation="10 MB")
            st.success(f"Log level updated to {log_level}")
            
        # Clear session data
        st.subheader("Session Management")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ Clear Processing Results"):
                st.session_state.processing_results = []
                st.success("Processing results cleared")
                
        with col2:
            if st.button("🗑️ Clear Crawling Results"):
                st.session_state.crawl_results = []
                st.success("Crawling results cleared")
                
    def _process_documents(self, files: List, options: Dict[str, Any]) -> None:
        """Process uploaded documents asynchronously."""
        st.session_state.current_job = 'document_processing'
        st.session_state.job_progress = 0
        
        # Create progress placeholder
        progress_placeholder = st.empty()
        
        try:
            # Run async processing
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            results = loop.run_until_complete(
                self.document_processor.process_files_async(files, options, progress_placeholder)
            )
            
            # Store results
            st.session_state.processing_results.extend(results)
            st.session_state.current_job = None
            st.success(f"✅ Successfully processed {len(results)} documents!")
            
        except Exception as e:
            logger.error(f"Document processing error: {e}")
            st.error(f"❌ Processing failed: {str(e)}")
            st.session_state.current_job = None
            
    def _start_crawling(self, urls: List[str], options: Dict[str, Any]) -> None:
        """Start web crawling asynchronously."""
        st.session_state.current_job = 'web_crawling'
        st.session_state.job_progress = 0
        
        # Create progress placeholder
        progress_placeholder = st.empty()
        
        try:
            # Run async crawling
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            results = loop.run_until_complete(
                self.web_crawler.crawl_urls_async(urls, options, progress_placeholder)
            )
            
            # Store results
            st.session_state.crawl_results.extend(results)
            st.session_state.current_job = None
            st.success(f"✅ Successfully crawled {len(results)} pages!")
            
        except Exception as e:
            logger.error(f"Web crawling error: {e}")
            st.error(f"❌ Crawling failed: {str(e)}")
            st.session_state.current_job = None
            
    def _show_processing_progress(self) -> None:
        """Show document processing progress."""
        st.info("🔄 Processing documents...")
        progress_bar = st.progress(st.session_state.job_progress)
        
    def _show_crawling_progress(self) -> None:
        """Show web crawling progress."""
        st.info("🕸️ Crawling websites...")
        progress_bar = st.progress(st.session_state.job_progress)
        
    def _export_results(self, df: pl.DataFrame, format: str, prefix: str = '') -> None:
        """Export results in the specified format."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}kontext_results_{timestamp}.{format}"
        
        try:
            if format == 'csv':
                df.write_csv(filename)
            elif format == 'json':
                df.write_json(filename)
            elif format == 'parquet':
                df.write_parquet(filename)
                
            st.success(f"✅ Results exported to {filename}")
            
        except Exception as e:
            logger.error(f"Export error: {e}")
            st.error(f"❌ Export failed: {str(e)}")


def main():
    """Application entry point."""
    try:
        app = KontextApp()
        app.run()
    except Exception as e:
        logger.error(f"Application error: {e}")
        st.error(f"❌ Application error: {str(e)}")


if __name__ == "__main__":
    main()