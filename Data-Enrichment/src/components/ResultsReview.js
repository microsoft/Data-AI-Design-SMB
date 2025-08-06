import React, { useState, useEffect } from 'react';
import { getAllAgentResults, getAgentResultsByTaskId, getTestData } from '../services/resultService';
import TokenSummary from './TokenSummary';
import TokenBadge from './TokenBadge';
import axios from 'axios';

const ResultsReview = () => {
  const [results, setResults] = useState({});
  const [selectedTaskId, setSelectedTaskId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showRawData, setShowRawData] = useState(false);
  const [useTestData, setUseTestData] = useState(false);
  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000';
  
  // Fetch all results on component mount or when useTestData changes
  useEffect(() => {
    const fetchResults = async () => {
      try {
        setLoading(true);
        
        let data;
        if (useTestData) {
          console.log('Fetching test data');
          data = await getTestData();
        } else {
          console.log('Fetching real data');
          data = await getAllAgentResults();
        }
        
        console.log('Agent results data:', data);
        setResults(data);
        
        // Add debug logging to check token usage
        for (const taskId in data) {
          for (const agentName in data[taskId]) {
            const agent = data[taskId][agentName];
            if (agent.result && agent.result.token_usage) {
              console.log(`Task ${taskId}, Agent ${agentName} has token usage:`, agent.result.token_usage);
            } else {
              console.log(`Task ${taskId}, Agent ${agentName} has NO token usage`);
              console.log('Result structure:', agent.result);
            }
          }
        }
        
        // Select the first task by default if available
        const taskIds = Object.keys(data);
        if (taskIds.length > 0 && !selectedTaskId) {
          setSelectedTaskId(taskIds[0]);
        }
        
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch agent results: ' + err.message);
        setLoading(false);
        console.error(err);
      }
    };
    
    fetchResults();
  }, [useTestData, API_BASE_URL, selectedTaskId]);
  
  // Format JSON for display
  const formatJson = (json) => {
    if (!json) return 'No data available';
    try {
      return JSON.stringify(json, null, 2);
    } catch (e) {
      return 'Error formatting JSON: ' + e.message;
    }
  };
  
  // Get task display name
  const getTaskDisplayName = (taskId) => {
    if (!taskId) return 'Unknown Task';
    
    // If the task has a hotel name in the results, use it
    const taskResults = results[taskId];
    if (taskResults && taskResults.PlannerAgent && taskResults.PlannerAgent.result) {
      const hotelData = taskResults.PlannerAgent.result.clean_record;
      if (hotelData && hotelData.name) {
        return `${hotelData.name}`;
      }
    }
    
    return `Task ${taskId}`;
  };
  
  // Handle task selection
  const handleTaskSelect = (taskId) => {
    setSelectedTaskId(taskId);
  };
  
  if (loading) {
    return <div className="p-4">Loading agent results...</div>;
  }
  
  if (error) {
    return <div className="p-4 text-red-600">{error}</div>;
  }
  
  const taskIds = Object.keys(results);
  const selectedTask = selectedTaskId ? results[selectedTaskId] : null;
  
  return (
    <div className="flex flex-col h-full">
      <h1 className="text-2xl font-bold p-4 bg-blue-100">Agent Results Review</h1>
      
      {taskIds.length === 0 ? (
        <div className="p-4">No agent results available. Run some tasks first.</div>
      ) : (
        <div className="flex flex-col h-full">
          {/* Token Summary */}
          <div className="p-4">
            <TokenSummary results={results} />
          </div>
          
          <div className="flex flex-row flex-grow overflow-hidden">
            {/* Task list sidebar */}
            <div className="w-1/4 border-r border-gray-300 overflow-y-auto">
              <h2 className="text-lg font-semibold p-3 bg-gray-100 border-b border-gray-300">Tasks</h2>
              <ul>
                {taskIds.map(taskId => (
                  <li 
                    key={taskId}
                    onClick={() => handleTaskSelect(taskId)}
                    className={`p-3 border-b border-gray-200 cursor-pointer hover:bg-gray-50 ${
                      selectedTaskId === taskId ? 'bg-blue-50 border-l-4 border-blue-500' : ''
                    }`}
                  >
                    <div className="flex flex-col gap-2">
                      <div className="flex justify-between items-center">
                        <div className="font-medium">{getTaskDisplayName(taskId)}</div>
                        {/* Debug info */}
                        <div className="text-xs bg-gray-100 px-2 py-1 rounded">
                          ID: {taskId.substring(0, 8)}...
                        </div>
                      </div>
                      
                      {/* Token usage in list item */}
                      {results[taskId].PlannerAgent?.result?.token_usage && (
                        <TokenBadge tokenUsage={results[taskId].PlannerAgent.result.token_usage} />
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            </div>
            
            {/* Results panel */}
            <div className="w-3/4 overflow-y-auto">
              {selectedTask ? (
                <div className="p-4">
                  <div className="flex flex-col gap-4 mb-4">
                    <div className="flex justify-between items-center">
                      <h2 className="text-xl font-semibold">{getTaskDisplayName(selectedTaskId)}</h2>
                      <div className="flex space-x-2">
                        <button 
                          onClick={() => setShowRawData(!showRawData)}
                          className="bg-gray-200 hover:bg-gray-300 text-gray-800 px-3 py-1 rounded text-sm"
                        >
                          {showRawData ? 'Hide Raw Data' : 'Show Raw Data'}
                        </button>
                        <button 
                          onClick={() => setUseTestData(!useTestData)}
                          className={`${useTestData ? 'bg-green-200 hover:bg-green-300 text-green-800' : 'bg-blue-200 hover:bg-blue-300 text-blue-800'} px-3 py-1 rounded text-sm`}
                        >
                          {useTestData ? 'Using Test Data' : 'Using Real Data'}
                        </button>
                      </div>
                    </div>
                    
                    {/* Token usage in header area */}
                    {selectedTask.PlannerAgent?.result?.token_usage && (
                      <div className="bg-gray-50 p-3 rounded-lg border border-gray-200">
                        <h3 className="font-medium mb-2 text-gray-700">Token Usage for This Hotel:</h3>
                        <div className="grid grid-cols-3 gap-3">
                          <div className="flex flex-col bg-purple-50 p-2 rounded-lg border border-purple-100">
                            <span className="text-xs text-purple-500">Input Tokens</span>
                            <span className="text-xl font-bold text-purple-700">
                              {selectedTask.PlannerAgent.result.token_usage.input_tokens?.toLocaleString() || 0}
                            </span>
                          </div>
                          <div className="flex flex-col bg-indigo-50 p-2 rounded-lg border border-indigo-100">
                            <span className="text-xs text-indigo-500">Output Tokens</span>
                            <span className="text-xl font-bold text-indigo-700">
                              {selectedTask.PlannerAgent.result.token_usage.output_tokens?.toLocaleString() || 0}
                            </span>
                          </div>
                          <div className="flex flex-col bg-blue-50 p-2 rounded-lg border border-blue-100">
                            <span className="text-xs text-blue-500">Total Tokens</span>
                            <span className="text-xl font-bold text-blue-700">
                              {(
                                (selectedTask.PlannerAgent.result.token_usage.input_tokens || 0) +
                                (selectedTask.PlannerAgent.result.token_usage.output_tokens || 0)
                              ).toLocaleString()}
                            </span>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                  
                  {/* Debug Info */}
                  <div className="mb-4 p-2 bg-gray-100 rounded text-sm">
                    <div>Selected Task ID: {selectedTaskId}</div>
                    <div>Task data keys: {JSON.stringify(Object.keys(selectedTask))}</div>
                  </div>
                  
                  {/* Raw Data Display */}
                  {showRawData && (
                    <div className="mb-6 p-3 bg-gray-50 rounded border border-gray-300 overflow-auto max-h-96">
                      <h3 className="font-medium mb-2">Raw Task Data:</h3>
                      <pre className="text-xs">{formatJson(selectedTask)}</pre>
                    </div>
                  )}
                  
                  {Object.keys(selectedTask).map(agentName => {
                    const agentResult = selectedTask[agentName];
                    console.log(`Rendering result for agent ${agentName}:`, agentResult);
                    if (agentResult.result && agentResult.result.token_usage) {
                      console.log(`Token usage for ${agentName}:`, agentResult.result.token_usage);
                    } else {
                      console.log(`No token usage found for ${agentName}`);
                    }
                    return (
                      <div key={agentName} className="mb-6 border rounded-lg overflow-hidden">
                        <div className="bg-gray-100 p-3 font-medium border-b flex justify-between items-center">
                          <div>
                            {agentName}
                            <span className="text-sm text-gray-500 ml-2">
                              {agentResult.timestamp ? new Date(agentResult.timestamp).toLocaleString() : ''}
                            </span>
                          </div>
                          {/* Status indicator */}
                          <div className={`text-sm px-2 py-1 rounded ${agentResult.status === 'completed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                            {agentResult.status || 'unknown'}
                          </div>
                        </div>
                        
                        {agentResult.result && agentResult.result.error ? (
                          <div className="p-4 bg-red-50 text-red-700">
                            <p className="font-medium">Error: {agentResult.result.error}</p>
                            {agentResult.result.details && (
                              <p className="mt-2">{agentResult.result.details}</p>
                            )}
                            
                            {/* Token Display Component */}
                            {agentResult.result.token_usage && (
                              <div className="mt-4">
                                <h4 className="font-medium text-gray-700 mb-2">Token Usage Details:</h4>
                                <div className="bg-purple-50 border border-purple-100 rounded-lg p-3">
                                  <div className="grid grid-cols-3 gap-3">
                                    <div>
                                      <div className="text-sm text-purple-700 font-medium">Input</div>
                                      <div className="text-xl font-bold text-purple-800">{agentResult.result.token_usage.input_tokens?.toLocaleString() || 0}</div>
                                    </div>
                                    <div>
                                      <div className="text-sm text-indigo-700 font-medium">Output</div>
                                      <div className="text-xl font-bold text-indigo-800">{agentResult.result.token_usage.output_tokens?.toLocaleString() || 0}</div>
                                    </div>
                                    <div>
                                      <div className="text-sm text-blue-700 font-medium">Total</div>
                                      <div className="text-xl font-bold text-blue-800">
                                        {(
                                          (agentResult.result.token_usage.input_tokens || 0) + 
                                          (agentResult.result.token_usage.output_tokens || 0)
                                        ).toLocaleString()}
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              </div>
                            )}
                          </div>
                        ) : agentResult.result && agentResult.result.discrepancy_summary ? (
                          <div className="p-4">
                            <h3 className="font-medium mb-2">Discrepancies Found:</h3>
                            <div className="bg-yellow-50 p-3 rounded mb-4">
                              {agentResult.result.discrepancy_summary}
                            </div>
                            
                            <h3 className="font-medium mb-2">Confidence Score:</h3>
                            <div className="bg-blue-50 p-3 rounded mb-4">
                              {agentResult.result.confidence_score ? (
                                <div>
                                  <div className="flex items-center">
                                    <div className="w-full bg-gray-200 rounded-full h-2.5">
                                      <div 
                                        className="bg-blue-600 h-2.5 rounded-full" 
                                        style={{ width: `${agentResult.result.confidence_score.overall_score * 100}%` }}
                                      ></div>
                                    </div>
                                    <span className="ml-2 font-bold">
                                      {Math.round(agentResult.result.confidence_score.overall_score * 100)}%
                                    </span>
                                  </div>
                                  <div className="mt-2 text-sm">
                                    {agentResult.result.confidence_score.explanation}
                                  </div>
                                </div>
                              ) : 'No confidence score available'}
                            </div>
                            
                            {/* Token Display Component */}
                            {agentResult.result.token_usage && (
                              <div className="mt-4">
                                <h4 className="font-medium text-gray-700 mb-2">Token Usage Details:</h4>
                                <div className="bg-purple-50 border border-purple-100 rounded-lg p-3">
                                  <div className="grid grid-cols-3 gap-3">
                                    <div>
                                      <div className="text-sm text-purple-700 font-medium">Input</div>
                                      <div className="text-xl font-bold text-purple-800">{agentResult.result.token_usage.input_tokens?.toLocaleString() || 0}</div>
                                    </div>
                                    <div>
                                      <div className="text-sm text-indigo-700 font-medium">Output</div>
                                      <div className="text-xl font-bold text-indigo-800">{agentResult.result.token_usage.output_tokens?.toLocaleString() || 0}</div>
                                    </div>
                                    <div>
                                      <div className="text-sm text-blue-700 font-medium">Total</div>
                                      <div className="text-xl font-bold text-blue-800">
                                        {(
                                          (agentResult.result.token_usage.input_tokens || 0) + 
                                          (agentResult.result.token_usage.output_tokens || 0)
                                        ).toLocaleString()}
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              </div>
                            )}
                            
                            <h3 className="font-medium mb-2 mt-4">Clean Record:</h3>
                            <pre className="bg-gray-50 p-3 rounded overflow-auto max-h-80">
                              {formatJson(agentResult.result.clean_record)}
                            </pre>
                          </div>
                        ) : (
                          <div className="p-4">
                            <pre className="overflow-auto max-h-96 bg-gray-50 p-3 rounded">
                              {formatJson(agentResult.result)}
                            </pre>
                            
                            {/* Token Display Component */}
                            {agentResult.result && agentResult.result.token_usage && (
                              <div className="mt-4">
                                <div className="bg-purple-50 border border-purple-100 rounded-lg p-3">
                                  <div className="grid grid-cols-3 gap-3">
                                    <div>
                                      <div className="text-sm text-purple-700 font-medium">Input</div>
                                      <div className="text-xl font-bold text-purple-800">{agentResult.result.token_usage.input_tokens?.toLocaleString() || 0}</div>
                                    </div>
                                    <div>
                                      <div className="text-sm text-indigo-700 font-medium">Output</div>
                                      <div className="text-xl font-bold text-indigo-800">{agentResult.result.token_usage.output_tokens?.toLocaleString() || 0}</div>
                                    </div>
                                    <div>
                                      <div className="text-sm text-blue-700 font-medium">Total</div>
                                      <div className="text-xl font-bold text-blue-800">
                                        {(
                                          (agentResult.result.token_usage.input_tokens || 0) + 
                                          (agentResult.result.token_usage.output_tokens || 0)
                                        ).toLocaleString()}
                                      </div>
                                    </div>
                                  </div>
                                </div>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="p-4">Select a task to view its results</div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResultsReview;
