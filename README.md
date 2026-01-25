<<<<<<< HEAD
# 🤖 Hierarchical Multi-Agent Web Automation System

A production-ready web automation system using hierarchical multi-agent architecture, inspired by OpenAI's Operator. This system uses vision-language models to understand web pages and autonomously complete complex tasks.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    HIGH-LEVEL LAYER                         │
│  ┌───────────────────────────────────────────────────────┐  │
│  │         Planner/Orchestrator Agent                    │  │
│  │  • Receives high-level goals                          │  │
│  │  • Creates task breakdown                             │  │
│  │  • Delegates to mid-level agents                      │  │
│  │  • Monitors progress and handles errors               │  │
│  └───────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                    MID-LEVEL LAYER                          │
│  ┌──────────────────────┐    ┌──────────────────────────┐  │
│  │   Vision Agent       │    │   Reasoning Agent        │  │
│  │  • Screenshot proc.  │◄───┤  • Action planning       │  │
│  │  • Element detection │    │  • Decision making       │  │
│  │  • OCR/Understanding │    │  • State management      │  │
│  └──────────────────────┘    └──────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                    LOW-LEVEL LAYER                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │         Web Controller Agents                         │  │
│  │  • Mouse control                                      │  │
│  │  • Keyboard input                                     │  │
│  │  • Click execution                                    │  │
│  │  • Scroll management                                  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## ✨ Features

- **🎯 Hierarchical Architecture**: Clean separation of concerns across three layers
- **👁️ Vision Understanding**: Uses GPT-4 Vision or Claude 3.5 to understand web pages
- **🧠 Intelligent Reasoning**: Plans actions based on visual observations and goals
- **🔄 Autonomous Execution**: Completes complex multi-step tasks without intervention
- **⚡ Async/Await**: Fully asynchronous for optimal performance
- **🛡️ Error Recovery**: Built-in retry logic and failure handling
- **📊 Real-time Monitoring**: Track progress during execution
- **🔌 Flexible**: Support for both OpenAI and Anthropic models

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- OpenAI API key OR Anthropic API key
- Chrome/Chromium browser (installed automatically by Playwright)

### Installation

1. **Clone the repository**
```bash
git clone <your-repo>
cd multi-agent-web-automation
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Install Playwright browsers**
```bash
playwright install chromium
```

4. **Set up environment variables**
```bash
# Create a .env file
echo "OPENAI_API_KEY=your-key-here" > .env
# OR for Anthropic
echo "ANTHROPIC_API_KEY=your-key-here" > .env
```

### Basic Usage

```python
import asyncio
from main import run_automation

async def main():
    result = await run_automation(
        goal="Search for 'Python tutorials' on Google and click the first result",
        starting_url="https://www.google.com",
        provider="openai",  # or "anthropic"
        headless=False
    )
    
    print(f"Success: {result['success']}")
    print(f"Steps taken: {result['steps_taken']}")

asyncio.run(main())
```

## 📖 Usage Examples

### Example 1: E-commerce Product Search

```python
from main import MultiAgentSystem

async with MultiAgentSystem(provider="openai") as system:
    result = await system.execute(
        goal="Find wireless headphones under $100 on Amazon",
        starting_url="https://www.amazon.com",
        max_steps=30
    )
```

### Example 2: Information Gathering

```python
result = await run_automation(
    goal="Navigate to Anthropic's website and find their contact email",
    starting_url="https://www.anthropic.com"
)
```

### Example 3: Form Filling

```python
async with MultiAgentSystem(provider="openai") as system:
    result = await system.execute(
        goal="""Fill out the contact form with:
        Name: John Doe
        Email: john@example.com
        Message: Interested in services""",
        starting_url="https://example.com/contact",
        constraints=["Don't submit the form"]
    )
```

### Example 4: Real-time Monitoring

```python
async with MultiAgentSystem(provider="openai") as system:
    task = asyncio.create_task(
        system.execute(
            goal="Search for machine learning tutorials",
            starting_url="https://www.google.com"
        )
    )
    
    while not task.done():
        status = await system.get_status()
        print(f"Progress: {status.get('current_step', 0)} steps")
        await asyncio.sleep(2)
    
    result = await task
