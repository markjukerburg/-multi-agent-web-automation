"""
Example Usage Scripts
Demonstrates different automation scenarios
"""

import asyncio
from main import MultiAgentSystem, run_automation


# ============================================================================
# Example 1: E-commerce Product Search
# ============================================================================

async def example_ecommerce_search():
    """Search for products on an e-commerce site"""
    
    print("\n" + "="*60)
    print("EXAMPLE 1: E-Commerce Product Search")
    print("="*60)
    
    result = await run_automation(
        goal="Search for 'wireless headphones' on Amazon and find the top 3 results with their prices",
        starting_url="https://www.amazon.com",
        headless=False,
        max_steps=30
    )
    
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Completed in {result['steps_taken']} steps")
    else:
        print(f"Failed: {result['error']}")


# ============================================================================
# Example 2: Information Gathering
# ============================================================================

async def example_info_gathering():
    """Gather information from a website"""
    
    print("\n" + "="*60)
    print("EXAMPLE 2: Information Gathering")
    print("="*60)
    
    async with MultiAgentSystem(provider="anthropic", headless=False) as system:
        result = await system.execute(
            goal="Navigate to OpenAI's website and find their contact email address",
            starting_url="https://www.openai.com"
        )
        
        print(f"Success: {result['success']}")
        print(f"Steps: {result.get('steps_taken', 0)}")


# ============================================================================
# Example 3: Form Filling
# ============================================================================

async def example_form_filling():
    """Fill out a web form"""
    
    print("\n" + "="*60)
    print("EXAMPLE 3: Form Filling")
    print("="*60)
    
    async with MultiAgentSystem(provider="anthropic", headless=False) as system:
        result = await system.execute(
            goal="""Navigate to a contact form and fill it with:
            Name: John Doe
            Email: john@example.com
            Message: I'm interested in your services
            Then submit the form""",
            starting_url="https://example.com/contact",
            constraints=["Don't actually submit the form, stop before clicking submit"]
        )
        
        print(f"Success: {result['success']}")


# ============================================================================
# Example 4: Multi-Step Research
# ============================================================================

async def example_research_task():
    """Complex multi-step research task"""
    
    print("\n" + "="*60)
    print("EXAMPLE 4: Multi-Step Research")
    print("="*60)
    
    async with MultiAgentSystem(provider="anthropic", headless=False) as system:
        result = await system.execute(
            goal="""Research climate change statistics:
            1. Go to Wikipedia
            2. Search for 'climate change'
            3. Find the current global temperature increase
            4. Navigate to a related scientific source
            5. Verify the information""",
            starting_url="https://www.wikipedia.org",
            max_steps=50
        )
        
        print(f"Success: {result['success']}")
        print(f"Final URL: {result.get('final_url', 'N/A')}")


# ============================================================================
# Example 5: Price Comparison
# ============================================================================

async def example_price_comparison():
    """Compare prices across multiple sites"""
    
    print("\n" + "="*60)
    print("EXAMPLE 5: Price Comparison")
    print("="*60)
    
    products_to_check = [
        {
            "site": "https://www.amazon.com",
            "product": "iPhone 15"
        },
        {
            "site": "https://www.bestbuy.com",
            "product": "iPhone 15"
        }
    ]
    
    results = []
    
    async with MultiAgentSystem(provider="anthropic", headless=True) as system:
        for product_info in products_to_check:
            result = await system.execute(
                goal=f"Search for '{product_info['product']}' and find the lowest price",
                starting_url=product_info['site'],
                max_steps=20
            )
            results.append({
                "site": product_info['site'],
                "success": result['success'],
                "steps": result.get('steps_taken', 0)
            })
    
    print("\nResults:")
    for r in results:
        print(f"  {r['site']}: {'✓' if r['success'] else '✗'} ({r['steps']} steps)")


# ============================================================================
# Example 6: Login and Dashboard Access
# ============================================================================

async def example_login_automation():
    """Automate login process (demo only - don't use with real credentials)"""
    
    print("\n" + "="*60)
    print("EXAMPLE 6: Login Automation (DEMO)")
    print("="*60)
    
    async with MultiAgentSystem(provider="openai", headless=False) as system:
        result = await system.execute(
            goal="""Navigate to the login page, 
            find the email and password fields (don't actually fill them),
            and identify the login button""",
            starting_url="https://example.com/login",
            constraints=[
                "Don't enter any real credentials",
                "Don't actually click the login button"
            ]
        )
        
        print(f"Success: {result['success']}")


# ============================================================================
# Example 7: Real-time Monitoring
# ============================================================================

