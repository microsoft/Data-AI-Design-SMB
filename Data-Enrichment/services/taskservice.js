import container from './azureCosmosClient';
import { v4 as uuidv4 } from 'uuid'; // Cosmos DB doesn't auto-generate IDs like Firestore, so we create them.

// --- Cosmos DB Interactions ---

/**
 * Fetches all tasks for a given user.
 * @param {string} userId - The ID of the user.
 * @param {function} callback - The callback to execute with the fetched tasks.
 */
export const fetchTasks = async (userId, callback) => {
    try {
        const querySpec = {
            query: "SELECT * FROM c WHERE c.userId = @userId",
            parameters: [
                {
                    name: "@userId",
                    value: userId
                }
            ]
        };
        const { resources: tasks } = await container.items.query(querySpec).fetchAll();
        callback(tasks);
    } catch (error) {
        console.error("Error fetching tasks from Cosmos DB:", error);
    }
};

/**
 * Sets up polling to simulate real-time updates from Cosmos DB.
 * In production, this would be replaced with Azure SignalR/Web PubSub
 * listening to the Cosmos DB Change Feed.
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
 * Adds a new task to the database.
 * @param {string} userId - The ID of the user.
 * @param {string} hotelName - The name of the hotel for the new task.
 */
export const handleAddTask = async (userId, hotelName) => {
    try {
        // Lookup Agent: Check for duplicates first.
        const querySpec = {
            query: "SELECT * FROM c WHERE c.userId = @userId AND c.hotelName = @hotelName",
            parameters: [
                { name: "@userId", value: userId },
                { name: "@hotelName", value: hotelName }
            ]
        };
        const { resources: existing } = await container.items.query(querySpec).fetchAll();
        if (existing.length > 0) {
            alert("A task for this hotel already exists.");
            return;
        }

        const newTask = {
            id: uuidv4(), // Generate a unique ID
            userId: userId, // userId is our partition key
            hotelName: hotelName,
            status: 'new',
            createdAt: new Date().toISOString()
        };

        await container.items.create(newTask);
    } catch (error) {
        console.error('Error adding task to Cosmos DB:', error);
    }
};

/**
 * Approves a task in the review stage.
 * @param {string} userId - The partition key.
 * @param {string} taskId - The ID of the task to update.
 */
export const handleApprove = async (userId, taskId) => {
    try {
        const { resource: task } = await container.item(taskId, userId).read();
        if (task) {
            task.status = 'complete';
            task.reviewedAt = new Date().toISOString();
            await container.item(taskId, userId).replace(task);
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
        const { resource: task } = await container.item(taskId, userId).read();
        if (task) {
            task.status = 'error';
            task.error = 'Manually rejected by user.';
            task.reviewedAt = new Date().toISOString();
            await container.item(taskId, userId).replace(task);
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
        await container.item(taskId, userId).delete();
    } catch (error) {
        console.error("Error deleting task: ", error);
    }
};
