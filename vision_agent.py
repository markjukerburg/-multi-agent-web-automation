"""
Mid-Level Vision Agent
Processes screenshots and provides structured observations
"""

import base64
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
import json
import logging
from models import (
    Observation, AgentRole, WebElement, TaskRequest,
    ActionCommand, ActionType
)
from web_controller import WebController

logger = logging.getLogger(__name__)


class VisionAgent:
    """
    Analyzes screenshots and web page state
    Provides structured observations to reasoning agent
    """
    
    def __init__(
        self,
        web_controller: WebController,
        provider: str = "anthropic",  # or "anthropic"
        api_key: Optional[str] = None
    ):
        self.web_controller = web_controller
        self.provider = provider
        
        if provider == "openai":
            self.client = AsyncOpenAI(api_key=api_key)
            self.model = "gpt-4-vision-preview"
        else:
            self.client = AsyncAnthropic(api_key=api_key)
            self.model = "claude-sonnet-4-5-20250929"
    
    async def observe(self, task_context: str) -> Observation:
        """
        Main observation method - analyzes current page state
        
        Args:
            task_context: What we're trying to accomplish
            
        Returns:
            Structured observation with detected elements and analysis
        """
        
        # Take screenshot
        print("screenshot result")

        screenshot_result = await self.web_controller.execute_action(
            ActionCommand(
                sender=AgentRole.VISION,
                receiver=AgentRole.WEB_CONTROLLER,
                action_type=ActionType.SCREENSHOT,
                parameters={"full_page": False}
            )
        )
        if(screenshot_result):
            print("screenshot result")
        if not screenshot_result.success:
            raise Exception("Failed to capture screenshot")
        
        screenshot_base64 = screenshot_result.result_data["screenshot_base64"]
        
        # Get page state
        page_state = await self.web_controller.get_current_state()
        
        # Extract basic elements
        detected_elements = await self.web_controller.extract_page_elements()
        
        # Use LLM to analyze screenshot in context
        analysis = await self._analyze_screenshot(
            screenshot_base64,
            task_context,
            page_state,
            detected_elements
        )
        
        return Observation(
            sender=AgentRole.VISION,
            receiver=AgentRole.REASONING,
            screenshot_base64=screenshot_base64,
            detected_elements=[elem.dict() for elem in detected_elements],
            page_url=page_state["url"],
            page_text=analysis.get("page_text", ""),
            analysis=analysis.get("analysis", ""),
            metadata={
                "viewport": page_state.get("viewport", {}),
                "interactive_elements_count": len(detected_elements)
            }
        )
    
    async def _analyze_screenshot(
        self,
        screenshot_base64: str,
        task_context: str,
        page_state: Dict[str, Any],
        detected_elements: List[WebElement]
    ) -> Dict[str, Any]:
        """
        Use vision LLM to analyze screenshot
        """
        
        # Create element summary for the prompt
        element_summary = self._create_element_summary(detected_elements)
        
        prompt = f"""You are analyzing a web page screenshot to help accomplish a task.

**Current Task Context:** {task_context}

**Current URL:** {page_state['url']}

**Detected Elements:**
{element_summary}

Please analyze this screenshot and provide:
1. A description of what you see on the page
2. Key interactive elements relevant to the task
3. Current state of the page (loading, form filled, error message, etc.)
4. Any notable text content
5. Obstacles or issues that might prevent task completion

Respond in JSON format:
{{
    "page_text": "Main visible text content",
    "analysis": "Your detailed analysis",
    "relevant_elements": ["List of element indices that are relevant to the task"],
    "page_state": "current_state_description",
    "recommended_focus": "What element or area to focus on next"
}}
"""
        
        if self.provider == "openai":
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{screenshot_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1500,
                temperature=0.1
            )
            
            content = response.choices[0].message.content
            
        else:  # Anthropic
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                temperature=0.1,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": screenshot_base64
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            )
            
            content = response.content[0].text
        
        try:
            # Extract JSON from response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            analysis = json.loads(content.strip())
            return analysis
            
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON from vision response")
            return {
                "page_text": "",
                "analysis": content,
                "relevant_elements": [],
                "page_state": "unknown",
                "recommended_focus": ""
            }
    
    def _create_element_summary(self, elements: List[WebElement]) -> str:
        """Create a readable summary of detected elements"""
        summary_lines = []
        
        for idx, elem in enumerate(elements):
            summary = f"{idx}. {elem.element_type.upper()}"
            if elem.text:
                summary += f" - Text: '{elem.text[:50]}'"
            if elem.attributes:
                summary += f" - Attrs: {elem.attributes}"
            summary_lines.append(summary)
        
        return "\n".join(summary_lines) if summary_lines else "No elements detected"
    
    async def verify_action_result(
        self,
        action: ActionCommand,
        expected_outcome: str
    ) -> Dict[str, Any]:
        """
        Verify if an action had the expected effect
        Used for validation after reasoning agent commands
        """
        
        # Take a fresh screenshot
        observation = await self.observe(
            f"Verifying that action '{action.action_type}' achieved: {expected_outcome}"
        )
        
        # Use LLM to verify
        verification_prompt = f"""
The following action was just executed:
Action: {action.action_type}
Parameters: {action.parameters}
Expected Outcome: {expected_outcome}

Based on the current screenshot and page state, did the action succeed?

Respond in JSON:
{{
    "success": true/false,
    "confidence": 0.0-1.0,
    "explanation": "Why you think it succeeded or failed",
    "observed_changes": "What changed on the page"
}}
"""
        
        # Similar LLM call as _analyze_screenshot
        # Implementation would be similar to above
        
        return {
            "success": True,  # Placeholder
            "confidence": 0.9,
            "observation": observation
        }