async def example_monitoring_with_status():
    """Monitor execution in real-time"""
    
    print("\n" + "="*60)
    print("EXAMPLE 7: Real-time Monitoring")
    print("="*60)
    
    async with MultiAgentSystem(provider="anthropic", headless=False) as system:
        # Start the task
        task = asyncio.create_task(
            system.execute(
                goal="Search for 'machine learning' on Google and click the first result",
                starting_url="https://www.google.com",
                max_steps=20
            )
        )
        
        # Monitor progress
        while not task.done():
            status = await system.get_status()
            print(f"Status: {status.get('status', 'unknown')} - "
                  f"Step {status.get('current_step', 0)}")
            await asyncio.sleep(2)
        
        result = await task
        print(f"\nFinal result: {'Success' if result['success'] else 'Failed'}")


# ============================================================================
# Example 8: Using Claude Instead of GPT-4
# ============================================================================

async def example_with_claude():
    """Same task but using Anthropic's Claude"""
    
    print("\n" + "="*60)
    print("EXAMPLE 8: Using Claude Vision")
    print("="*60)
    
    result = await run_automation(
        goal="Navigate to Anthropic's website and find information about Claude",
        starting_url="https://www.anthropic.com",
        provider="anthropic",  # Use Claude instead of GPT-4
        headless=False
    )
    
    print(f"Success: {result['success']}")


# ============================================================================
# Example 9: Error Handling and Recovery
# ============================================================================

async def example_error_handling():
    """Demonstrate error handling"""
    
    print("\n" + "="*60)
    print("EXAMPLE 9: Error Handling")
    print("="*60)
    
    try:
        async with MultiAgentSystem(provider="openai", headless=False) as system:
            # Intentionally difficult task
            result = await system.execute(
                goal="Navigate to a page that doesn't exist",
                starting_url="https://example.com/this-page-does-not-exist-404",
                max_steps=5
            )
            
            print(f"Result: {result}")
    except Exception as e:
        print(f"Caught exception: {e}")


# ============================================================================
# Example 10: Sequential Tasks
# ============================================================================

async def example_sequential_tasks():
    """Execute multiple tasks in sequence"""
    
    print("\n" + "="*60)
    print("EXAMPLE 10: Sequential Tasks")
    print("="*60)
    
    tasks = [
        {
            "goal": "Search for 'Python programming' on Wikipedia",
            "url": "https://www.wikipedia.org"
        },
        {
            "goal": "Search for 'JavaScript tutorial' on MDN",
            "url": "https://developer.mozilla.org"
        }
    ]
    
    async with MultiAgentSystem(provider="openai", headless=True) as system:
        for idx, task in enumerate(tasks, 1):
            print(f"\nTask {idx}: {task['goal']}")
            result = await system.execute(
                goal=task['goal'],
                starting_url=task['url'],
                max_steps=15
            )
            print(f"  Result: {'✓' if result['success'] else '✗'}")


# ============================================================================
# Run All Examples
# ============================================================================

async def run_all_examples():
    """Run all examples (carefully - this will take time!)"""
    
    examples = [
        ("E-Commerce Search", example_ecommerce_search),
        ("Info Gathering", example_info_gathering),
        ("Form Filling", example_form_filling),
        ("Research Task", example_research_task),
        ("Price Comparison", example_price_comparison),
        ("Login Automation", example_login_automation),
        ("Real-time Monitoring", example_monitoring_with_status),
        ("Using Claude", example_with_claude),
        ("Error Handling", example_error_handling),
        ("Sequential Tasks", example_sequential_tasks),
    ]
    
    for name, example_func in examples:
        print(f"\n\n{'='*60}")
        print(f"Running: {name}")
        print(f"{'='*60}")
        try:
            await example_func()
        except Exception as e:
            print(f"Example failed: {e}")
        
        print("\nPress Enter to continue to next example...")
        input()


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        example_num = sys.argv[1]
        
        examples_map = {
            "1": example_ecommerce_search,
            "2": example_info_gathering,
            "3": example_form_filling,
            "4": example_research_task,
            "5": example_price_comparison,
            "6": example_login_automation,
            "7": example_monitoring_with_status,
            "8": example_with_claude,
            "9": example_error_handling,
            "10": example_sequential_tasks,
        }
        
        if example_num in examples_map:
            asyncio.run(examples_map[example_num]())
        else:
            print(f"Unknown example: {example_num}")
            print("Available examples: 1-10")
    else:
        print("Usage: python examples.py [example_number]")
        print("Examples:")
        print("  1 - E-Commerce Search")
        print("  2 - Info Gathering")
        print("  3 - Form Filling")
        print("  4 - Research Task")
        print("  5 - Price Comparison")
        print("  6 - Login Automation")
        print("  7 - Real-time Monitoring")
        print("  8 - Using Claude")
        print("  9 - Error Handling")
        print("  10 - Sequential Tasks")
