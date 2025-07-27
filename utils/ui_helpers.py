"""
UI Helper Functions for Kontext.

Provides utilities for custom styling, navigation, and UI components
following Streamlit best practices and modern design patterns.
"""

import streamlit as st
from streamlit_option_menu import option_menu
from typing import Dict, Any, List, Optional
import base64
from pathlib import Path

def apply_custom_css() -> None:
    """Apply custom CSS styling to the Streamlit app."""
    
    css = """
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Root variables for consistent theming */
    :root {
        --primary-color: #1f2937;
        --secondary-color: #3b82f6;
        --accent-color: #10b981;
        --background-color: #f8fafc;
        --surface-color: #ffffff;
        --text-primary: #1f2937;
        --text-secondary: #6b7280;
        --border-color: #e5e7eb;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
        --border-radius: 8px;
        --transition: all 0.2s ease-in-out;
    }
    
    /* Global styles */
    .main {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: var(--background-color);
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        color: white;
        padding: 2rem 0;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 var(--border-radius) var(--border-radius);
        box-shadow: var(--shadow-lg);
    }
    
    .main-header h1 {
        font-weight: 700;
        font-size: 2.5rem;
        margin: 0;
        text-align: center;
    }
    
    .main-header p {
        text-align: center;
        opacity: 0.9;
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: var(--surface-color);
        border-right: 1px solid var(--border-color);
    }
    
    /* Card components */
    .custom-card {
        background: var(--surface-color);
        border-radius: var(--border-radius);
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: var(--shadow-sm);
        border: 1px solid var(--border-color);
        transition: var(--transition);
    }
    
    .custom-card:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-2px);
    }
    
    .card-header {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, var(--secondary-color) 0%, var(--accent-color) 100%);
        color: white;
        border: none;
        border-radius: var(--border-radius);
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        font-family: 'Inter', sans-serif;
        transition: var(--transition);
        box-shadow: var(--shadow-sm);
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Progress bars */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--secondary-color) 0%, var(--accent-color) 100%);
        border-radius: var(--border-radius);
    }
    
    /* File uploader */
    .stFileUploader > div {
        background: var(--surface-color);
        border: 2px dashed var(--border-color);
        border-radius: var(--border-radius);
        padding: 2rem;
        text-align: center;
        transition: var(--transition);
    }
    
    .stFileUploader > div:hover {
        border-color: var(--secondary-color);
        background: rgba(59, 130, 246, 0.05);
    }
    
    /* Metrics */
    .metric-container {
        display: flex;
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .metric-card {
        flex: 1;
        background: var(--surface-color);
        border-radius: var(--border-radius);
        padding: 1rem;
        text-align: center;
        box-shadow: var(--shadow-sm);
        border: 1px solid var(--border-color);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: var(--secondary-color);
        margin: 0;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: var(--text-secondary);
        margin: 0.25rem 0 0 0;
    }
    
    /* Status indicators */
    .status-success {
        background: rgba(16, 185, 129, 0.1);
        color: #059669;
        padding: 0.5rem 1rem;
        border-radius: var(--border-radius);
        border: 1px solid rgba(16, 185, 129, 0.2);
        font-weight: 500;
    }
    
    .status-error {
        background: rgba(239, 68, 68, 0.1);
        color: #dc2626;
        padding: 0.5rem 1rem;
        border-radius: var(--border-radius);
        border: 1px solid rgba(239, 68, 68, 0.2);
        font-weight: 500;
    }
    
    .status-warning {
        background: rgba(245, 158, 11, 0.1);
        color: #d97706;
        padding: 0.5rem 1rem;
        border-radius: var(--border-radius);
        border: 1px solid rgba(245, 158, 11, 0.2);
        font-weight: 500;
    }
    
    /* Data tables */
    .stDataFrame {
        border-radius: var(--border-radius);
        overflow: hidden;
        box-shadow: var(--shadow-sm);
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: var(--surface-color);
        border-radius: var(--border-radius);
        border: 1px solid var(--border-color);
        font-weight: 500;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
        
        .metric-container {
            flex-direction: column;
        }
        
        .custom-card {
            padding: 1rem;
        }
    }
    
    /* Animation keyframes */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.3s ease-out;
    }
    
    /* Loading spinner */
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid rgba(59, 130, 246, 0.3);
        border-radius: 50%;
        border-top-color: var(--secondary-color);
        animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* Tooltip styling */
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
    }
    
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: var(--primary-color);
        color: white;
        text-align: center;
        border-radius: var(--border-radius);
        padding: 0.5rem;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 0.875rem;
    }
    
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)

def create_sidebar_navigation() -> str:
    """
    Create sidebar navigation menu.
    
    Returns:
        Selected menu option
    """
    with st.sidebar:
        st.markdown("### 🌐 Kontext")
        st.markdown("---")
        
        selected = option_menu(
            menu_title=None,
            options=[
                "Document Processing",
                "Web Crawling", 
                "Results & Export",
                "Settings"
            ],
            icons=[
                "file-earmark-text",
                "globe",
                "download",
                "gear"
            ],
            menu_icon="cast",
            default_index=0,
            styles={
                "container": {
                    "padding": "0!important",
                    "background-color": "transparent"
                },
                "icon": {
                    "color": "#3b82f6",
                    "font-size": "18px"
                },
                "nav-link": {
                    "font-size": "16px",
                    "text-align": "left",
                    "margin": "0px",
                    "padding": "10px 15px",
                    "border-radius": "8px",
                    "color": "#1f2937",
                    "background-color": "transparent"
                },
                "nav-link-selected": {
                    "background-color": "#3b82f6",
                    "color": "white",
                    "font-weight": "500"
                }
            }
        )
        
        # Add session info
        st.markdown("---")
        st.markdown("### 📊 Session Info")
        
        # Get session summary from session manager
        if hasattr(st.session_state, 'processing_results'):
            processing_count = len(st.session_state.processing_results)
            crawl_count = len(st.session_state.crawl_results)
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Documents", processing_count)
            with col2:
                st.metric("Pages", crawl_count)
        
        # Current job status
        if st.session_state.get('current_job'):
            st.markdown("### 🔄 Current Job")
            job_info = {
                'type': st.session_state.current_job,
                'progress': st.session_state.get('job_progress', 0)
            }
            st.write(f"**{job_info['type'].replace('_', ' ').title()}**")
            st.progress(job_info['progress'])
    
    return selected

def create_metric_cards(metrics: Dict[str, Any]) -> None:
    """
    Create metric cards display.
    
    Args:
        metrics: Dictionary of metrics to display
    """
    if not metrics:
        return
    
    # Calculate number of columns based on metrics count
    num_metrics = len(metrics)
    cols = st.columns(min(num_metrics, 4))
    
    for i, (key, value) in enumerate(metrics.items()):
        with cols[i % len(cols)]:
            # Format the key for display
            display_key = key.replace('_', ' ').title()
            
            # Format the value
            if isinstance(value, (int, float)):
                if value >= 1000000:
                    display_value = f"{value/1000000:.1f}M"
                elif value >= 1000:
                    display_value = f"{value/1000:.1f}K"
                else:
                    display_value = str(value)
            else:
                display_value = str(value)
            
            st.metric(display_key, display_value)

def create_status_indicator(status: str, message: str = "") -> None:
    """
    Create a status indicator with appropriate styling.
    
    Args:
        status: Status type ('success', 'error', 'warning', 'info')
        message: Status message
    """
    status_icons = {
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️'
    }
    
    status_colors = {
        'success': '#10b981',
        'error': '#ef4444',
        'warning': '#f59e0b',
        'info': '#3b82f6'
    }
    
    icon = status_icons.get(status, 'ℹ️')
    color = status_colors.get(status, '#3b82f6')
    
    st.markdown(
        f"""
        <div style="
            background: {color}15;
            color: {color};
            padding: 0.75rem 1rem;
            border-radius: 8px;
            border: 1px solid {color}30;
            font-weight: 500;
            margin: 0.5rem 0;
        ">
            {icon} {message}
        </div>
        """,
        unsafe_allow_html=True
    )

def create_progress_card(title: str, progress: float, details: Optional[Dict[str, Any]] = None) -> None:
    """
    Create a progress card with details.
    
    Args:
        title: Progress card title
        progress: Progress value (0.0 to 1.0)
        details: Optional details to display
    """
    st.markdown(
        f"""
        <div class="custom-card">
            <div class="card-header">
                <span class="loading-spinner"></span>
                {title}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Progress bar
    st.progress(progress)
    
    # Progress percentage
    st.write(f"**{progress*100:.1f}% Complete**")
    
    # Additional details
    if details:
        with st.expander("📊 Details"):
            for key, value in details.items():
                st.write(f"**{key.replace('_', ' ').title()}:** {value}")

