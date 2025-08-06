import React from 'react';

const TokenSummary = ({ results }) => {
  console.log('TokenSummary: Calculating from results:', results);
  
  // Calculate total token usage across all tasks
  const calculateTotalTokens = () => {
    let totalInput = 0;
    let totalOutput = 0;
    let taskCount = 0;
    let tasksWithTokens = 0;
    
    for (const taskId in results) {
      taskCount++;
      let hasTokenData = false;
      
      for (const agentName in results[taskId]) {
        const agentData = results[taskId][agentName];
        console.log(`TokenSummary: Checking ${taskId} > ${agentName}:`, agentData);
        
        if (agentData.result && agentData.result.token_usage) {
          const inputTokens = agentData.result.token_usage.input_tokens || 0;
          const outputTokens = agentData.result.token_usage.output_tokens || 0;
          
          console.log(`TokenSummary: Found tokens - Input: ${inputTokens}, Output: ${outputTokens}`);
          
          totalInput += inputTokens;
          totalOutput += outputTokens;
          hasTokenData = true;
        }
      }
      
      if (hasTokenData) {
        tasksWithTokens++;
      }
    }
    
    return {
      totalInput,
      totalOutput,
      totalTokens: totalInput + totalOutput,
      taskCount,
      tasksWithTokens
    };
  };
  
  const tokenSummary = calculateTotalTokens();
  console.log('TokenSummary: Final calculation:', tokenSummary);
  
  return (
    <div className="bg-indigo-50 p-4 rounded-lg shadow-sm mb-6">
      <h2 className="text-xl font-semibold mb-3 text-indigo-800">Token Usage Summary</h2>
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4 text-center">
        <div className="bg-white p-3 rounded-lg shadow-sm">
          <div className="text-indigo-600 text-sm font-medium">Total Tasks</div>
          <div className="text-3xl font-bold text-indigo-900">{tokenSummary.taskCount}</div>
        </div>
        <div className="bg-white p-3 rounded-lg shadow-sm">
          <div className="text-indigo-600 text-sm font-medium">Tasks with Tokens</div>
          <div className="text-3xl font-bold text-indigo-900">{tokenSummary.tasksWithTokens}</div>
        </div>
        <div className="bg-white p-3 rounded-lg shadow-sm">
          <div className="text-indigo-600 text-sm font-medium">Input Tokens</div>
          <div className="text-3xl font-bold text-indigo-900">{tokenSummary.totalInput.toLocaleString()}</div>
        </div>
        <div className="bg-white p-3 rounded-lg shadow-sm">
          <div className="text-indigo-600 text-sm font-medium">Output Tokens</div>
          <div className="text-3xl font-bold text-indigo-900">{tokenSummary.totalOutput.toLocaleString()}</div>
        </div>
        <div className="bg-white p-3 rounded-lg shadow-sm">
          <div className="text-indigo-600 text-sm font-medium">Total Tokens</div>
          <div className="text-3xl font-bold text-indigo-900">{tokenSummary.totalTokens.toLocaleString()}</div>
        </div>
      </div>
    </div>
  );
};

export default TokenSummary;
