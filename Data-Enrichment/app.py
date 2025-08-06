# app.py
import os
import asyncio
import json
import datetime

# Load environment variables at the very top
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS  # Import CORS

# Import the planner logic after the environment is configured
from sk_planner import run_batch_workflow, search_accounts_in_db

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# In-memory storage for agent results
agent_results = {}

# Initialize with a default entry for debugging
agent_results["test_entry"] = {
    "TestAgent": {
        "result": {
            "message": "This is a test entry to verify agent_results is working",
            "token_usage": {
                "input_tokens": 150,
                "output_tokens": 75
            }
        },
        "timestamp": datetime.datetime.now().isoformat()
    }
}

# Initialize with a default entry for debugging
agent_results["test_entry"] = {
    "TestAgent": {
        "result": {"message": "This is a test entry to verify agent_results is working"},
        "timestamp": datetime.datetime.now().isoformat()
    }
}

# --- Flask Routes ---

@app.route('/')
def index():
    """Renders the main HTML page."""
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_data_wrapper():
    """
    Synchronous wrapper for our main batch validation workflow.
    """
    try:
        data = request.json
        result = asyncio.run(run_batch_workflow(data))
        return jsonify(result)
    except Exception as e:
        print(f"ERROR: An error occurred in the validation workflow: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "An internal server error occurred.", "details": str(e)}), 500

@app.route('/search_accounts', methods=['POST'])
def search_accounts_wrapper():
    """
    Synchronous wrapper for the direct account search feature.
    """
    try:
        data = request.json
        query = data.get('query')
        if not query:
            return jsonify({"error": "Query parameter is required."}), 400
        results = asyncio.run(search_accounts_in_db(query))
        return jsonify(results)
    except Exception as e:
        print(f"ERROR: An error occurred in the account search: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "An internal server error occurred.", "details": str(e)}), 500

@app.route('/api/agent-results', methods=['GET'])
def get_agent_results():
    """
    Get all agent results or filter by task_id
    """
    task_id = request.args.get('task_id')
    print(f"INFO: Getting agent results. Current results structure: {list(agent_results.keys())}")
    
    # Debug log for token usage
    for t_id, agents in agent_results.items():
        for agent_name, agent_data in agents.items():
            if 'result' in agent_data and isinstance(agent_data['result'], dict) and 'token_usage' in agent_data['result']:
                print(f"INFO: Task {t_id}, Agent {agent_name} has token usage: {agent_data['result']['token_usage']}")
            else:
                print(f"INFO: Task {t_id}, Agent {agent_name} does NOT have token usage")
    
    if task_id:
        results = agent_results.get(task_id, {})
        return jsonify({"task_id": task_id, "results": results})
    else:
        return jsonify(agent_results)

@app.route('/api/agent-results/<task_id>', methods=['POST'])
def save_agent_result(task_id):
    """
    Save the result of an agent processing step
    """
    try:
        data = request.json
        agent_name = data.get('agent_name')
        result = data.get('result')
        timestamp = datetime.datetime.now().isoformat()
        
        print(f"INFO: Saving result for task {task_id}, agent {agent_name}")
        
        if task_id not in agent_results:
            agent_results[task_id] = {}
            
        agent_results[task_id][agent_name] = {
            "result": result,
            "timestamp": timestamp
        }
        
        print(f"INFO: Updated agent_results: {agent_results}")
        
        return jsonify({"status": "success", "message": f"Result saved for task {task_id}, agent {agent_name}"})
    except Exception as e:
        print(f"ERROR: Failed to save agent result: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/results')
def results_page():
    """Renders the results review page."""
    return render_template('results.html')

@app.route('/debug/agent-results')
def debug_agent_results():
    """Debug endpoint to view the current state of agent_results"""
    return jsonify({
        "agent_results": agent_results,
        "count": len(agent_results),
        "keys": list(agent_results.keys()),
        "timestamp": datetime.datetime.now().isoformat()
    })

@app.route('/debug/token-test-data')
def debug_token_test_data():
    """Generate test data with token usage for frontend testing"""
    test_data = {
        "test_task_1": {
            "TestAgent": {
                "result": {
                    "message": "This is a test message",
                    "token_usage": {
                        "input_tokens": 123,
                        "output_tokens": 456
                    }
                },
                "timestamp": datetime.datetime.now().isoformat()
            }
        },
        "test_task_2": {
            "PlannerAgent": {
                "result": {
                    "clean_record": {
                        "name": "Test Hotel",
                        "address": "123 Test Street"
                    },
                    "discrepancy_summary": "No discrepancies found",
                    "confidence_score": {
                        "overall_score": 0.95,
                        "explanation": "High confidence in data"
                    },
                    "token_usage": {
                        "input_tokens": 789,
                        "output_tokens": 321
                    }
                },
                "timestamp": datetime.datetime.now().isoformat()
            }
        }
    }
    return jsonify(test_data)

@app.route('/debug/agent-results-verbose')
def debug_agent_results_verbose():
    """More detailed debug endpoint for agent results with token usage info"""
    verbose_results = {}
    
    for task_id, task_data in agent_results.items():
        verbose_results[task_id] = {}
        for agent_name, agent_data in task_data.items():
            token_usage = None
            if 'result' in agent_data and isinstance(agent_data['result'], dict):
                token_usage = agent_data['result'].get('token_usage')
            
            verbose_results[task_id][agent_name] = {
                'has_result': 'result' in agent_data,
                'result_is_dict': isinstance(agent_data.get('result'), dict),
                'has_token_usage': token_usage is not None,
                'token_usage': token_usage
            }
    
    return jsonify(verbose_results)

if __name__ == '__main__':
    app.run(debug=True)
