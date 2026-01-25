"""
Multi-Agent Web Automation System
Main Integration File
"""

import asyncio
import logging
from typing import Optional, List, Dict, Any
import os

from web_controller import WebController
from vision_agent import VisionAgent
from reasoning_agent import ReasoningAgent
from orchestrator import Orchestrator
from models import SystemConfig, AgentConfig, AgentRole

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MultiAgentSystem:
    """
    Main system that initializes and coordinates all agents
    Provides a simple interface for users
    """
    
    def __init__(
        self,
        openai_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None,
        provider: str = "anthropic",  # or "anthropic"
        headless: bool = False
    ):
        """
        Initialize the multi-agent system
        
        Args:
            openai_api_key: OpenAI API key (for GPT-4 Vision)
            anthropic_api_key: Anthropic API key (for Claude)
            provider: Which LLM provider to use ("openai" or "anthropic")
            headless: Run browser in headless mode
        """
        
        # Get API keys from environment if not provided
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        # print("envkey",os.getenv("ANTHROPIC_API_KEY"))
        self.anthropic_api_key = anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
        # print("api",self.anthropic_api_key)
        self.provider = provider
        self.headless = headless
        
        # Validate API keys
        # if provider == "openai" and not self.openai_api_key:
        #    raise ValueError("OpenAI API key required when using OpenAI provider")
        if provider == "anthropic" and not self.anthropic_api_key:
            raise ValueError("Anthropic API key required when using Anthropic provider")
        
        # Initialize agents (done in async startup)
        self.web_controller: Optional[WebController] = None
        self.vision_agent: Optional[VisionAgent] = None
        self.reasoning_agent: Optional[ReasoningAgent] = None
        self.orchestrator: Optional[Orchestrator] = None
        
        self._initialized = False
    
    async def initialize(self):
        """Initialize all agents"""
        if self._initialized:
            return
        
        logger.info("Initializing Multi-Agent System...")
        
        # Layer 1: Web Controller (Low-level)
        self.web_controller = WebController(headless=self.headless)
        await self.web_controller.initialize()
        logger.info("✓ Web Controller initialized")
        
        # Layer 2: Vision Agent (Mid-level)
        api_key = self.openai_api_key if self.provider == "openai" else self.anthropic_api_key
        self.vision_agent = VisionAgent(
            web_controller=self.web_controller,
            provider=self.provider,
            api_key=api_key
        )
        logger.info("✓ Vision Agent initialized")
        
        # Layer 2: Reasoning Agent (Mid-level)
        self.reasoning_agent = ReasoningAgent(
            provider=self.provider,
            api_key=api_key
        )
        logger.info("✓ Reasoning Agent initialized")
        
        # Layer 3: Orchestrator (High-level)
        self.orchestrator = Orchestrator(
            web_controller=self.web_controller,
            vision_agent=self.vision_agent,
            reasoning_agent=self.reasoning_agent,
            provider=self.provider,
            api_key=api_key
        )
        logger.info("✓ Orchestrator initialized")
        
        self._initialized = True
        logger.info("🚀 Multi-Agent System ready!")
    
    async def execute(
        self,
        goal: str,
        starting_url: Optional[str] = None,
        max_steps: int = 50,
        constraints: List[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a high-level goal
        
        Args:
            goal: What to accomplish (e.g., "Search for laptops under $1000 on Amazon")
            starting_url: Optional URL to start from
            max_steps: Maximum actions to take
            constraints: Optional constraints (e.g., "Don't click checkout")
            
        Returns:
            Result dictionary with success status and details
            
        Example:
            result = await system.execute(
                goal="Find the contact email for OpenAI",
                starting_url="https://openai.com"
            )
        """
        
        if not self._initialized:
            await self.initialize()
        
        logger.info(f"Executing goal: {goal}")
        
        result = await self.orchestrator.execute_goal(
            goal=goal,
            starting_url=starting_url,
            max_steps=max_steps,
            constraints=constraints
        )
        
        return result
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current execution status"""
        if not self._initialized or not self.orchestrator:
            return {"status": "not_initialized"}
        
        return await self.orchestrator.get_status()
    
    async def shutdown(self):
        """Clean shutdown of all agents"""
        logger.info("Shutting down Multi-Agent System...")
        
        if self.web_controller:
            await self.web_controller.shutdown()
        
        logger.info("✓ System shutdown complete")
        self._initialized = False
    
    async def __aenter__(self):
        """Context manager support"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager cleanup"""
        await self.shutdown()


# ============================================================================
# Convenience Functions
# ============================================================================

async def run_automation(
    goal: str,
    starting_url: Optional[str] = None,
    provider: str = "anthropic",
    headless: bool = False,
    max_steps: int = 50
) -> Dict[str, Any]:
    """
    Convenience function to run a single automation task
    
    Example:
        result = await run_automation(
            goal="Find iPhone 15 prices on Best Buy",
            starting_url="https://www.bestbuy.com",
            headless=True
        )
    """
    
    async with MultiAgentSystem(provider=provider, headless=headless) as system:
        result = await system.execute(
            goal=goal,
            starting_url=starting_url,
            max_steps=max_steps
        )
        return result


# ============================================================================
# Main Entry Point (for testing)
# ============================================================================

async def main():
    """Test the system with a simple task"""
    
    # Example 1: Search for something
    async with MultiAgentSystem(provider="anthropic", headless=False) as system:
        result = await system.execute(
            goal="Search for 'artificial intelligence' on Wikipedia and read the first paragraph",
            starting_url="https://www.wikipedia.org"
        )
        
        print("\n" + "="*50)
        print("RESULT:")
        print("="*50)
        print(f"Success: {result['success']}")
        print(f"Steps taken: {result.get('steps_taken', 0)}")
        if result['success']:
            print(f"Final URL: {result.get('final_url', 'N/A')}")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    asyncio.run(main())
