"""
Utility Functions
Helper functions for the multi-agent system
"""

import base64
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import asyncio


# ============================================================================
# Logging Utilities
# ============================================================================

def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
):
    """
    Setup logging configuration
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional file to write logs to
        log_format: Log message format
    """
    
    handlers = [logging.StreamHandler()]
    
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=handlers
    )


# ============================================================================
# File Utilities
# ============================================================================

def save_screenshot(
    screenshot_base64: str,
    directory: str = "./screenshots",
    filename: Optional[str] = None
) -> str:
    """
    Save a base64 screenshot to file
    
    Args:
        screenshot_base64: Base64 encoded image
        directory: Directory to save to
        filename: Optional filename (auto-generated if not provided)
        
    Returns:
        Path to saved file
    """
    
    Path(directory).mkdir(parents=True, exist_ok=True)
    
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
    
    filepath = Path(directory) / filename
    
    # Decode and save
    image_bytes = base64.b64decode(screenshot_base64)
    filepath.write_bytes(image_bytes)
    
    return str(filepath)


def save_execution_log(
    execution_data: Dict[str, Any],
    directory: str = "./logs",
    filename: Optional[str] = None
) -> str:
    """
    Save execution log to JSON file
    
    Args:
        execution_data: Execution data to save
        directory: Directory to save to
        filename: Optional filename
        
    Returns:
        Path to saved file
    """
    
    Path(directory).mkdir(parents=True, exist_ok=True)
    
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"execution_{timestamp}.json"
    
    filepath = Path(directory) / filename
    
    with open(filepath, 'w') as f:
        json.dump(execution_data, f, indent=2, default=str)
    
    return str(filepath)


# ============================================================================
# Data Processing Utilities
# ============================================================================

def extract_json_from_llm_response(response: str) -> Dict[str, Any]:
    """
    Extract JSON from LLM response that might contain markdown code blocks
    
    Args:
        response: LLM response text
        
    Returns:
        Parsed JSON dictionary
    """
    
    # Try to extract from markdown code blocks
    if "```json" in response:
        response = response.split("```json")[1].split("```")[0]
    elif "```" in response:
        response = response.split("```")[1].split("```")[0]
    
    # Clean and parse
    response = response.strip()
    return json.loads(response)


def create_element_summary(elements: List[Dict[str, Any]]) -> str:
    """
    Create a readable summary of web elements
    
    Args:
        elements: List of element dictionaries
        
    Returns:
        Formatted string summary
    """
    
    if not elements:
        return "No elements found"
    
    summary_lines = []
    for idx, elem in enumerate(elements):
        element_type = elem.get("element_type", "unknown").upper()
        text = elem.get("text", "")[:50]
        coords = elem.get("coordinates", {})
        
        line = f"{idx}. {element_type}"
        if text:
            line += f" - '{text}'"
        if coords:
            line += f" @ ({coords.get('x', 0):.0f}, {coords.get('y', 0):.0f})"
        
        summary_lines.append(line)
    
    return "\n".join(summary_lines)


# ============================================================================
# Validation Utilities
# ============================================================================

def validate_url(url: str) -> bool:
    """
    Validate if a string is a proper URL
    
    Args:
        url: URL string to validate
        
    Returns:
        True if valid, False otherwise
    """
    
    from urllib.parse import urlparse
    
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def is_safe_domain(url: str, blocked_domains: List[str]) -> bool:
    """
    Check if a URL's domain is safe (not in blocklist)
    
    Args:
        url: URL to check
        blocked_domains: List of blocked domain strings
        
    Returns:
        True if safe, False if blocked
    """
    
    from urllib.parse import urlparse
    
    domain = urlparse(url).netloc.lower()
    
    for blocked in blocked_domains:
        if blocked.lower() in domain:
            return False
    
    return True


# ============================================================================
# Rate Limiting Utilities
# ============================================================================

