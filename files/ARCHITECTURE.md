# Hierarchical Multi-Agent Web Automation System

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    HIGH-LEVEL LAYER                         │
│  ┌───────────────────────────────────────────────────────┐  │
│  │         Planner/Orchestrator Agent                    │  │
│  │  - Goal decomposition                                 │  │
│  │  - Task delegation                                    │  │
│  │  - Progress monitoring                                │  │
│  │  - Error recovery                                     │  │
│  └───────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    MID-LEVEL LAYER                          │
│  ┌──────────────────────┐    ┌──────────────────────────┐  │
│  │   Vision Agent       │    │   Reasoning Agent        │  │
│  │  - Screenshot proc.  │◄───┤  - Action planning       │  │
│  │  - Element detection │    │  - Decision making       │  │
│  │  - OCR/Text extract  │    │  - State management      │  │
│  └──────────────────────┘    └──────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    LOW-LEVEL LAYER                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │         Web Controller Agents                         │  │
│  │  - Mouse control                                      │  │
│  │  - Keyboard input                                     │  │
│  │  - Click execution                                    │  │
│  │  - Scroll management                                  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Core Framework
- **Python 3.11+**: Primary language
- **LangChain**: Agent orchestration and LLM integration
- **LangGraph**: Multi-agent workflow management

### Vision & AI
- **GPT-4 Vision / Claude 3.5 Sonnet**: Vision processing
- **GPT-4/Claude**: Reasoning and planning
- **OpenCV**: Image processing
- **pytesseract**: OCR capabilities

### Web Automation
- **Playwright**: Modern browser automation
- **Selenium**: Fallback/legacy support
- **pyautogui**: Direct mouse/keyboard control

### Communication & State
- **Redis**: Agent state management
- **WebSocket**: Real-time communication
- **Pydantic**: Type-safe message passing

## Component Breakdown

### 1. High-Level: Planner/Orchestrator
- Receives high-level user goals
- Breaks down into sequential tasks
- Delegates to mid-level agents
- Monitors overall progress
- Handles failures and retries

### 2. Mid-Level: Vision & Reasoning
**Vision Agent:**
- Takes screenshots of current browser state
- Identifies interactive elements (buttons, forms, links)
- Extracts relevant text and context
- Provides structured observations

**Reasoning Agent:**
- Receives vision observations
- Determines next action based on goal
- Selects appropriate web controller command
- Validates action feasibility

### 3. Low-Level: Web Controllers
- Executes atomic actions
- No decision-making logic
- Direct browser interaction
- Reports execution status

## Message Flow

```
User Goal → Planner
           ↓
Planner → Creates Task Queue
           ↓
For Each Task:
    Planner → Vision Agent (Get current state)
           ↓
    Vision → Screenshot + Analysis
           ↓
    Vision → Reasoning Agent (Current state + Goal)
           ↓
    Reasoning → Determines Action
           ↓
    Reasoning → Web Controller (Execute command)
           ↓
    Controller → Executes & Reports
           ↓
    Report → Planner (Update progress)
```

## Implementation Phases

1. **Phase 1**: Low-level web controllers
2. **Phase 2**: Vision agent with screenshot processing
3. **Phase 3**: Reasoning agent with action planning
4. **Phase 4**: Orchestrator with goal decomposition
5. **Phase 5**: Integration and error handling
6. **Phase 6**: Monitoring and optimization

## Key Design Principles

1. **Separation of Concerns**: Each agent has a single responsibility
2. **Abstraction Layers**: Higher agents don't know implementation details
3. **Stateless Execution**: Controllers are stateless; state lives in orchestrator
4. **Observable System**: Every action is logged and traceable
5. **Fault Tolerance**: Each layer can recover from failures independently
