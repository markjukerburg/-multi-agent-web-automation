# 🚀 Quick Start Guide

Get up and running with the Multi-Agent Web Automation System in 5 minutes!

## 📋 Prerequisites

- Python 3.11 or higher
- API key from either:
  - OpenAI (for GPT-4 Vision)
  - Anthropic (for Claude)
- Basic understanding of Python async/await

## ⚡ Installation Steps

### 1. Install Dependencies

```bash
# Make setup script executable
chmod +x setup.sh

# Run setup
./setup.sh
```

Or manually:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### 2. Configure API Keys

Create a `.env` file:

```bash
# For OpenAI
OPENAI_API_KEY=your-openai-key-here

# OR for Anthropic
ANTHROPIC_API_KEY=your-anthropic-key-here
```

### 3. Run Your First Automation

Create a file `my_first_automation.py`:

```python
import asyncio
from main import run_automation

async def main():
    result = await run_automation(
        goal="Go to Google and search for 'Python tutorials'",
        starting_url="https://www.google.com",
        provider="openai",  # or "anthropic"
        headless=False  # Watch it happen!
    )
    
    print(f"\nSuccess: {result['success']}")
    print(f"Steps taken: {result['steps_taken']}")
    
    if not result['success']:
        print(f"Error: {result.get('error', 'Unknown')}")

if __name__ == "__main__":
    asyncio.run(main())
```

Run it:

```bash
python my_first_automation.py
```

## 📚 Simple Examples

### Example 1: Basic Web Search

```python
import asyncio
from main import run_automation

async def google_search():
    result = await run_automation(
        goal="Search for 'artificial intelligence' and click the Wikipedia result",
        starting_url="https://www.google.com"
    )
    return result

asyncio.run(google_search())
```

### Example 2: E-commerce Price Check

```python
from main import MultiAgentSystem

async def check_price():
    async with MultiAgentSystem(provider="openai") as system:
        result = await system.execute(
            goal="Find the price of iPhone 15 on Best Buy",
            starting_url="https://www.bestbuy.com",
            max_steps=20
        )
        return result

asyncio.run(check_price())
```

### Example 3: Information Gathering

```python
async def find_contact():
    async with MultiAgentSystem(provider="openai") as system:
        result = await system.execute(
            goal="Navigate to Anthropic.com and find their contact email",
            starting_url="https://www.anthropic.com"
        )
        return result

asyncio.run(find_contact())
```

## 🎮 Interactive Mode

You can also run the examples interactively:

```bash
# Run a specific example
python examples.py 1

# Example options:
# 1 - E-Commerce Search
# 2 - Information Gathering
# 3 - Form Filling
# 4 - Research Task
# ... and more
```

## 🔧 Customization

### Change LLM Provider

```python
# Use OpenAI
system = MultiAgentSystem(provider="openai")

# Use Anthropic
system = MultiAgentSystem(provider="anthropic")
```

### Headless Mode

```python
# Show browser (good for learning/debugging)
system = MultiAgentSystem(headless=False)

# Hide browser (good for production)
system = MultiAgentSystem(headless=True)
```

### Add Constraints

```python
result = await system.execute(
    goal="Fill out contact form with test data",
    constraints=[
        "Don't actually submit the form",
        "Use fake data only"
    ]
)
```

### Limit Steps

```python
result = await system.execute(
    goal="Search for products",
    max_steps=10  # Stop after 10 actions
)
```

## 📊 Monitor Progress

```python
import asyncio
from main import MultiAgentSystem

async def monitor_task():
    async with MultiAgentSystem() as system:
        # Start task
        task = asyncio.create_task(
            system.execute(
                goal="Your goal here",
                max_steps=30
            )
        )
        
        # Monitor in real-time
        while not task.done():
            status = await system.get_status()
            print(f"Progress: Step {status.get('current_step', 0)}")
            await asyncio.sleep(2)
        
        # Get final result
        result = await task
        return result

asyncio.run(monitor_task())
```

## 🐛 Debugging Tips

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Save Screenshots

Edit `config.py`:

```python
EXECUTION_CONFIG = {
    "screenshot_every_step": True,
    "save_screenshots": True,
    "screenshot_directory": "./debug_screenshots"
}
```

### Watch Browser

```python
# Never run headless during debugging
system = MultiAgentSystem(headless=False)
```

## ⚠️ Common Issues

### "API key not found"
- Make sure `.env` file exists
- Check that API key is valid
- Verify environment variable is loaded

### "Browser not found"
```bash
# Reinstall browsers
playwright install chromium
```

### "Import errors"
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### "Task gets stuck"
- Reduce `max_steps` to test
- Check if goal is too vague
- Try headless=False to watch what's happening

## 💡 Tips for Success

1. **Start Simple**: Begin with basic navigation tasks
2. **Be Specific**: Clear goals get better results
3. **Watch It Work**: Use headless=False initially
4. **Monitor Costs**: Vision API calls add up quickly
5. **Add Constraints**: Use safety constraints for sensitive tasks
6. **Test Incrementally**: Break complex tasks into smaller ones

## 📖 Next Steps

1. Read the full [README.md](README.md)
2. Explore [examples.py](examples.py) for more use cases
3. Check [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system
4. Customize [config.py](config.py) for your needs
5. Run tests with `pytest test_system.py`

## 🆘 Getting Help

- Check logs in `./logs/` directory
- Look at saved screenshots in `./screenshots/`
- Read error messages carefully
- Try reducing complexity of the goal
- Use debug logging mode

## 🎯 Your First Real Task

Try this realistic example:

```python
import asyncio
from main import run_automation

async def research_task():
    """Research a topic across multiple sources"""
    
    # Step 1: Wikipedia search
    wiki_result = await run_automation(
        goal="Search for 'machine learning' on Wikipedia and summarize the first paragraph",
        starting_url="https://www.wikipedia.org",
        max_steps=10
    )
    
    print("Wikipedia done!")
    
    # Step 2: Academic source
    academic_result = await run_automation(
        goal="Search for 'machine learning papers' on Google Scholar",
        starting_url="https://scholar.google.com",
        max_steps=10
    )
    
    print("Scholar done!")
    
    return {
        "wikipedia": wiki_result['success'],
        "scholar": academic_result['success']
    }

# Run it
result = asyncio.run(research_task())
print(f"\nResults: {result}")
```

---

**Ready to build something amazing? Let's go! 🚀**
