"""
Test Suite for Multi-Agent Web Automation System
Run with: pytest test_system.py -v
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from models import (
    ActionType, ActionCommand, AgentRole,
    ExecutionResult, Observation, WebElement
)
from web_controller import WebController
from vision_agent import VisionAgent
from reasoning_agent import ReasoningAgent
from orchestrator import Orchestrator


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
async def web_controller():
    """Create a web controller for testing"""
    controller = WebController(headless=True)
    await controller.initialize()
    yield controller
    await controller.shutdown()


@pytest.fixture
def mock_vision_agent():
    """Mock vision agent"""
    agent = Mock()
    agent.observe = AsyncMock(return_value=Observation(
        sender=AgentRole.VISION,
        receiver=AgentRole.REASONING,
        screenshot_base64="mock_base64",
        detected_elements=[],
        page_url="https://example.com",
        analysis="Test page"
    ))
    return agent


@pytest.fixture
def mock_reasoning_agent():
    """Mock reasoning agent"""
    agent = Mock()
    agent.decide_action = AsyncMock(return_value=ActionCommand(
        sender=AgentRole.REASONING,
        receiver=AgentRole.WEB_CONTROLLER,
        action_type=ActionType.CLICK,
        parameters={"selector": "button"}
    ))
    return agent


# ============================================================================
# Web Controller Tests
# ============================================================================

@pytest.mark.asyncio
async def test_web_controller_initialization(web_controller):
    """Test web controller initializes correctly"""
    assert web_controller.browser is not None
    assert web_controller.page is not None


@pytest.mark.asyncio
async def test_web_controller_navigation(web_controller):
    """Test navigation command"""
    command = ActionCommand(
        sender=AgentRole.REASONING,
        receiver=AgentRole.WEB_CONTROLLER,
        action_type=ActionType.NAVIGATE,
        parameters={"url": "https://example.com"}
    )
    
    result = await web_controller.execute_action(command)
    
    assert result.success is True
    assert result.action_executed == ActionType.NAVIGATE
    assert "example.com" in result.result_data.get("url", "")


@pytest.mark.asyncio
async def test_web_controller_screenshot(web_controller):
    """Test screenshot capture"""
    # Navigate first
    nav_command = ActionCommand(
        sender=AgentRole.REASONING,
        receiver=AgentRole.WEB_CONTROLLER,
        action_type=ActionType.NAVIGATE,
        parameters={"url": "https://example.com"}
    )
    await web_controller.execute_action(nav_command)
    
    # Take screenshot
    screenshot_command = ActionCommand(
        sender=AgentRole.VISION,
        receiver=AgentRole.WEB_CONTROLLER,
        action_type=ActionType.SCREENSHOT,
        parameters={}
    )
    
    result = await web_controller.execute_action(screenshot_command)
    
    assert result.success is True
    assert "screenshot_base64" in result.result_data
    assert len(result.result_data["screenshot_base64"]) > 0


@pytest.mark.asyncio
async def test_web_controller_wait(web_controller):
    """Test wait command"""
    command = ActionCommand(
        sender=AgentRole.REASONING,
        receiver=AgentRole.WEB_CONTROLLER,
        action_type=ActionType.WAIT,
        parameters={"duration_ms": 100}
    )
    
    result = await web_controller.execute_action(command)
    
    assert result.success is True
    assert result.execution_time_ms >= 100


# ============================================================================
# Model Tests
# ============================================================================

def test_action_command_creation():
    """Test action command model"""
    command = ActionCommand(
        sender=AgentRole.REASONING,
        receiver=AgentRole.WEB_CONTROLLER,
        action_type=ActionType.CLICK,
        parameters={"selector": "button"},
        reasoning="Click the submit button"
    )
    
    assert command.action_type == ActionType.CLICK
    assert command.parameters["selector"] == "button"
    assert command.sender == AgentRole.REASONING


def test_execution_result_creation():
    """Test execution result model"""
    result = ExecutionResult(
        sender=AgentRole.WEB_CONTROLLER,
        receiver=AgentRole.REASONING,
        success=True,
        action_executed=ActionType.CLICK,
        execution_time_ms=250.5
    )
    
    assert result.success is True
    assert result.execution_time_ms == 250.5


def test_web_element_model():
    """Test web element model"""
    element = WebElement(
        element_type="button",
        text="Submit",
        coordinates={"x": 100, "y": 200, "width": 80, "height": 40},
        confidence=0.95
    )
    
    assert element.element_type == "button"
    assert element.text == "Submit"
    assert element.confidence == 0.95


# ============================================================================
# Integration Tests
# ============================================================================

@pytest.mark.asyncio
async def test_basic_workflow(web_controller, mock_vision_agent, mock_reasoning_agent):
    """Test basic observe-reason-act workflow"""
    
    # Navigate
    nav_result = await web_controller.execute_action(ActionCommand(
        sender=AgentRole.ORCHESTRATOR,
        receiver=AgentRole.WEB_CONTROLLER,
        action_type=ActionType.NAVIGATE,
        parameters={"url": "https://example.com"}
    ))
    assert nav_result.success
    
    # Observe
    observation = await mock_vision_agent.observe("test task")
    assert observation.page_url == "https://example.com"
    
    # Reason
    action = await mock_reasoning_agent.decide_action(observation, "test goal")
    assert action.action_type == ActionType.CLICK


# ============================================================================
# Error Handling Tests
# ============================================================================

@pytest.mark.asyncio
async def test_invalid_navigation(web_controller):
    """Test handling of invalid URL"""
    command = ActionCommand(
        sender=AgentRole.REASONING,
        receiver=AgentRole.WEB_CONTROLLER,
        action_type=ActionType.NAVIGATE,
        parameters={"url": "https://this-domain-definitely-does-not-exist-12345.com"}
    )
    
    result = await web_controller.execute_action(command)
    assert result.success is False
    assert result.error_message is not None


@pytest.mark.asyncio
async def test_invalid_action_type(web_controller):
    """Test handling of invalid action type"""
    # This should be caught by Pydantic validation
    with pytest.raises(ValueError):
        ActionCommand(
            sender=AgentRole.REASONING,
            receiver=AgentRole.WEB_CONTROLLER,
            action_type="INVALID_ACTION",  # Invalid
            parameters={}
        )


# ============================================================================
# Performance Tests
# ============================================================================

@pytest.mark.asyncio
async def test_screenshot_performance(web_controller):
    """Test screenshot capture performance"""
    await web_controller.execute_action(ActionCommand(
        sender=AgentRole.ORCHESTRATOR,
        receiver=AgentRole.WEB_CONTROLLER,
        action_type=ActionType.NAVIGATE,
        parameters={"url": "https://example.com"}
    ))
    
    command = ActionCommand(
        sender=AgentRole.VISION,
        receiver=AgentRole.WEB_CONTROLLER,
        action_type=ActionType.SCREENSHOT,
        parameters={}
    )
    
    result = await web_controller.execute_action(command)
    
    # Screenshot should take less than 5 seconds
    assert result.execution_time_ms < 5000


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
