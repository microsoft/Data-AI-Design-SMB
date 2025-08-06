import React from 'react';
import { Icon, TaskCard } from '../helper';

// Column component for each agent status
const AgentColumn = ({ title, icon, tasks, status, onApprove, onReject, onDelete }) => {
    const statusConfig = {
        new: { color: "blue", icon: "lookup" },
        processing: { color: "purple", icon: "bot" },
        transforming: { color: "indigo", icon: "transform" },
        review: { color: "yellow", icon: "user" },
        complete: { color: "green", icon: "check" },
        error: { color: "red", icon: "close" },
    };
    const { color } = statusConfig[status];

    return (
        <div className="bg-gray-800/60 rounded-xl p-4 flex-1 min-w-[280px] flex flex-col">
            <div className="flex items-center mb-4 pb-2 border-b-2" style={{ borderColor: `var(--${color}-500)` }}>
                <Icon name={icon} className="w-6 h-6 mr-2" style={{ color: `var(--${color}-400)` }} />
                <h3 className="font-bold text-lg text-white">{title}</h3>
                <span className="ml-auto bg-gray-700 text-white text-sm font-semibold rounded-full px-3 py-1">{tasks.length}</span>
            </div>
            <div className="space-y-3 overflow-y-auto flex-grow pr-1">
                {tasks.map(task => (
                    <TaskCard key={task.id} task={task} onApprove={onApprove} onReject={onReject} onDelete={onDelete} />
                ))}
            </div>
        </div>
    );
};

export default AgentColumn;