class RateLimiter:
    """Simple rate limiter for API calls"""
    
    def __init__(self, max_calls: int, time_window_seconds: int):
        self.max_calls = max_calls
        self.time_window = time_window_seconds
        self.calls = []
    
    async def acquire(self):
        """Wait if necessary to respect rate limit"""
        now = datetime.now()
        
        # Remove old calls outside time window
        cutoff = now.timestamp() - self.time_window
        self.calls = [t for t in self.calls if t > cutoff]
        
        # If at limit, wait
        if len(self.calls) >= self.max_calls:
            oldest_call = min(self.calls)
            wait_time = (oldest_call + self.time_window) - now.timestamp()
            if wait_time > 0:
                await asyncio.sleep(wait_time)
                self.calls = []
        
        # Record this call
        self.calls.append(now.timestamp())


# ============================================================================
# Progress Tracking
# ============================================================================

class ProgressTracker:
    """Track progress of multi-step tasks"""
    
    def __init__(self, total_steps: Optional[int] = None):
        self.total_steps = total_steps
        self.current_step = 0
        self.steps_completed = []
        self.start_time = datetime.now()
    
    def update(self, step_description: str):
        """Update progress"""
        self.current_step += 1
        self.steps_completed.append({
            "step": self.current_step,
            "description": step_description,
            "timestamp": datetime.now()
        })
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current progress"""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        progress = {
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "elapsed_seconds": elapsed,
            "steps_completed": self.steps_completed
        }
        
        if self.total_steps:
            progress["percentage"] = (self.current_step / self.total_steps) * 100
            
            if self.current_step > 0:
                avg_time_per_step = elapsed / self.current_step
                remaining_steps = self.total_steps - self.current_step
                progress["estimated_remaining_seconds"] = avg_time_per_step * remaining_steps
        
        return progress


# ============================================================================
# Retry Utilities
# ============================================================================

async def retry_async(
    func,
    max_retries: int = 3,
    delay_seconds: float = 1.0,
    exponential_backoff: bool = True
):
    """
    Retry an async function with exponential backoff
    
    Args:
        func: Async function to retry
        max_retries: Maximum number of retry attempts
        delay_seconds: Initial delay between retries
        exponential_backoff: Use exponential backoff
        
    Returns:
        Function result
    """
    
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            last_exception = e
            
            if attempt < max_retries - 1:
                wait_time = delay_seconds * (2 ** attempt if exponential_backoff else 1)
                await asyncio.sleep(wait_time)
    
    raise last_exception


# ============================================================================
# Cost Estimation
# ============================================================================

class CostEstimator:
    """Estimate API costs for LLM calls"""
    
    # Pricing per 1K tokens (approximate)
    PRICES = {
        "gpt-4-vision-preview": {"input": 0.01, "output": 0.03},
        "gpt-4-turbo-preview": {"input": 0.01, "output": 0.03},
        "claude-sonnet-4-5-20250929": {"input": 0.003, "output": 0.015},
    }
    
    def __init__(self):
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.calls_by_model = {}
    
    def add_call(self, model: str, input_tokens: int, output_tokens: int):
        """Record an API call"""
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        
        if model not in self.calls_by_model:
            self.calls_by_model[model] = {
                "input_tokens": 0,
                "output_tokens": 0,
                "calls": 0
            }
        
        self.calls_by_model[model]["input_tokens"] += input_tokens
        self.calls_by_model[model]["output_tokens"] += output_tokens
        self.calls_by_model[model]["calls"] += 1
    
    def get_total_cost(self) -> float:
        """Calculate total estimated cost"""
        total = 0.0
        
        for model, usage in self.calls_by_model.items():
            if model in self.PRICES:
                prices = self.PRICES[model]
                input_cost = (usage["input_tokens"] / 1000) * prices["input"]
                output_cost = (usage["output_tokens"] / 1000) * prices["output"]
                total += input_cost + output_cost
        
        return total
    
    def get_summary(self) -> Dict[str, Any]:
        """Get cost summary"""
        return {
            "total_cost": self.get_total_cost(),
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "by_model": self.calls_by_model
        }
