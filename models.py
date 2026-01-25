"""
Base Models and Message Types for Multi-Agent System
Provides type-safe communication between agents
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime


class ActionType(str, Enum):
    """Available web actions"""
    CLICK = "click"
    TYPE = "type"
    SCROLL = "scroll"
    NAVIGATE = "navigate"
    WAIT = "wait"
    SCREENSHOT = "screenshot"
    PRESS_KEY = "press_key"
    HOVER = "hover"


class AgentRole(str, Enum):
    """Agent hierarchy roles"""
    ORCHESTRATOR = "orchestrator"
    VISION = "vision"
    REASONING = "reasoning"
    WEB_CONTROLLER = "web_controller"


class MessageType(str, Enum):
    """Inter-agent message types"""
    TASK_REQUEST = "task_request"
    OBSERVATION = "observation"
    ACTION_COMMAND = "action_command"
    EXECUTION_RESULT = "execution_result"
    ERROR = "error"
    STATUS_UPDATE = "status_update"


# ============================================================================
# Message Models
# ============================================================================

class BaseMessage(BaseModel):
    """Base class for all agent messages"""
    message_id: str = Field(default_factory=lambda: datetime.now().strftime("%Y%m%d%H%M%S%f"))
    message_type: MessageType
    sender: AgentRole
    receiver: AgentRole
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TaskRequest(BaseMessage):
    """High-level task from orchestrator to mid-level agents"""
    message_type: MessageType = MessageType.TASK_REQUEST
    goal: str
    context: Dict[str, Any] = Field(default_factory=dict)
    constraints: List[str] = Field(default_factory=list)


class Observation(BaseMessage):
    """Vision agent's analysis of current state"""
    message_type: MessageType = MessageType.OBSERVATION
    screenshot_path: Optional[str] = None
    screenshot_base64: Optional[str] = None
    detected_elements: List[Dict[str, Any]] = Field(default_factory=list)
    page_text: str = ""
    page_url: str = ""
    analysis: str = ""  # LLM's interpretation


class ActionCommand(BaseMessage):
    """Command from reasoning agent to web controller"""
    message_type: MessageType = MessageType.ACTION_COMMAND
    action_type: ActionType
    parameters: Dict[str, Any] = Field(default_factory=dict)
    reasoning: str = ""  # Why this action was chosen


class ExecutionResult(BaseMessage):
    """Result from web controller after executing action"""
    message_type: MessageType = MessageType.EXECUTION_RESULT
    success: bool
    action_executed: ActionType
    result_data: Dict[str, Any] = Field(default_factory=dict)
    error_message: Optional[str] = None
    execution_time_ms: float = 0.0


class ErrorMessage(BaseMessage):
    """Error communication between agents"""
    message_type: MessageType = MessageType.ERROR
    error_type: str
    error_details: str
    recoverable: bool = True
    suggested_action: Optional[str] = None


class StatusUpdate(BaseMessage):
    """Progress updates from any agent"""
    message_type: MessageType = MessageType.STATUS_UPDATE
    status: str
    progress_percentage: Optional[float] = None
    details: str = ""


# ============================================================================
# State Models
# ============================================================================

class BrowserState(BaseModel):
    """Current browser state"""
    url: str
    title: str
    screenshot_path: Optional[str] = None
    cookies: Dict[str, str] = Field(default_factory=dict)
    local_storage: Dict[str, str] = Field(default_factory=dict)
    page_loaded: bool = False


class TaskState(BaseModel):
    """Task execution state"""
    task_id: str
    goal: str
    status: str  # pending, in_progress, completed, failed
    current_step: int = 0
    total_steps: Optional[int] = None
    steps_completed: List[str] = Field(default_factory=list)
    browser_state: Optional[BrowserState] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class WebElement(BaseModel):
    """Detected web element"""
    element_type: str  # button, input, link, etc.
    text: str = ""
    coordinates: Dict[str, float] = Field(default_factory=dict)  # x, y, width, height
    attributes: Dict[str, str] = Field(default_factory=dict)
    confidence: float = 1.0  # Detection confidence
    selector: Optional[str] = None  # CSS selector if available


# ============================================================================
# Configuration Models
# ============================================================================

class AgentConfig(BaseModel):
    """Configuration for individual agents"""
    agent_role: AgentRole
    llm_model: str = "gpt-4-turbo-preview"
    vision_model: str = "gpt-4-vision-preview"
    temperature: float = 0.1
    max_retries: int = 3
    timeout_seconds: int = 30


class SystemConfig(BaseModel):
    """Overall system configuration"""
    orchestrator_config: AgentConfig
    vision_config: AgentConfig
    reasoning_config: AgentConfig
    browser_headless: bool = False
    screenshot_on_every_action: bool = True
    max_task_duration_seconds: int = 300
    redis_url: str = "redis://localhost:6379"
    log_level: str = "INFO"
