"""
Mid-Level Reasoning Agent
Receives observations and determines next actions
"""

import json
from typing import Optional, Dict, Any, List
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
import logging

from models import (
    Observation, ActionCommand, ActionType,
    AgentRole, TaskRequest
)

logger = logging.getLogger(__name__)


class ReasoningAgent:
    """
    Analyzes observations and plans actions
    Bridge between vision understanding and execution
    """
    
    def __init__(
        self,
        provider: str = "openai",
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.provider = provider
        
        if provider == "openai":
            self.client = AsyncOpenAI(api_key=api_key)
            self.model = model or "gpt-4-turbo-preview"
        else:
            self.client = AsyncAnthropic(api_key=api_key)
            self.model = model or "claude-3-5-sonnet-20241022"
        
        self.conversation_history: List[Dict[str, Any]] = []
    
    async def decide_action(
        self,
        observation: Observation,
        task_goal: str,
        previous_actions: List[ActionCommand] = None
    ) -> ActionCommand:
        """
        Main reasoning method - decides what action to take next
        
        Args:
            observation: Current state from vision agent
            task_goal: Overall goal we're trying to achieve
            previous_actions: History of actions taken
            
        Returns:
            Action command to execute
        """
        
        previous_actions = previous_actions or []
        
        # Build reasoning prompt
        prompt = self._build_reasoning_prompt(
            observation,
            task_goal,
            previous_actions
        )
        
        # Get decision from LLM
        decision = await self._get_llm_decision(prompt)
        
        # Convert decision to action command
        action_command = self._create_action_command(decision)
        
        # Store in history for context
        self.conversation_history.append({
            "observation": observation.dict(),
            "decision": decision,
            "action": action_command.dict()
        })
        
        return action_command
    
    def _build_reasoning_prompt(
        self,
        observation: Observation,
        task_goal: str,
        previous_actions: List[ActionCommand]
    ) -> str:
        """Build comprehensive reasoning prompt"""
        
        # Create action history summary
        action_history = ""
        if previous_actions:
            action_history = "**Previous Actions:**\n"
            for idx, action in enumerate(previous_actions[-5:], 1):  # Last 5 actions
                action_history += f"{idx}. {action.action_type}: {action.parameters}\n"
                if action.reasoning:
                    action_history += f"   Reasoning: {action.reasoning}\n"
        
        # Create element list
        elements_list = ""
        if observation.detected_elements:
            elements_list = "**Interactive Elements:**\n"
            for idx, elem in enumerate(observation.detected_elements):
                elements_list += (
                    f"{idx}. {elem['element_type']} - "
                    f"Text: '{elem.get('text', '')}' - "
                    f"Position: ({elem['coordinates'].get('x', 0):.0f}, "
                    f"{elem['coordinates'].get('y', 0):.0f})\n"
                )
        
        prompt = f"""You are a web automation reasoning agent. Your job is to analyze the current page state and decide the next action to take.

**TASK GOAL:** {task_goal}

**CURRENT PAGE:**
- URL: {observation.page_url}
- Vision Analysis: {observation.analysis}

{elements_list}

{action_history}

**Available Actions:**
- CLICK: Click on an element (requires element index or coordinates)
- TYPE: Type text into an input field (requires element index and text)
- SCROLL: Scroll the page (direction: up/down/top/bottom)
- NAVIGATE: Go to a different URL
- WAIT: Wait for page to load or element to appear
- PRESS_KEY: Press a keyboard key (Enter, Tab, etc.)
- HOVER: Hover over an element

**Instructions:**
1. Analyze the current state
2. Determine if we're making progress toward the goal
3. Choose the most appropriate next action
4. Provide clear reasoning

**IMPORTANT:**
- If you need to click/type on an element, reference it by its index from the list above
- Be specific about parameters (which element, what text, etc.)
- Consider if we need to wait for page loading
- If the goal is achieved, use action type "COMPLETE"

Respond in JSON format:
{{
    "thought_process": "Your step-by-step reasoning",
    "action_type": "CLICK|TYPE|SCROLL|NAVIGATE|WAIT|PRESS_KEY|HOVER|COMPLETE",
    "parameters": {{
        // Action-specific parameters
        // For CLICK: {{"element_index": 0}} or {{"coordinates": {{"x": 100, "y": 200}}}}
        // For TYPE: {{"element_index": 0, "text": "search query"}}
        // For SCROLL: {{"direction": "down", "amount": 500}}
        // For NAVIGATE: {{"url": "https://example.com"}}
        // For WAIT: {{"duration_ms": 2000}} or {{"element_index": 0}}
        // For PRESS_KEY: {{"key": "Enter"}}
    }},
    "expected_outcome": "What should happen after this action",
    "progress_assessment": "Are we getting closer to the goal? (yes/no/stuck)",
    "confidence": 0.0-1.0
}}
"""
        
        return prompt
    
    async def _get_llm_decision(self, prompt: str) -> Dict[str, Any]:
        """Get decision from LLM"""
        
        if self.provider == "openai":
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a web automation reasoning agent. You analyze page states and decide actions to accomplish user goals. Always respond with valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            
        else:  # Anthropic
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.1,
                system="You are a web automation reasoning agent. You analyze page states and decide actions to accomplish user goals. Always respond with valid JSON.",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            content = response.content[0].text
        
        # Parse JSON response
        try:
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            decision = json.loads(content.strip())
            return decision
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response: {e}")
            logger.error(f"Content: {content}")
            raise
    
    def _create_action_command(self, decision: Dict[str, Any]) -> ActionCommand:
        """Convert LLM decision to action command"""
        
        action_type_str = decision.get("action_type", "WAIT")
        
        # Handle COMPLETE as a special case
        if action_type_str == "COMPLETE":
            return ActionCommand(
                sender=AgentRole.REASONING,
                receiver=AgentRole.WEB_CONTROLLER,
                action_type=ActionType.WAIT,  # Use WAIT as placeholder
                parameters={"duration_ms": 0},
                reasoning="Task completed",
                metadata={"task_complete": True}
            )
        
        # Map string to enum
        try:
            action_type = ActionType(action_type_str.lower())
        except ValueError:
            logger.warning(f"Unknown action type: {action_type_str}, defaulting to WAIT")
            action_type = ActionType.WAIT
        
        # Process parameters
        parameters = decision.get("parameters", {})
        
        # Convert element_index to actual selector if needed
        if "element_index" in parameters:
            # This would be filled in by cross-referencing with observation
            # For now, we'll leave it as-is and handle in web controller
            pass
        
        return ActionCommand(
            sender=AgentRole.REASONING,
            receiver=AgentRole.WEB_CONTROLLER,
            action_type=action_type,
            parameters=parameters,
            reasoning=decision.get("thought_process", ""),
            metadata={
                "expected_outcome": decision.get("expected_outcome", ""),
                "confidence": decision.get("confidence", 0.8),
                "progress_assessment": decision.get("progress_assessment", "unknown")
            }
        )
    
    async def assess_progress(
        self,
        task_goal: str,
        observations: List[Observation]
    ) -> Dict[str, Any]:
        """
        Assess overall progress toward goal
        Used by orchestrator to determine if we're stuck
        """
        
        if not observations:
            return {
                "progress_percentage": 0,
                "assessment": "No observations yet",
                "stuck": False
            }
        
        # Build summary of journey
        summary = f"Task Goal: {task_goal}\n\n"
        summary += "Journey so far:\n"
        for idx, obs in enumerate(observations[-10:], 1):
            summary += f"{idx}. Page: {obs.page_url}\n"
            summary += f"   Analysis: {obs.analysis[:100]}...\n"
        
        prompt = f"""{summary}

Based on the observations above, assess our progress:
1. What percentage complete are we? (0-100)
2. Are we making progress or stuck in a loop?
3. What should we do next?

Respond in JSON:
{{
    "progress_percentage": 0-100,
    "assessment": "Detailed assessment",
    "stuck": true/false,
    "recommendation": "What to do next"
}}
"""
        
        decision = await self._get_llm_decision(prompt)
        return decision
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
