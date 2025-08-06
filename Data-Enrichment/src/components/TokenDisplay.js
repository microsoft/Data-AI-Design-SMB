import React from 'react';

const TokenDisplay = ({ tokenUsage }) => {
  if (!tokenUsage) {
    console.log('TokenDisplay: No token usage data provided');
    return (
      <div className="bg-gray-100 p-3 rounded-lg shadow-sm mb-4">
        <h3 className="text-gray-600 font-medium mb-2">No Token Usage Data Available</h3>
      </div>
    );
  }
  
  console.log('TokenDisplay: Displaying token usage:', tokenUsage);
  const input_tokens = tokenUsage.input_tokens || 0;
  const output_tokens = tokenUsage.output_tokens || 0;
  const total = input_tokens + output_tokens;
  
  return (
    <div className="bg-purple-100 p-3 rounded-lg shadow-sm mb-4">
      <h3 className="text-purple-800 font-medium mb-2">Token Usage:</h3>
      <div className="grid grid-cols-3 gap-2 text-center">
        <div className="bg-white p-2 rounded shadow-sm">
          <div className="text-sm text-gray-600">Input</div>
          <div className="text-xl font-bold text-purple-700">{input_tokens}</div>
        </div>
        <div className="bg-white p-2 rounded shadow-sm">
          <div className="text-sm text-gray-600">Output</div>
          <div className="text-xl font-bold text-purple-700">{output_tokens}</div>
        </div>
        <div className="bg-white p-2 rounded shadow-sm">
          <div className="text-sm text-gray-600">Total</div>
          <div className="text-xl font-bold text-purple-700">{total}</div>
        </div>
      </div>
    </div>
  );
};

export default TokenDisplay;
