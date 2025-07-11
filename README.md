# 🤖 JobApp AI Agent - Intelligent Career Automation System

> **A sophisticated multi-agent AI system that revolutionizes job hunting through autonomous CV optimization, intelligent job matching, and automated application workflows.**

## 🌟 Project Overview

JobApp AI Agent is an advanced AI-powered career automation platform that demonstrates cutting-edge agent orchestration, intelligent document processing, and automated workflow management. This system employs a multi-agent architecture using CrewAI framework to create a fully autonomous job discovery and CV optimization pipeline.

### 🎯 What This Project Demonstrates

This portfolio project showcases **deep expertise in AI agent development**, including:

- **Multi-Agent Orchestration**: Sophisticated agent coordination using CrewAI framework
- **Intelligent Task Planning**: Dynamic task decomposition and execution
- **Advanced LLM Integration**: Strategic use of OpenAI models for content analysis and generation
- **Autonomous Decision Making**: Agents that adapt and respond to dynamic job market data
- **Complex Workflow Automation**: End-to-end automation from CV analysis to tailored application generation

---

## 🏗️ System Architecture

### Multi-Agent Design Pattern

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Researcher    │    │    Optimizer     │    │    Database     │
│     Agent       │───▶│     Agent        │───▶│     Layer       │
│                 │    │                  │    │                 │
│ • CV Analysis   │    │ • Score Calc     │    │ • PostgreSQL    │
│ • Job Search    │    │ • CV Tailoring   │    │ • Transaction   │
│ • Data Filter   │    │ • PDF Generation │    │ • Persistence   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### 🔧 Technical Architecture

**Frontend Layer** (Vanilla JavaScript SPA)
- Dynamic routing and state management
- Real-time status updates via polling
- Responsive UI with modern design patterns
- Asynchronous API communication

**Backend Layer** (FastAPI + Async Processing)
- RESTful API design with async/await patterns
- Background task execution with thread management
- Database connection pooling and transaction management
- Error handling and logging systems

**Agent Layer** (CrewAI + Advanced AI Tools)
- **Researcher Agent**: Autonomous job discovery and filtering
- **Optimizer Agent**: Intelligent CV tailoring and scoring algorithms
- **Tool Integration**: PDF processing, web search, database operations
- **Task Orchestration**: Sequential and parallel task execution

**Data Layer** (PostgreSQL + Advanced Schemas)
- Normalized database design with proper indexing
- BYTEA storage for binary PDF data
- Transaction integrity with ACID compliance
- Optimized queries for performance

---

## 🚀 Key Features & Capabilities

### 🧠 Intelligent CV Analysis
- **Deep Content Extraction**: Advanced PDF parsing and content analysis
- **Skill Mapping**: Automatic identification of technical skills and experience levels
- **Context Understanding**: Semantic analysis of work experience and projects

### 🔍 Autonomous Job Discovery
- **Multi-Platform Search**: LinkedIn, Kariyer.net, Indeed, Glassdoor integration
- **Smart Filtering**: Location, salary, company size, and recency filters
- **Quality Assurance**: Rejection of outdated or irrelevant postings

### 🎯 Intelligent Matching Algorithm
```python
Match Score = (Required Skills Match × 60%) + 
              (Preferred Skills Match × 25%) + 
              (Experience Level Match × 15%)
```

### 📄 Dynamic CV Optimization
- **Content Tailoring**: Emphasis on relevant skills for each specific job
- **Keyword Optimization**: ATS-friendly formatting and terminology
- **Professional PDF Generation**: ReportLab-based PDF creation with custom styling
- **Maintain Authenticity**: Never adds skills not present in original CV

### 💾 Advanced Data Management
- **Automated Storage**: Seamless job and CV data persistence
- **Processing State Tracking**: Comprehensive workflow state management
- **Binary Data Handling**: Efficient PDF storage and retrieval
- **Data Integrity**: Transaction management and error recovery

---

## 🛠️ Technical Skills Demonstrated