```

## 🏗️ Project Structure

```
multi-agent-web-automation/
├── models.py              # Data models and message types
├── web_controller.py      # Low-level browser automation
├── vision_agent.py        # Vision processing and analysis
├── reasoning_agent.py     # Action planning and reasoning
├── orchestrator.py        # High-level task coordination
├── main.py               # Main system integration
├── config.py             # Configuration settings
├── examples.py           # Usage examples
├── requirements.txt      # Python dependencies
├── ARCHITECTURE.md       # Detailed architecture docs
└── README.md            # This file
```

## ⚙️ Configuration

Edit `config.py` to customize:

- **LLM Provider**: Choose between OpenAI or Anthropic
- **Models**: Specify which models to use for each agent
- **Browser Settings**: Headless mode, viewport size, etc.
- **Execution**: Max steps, retry logic, timeouts
- **Safety**: Blocked domains, rate limiting, constraints

```python
# config.py
PROVIDER = "openai"  # or "anthropic"
SYSTEM_CONFIG = SystemConfig(
    browser_headless=False,
    max_task_duration_seconds=300,
    screenshot_on_every_action=True
)
```

## 🔧 Advanced Usage

### Custom Agent Configuration

```python
from models import AgentConfig, AgentRole

custom_config = AgentConfig(
    agent_role=AgentRole.REASONING,
    llm_model="gpt-4-turbo-preview",
    temperature=0.1,
    max_retries=3
)
```

### Error Handling

```python
try:
    async with MultiAgentSystem(provider="openai") as system:
        result = await system.execute(
            goal="Your task here",
            max_steps=20
        )
except Exception as e:
    print(f"Error: {e}")
```

### Sequential Tasks

```python
async with MultiAgentSystem(provider="openai") as system:
    for task in tasks:
        result = await system.execute(
            goal=task['goal'],
            starting_url=task['url']
        )
        print(f"Task completed: {result['success']}")
```

## 🎯 How It Works

### 1. **Task Planning** (Orchestrator)
- Receives high-level goal from user
- Uses LLM to break down into logical steps
- Creates execution plan

### 2. **Observation Loop** (Vision Agent)
- Takes screenshot of current page state
- Uses GPT-4 Vision/Claude to analyze
- Detects interactive elements
- Provides structured observations

### 3. **Action Planning** (Reasoning Agent)
- Receives observations from Vision Agent
- Determines next best action
- Considers previous actions and goal progress
- Outputs specific action commands

### 4. **Execution** (Web Controller)
- Receives action commands
- Executes browser automation (click, type, scroll, etc.)
- Reports success/failure
- No decision-making - purely executional

### 5. **Iteration**
- Loop continues until goal is achieved or max steps reached
- Progress monitored by Orchestrator
- Errors handled with retry logic

## 📊 Performance Considerations

- **API Costs**: Vision API calls are expensive (~$0.01-0.03 per image)
- **Speed**: Each step takes 2-5 seconds (vision analysis + reasoning)
- **Rate Limits**: Be mindful of OpenAI/Anthropic rate limits
- **Optimization Tips**:
  - Use headless mode in production
  - Cache repeated observations
  - Reduce screenshot frequency for simple tasks
  - Use cheaper models for reasoning where appropriate

## 🔒 Safety & Constraints

```python
# Don't allow purchases
result = await system.execute(
    goal="Find products but don't buy anything",
    constraints=[
        "Don't click checkout",
        "Don't enter payment information"
    ]
)
```

Built-in safety features:
- Domain blacklisting
- Rate limiting
- Action constraints
- Automatic retry limits
- Timeout protection

## 🐛 Debugging

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Save screenshots:

```python
# config.py
EXECUTION_CONFIG = {
    "screenshot_every_step": True,
    "save_screenshots": True,
    "screenshot_directory": "./debug_screenshots"
}
```

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- [ ] Better element detection algorithms
- [ ] Support for more browsers (Firefox, Safari)
- [ ] Caching layer for LLM responses
- [ ] More sophisticated error recovery
- [ ] Performance optimizations
- [ ] Additional safety constraints
- [ ] Test coverage

## 📝 License

MIT License - feel free to use in your projects!

## 🙏 Acknowledgments

- Inspired by OpenAI's Operator
- Built with Playwright, LangChain, and modern LLMs
- Thanks to the open-source community

## 📞 Support

- **Issues**: Open a GitHub issue
- **Questions**: Use GitHub Discussions
- **Email**: adarshaduu8055@gmail.com

## 🚀 Roadmap

- [ ] Add support for more LLM providers (Google Gemini, Mistral)
- [ ] Implement parallel task execution
- [ ] Add browser extension for manual intervention
- [ ] Create web UI for task monitoring
- [ ] Add support for mobile browsers
- [ ] Implement learning from past executions
- [ ] Add multi-modal understanding (audio, video)

---

**Built with ❤️ for autonomous web automation**
=======

>>>>>>> c68ab4fccb3bada39732dbbfe8b7f87dc992b4a3
