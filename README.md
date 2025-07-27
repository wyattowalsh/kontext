# Kontext - Document Processing & Web Crawling Platform

A production-ready Streamlit application for processing documents and crawling websites with modern async architecture, comprehensive validation, and responsive UI design.

## 🌟 Features

### Document Processing
- **Multi-format Support**: PDF, DOCX, TXT, HTML, Markdown
- **Advanced Extraction**: Uses `docling` library for LLM-ready context extraction
- **Parallel Processing**: Async processing with configurable concurrency
- **Rich Metadata**: Extract tables, images, and structured content
- **Progress Tracking**: Real-time progress bars and status updates

### Web Crawling
- **Crawlee Integration**: Professional web crawling with Playwright
- **Smart Compliance**: Robots.txt respect and domain restrictions
- **Sitemap Discovery**: Automatic sitemap parsing and URL discovery
- **Configurable Strategies**: BFS/DFS crawling with depth and URL limits
- **Content Extraction**: Full page content, metadata, and link analysis

### Architecture & Quality
- **Modular OOP Design**: Clean separation of concerns
- **Async/Parallel Processing**: High-performance concurrent operations
- **Polars Integration**: Fast data processing and export
- **Comprehensive Logging**: Structured logging with Loguru
- **Input Validation**: Security-focused validation and sanitization
- **Session Management**: Persistent state and job tracking

## 🚀 Quick Start

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd kontext
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment** (optional):
   ```bash
   cp .env.example .env
   # Edit .env with your preferences
   ```

4. **Run the application**:
   ```bash
   streamlit run app.py
   ```

### Usage

1. **Document Processing**:
   - Navigate to "Document Processing" in the sidebar
   - Upload files (PDF, DOCX, TXT, HTML, MD)
   - Configure processing options
   - Click "Start Processing" and monitor progress
   - View results and export in multiple formats

2. **Web Crawling**:
   - Navigate to "Web Crawling" in the sidebar
   - Enter starting URLs (one per line)
   - Configure crawling parameters
   - Click "Start Crawling" and monitor progress
   - Review crawled content and export results

3. **Results & Export**:
   - View all processing and crawling results
   - Export data in CSV, JSON, or Parquet formats
   - Analyze content metrics and statistics

## 📁 Project Structure

```
kontext/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── config/
│   ├── __init__.py
│   ├── settings.py       # Configuration management
│   └── config.yaml       # Default configuration
├── processing/
│   ├── __init__.py
│   └── document_processor.py  # Document processing logic
├── crawling/
│   ├── __init__.py
│   └── crawler.py        # Web crawling logic
├── utils/
│   ├── __init__.py
│   ├── session_manager.py    # Session state management
│   ├── ui_helpers.py         # UI components and styling
│   └── validators.py         # Input validation utilities
├── logs/                 # Application logs
└── .env.example         # Environment variables template
```

## ⚙️ Configuration

### Environment Variables

Key environment variables for customization:

- `KONTEXT_DEBUG`: Enable debug mode (default: false)
- `KONTEXT_MAX_FILE_SIZE_MB`: Maximum file size for uploads (default: 50)
- `KONTEXT_MAX_WORKERS`: Parallel processing workers (default: 4)
- `KONTEXT_USER_AGENT`: User agent for web crawling
- `KONTEXT_LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

### Configuration File

Edit `config/config.yaml` to customize:

- Document processing settings
- Web crawling parameters
- UI preferences
- Logging configuration

## 🛡️ Security Features

- **Input Validation**: Comprehensive validation for all user inputs
- **File Security**: Magic number validation and content scanning
- **URL Safety**: Private network detection and suspicious pattern filtering
- **Path Traversal Protection**: Safe file path handling
- **Robots.txt Compliance**: Respectful web crawling practices

## 🎨 UI/UX Features

- **Responsive Design**: Mobile-friendly layout with breakpoints
- **Custom Theming**: Modern design with consistent color system
- **Progress Tracking**: Real-time progress bars and status indicators
- **Interactive Navigation**: Sidebar navigation with session info
- **Export Options**: Multiple format support with one-click export
- **Error Handling**: Graceful error display and recovery

## 📊 Data Processing

### Supported Formats

**Documents**:
- PDF (with OCR and table extraction)
- DOCX (with table and metadata extraction)
- TXT (plain text processing)
- HTML (with content and link extraction)
- Markdown (with HTML conversion)

**Export Formats**:
- CSV (tabular data)
- JSON (structured data)
- Parquet (optimized columnar format)

### Processing Features

- **Chunking**: Configurable text chunking for LLM processing
- **Metadata Extraction**: Title, description, word count, character count
- **Table Extraction**: Structured table data with captions
- **Image Analysis**: Image descriptions and positioning (when available)
- **Link Analysis**: URL extraction and validation

## 🕷️ Web Crawling

### Crawling Features

- **Domain Restriction**: Limit crawling to specific domains
- **Depth Control**: Configurable maximum crawl depth
- **URL Limits**: Maximum number of URLs to process
- **Concurrent Processing**: Configurable parallel request handling
- **Rate Limiting**: Delay between requests for respectful crawling

### Content Extraction

- **Full Text**: Clean text content extraction
- **Metadata**: Title, description, and meta tags
- **Headings**: Structured heading hierarchy (H1-H6)
- **Links**: Internal and external link discovery
- **Status Tracking**: HTTP status codes and error handling

## 🔧 Development

### Code Quality

- **Type Hints**: Full type annotation throughout
- **PEP 8 Compliance**: Consistent code formatting
- **Comprehensive Docstrings**: Detailed function documentation
- **Error Handling**: Graceful error recovery and logging
- **Testing Ready**: Modular design for easy unit testing

### Architecture Principles

- **Single Responsibility**: Each module has a clear purpose
- **Dependency Injection**: Configuration-driven initialization
- **Async First**: Non-blocking operations for better performance
- **Data Immutability**: Safe data handling with Polars
- **Session Isolation**: Clean session state management

## 📝 Logging

Structured logging with Loguru provides:

- **Rotation**: Automatic log file rotation (10MB limit)
- **Retention**: 7-day log retention policy
- **Levels**: Configurable logging levels
- **Format**: Consistent timestamp and context formatting
- **Performance**: Minimal overhead with async logging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with proper documentation
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues, questions, or contributions:

1. Check the documentation and configuration
2. Review logs in the `logs/` directory
3. Open an issue with detailed information
4. Include relevant log entries and configuration

## 🚀 Performance Tips

1. **File Processing**: Use smaller chunk sizes for faster processing
2. **Web Crawling**: Reduce concurrent requests for slower sites
3. **Memory Usage**: Process large datasets in batches
4. **Export**: Use Parquet format for large datasets
5. **Logging**: Set appropriate log levels for production use

---

Built with ❤️ using Streamlit, Crawlee, Docling, and modern Python practices.