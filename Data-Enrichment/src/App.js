import React, { useState, useEffect } from 'react';
import { auth, onAuthStateChanged } from './auth';
import { onTasksChange, handleAddTask, handleApprove, handleReject, handleDelete } from './services/taskService';
import { runProcessAgent, runTransformAgent } from './services/agentService';

import AgentColumn from './components/AgentColumn';
import ResultsReview from './components/ResultsReview';
import Spinner from './components/Spinner';
import Icon from './components/Icon';

function App() {
    const [userId, setUserId] = useState(null);
    const [tasks, setTasks] = useState([]);
    const [newHotelName, setNewHotelName] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [processingAgents, setProcessingAgents] = useState({});
    const [statusMessages, setStatusMessages] = useState([]);
    const [showStatusPanel, setShowStatusPanel] = useState(true);
    const [activeTab, setActiveTab] = useState('workflow'); // 'workflow' or 'results'

    // --- User Authentication ---
    useEffect(() => {
        const unsubscribe = onAuthStateChanged((user) => {
            if (user) {
                setUserId(user.uid);
            } else {
                setUserId(null); // Should trigger sign-in flow if needed
            }
        });
        return () => unsubscribe();
    }, []);

    // --- Real-time Task Listener ---
    useEffect(() => {
        if (!userId) return;
        const unsubscribe = onTasksChange(userId, setTasks);
        return () => unsubscribe();
    }, [userId]);

    // Add status message to the list with timestamp
    const addStatusMessage = (message) => {
        const timestamp = new Date().toLocaleTimeString();
        setStatusMessages(prev => [...prev.slice(-19), `[${timestamp}] ${message}`]);
    };

    // Clear all status messages
    const clearStatusMessages = () => {
        setStatusMessages([]);
    };

    // --- Agent Triggering Mechanism ---
    useEffect(() => {
        if (!userId) return;
        tasks.forEach(task => {
            if (!processingAgents[task.id]) {
                if (task.status === 'new') {
                    setProcessingAgents(prev => ({ ...prev, [task.id]: true }));
                    addStatusMessage(`Started Azure AI Search lookup for: "${task.hotelName}"`);
                    runProcessAgent(userId, task).then(() => {
                        addStatusMessage(`Completed Azure AI Search lookup for "${task.hotelName}"`);
                    }).catch(err => {
                        addStatusMessage(`Error during Azure AI Search lookup for "${task.hotelName}": ${err.message}`);
                    }).finally(() => {
                        setProcessingAgents(prev => {
                            const newAgents = { ...prev };
                            delete newAgents[task.id];
                            return newAgents;
                        });
                    });
                } else if (task.status === 'transforming') {
                    setProcessingAgents(prev => ({ ...prev, [task.id]: true }));
                    addStatusMessage(`Started transforming data for "${task.hotelName}"`);
                    runTransformAgent(userId, task).then(() => {
                        addStatusMessage(`Completed transformation of "${task.hotelName}"`);
                    }).catch(err => {
                        addStatusMessage(`Error transforming "${task.hotelName}": ${err.message}`);
                    }).finally(() => {
                        setProcessingAgents(prev => {
                            const newAgents = { ...prev };
                            delete newAgents[task.id];
                            return newAgents;
                        });
                    });
                }
            }
        });
    }, [tasks, userId, processingAgents]);

    // --- UI Event Handlers ---
    const onAddTask = async (e) => {
        e.preventDefault();
        if (!newHotelName.trim() || !userId) return;
        setIsSubmitting(true);
        addStatusMessage(`Adding new hotel: "${newHotelName.trim()}"`);
        try {
            await handleAddTask(userId, newHotelName.trim());
            addStatusMessage(`Successfully added hotel: "${newHotelName.trim()}"`);
        } catch (error) {
            addStatusMessage(`Failed to add hotel: ${error.message}`);
        }
        setNewHotelName('');
        setIsSubmitting(false);
    };

    const onApprove = (taskId) => {
        const task = tasks.find(t => t.id === taskId);
        addStatusMessage(`Approving hotel data: "${task?.hotelName || taskId}"`);
        return handleApprove(userId, taskId);
    };
    
    const onReject = (taskId) => {
        const task = tasks.find(t => t.id === taskId);
        addStatusMessage(`Rejecting hotel data: "${task?.hotelName || taskId}"`);
        return handleReject(userId, taskId);
    };
    
    const onDelete = (taskId) => {
        const task = tasks.find(t => t.id === taskId);
        addStatusMessage(`Deleting hotel task: "${task?.hotelName || taskId}"`);
        return handleDelete(userId, taskId);
    };
    
    // Filter tasks for each column
    const filterTasks = (status) => tasks.filter(task => task.status === status);

    if (!userId) {
        return (
            <div className="bg-gray-900 text-white min-h-screen flex items-center justify-center">
                <div className="flex items-center gap-3 text-lg">
                    <Spinner /> Authenticating...
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-100 text-gray-900">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="header mb-6">
                    <h1 className="text-3xl font-bold text-gray-900">HopSkip Data Validation</h1>
                    
                    {/* Tab Navigation */}
                    <div className="flex border-b border-gray-200 mt-4">
                        <button
                            onClick={() => setActiveTab('workflow')}
                            className={`py-2 px-4 font-medium text-sm ${
                                activeTab === 'workflow' 
                                    ? 'border-b-2 border-blue-500 text-blue-600' 
                                    : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            }`}
                        >
                            Workflow
                        </button>
                        <button
                            onClick={() => setActiveTab('results')}
                            className={`py-2 px-4 font-medium text-sm ${
                                activeTab === 'results' 
                                    ? 'border-b-2 border-blue-500 text-blue-600' 
                                    : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
                            }`}
                        >
                            Results Review
                        </button>
                    </div>
                </div>
                
                {activeTab === 'workflow' ? (
                    <>
                        <div className="controls-bar p-4 bg-white rounded-lg shadow mb-6 flex flex-col md:flex-row items-start md:items-center gap-4">
                            {/* Form to add a new hotel task */}
                            <form onSubmit={onAddTask} className="flex-grow flex flex-col sm:flex-row gap-2 w-full">
                                <input
                                    type="text"
                                    value={newHotelName}
                                    onChange={(e) => setNewHotelName(e.target.value)}
                                    className="flex-grow border border-gray-300 rounded-md px-4 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                                    placeholder="Enter hotel name or batch JSON..."
                                />
                                <button
                                    type="submit"
                                    disabled={isSubmitting}
                                    className="bg-blue-600 hover:bg-blue-700 text-white rounded-md px-4 py-2 transition-colors duration-200 ease-in-out flex items-center"
                                >
                                    {isSubmitting ? <Spinner className="mr-2" /> : <Icon name="plus" className="w-5 h-5 mr-2" />}
                                    Add Task
                                </button>
                            </form>
                        </div>

                        {/* Process Status Panel */}
                        <div className="process-status-panel mb-6">
                            <div className="bg-gray-900 text-white p-2 rounded-t-lg flex justify-between items-center">
                                <h3 className="font-medium text-sm ml-2">Process Log</h3>
                                <div className="flex gap-1">
                                    <button 
                                        onClick={() => setShowStatusPanel(!showStatusPanel)} 
                                        className="bg-gray-700/50 hover:bg-gray-700 text-gray-300 hover:text-white transition-all p-1.5 rounded"
                                        title={showStatusPanel ? "Minimize" : "Expand"}
                                    >
                                        <Icon name={showStatusPanel ? "chevron-down" : "chevron-up"} className="w-4 h-4" />
                                    </button>
                                    <button 
                                        onClick={clearStatusMessages} 
                                        className="bg-gray-700/50 hover:bg-gray-700 text-gray-300 hover:text-white transition-all p-1.5 rounded"
                                        title="Clear log"
                                    >
                                        <Icon name="trash" className="w-4 h-4" />
                                    </button>
                                </div>
                            </div>

                            {showStatusPanel && (
                                <div className="process-log bg-gradient-to-b from-gray-900/80 to-gray-900/50 p-4 max-h-64 overflow-y-auto font-mono text-sm">
                                    {statusMessages.length === 0 ? (
                                        <div className="text-gray-500 italic text-center py-8">No activity to display</div>
                                    ) : (
                                        statusMessages.map((msg, idx) => (
                                            <div key={idx} className="process-log-message py-1.5 border-b border-gray-800/50 last:border-0">
                                                {msg}
                                            </div>
                                        ))
                                    )}
                                </div>
                            )}
                        </div>

                        {/* Agent Columns - Using CSS Grid for better layout */}
                        <div className="agent-grid">
                            <AgentColumn title="AI Search Lookup" icon="lookup" status="new" tasks={filterTasks('new')} onDelete={onDelete} />
                            <AgentColumn title="Processing" icon="bot" status="processing" tasks={filterTasks('processing')} onDelete={onDelete} />
                            <AgentColumn title="Transforming" icon="transform" status="transforming" tasks={filterTasks('transforming')} onDelete={onDelete} />
                            <AgentColumn title="Manual Review" icon="user" status="review" tasks={filterTasks('review')} onApprove={onApprove} onReject={onReject} onDelete={onDelete} />
                            <AgentColumn title="Complete" icon="check" status="complete" tasks={filterTasks('complete')} onDelete={onDelete} />
                            <AgentColumn title="Error" icon="close" status="error" tasks={filterTasks('error')} onDelete={onDelete} />
                        </div>
                    </>
                ) : (
                    <div className="bg-white shadow rounded-lg overflow-hidden">
                        <ResultsReview />
                    </div>
                )}
            </div>
        </div>
    );
}

export default App;
