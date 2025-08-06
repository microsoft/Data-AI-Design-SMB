import React from 'react';
import Icon from './Icon';

// Card to display each hotel processing task
const TaskCard = ({ task, onApprove, onReject, onDelete }) => {
    const { id, hotelName, status, extractedData, reliabilityScore, error } = task;

    const renderCardContent = () => {
        if (status === 'error' && error) {
            return <p className="text-red-400 text-xs italic">Error: {error}</p>;
        }
        if (extractedData) {
            return (
                <div className="text-xs text-gray-300 space-y-1 mt-2">
                    <p><strong>Address:</strong> {extractedData.address || 'N/A'}</p>
                    <p><strong>Chain/Brand:</strong> {extractedData.chainBrand || 'N/A'}</p>
                    <p><strong>Room Count:</strong> {extractedData.roomCount || 'N/A'}</p>
                    {reliabilityScore && <p><strong>Confidence:</strong> <span className={`font-bold ${reliabilityScore > 80 ? 'text-green-400' : 'text-yellow-400'}`}>{reliabilityScore}%</span></p>}
                </div>
            );
        }
        return null;
    };

    return (
        <div className="task-card bg-gray-700/50 rounded-lg p-3 shadow-lg border border-gray-600/50 relative hover:bg-gray-700/80 hover:border-gray-500/50 transition-all duration-200">
            <button 
                onClick={() => onDelete(id)} 
                className="absolute top-2 right-2 text-gray-400 hover:text-red-400 transition-colors bg-gray-800/50 rounded-full p-1 hover:bg-gray-800/80"
                title="Delete task"
            >
                <Icon name="close" className="w-3 h-3" />
            </button>
            <h4 className="font-bold text-white pr-4 mb-1">{hotelName}</h4>
            {renderCardContent()}
            {status === 'review' && (
                <div className="mt-3 flex gap-2">
                    <button 
                        onClick={() => onApprove(id)} 
                        className="flex-1 bg-green-600 hover:bg-green-500 text-white text-xs font-bold py-1.5 px-3 rounded-md flex items-center justify-center gap-1.5 transition-all duration-200 hover:shadow-md hover:shadow-green-900/30"
                    >
                        <Icon name="check" /> Approve
                    </button>
                    <button 
                        onClick={() => onReject(id)} 
                        className="flex-1 bg-red-600 hover:bg-red-500 text-white text-xs font-bold py-1.5 px-3 rounded-md flex items-center justify-center gap-1.5 transition-all duration-200 hover:shadow-md hover:shadow-red-900/30"
                    >
                        <Icon name="close" /> Reject
                    </button>
                </div>
            )}
        </div>
    );
};

export default TaskCard;
