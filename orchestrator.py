"""
High-Level Orchestrator Agent
Coordinates all agents and manages task execution
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic
import logging

from models import (
    TaskRequest, TaskState, AgentRole,
    ActionCommand, Observation, ExecutionResult
)
from vision_agent import VisionAgent
from reasoning_agent import ReasoningAgent
from web_controller import WebController

logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Top-level agent that:
    1. Receives high-level goals
    2. Plans task breakdown
    3. Coordinates vision, reasoning, and execution
    4. Monitors progress and handles errors
    """
    
    def __init__(
        self,
        web_controller: WebController,
        vision_agent: VisionAgent,
        reasoning_agent: ReasoningAgent,
        provider: str = "anthropic",  # or "openai"
        api_key: Optional[str] = None
    ):
        self.web_controller = web_controller
        self.vision_agent = vision_agent
        self.reasoning_agent = reasoning_agent
        
        self.provider = provider
        if provider == "openai":
            self.client = AsyncOpenAI(api_key=api_key)
            self.model = "gpt-4-turbo-preview"
        else:
            self.client = AsyncAnthropic(api_key=api_key)
            self.model = "claude-sonnet-4-5-20250929"
        
        self.current_task: Optional[TaskState] = None
        self.task_history: List[TaskState] = []
    
    async def execute_goal(
        self,
        goal: str,
        starting_url: Optional[str] = None,
        max_steps: int = 50,
        constraints: List[str] = None
    ) -> Dict[str, Any]:
        """
        Main entry point - execute a high-level goal
        
        Args:
            goal: What to accomplish (e.g., "Search for iPhone 15 on Amazon")
            starting_url: Optional starting point
            max_steps: Maximum number of actions to prevent infinite loops
            constraints: Optional constraints (e.g., "Don't make purchases")
            
        Returns:
            Execution result with success status and details
        """
        
        logger.info(f"Starting goal execution: {goal}")
        
        # Initialize task state
        task_id = f"task_{len(self.task_history) + 1}"
        self.current_task = TaskState(
            task_id=task_id,
            goal=goal,
            status="in_progress"
        )
        
        try:
            # Phase 1: Plan the task
            task_plan = await self._plan_task(goal, starting_url, constraints)
            logger.info(f"Task plan created: {len(task_plan.get('steps', []))} steps")
            
            # Phase 2: Navigate to starting point if needed
            if starting_url:
                await self._navigate_to_start(starting_url)
            
            # Phase 3: Execute the plan
            result = await self._execute_task_loop(
                goal,
                task_plan,
                max_steps
            )
            
            self.current_task.status = "completed" if result["success"] else "failed"
            self.task_history.append(self.current_task)
            
            return result
            
        except Exception as e:
            logger.error(f"Task execution failed: {e}")
            self.current_task.status = "failed"
            self.task_history.append(self.current_task)
            
            return {
                "success": False,
                "error": str(e),
                "steps_completed": len(self.current_task.steps_completed)
            }
    
    async def _plan_task(
        self,
        goal: str,
        starting_url: Optional[str],
        constraints: List[str]
    ) -> Dict[str, Any]:
        """
        Use LLM to create a high-level task plan
        """
        
        constraints_text = ""
        if constraints:
            constraints_text = "\n**Constraints:**\n" + "\n".join(f"- {c}" for c in constraints)
        
        prompt = f"""You are a task planning agent for web automation. Break down a high-level goal into logical steps.

**Goal:** {goal}

**Starting URL:** {starting_url or "Not specified - agent will determine"}
{constraints_text}

Create a high-level plan with 3-7 major steps. Each step should be a meaningful milestone.

Examples:
- Goal: "Buy a book on Amazon"
  Steps: 1) Navigate to Amazon, 2) Search for book, 3) Select book from results, 4) Add to cart, 5) Proceed to checkout

- Goal: "Find contact information for a company"
  Steps: 1) Navigate to company website, 2) Find contact/about page, 3) Extract contact details

Respond in JSON:
{{
    "steps": [
        {{
            "step_number": 1,
            "description": "What to accomplish in this step",
            "success_criteria": "How to know this step is complete"
        }}
    ],
    "estimated_actions": "Rough estimate of total actions needed (5-50)",
    "potential_challenges": ["List of things that might go wrong"]
}}
"""
        
        if self.provider == "openai":
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a task planning expert. Create clear, actionable plans."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1000
            )
            content = response.choices[0].message.content
        else:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.2,
                system="You are a task planning expert. Create clear, actionable plans.",
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.content[0].text
        
        # Parse response
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        
        return json.loads(content.strip())
    
    async def _navigate_to_start(self, url: str):
        """Navigate to starting URL"""
        logger.info(f"Navigating to starting URL: {url}")
        
        nav_command = ActionCommand(
            sender=AgentRole.ORCHESTRATOR,
            receiver=AgentRole.WEB_CONTROLLER,
            action_type="navigate",
            parameters={"url": url}
        )
        
        result = await self.web_controller.execute_action(nav_command)
        if not result.success:
            raise Exception(f"Failed to navigate to {url}: {result.error_message}")
    
    async def _execute_task_loop(
        self,
        goal: str,
        task_plan: Dict[str, Any],
        max_steps: int
    ) -> Dict[str, Any]:
        """
        Main execution loop: observe -> reason -> act -> repeat
        """
        
        actions_taken: List[ActionCommand] = []
        observations: List[Observation] = []
        
        for step_num in range(max_steps):
            logger.info(f"Executing step {step_num + 1}/{max_steps}")
            
            try:
                # Step 1: OBSERVE (Vision Agent)
                observation = await self.vision_agent.observe(
                    task_context=f"Goal: {goal}\nCurrent step: {step_num + 1}"
                )
                observations.append(observation)
                logger.debug(f"Observation: {observation.analysis[:100]}...")
                
                # Step 2: REASON (Reasoning Agent)
                action = await self.reasoning_agent.decide_action(
                    observation=observation,
                    task_goal=goal,
                    previous_actions=actions_taken
                )
                logger.info(f"Decided action: {action.action_type} - {action.reasoning[:100]}")
                
                # Check if task is complete
                if action.metadata.get("task_complete"):
                    logger.info("Task marked as complete by reasoning agent")
                    return {
                        "success": True,
                        "message": "Goal achieved",
                        "steps_taken": len(actions_taken),
                        "final_url": observation.page_url
                    }
                
                # Step 3: ACT (Web Controller)
                result = await self.web_controller.execute_action(action)
                actions_taken.append(action)
                
                if not result.success:
                    logger.warning(f"Action failed: {result.error_message}")
                    # Decide whether to retry or give up
                    if await self._should_retry(action, result):
                        logger.info("Retrying after failure")
                        continue
                    else:
                        return {
                            "success": False,
                            "error": f"Action failed: {result.error_message}",
                            "steps_taken": len(actions_taken)
                        }
                
                # Step 4: Wait a bit for page to update
                await asyncio.sleep(1)
                
                # Step 5: Check if we're stuck
                if step_num > 0 and step_num % 10 == 0:
                    progress = await self.reasoning_agent.assess_progress(
                        goal, observations
                    )
                    
                    if progress.get("stuck"):
                        logger.warning("Detected stuck state")
                        return {
                            "success": False,
                            "error": "Agent appears to be stuck in a loop",
                            "steps_taken": len(actions_taken),
                            "assessment": progress.get("assessment")
                        }
                
                # Update task state
                self.current_task.current_step = step_num + 1
                self.current_task.steps_completed.append(action.reasoning[:100])
                
            except Exception as e:
                logger.error(f"Error in execution loop: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "steps_taken": len(actions_taken)
                }
        
        # Reached max steps without completion
        return {
            "success": False,
            "error": f"Reached maximum steps ({max_steps}) without completing goal",
            "steps_taken": len(actions_taken)
        }
    
    async def _should_retry(
        self,
        failed_action: ActionCommand,
        result: ExecutionResult
    ) -> bool:
        """
        Determine if we should retry after a failure
        Simple heuristic for now - could be more sophisticated
        """
        
        # Don't retry navigation errors
        if failed_action.action_type == "navigate":
            return False
        
        # Retry timeout errors
        if "timeout" in result.error_message.lower():
            return True
        
        # Don't retry element not found more than once
        if "not found" in result.error_message.lower():
            return False
        
        return True
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current execution status"""
        if not self.current_task:
            return {"status": "idle"}
        
        return {
            "status": self.current_task.status,
            "goal": self.current_task.goal,
            "current_step": self.current_task.current_step,
            "steps_completed": len(self.current_task.steps_completed),
            "recent_actions": self.current_task.steps_completed[-3:]
        }
    
    def reset(self):
        """Reset orchestrator state"""
        self.current_task = None
        self.reasoning_agent.clear_history()
