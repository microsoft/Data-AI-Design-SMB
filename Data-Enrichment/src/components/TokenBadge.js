import React from 'react';

const TokenBadge = ({ tokenUsage }) => {
  if (!tokenUsage) return null;
  
  const { input_tokens, output_tokens } = tokenUsage;
  const total = (input_tokens || 0) + (output_tokens || 0);
  
  return (
    <div className="flex space-x-2 items-center">
      <div className="text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded-full">
        In: {input_tokens?.toLocaleString() || 0}
      </div>
      <div className="text-xs bg-indigo-100 text-indigo-800 px-2 py-1 rounded-full">
        Out: {output_tokens?.toLocaleString() || 0}
      </div>
      <div className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
        Total: {total.toLocaleString()}
      </div>
    </div>
  );
};

export default TokenBadge;