def create_file_upload_area(
    label: str,
    accepted_types: List[str],
    help_text: Optional[str] = None,
    multiple: bool = True
) -> Any:
    """
    Create a styled file upload area.
    
    Args:
        label: Upload area label
        accepted_types: List of accepted file types
        help_text: Optional help text
        multiple: Whether to accept multiple files
        
    Returns:
        Uploaded files
    """
    st.markdown(
        f"""
        <div class="card-header">
            📁 {label}
        </div>
        """,
        unsafe_allow_html=True
    )
    
    uploaded_files = st.file_uploader(
        label="",
        type=accepted_types,
        accept_multiple_files=multiple,
        help=help_text,
        label_visibility="collapsed"
    )
    
    if uploaded_files:
        if multiple and isinstance(uploaded_files, list):
            st.success(f"✅ {len(uploaded_files)} files selected")
        else:
            st.success("✅ File selected")
    
    return uploaded_files

def create_results_table(data: List[Dict[str, Any]], title: str = "Results") -> None:
    """
    Create a formatted results table.
    
    Args:
        data: List of result dictionaries
        title: Table title
    """
    if not data:
        st.info("🔍 No results to display")
        return
    
    st.markdown(
        f"""
        <div class="card-header">
            📊 {title}
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Convert to DataFrame for display
    import polars as pl
    df = pl.DataFrame(data)
    
    # Display table
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )
    
    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Items", len(data))
    with col2:
        if 'word_count' in data[0]:
            total_words = sum(item.get('word_count', 0) for item in data)
            st.metric("Total Words", f"{total_words:,}")
    with col3:
        if 'char_count' in data[0]:
            total_chars = sum(item.get('char_count', 0) for item in data)
            st.metric("Total Characters", f"{total_chars:,}")

def create_export_buttons(data: List[Dict[str, Any]], prefix: str = "") -> None:
    """
    Create export buttons for data.
    
    Args:
        data: Data to export
        prefix: Filename prefix
    """
    if not data:
        return
    
    st.markdown("### 📥 Export Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Export CSV", key=f"{prefix}_csv"):
            # Export logic would be handled by the calling component
            st.success("CSV export initiated")
    
    with col2:
        if st.button("📋 Export JSON", key=f"{prefix}_json"):
            st.success("JSON export initiated")
    
    with col3:
        if st.button("🗃️ Export Parquet", key=f"{prefix}_parquet"):
            st.success("Parquet export initiated")

def show_help_modal(title: str, content: str) -> None:
    """
    Show a help modal with information.
    
    Args:
        title: Modal title
        content: Modal content
    """
    with st.expander(f"❓ {title}"):
        st.markdown(content)

def create_settings_section(title: str, settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a settings section with form controls.
    
    Args:
        title: Section title
        settings: Current settings
        
    Returns:
        Updated settings
    """
    st.markdown(f"### ⚙️ {title}")
    
    updated_settings = {}
    
    for key, value in settings.items():
        display_key = key.replace('_', ' ').title()
        
        if isinstance(value, bool):
            updated_settings[key] = st.checkbox(display_key, value=value)
        elif isinstance(value, int):
            updated_settings[key] = st.number_input(display_key, value=value)
        elif isinstance(value, float):
            updated_settings[key] = st.number_input(display_key, value=value, format="%.2f")
        elif isinstance(value, str):
            updated_settings[key] = st.text_input(display_key, value=value)
        elif isinstance(value, list):
            # Handle list inputs as multiselect or text area
            if all(isinstance(item, str) for item in value):
                updated_settings[key] = st.multiselect(
                    display_key,
                    options=value,
                    default=value
                )
            else:
                updated_settings[key] = value
        else:
            updated_settings[key] = value
    
    return updated_settings