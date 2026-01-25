"""
Low-Level Web Controller Agents
These agents handle direct browser interaction without decision-making
"""

import asyncio
import time
import base64
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Page, Browser
from models import (
    ActionCommand, ExecutionResult, ActionType, 
    AgentRole, WebElement
)
import logging

logger = logging.getLogger(__name__)


class WebController:
    """
    Low-level agent that executes web actions
    No reasoning - just follows commands
    """
    
    def __init__(self, headless: bool = False):
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.playwright = None
        
    async def initialize(self):
        """Initialize browser instance"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        self.page = await self.browser.new_page()
        logger.info("WebController initialized")
        
    async def shutdown(self):
        """Clean shutdown"""
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("WebController shutdown")
        
    async def execute_action(self, command: ActionCommand) -> ExecutionResult:
        """
        Execute a single action command
        This is the main entry point for web automation
        """
        start_time = time.time()
        
        try:
            result_data = {}
            
            # Route to appropriate handler
            if command.action_type == ActionType.NAVIGATE:
                result_data = await self._navigate(command.parameters)
                
            elif command.action_type == ActionType.CLICK:
                result_data = await self._click(command.parameters)
                
            elif command.action_type == ActionType.TYPE:
                result_data = await self._type_text(command.parameters)
                
            elif command.action_type == ActionType.SCROLL:
                result_data = await self._scroll(command.parameters)
                
            elif command.action_type == ActionType.WAIT:
                result_data = await self._wait(command.parameters)
                
            elif command.action_type == ActionType.SCREENSHOT:
                result_data = await self._screenshot(command.parameters)
                
            elif command.action_type == ActionType.PRESS_KEY:
                result_data = await self._press_key(command.parameters)
                
            elif command.action_type == ActionType.HOVER:
                result_data = await self._hover(command.parameters)
            
            else:
                raise ValueError(f"Unknown action type: {command.action_type}")
            
            execution_time = (time.time() - start_time) * 1000
            
            return ExecutionResult(
                sender=AgentRole.WEB_CONTROLLER,
                receiver=command.sender,
                success=True,
                action_executed=command.action_type,
                result_data=result_data,
                execution_time_ms=execution_time,
                metadata={"command_id": command.message_id}
            )
            
        except Exception as e:
            logger.error(f"Action execution failed: {e}")
            execution_time = (time.time() - start_time) * 1000
            
            return ExecutionResult(
                sender=AgentRole.WEB_CONTROLLER,
                receiver=command.sender,
                success=False,
                action_executed=command.action_type,
                error_message=str(e),
                execution_time_ms=execution_time,
                metadata={"command_id": command.message_id}
            )
    
    # ========================================================================
    # Action Handlers
    # ========================================================================
    
    async def _navigate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Navigate to URL"""
        url = params.get("url")
        if not url:
            raise ValueError("URL required for navigate action")
            
        await self.page.goto(url, wait_until="domcontentloaded")
        await self.page.wait_for_load_state("networkidle", timeout=10000)
        
        return {
            "url": self.page.url,
            "title": await self.page.title()
        }
    
    async def _click(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Click on element"""
        selector = params.get("selector")
        text = params.get("text")
        coordinates = params.get("coordinates")
        
        if selector:
            # Click by CSS selector
            await self.page.click(selector)
            return {"method": "selector", "selector": selector}
            
        elif text:
            # Click by text content
            await self.page.get_by_text(text).first.click()
            return {"method": "text", "text": text}
            
        elif coordinates:
            # Click by coordinates
            x = coordinates.get("x")
            y = coordinates.get("y")
            await self.page.mouse.click(x, y)
            return {"method": "coordinates", "x": x, "y": y}
            
        else:
            raise ValueError("Click requires selector, text, or coordinates")
    
    async def _type_text(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Type text into an input field"""
        selector = params.get("selector")
        text = params.get("text", "")
        clear_first = params.get("clear_first", False)
        
        if not selector:
            raise ValueError("Selector required for type action")
        
        if clear_first:
            await self.page.fill(selector, "")
        
        await self.page.type(selector, text, delay=50)  # Human-like typing
        
        return {
            "selector": selector,
            "text_length": len(text),
            "cleared": clear_first
        }
    
    async def _scroll(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Scroll the page"""
        direction = params.get("direction", "down")
        amount = params.get("amount", 500)
        
        if direction == "down":
            await self.page.evaluate(f"window.scrollBy(0, {amount})")
        elif direction == "up":
            await self.page.evaluate(f"window.scrollBy(0, -{amount})")
        elif direction == "top":
            await self.page.evaluate("window.scrollTo(0, 0)")
        elif direction == "bottom":
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        
        return {"direction": direction, "amount": amount}
    
    async def _wait(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Wait for specified duration or condition"""
        duration_ms = params.get("duration_ms", 1000)
        selector = params.get("selector")
        
        if selector:
            # Wait for element to appear
            await self.page.wait_for_selector(selector, timeout=duration_ms)
            return {"type": "selector", "selector": selector}
        else:
            # Simple delay
            await asyncio.sleep(duration_ms / 1000)
            return {"type": "delay", "duration_ms": duration_ms}
    
    async def _screenshot(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Take screenshot"""
        full_page = params.get("full_page", False)
        path = params.get("path")
        
        screenshot_bytes = await self.page.screenshot(full_page=full_page)
        screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
        
        result = {
            "screenshot_base64": screenshot_base64,
            "full_page": full_page,
            "size_bytes": len(screenshot_bytes)
        }
        
        if path:
            with open(path, 'wb') as f:
                f.write(screenshot_bytes)
            result["path"] = path
        
        return result
    
    async def _press_key(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Press a keyboard key"""
        key = params.get("key")
        if not key:
            raise ValueError("Key required for press_key action")
        
        await self.page.keyboard.press(key)
        return {"key": key}
    
    async def _hover(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Hover over element"""
        selector = params.get("selector")
        if not selector:
            raise ValueError("Selector required for hover action")
        
        await self.page.hover(selector)
        return {"selector": selector}
    
    # ========================================================================
    # State Inspection Methods
    # ========================================================================
    
    async def get_current_state(self) -> Dict[str, Any]:
        """Get current browser state for vision agent"""
        return {
            "url": self.page.url,
            "title": await self.page.title(),
            "cookies": await self.page.context.cookies(),
            "viewport": self.page.viewport_size
        }
    
    async def extract_page_elements(self) -> list[WebElement]:
        """Extract interactive elements for vision processing"""
        # This will be enhanced by the vision agent
        # For now, basic element extraction
        
        elements = []
        
        # Get all buttons
        buttons = await self.page.query_selector_all("button")
        for btn in buttons:
            box = await btn.bounding_box()
            text = await btn.inner_text()
            if box:
                elements.append(WebElement(
                    element_type="button",
                    text=text,
                    coordinates={
                        "x": box["x"],
                        "y": box["y"],
                        "width": box["width"],
                        "height": box["height"]
                    }
                ))
        
        # Get all links
        links = await self.page.query_selector_all("a")
        for link in links[:20]:  # Limit to first 20
            box = await link.bounding_box()
            text = await link.inner_text()
            href = await link.get_attribute("href")
            if box:
                elements.append(WebElement(
                    element_type="link",
                    text=text,
                    coordinates={
                        "x": box["x"],
                        "y": box["y"],
                        "width": box["width"],
                        "height": box["height"]
                    },
                    attributes={"href": href or ""}
                ))
        
        # Get all inputs
        inputs = await self.page.query_selector_all("input")
        for inp in inputs:
            box = await inp.bounding_box()
            input_type = await inp.get_attribute("type")
            placeholder = await inp.get_attribute("placeholder")
            if box:
                elements.append(WebElement(
                    element_type="input",
                    text=placeholder or "",
                    coordinates={
                        "x": box["x"],
                        "y": box["y"],
                        "width": box["width"],
                        "height": box["height"]
                    },
                    attributes={"type": input_type or "text"}
                ))
        
        return elements
