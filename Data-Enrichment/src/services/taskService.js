import { v4 as uuidv4 } from 'uuid';
import taskClient from './taskClient';

// --- Task Service Interactions ---

/**
 * Fetches all tasks for a given user.
 * @param {string} userId - The ID of the user.
 * @param {function} callback - The callback to execute with the fetched tasks.
 */
export const fetchTasks = async (userId, callback) => {
    try {
        const tasks = await taskClient.queryTasks(userId);
        callback(tasks);
    } catch (error) {
        console.error("Error fetching tasks:", error);
    }
};

/**
 * Sets up polling to simulate real-time updates.
 * @param {string} userId - The ID of the user.
 * @param {function} callback - The callback to execute with the fetched tasks.
 */
export const onTasksChange = (userId, callback) => {
    // Initial fetch
    fetchTasks(userId, callback);
    
    // Set up polling every 3 seconds
    const intervalId = setInterval(() => {
        fetchTasks(userId, callback);
    }, 3000);
    
    // Return unsubscribe function
    return () => clearInterval(intervalId);
};

/**
 * Adds a new task and initiates the AI Search lookup.
 * @param {string} userId - The ID of the user.
 * @param {string} hotelName - The name of the hotel for the new task.
 */
export const handleAddTask = async (userId, hotelName) => {
    try {
        // Lookup Agent: Check for duplicates first.
        const existing = await taskClient.queryTasks(userId, hotelName);
        if (existing.length > 0) {
            alert("A task for this hotel already exists.");
            return;
        }

        // Create a new task
        const newTask = {
            id: uuidv4(),
            userId: userId,
            hotelName: hotelName,
            status: 'new',
            searchSource: 'azure-ai-search',
            createdAt: new Date().toISOString()
        };

        await taskClient.createTask(newTask);
    } catch (error) {
        console.error('Error adding task:', error);
    }
};

/**
 * Approves a task in the review stage.
 * @param {string} userId - The partition key.
 * @param {string} taskId - The ID of the task to update.
 */
export const handleApprove = async (userId, taskId) => {
    try {
        const task = await taskClient.getTask(taskId, userId);
        if (task) {
            task.status = 'complete';
            task.reviewedAt = new Date().toISOString();
            await taskClient.updateTask(task);
        }
    } catch (error) {
        console.error("Error approving task:", error);
    }
};

/**
 * Rejects a task in the review stage.
 * @param {string} userId - The partition key.
 * @param {string} taskId - The ID of the task to update.
 */
export const handleReject = async (userId, taskId) => {
    try {
        const task = await taskClient.getTask(taskId, userId);
        if (task) {
            task.status = 'error';
            task.error = 'Manually rejected by user.';
            task.reviewedAt = new Date().toISOString();
            await taskClient.updateTask(task);
        }
    } catch (error) {
        console.error("Error rejecting task:", error);
    }
};

/**
 * Deletes a task from the database.
 * @param {string} userId - The partition key.
 * @param {string} taskId - The ID of the task to delete.
 */
export const handleDelete = async (userId, taskId) => {
    try {
        await taskClient.deleteTask(taskId, userId);
    } catch (error) {
        console.error("Error deleting task: ", error);
    }
};
