# Data Validation Platform

A Flask application that demonstrates a multi-agent data pipeline for hotel data processing using Azure services.

> **Note**: Several unused or duplicated files have been moved to the `archive` directory. See the README.md file in the archive directory for details.

## Architecture

This application uses:
- **Frontend**: HTML/CSS with Tailwind and Vue.js
- **Backend**: Flask Python API
- **AI Orchestration**: Semantic Kernel for agent coordination
- **AI Services**: Azure OpenAI for data extraction and transformation
- **Data Storage**: Azure AI Search for hotel database 
- **In-memory Storage**: For agent results

## Process Flow

When a validation process is initiated, the application follows this workflow:

1. **User Input**: 
   - User selects hotel brands and location through the web interface
   - User initiates the process by clicking "Start Validation"

2. **Data Retrieval**:
   - Flask server receives the request and calls `run_batch_workflow`
   - The workflow queries Azure AI Search for hotels matching the specified brands and location
   - Hotel records are retrieved and prepared for processing

3. **Agent Orchestration**:
   - For each hotel, a new processing task is created with `process_single_hotel`
   - Tasks are executed concurrently using `asyncio.gather`

4. **Hotel Processing**:
   - `WebLookupAgent` retrieves fresh hotel data from web sources
   - Data discrepancies between stored and web data are identified
   - `ConfidenceAgent` analyzes discrepancies to generate confidence scores
   - A consolidated record with the most accurate data is created

5. **Result Storage**:
   - Processing results are stored in memory via the `/api/agent-results/{task_id}` endpoint
   - Results include original records, clean records, discrepancies, and confidence scores

6. **Result Review**:
   - Users can navigate to the Results page to review agent processing outcomes
   - The Results page initially shows a summary table with processing runs, including:
     - When the process was run (timestamp)
     - Location that was searched
     - Hotel chain(s) that were processed
   - Users can click on a run to see a breakdown of all hotels processed in that batch
   - Hotel detail views include data discrepancies, confidence scores, and expandable data sections

## Agent System

The application uses Semantic Kernel to orchestrate specialized AI agents:

### WebLookupAgent
- **Purpose**: Retrieve fresh hotel information from web sources
- **Key Function**: `get_hotel_info_from_web`
- **Inputs**: Hotel name, location
- **Outputs**: Geographic coordinates, address data

### ConfidenceAgent
- **Purpose**: Analyze data discrepancies and generate confidence scores
- **Key Function**: `generate_confidence_score`
- **Inputs**: Discrepancy summary
- **Outputs**: Confidence score, reasoning, and recommendations

### PlannerAgent (ChatCompletionAgent)
- **Purpose**: Orchestrate the overall process for each hotel
- **Functions**: Calls WebLookupAgent and ConfidenceAgent
- **Process**:
  1. Gets fresh hotel data from web
  2. Compares with database record
  3. Summarizes discrepancies
  4. Generates confidence score
  5. Creates consolidated record with best data

## Key Components

### sk_planner.py
- **Purpose**: Core processing logic and agent orchestration
- **Key Functions**:
  - `run_batch_workflow`: Main entry point for processing
  - `process_single_hotel`: Processes individual hotel records
  - `find_hotels_in_db`: Searches Azure AI Search for hotels
  - `save_agent_result`: Stores agent results for review

### app.py
- **Purpose**: Flask web server and API endpoints
- **Key Routes**:
  - `/`: Main workflow interface
  - `/process`: Initiates batch processing
  - `/api/agent-results`: Stores and retrieves agent results
  - `/results`: Results review interface

### Templates
- **index.html**: Main workflow interface for initiating processing
- **results.html**: Results review interface with two views:
  - **Summary View**: Table showing processing runs with timestamps, locations, and hotel chains
  - **Detail View**: Breakdown of all hotels processed within a selected run

## Detailed Process Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│                          User Interface                             │
│                                                                     │
└───────────────────────────────────┬─────────────────────────────────┘
                                    │
                                    │ User selects brands and location
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│                      Flask Server (app.py)                          │
│                                                                     │
└───────────────────────────────────┬─────────────────────────────────┘
                                    │
                                    │ Call run_batch_workflow
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│                  find_hotels_in_db (sk_planner.py)                  │
│                                                                     │
└───────────────────────────────────┬─────────────────────────────────┘
                                    │
                                    │ Query Azure AI Search
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│                 process_single_hotel (For each hotel)               │
│                                                                     │
└───────────────────────────────────┬─────────────────────────────────┘
                                    │
                                    │ Create ChatCompletionAgent
                                    ▼
                  ┌─────────────────┴─────────────────┐
                  │                                   │
                  ▼                                   ▼
┌─────────────────────────────┐       ┌─────────────────────────────┐
│                             │       │                             │
│  WebLookupAgent             │       │  ConfidenceAgent            │
│  get_hotel_info_from_web    │       │  generate_confidence_score  │
│                             │       │                             │
└─────────────────┬───────────┘       └───────────┬─────────────────┘
                  │                               │
                  │                               │
                  ▼                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│             Agent processes results and creates final JSON          │
│                                                                     │
└───────────────────────────────────┬─────────────────────────────────┘
                                    │
                                    │ Store results
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│            save_agent_result -> /api/agent-results/{task_id}        │
│                                                                     │
└───────────────────────────────────┬─────────────────────────────────┘
                                    │
                                    │ User navigates to Results page
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│            Results Review Page (results.html)                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Mermaid Diagram