### **AI & Machine Learning**
- **CrewAI Framework**: Advanced agent orchestration and task management
- **LangChain Integration**: Tool chaining and LLM workflow automation
- **OpenAI API**: Strategic model selection and prompt engineering
- **Semantic Search**: Vector embeddings and similarity matching

### **Backend Development**
- **FastAPI**: Async web framework with dependency injection
- **PostgreSQL**: Advanced database design and optimization
- **Concurrent Programming**: Thread-safe operations and background tasks
- **API Design**: RESTful principles with proper HTTP status codes

### **Frontend Development**
- **Vanilla JavaScript**: Modern ES6+ patterns and async programming
- **SPA Architecture**: Client-side routing and state management
- **Responsive Design**: Mobile-first approach with CSS Grid/Flexbox
- **User Experience**: Intuitive interfaces with real-time feedback

### **DevOps & Architecture**
- **Package Management**: uv for Python dependencies, npm alternatives
- **Environment Configuration**: Proper secrets management and environment isolation
- **Database Migrations**: Schema management and version control
- **Error Handling**: Comprehensive logging and exception management

### **Document Processing**
- **PDF Generation**: ReportLab for professional document creation
- **Content Analysis**: Advanced text extraction and parsing
- **Binary Data Handling**: Efficient storage and retrieval of large files
- **Format Optimization**: ATS-compatible document formatting


## 🚀 Getting Started

### Prerequisites
- Python 3.10+ with uv package manager
- PostgreSQL 12+
- OpenAI API key
- SerperDev API key

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/albatrosfirst/jobapp_AI_Agent.git
cd jobapp_AI_Agent
```

2. **Setup Agent Environment**
```bash
cd jobapp_agent
uv sync
```

3. **Setup Backend Environment**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

4. **Configure Environment Variables**
```bash
# Create .env file in jobapp_agent directory
OPENAI_API_KEY=your_openai_api_key
SERPER_API_KEY=your_serper_api_key
DATABASE_URL=postgresql://username:password@localhost:5432/jobapp_db
```

5. **Database Setup**
```bash
# Create PostgreSQL database
createdb jobapp_db
# Schema will be auto-created on first run
```

### 🎮 Usage

1. **Start the Backend API**
```bash
cd backend
python3 main.py
# API runs on http://localhost:8000
```

2. **Open the Frontend**
```bash
# Serve the frontend directory
cd frontend
python3 -m http.server 8080
# Open http://localhost:8080
```

3. **Run the AI Agent System**
```bash
cd jobapp_agent
uv run jobapp_agent
# Or test with: uv run test 1 gpt-4
```

### 📱 Web Interface

- **Dashboard**: Real-time agent status and job discovery metrics
- **CV Management**: View and download optimized CVs with match scores
- **Job Listings**: Browse discovered opportunities with filtering
- **Agent Controls**: Start/stop agent processes and monitor progress

---

## 🔬 Advanced Features

### **Intelligent Retry Logic**
The system implements sophisticated retry mechanisms for handling API rate limits and network issues:

```python
@retry(max_attempts=3, backoff_factor=2)
async def search_jobs_with_retry(query: str) -> List[Job]:
    # Intelligent retry with exponential backoff
```

### **Dynamic Prompt Engineering**
Context-aware prompt generation based on CV content and job requirements:

```python
def generate_optimization_prompt(cv_content: str, job_desc: str) -> str:
    # Dynamic prompt creation with skill mapping
```

### **Real-time Status Tracking**
WebSocket-like polling for live updates of agent processing status:

```javascript
async updateAgentStatus() {
    // Real-time status monitoring with automatic refresh
}
```


### Development Setup
```bash
# Install development dependencies
cd jobapp_agent && uv add --dev pytest black flake8
cd backend && pip install -r requirements-dev.txt
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🌟 Acknowledgments

- **CrewAI** for the powerful agent orchestration framework
- **OpenAI** for state-of-the-art language models
- **FastAPI** for the excellent async web framework
- **PostgreSQL** for robust data persistence
