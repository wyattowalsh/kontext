"""
Session Management Utilities for Kontext.

Handles Streamlit session state management for long-running jobs,
progress tracking, and result persistence.
"""

import streamlit as st
from typing import Any, Dict, Optional, List
from datetime import datetime, timedelta
import json
from pathlib import Path
from loguru import logger

class SessionManager:
    """
    Manages Streamlit session state for the Kontext application.
    
    Provides utilities for job tracking, progress management,
    and session data persistence.
    """
    
    def __init__(self):
        """Initialize the session manager."""
        self._initialize_session_state()
    
    def _initialize_session_state(self) -> None:
        """Initialize default session state variables."""
        defaults = {
            'processing_results': [],
            'crawl_results': [],
            'current_job': None,
            'job_progress': 0.0,
            'job_start_time': None,
            'job_status': 'idle',
            'error_messages': [],
            'success_messages': [],
            'user_preferences': {
                'theme': 'light',
                'results_per_page': 50,
                'auto_export': False,
                'default_chunk_size': 512
            },
            'session_id': self._generate_session_id(),
            'last_activity': datetime.now().isoformat()
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    def _generate_session_id(self) -> str:
        """Generate a unique session identifier."""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def start_job(self, job_type: str, job_data: Optional[Dict[str, Any]] = None) -> None:
        """
        Start a new job and update session state.
        
        Args:
            job_type: Type of job ('document_processing' or 'web_crawling')
            job_data: Additional job data
        """
        st.session_state.current_job = job_type
        st.session_state.job_progress = 0.0
        st.session_state.job_start_time = datetime.now().isoformat()
        st.session_state.job_status = 'running'
        
        if job_data:
            st.session_state[f'{job_type}_job_data'] = job_data
        
        logger.info(f"Started job: {job_type}")
    
    def update_job_progress(self, progress: float, message: Optional[str] = None) -> None:
        """
        Update job progress.
        
        Args:
            progress: Progress value between 0.0 and 1.0
            message: Optional progress message
        """
        st.session_state.job_progress = max(0.0, min(1.0, progress))
        
        if message:
            st.session_state.job_status_message = message
        
        # Update last activity
        st.session_state.last_activity = datetime.now().isoformat()
    
    def complete_job(self, results: List[Dict[str, Any]], success: bool = True) -> None:
        """
        Complete the current job and store results.
        
        Args:
            results: Job results
            success: Whether the job completed successfully
        """
        if not st.session_state.current_job:
            return
        
        job_type = st.session_state.current_job
        
        if success:
            # Store results based on job type
            if job_type == 'document_processing':
                st.session_state.processing_results.extend(results)
            elif job_type == 'web_crawling':
                st.session_state.crawl_results.extend(results)
            
            st.session_state.job_status = 'completed'
            self.add_success_message(f"Job completed successfully: {len(results)} items processed")
        else:
            st.session_state.job_status = 'failed'
            self.add_error_message(f"Job failed: {job_type}")
        
        # Calculate job duration
        if st.session_state.job_start_time:
            start_time = datetime.fromisoformat(st.session_state.job_start_time)
            duration = datetime.now() - start_time
            st.session_state.last_job_duration = str(duration)
        
        # Reset job state
        st.session_state.current_job = None
        st.session_state.job_progress = 0.0
        
        logger.info(f"Completed job: {job_type}, success: {success}")
    
    def cancel_job(self) -> None:
        """Cancel the current job."""
        if st.session_state.current_job:
            job_type = st.session_state.current_job
            st.session_state.current_job = None
            st.session_state.job_progress = 0.0
            st.session_state.job_status = 'cancelled'
            
            self.add_error_message(f"Job cancelled: {job_type}")
            logger.info(f"Cancelled job: {job_type}")
    
    def is_job_running(self) -> bool:
        """Check if a job is currently running."""
        return st.session_state.current_job is not None
    
    def get_current_job_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the current job."""
        if not self.is_job_running():
            return None
        
        start_time = None
        if st.session_state.job_start_time:
            start_time = datetime.fromisoformat(st.session_state.job_start_time)
        
        return {
            'job_type': st.session_state.current_job,
            'progress': st.session_state.job_progress,
            'status': st.session_state.job_status,
            'start_time': start_time,
            'duration': datetime.now() - start_time if start_time else None,
            'status_message': st.session_state.get('job_status_message', '')
        }
    
    def add_success_message(self, message: str) -> None:
        """Add a success message to the session."""
        st.session_state.success_messages.append({
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 10 messages
        if len(st.session_state.success_messages) > 10:
            st.session_state.success_messages = st.session_state.success_messages[-10:]
    
    def add_error_message(self, message: str) -> None:
        """Add an error message to the session."""
        st.session_state.error_messages.append({
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 10 messages
        if len(st.session_state.error_messages) > 10:
            st.session_state.error_messages = st.session_state.error_messages[-10:]
    
    def get_recent_messages(self, message_type: str = 'all') -> List[Dict[str, Any]]:
        """
        Get recent messages.
        
        Args:
            message_type: Type of messages ('success', 'error', or 'all')
            
        Returns:
            List of recent messages
        """
        messages = []
        
        if message_type in ['success', 'all']:
            for msg in st.session_state.success_messages:
                messages.append({**msg, 'type': 'success'})
        
        if message_type in ['error', 'all']:
            for msg in st.session_state.error_messages:
                messages.append({**msg, 'type': 'error'})
        
        # Sort by timestamp
        messages.sort(key=lambda x: x['timestamp'], reverse=True)
        return messages
    
    def clear_messages(self, message_type: str = 'all') -> None:
        """
        Clear messages from session.
        
        Args:
            message_type: Type of messages to clear ('success', 'error', or 'all')
        """
        if message_type in ['success', 'all']:
            st.session_state.success_messages = []
        
        if message_type in ['error', 'all']:
            st.session_state.error_messages = []
    
    def get_results_summary(self) -> Dict[str, Any]:
        """Get a summary of all results in the session."""
        processing_count = len(st.session_state.processing_results)
        crawl_count = len(st.session_state.crawl_results)
        
        # Calculate total content metrics
        total_words = 0
        total_chars = 0
        
        for result in st.session_state.processing_results:
            total_words += result.get('word_count', 0)
            total_chars += result.get('char_count', 0)
        
        for result in st.session_state.crawl_results:
            total_words += result.get('word_count', 0)
            total_chars += result.get('char_count', 0)
        
        return {
            'processing_results_count': processing_count,
            'crawl_results_count': crawl_count,
            'total_results': processing_count + crawl_count,
            'total_words': total_words,
            'total_chars': total_chars,
            'session_id': st.session_state.session_id,
            'last_activity': st.session_state.last_activity
        }
    
    def clear_all_results(self) -> None:
        """Clear all results from the session."""
        st.session_state.processing_results = []
        st.session_state.crawl_results = []
        self.add_success_message("All results cleared")
        logger.info("Cleared all session results")
    
    def export_session_data(self, output_path: Optional[str] = None) -> str:
        """
        Export session data to JSON file.
        
        Args:
            output_path: Output file path
            
        Returns:
            Path to exported file
        """
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            session_id = st.session_state.session_id
            output_path = f"kontext_session_{session_id}_{timestamp}.json"
        
        session_data = {
            'session_id': st.session_state.session_id,
            'export_timestamp': datetime.now().isoformat(),
            'processing_results': st.session_state.processing_results,
            'crawl_results': st.session_state.crawl_results,
            'user_preferences': st.session_state.user_preferences,
            'summary': self.get_results_summary()
        }
        
        with open(output_path, 'w') as f:
            json.dump(session_data, f, indent=2, default=str)
        
        logger.info(f"Session data exported to {output_path}")
        return output_path
    
    def load_session_data(self, file_path: str) -> bool:
        """
        Load session data from JSON file.
        
        Args:
            file_path: Path to session data file
            
        Returns:
            True if loaded successfully
        """
        try:
            with open(file_path, 'r') as f:
                session_data = json.load(f)
            
            # Restore session data
            st.session_state.processing_results = session_data.get('processing_results', [])
            st.session_state.crawl_results = session_data.get('crawl_results', [])
            st.session_state.user_preferences.update(
                session_data.get('user_preferences', {})
            )
            
            self.add_success_message(f"Session data loaded from {file_path}")
            logger.info(f"Session data loaded from {file_path}")
            return True
            
        except Exception as e:
            self.add_error_message(f"Failed to load session data: {str(e)}")
            logger.error(f"Failed to load session data from {file_path}: {e}")
            return False
    
    def update_user_preference(self, key: str, value: Any) -> None:
        """
        Update a user preference.
        
        Args:
            key: Preference key
            value: Preference value
        """
        st.session_state.user_preferences[key] = value
        st.session_state.last_activity = datetime.now().isoformat()
        logger.debug(f"Updated user preference: {key} = {value}")
    
    def get_user_preference(self, key: str, default: Any = None) -> Any:
        """
        Get a user preference value.
        
        Args:
            key: Preference key
            default: Default value if key not found
            
        Returns:
            Preference value
        """
        return st.session_state.user_preferences.get(key, default)