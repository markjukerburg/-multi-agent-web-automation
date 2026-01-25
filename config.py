"""
Configuration File
Customize system behavior
"""

from models import SystemConfig, AgentConfig, AgentRole


# ============================================================================
# API Configuration
# ============================================================================

# Choose your LLM provider: "openai" or "anthropic"
PROVIDER = "anthropic"

# API Keys (set in environment variables for security)
# OPENAI_API_KEY = "your-key-here"  # Don't hardcode!
# ANTHROPIC_API_KEY = "your-key-here"  # Don't hardcode!


# ============================================================================
# Model Configuration
# ============================================================================

# OpenAI Models
OPENAI_VISION_MODEL = "gpt-4-vision-preview"
OPENAI_REASONING_MODEL = "gpt-4-turbo-preview"
OPENAI_PLANNING_MODEL = "gpt-4-turbo-preview"

# Anthropic Models
ANTHROPIC_VISION_MODEL = "claude-sonnet-4-5-20250929"
ANTHROPIC_REASONING_MODEL = "claude-sonnet-4-5-20250929"
ANTHROPIC_PLANNING_MODEL = "claude-sonnet-4-5-20250929"


# ============================================================================
# Agent Configuration
# ============================================================================

ORCHESTRATOR_CONFIG = AgentConfig(
    agent_role=AgentRole.ORCHESTRATOR,
    llm_model=OPENAI_PLANNING_MODEL if PROVIDER == "openai" else ANTHROPIC_PLANNING_MODEL,
    temperature=0.2,  # More deterministic for planning
    max_retries=3,
    timeout_seconds=60
)

VISION_CONFIG = AgentConfig(
    agent_role=AgentRole.VISION,
    vision_model=OPENAI_VISION_MODEL if PROVIDER == "openai" else ANTHROPIC_VISION_MODEL,
    temperature=0.1,  # Very deterministic for vision
    max_retries=2,
    timeout_seconds=30
)

REASONING_CONFIG = AgentConfig(
    agent_role=AgentRole.REASONING,
    llm_model=OPENAI_REASONING_MODEL if PROVIDER == "openai" else ANTHROPIC_REASONING_MODEL,
    temperature=0.1,  # Deterministic for reasoning
    max_retries=3,
    timeout_seconds=45
)


# ============================================================================
# System Configuration
# ============================================================================

SYSTEM_CONFIG = SystemConfig(
    orchestrator_config=ORCHESTRATOR_CONFIG,
    vision_config=VISION_CONFIG,
    reasoning_config=REASONING_CONFIG,
    browser_headless=False,  # Set to True for production
    screenshot_on_every_action=True,  # Useful for debugging
    max_task_duration_seconds=300,  # 5 minutes max per task
    redis_url="redis://localhost:6379",  # For state management
    log_level="INFO"  # DEBUG, INFO, WARNING, ERROR
)


# ============================================================================
# Browser Configuration
# ============================================================================

BROWSER_CONFIG = {
    "headless": False,
    "viewport": {
        "width": 1920,
        "height": 1080
    },
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "timeout": 30000,  # 30 seconds
    "slow_mo": 0,  # Milliseconds to slow down operations (useful for debugging)
}


# ============================================================================
# Execution Configuration
# ============================================================================

EXECUTION_CONFIG = {
    "max_steps_per_task": 50,
    "step_delay_ms": 1000,  # Wait between steps
    "retry_on_failure": True,
    "max_retries": 3,
    "screenshot_every_step": True,
    "save_screenshots": True,
    "screenshot_directory": "./screenshots",
}


# ============================================================================
# Logging Configuration
# ============================================================================

LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "save_to_file": True,
    "log_directory": "./logs",
    "rotate_logs": True,
    "max_log_size_mb": 10,
}


# ============================================================================
# Advanced Configuration
# ============================================================================

ADVANCED_CONFIG = {
    # Vision processing
    "vision": {
        "image_quality": 0.9,  # JPEG quality for screenshots
        "resize_images": True,  # Resize to reduce API costs
        "max_image_size": (1920, 1080),
    },
    
    # Reasoning
    "reasoning": {
        "enable_chain_of_thought": True,
        "enable_self_reflection": True,
        "max_reasoning_depth": 3,
    },
    
    # Error handling
    "error_handling": {
        "auto_retry": True,
        "fallback_strategies": ["retry", "skip", "abort"],
        "max_consecutive_failures": 5,
    },
    
    # Performance
    "performance": {
        "enable_caching": True,
        "cache_screenshots": True,
        "cache_llm_responses": False,  # Be careful with this
    },
}


# ============================================================================
# Safety Configuration
# ============================================================================

SAFETY_CONFIG = {
    # Constraints
    "allow_purchases": False,
    "allow_downloads": False,
    "allow_form_submissions": True,
    "allow_navigation_external": True,
    
    # Blacklisted domains
    "blocked_domains": [
        "example-malicious.com",
    ],
    
    # Rate limiting
    "max_requests_per_minute": 60,
    "enable_rate_limiting": True,
}
