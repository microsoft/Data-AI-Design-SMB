import React from 'react';
import Icon from './Icon';
import TaskCard from './TaskCard';

// Column component for each agent status
const AgentColumn = ({ title, icon, tasks, status, onApprove, onReject, onDelete }) => {
    const statusConfig = {
        new: { color: "blue", icon: "lookup", description: "Ready for Azure AI Search lookup" },
        processing: { color: "purple", icon: "bot", description: "Processing with Azure AI Search" },
        transforming: { color: "indigo", icon: "transform", description: "Transforming data with AI" },
        review: { color: "yellow", icon: "user", description: "Needs manual review" },
        complete: { color: "green", icon: "check", description: "Processing complete" },
        error: { color: "red", icon: "close", description: "Error occurred" },
    };
    const { color } = statusConfig[status];

    return (
        <div className="agent-column bg-gray-800/60 rounded-xl p-4 flex-1 min-w-[280px] flex flex-col shadow-lg border border-gray-700/30 transition-all duration-200 hover:border-gray-600/50">
            <div className="flex items-center mb-4 pb-2 border-b-2" style={{ borderColor: `var(--${color}-500)` }}>
                <div className="agent-icon p-2 rounded-lg mr-2" style={{ backgroundColor: `var(--${color}-500)25` }}>
                    <Icon name={icon} className="w-6 h-6" style={{ color: `var(--${color}-400)` }} />
                </div>
                <div>
                    <h3 className="font-bold text-lg text-white">{title}</h3>
                    {statusConfig[status]?.description && (
                        <p className="text-xs text-gray-400">{statusConfig[status].description}</p>
                    )}
                </div>
                <span className="ml-auto bg-gray-700 text-white text-sm font-semibold rounded-full px-3 py-1 border border-gray-600/50">{tasks.length}</span>
            </div>
            <div className="space-y-3 overflow-y-auto flex-grow pr-1 agent-cards">
                {tasks.length === 0 ? (
                    <div className="empty-state text-center py-8 text-gray-500 italic">
                        No tasks in this stage
                    </div>
                ) : (
                    tasks.map(task => (
                        <TaskCard key={task.id} task={task} onApprove={onApprove} onReject={onReject} onDelete={onDelete} />
                    ))
                )}
            </div>
        </div>
    );
};

export default AgentColumn;