For easy integration with documentation tools, here's the same diagram in Mermaid format:

```mermaid
flowchart TD
    %% Define nodes
    UI[User Interface]
    Flask[Flask Server \n app.py]
    FindHotels[find_hotels_in_db \n sk_planner.py]
    ProcessHotel[process_single_hotel \n For each hotel]
    WebAgent[WebLookupAgent \n get_hotel_info_from_web]
    ConfidenceAgent[ConfidenceAgent \n generate_confidence_score]
    ProcessResults[Agent processes results \n creates final JSON]
    SaveResults[save_agent_result \n /api/agent-results/{task_id}]
    ResultsPage[Results Review Page \n results.html]
    
    %% Define connections
    UI --> |User selects brands and location| Flask
    Flask --> |Call run_batch_workflow| FindHotels
    FindHotels --> |Query Azure AI Search| ProcessHotel
    ProcessHotel --> |Create ChatCompletionAgent| WebAgent & ConfidenceAgent
    WebAgent --> ProcessResults
    ConfidenceAgent --> ProcessResults
    ProcessResults --> |Store results| SaveResults
    SaveResults --> |User navigates to Results page| ResultsPage
    
    %% Styling
    classDef uiNode fill:#f9f9f9,stroke:#333,stroke-width:2px;
    classDef serverNode fill:#d4e6f1,stroke:#333,stroke-width:2px;
    classDef agentNode fill:#d5f5e3,stroke:#333,stroke-width:2px;
    classDef processingNode fill:#fdebd0,stroke:#333,stroke-width:2px;
    classDef storageNode fill:#ebdef0,stroke:#333,stroke-width:2px;
    
    class UI uiNode;
    class Flask,FindHotels serverNode;
    class WebAgent,ConfidenceAgent agentNode;
    class ProcessHotel,ProcessResults processingNode;
    class SaveResults,ResultsPage storageNode;
```

This Mermaid diagram can be rendered in GitHub, GitLab, and many other Markdown viewers or documentation tools.

## Setup Instructions

### Prerequisites

- Python (v3.8+)
- Azure Subscription with:
  - Azure OpenAI API access
  - Azure AI Search index with hotel data

### Environment Variables

Create a `.env` file with the following configuration:

```
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=your_deployment_name

# Azure AI Search Configuration
AZURE_SEARCH_ENDPOINT=your_search_endpoint
AZURE_SEARCH_INDEX_NAME=your_index_name
AZURE_SEARCH_KEY=your_search_key
AZURE_SEARCH_HOTEL_NAME_FIELD=name
AZURE_SEARCH_BRAND_FIELDS=brandId,chainId
AZURE_SEARCH_CITY_FIELD=city
AZURE_SEARCH_STATE_FIELD=state

# Optional: Bing Search for additional grounding
BING_SEARCH_API_KEY=your_bing_api_key
```

## Running the Application

### Option 1: Running with Python

1. Create a Python virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Unix/Mac
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Start the Flask server:
```bash
python app.py
```

4. Open the application in your browser (default: http://localhost:5000)

## API Endpoints

- **POST /process**
  - Initiates batch workflow
  - Payload: `{"companies": ["Hilton", "Marriott"], "location": "New York, NY"}`

- **POST /search_accounts**
  - Direct search for hotel accounts
  - Payload: `{"query": "Hilton New York"}`

- **GET /api/agent-results**
  - Retrieves all agent results or filter by task_id
  - Query params: `?task_id=123` (optional)

- **POST /api/agent-results/{task_id}**
  - Saves agent results for a specific task
  - Payload: `{"agent_name": "PlannerAgent", "result": {...}}`

## Usage

1. Open the application in your browser (default: http://localhost:5000)
2. On the main page:
   - Select one or more hotel brands (e.g., Hilton, Marriott)
   - Enter a location (e.g., "New York, NY" or "CA")
   - Click "Start Validation" to begin processing
3. The system will:
   - Search for hotels matching your criteria
   - Process each hotel using AI agents
   - Store the results for review
4. Navigate to the Results page using the link at the top
5. On the Results page:
   - View a list of processing runs with timestamps, locations, and hotel chains
   - Click on a run to see all hotels processed in that batch
   - Review data discrepancies and confidence scores for each hotel
   - See clean hotel records with the most accurate data

## System Data Flow

1. **Database Query**: The application queries Azure AI Search to find hotel records matching the selected brands and location
2. **Data Extraction**: For each hotel, WebLookupAgent extracts fresh data from web sources
3. **Data Comparison**: Discrepancies between database and web data are identified
4. **Confidence Analysis**: ConfidenceAgent analyzes discrepancies and generates confidence scores
5. **Data Consolidation**: A consolidated "clean record" is created with the most accurate information
6. **Result Storage**: Processing results are stored for review
7. **Result Review**: Users can review processing results on the Results page

## Development Notes

- The application uses Semantic Kernel to orchestrate AI operations
- `asyncio.gather` is used to process multiple hotels concurrently
- Agent results are stored in-memory (can be enhanced with a persistent database)
- Flask's Jinja2 templates and Vue.js are used for the front-end
- Data discrepancies are highlighted for user review
- Confidence scores include detailed reasoning and recommendations
