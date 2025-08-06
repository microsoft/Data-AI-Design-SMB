/**
 * Task Client for HopSkip application
 * Uses API calls to the backend for data operations
 */

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://127.0.0.1:5001';
const taskCache = {};

const taskClient = {
  queryTasks: async (userId, hotelName = null) => {
    try {
      if (!userId) {
        console.error("User ID is required for querying tasks");
        return [];
      }
      const endpoint = hotelName
        ? `${API_BASE_URL}/tasks?userId=${encodeURIComponent(userId)}&hotelName=${encodeURIComponent(hotelName)}`
        : `${API_BASE_URL}/tasks?userId=${encodeURIComponent(userId)}`;
      const response = await fetch(endpoint);
      if (!response.ok) {
        console.error("Error fetching tasks from backend");
        return [];
      }
      const tasks = await response.json();
      tasks.forEach(task => {
        const key = `${userId}:${task.id}`;
        taskCache[key] = task;
      });
      return tasks;
    } catch (error) {
      console.error("Error in queryTasks:", error);
      return [];
    }
  },

  createTask: async (item) => {
    try {
      const response = await fetch(`${API_BASE_URL}/tasks`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(item),
      });
      if (!response.ok) {
        throw new Error(`Error creating task: ${response.statusText}`);
      }
      const createdItem = await response.json();
      const key = `${item.userId}:${item.id}`;
      taskCache[key] = createdItem;
      return createdItem;
    } catch (error) {
      console.error("Error creating task:", error);
      throw error;
    }
  },

  getTask: async (itemId, userId) => {
    try {
      const key = `${userId}:${itemId}`;
      if (taskCache[key]) {
        return taskCache[key];
      }
      const response = await fetch(`${API_BASE_URL}/tasks/${itemId}?userId=${encodeURIComponent(userId)}`);
      if (!response.ok) {
        throw new Error(`Task not found or error fetching task: ${response.statusText}`);
      }
      const task = await response.json();
      taskCache[key] = task;
      return task;
    } catch (error) {
      console.error(`Error reading task ${itemId}:`, error);
      throw error;
    }
  },

  updateTask: async (task) => {
    try {
      const response = await fetch(`${API_BASE_URL}/tasks/${task.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(task),
      });
      if (!response.ok) {
        throw new Error(`Error updating task: ${response.statusText}`);
      }
      const updatedTask = await response.json();
      const key = `${task.userId}:${task.id}`;
      taskCache[key] = updatedTask;
      return updatedTask;
    } catch (error) {
      console.error(`Error updating task ${task.id}:`, error);
      throw error;
    }
  },

  deleteTask: async (itemId, userId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/tasks/${itemId}?userId=${encodeURIComponent(userId)}`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        throw new Error(`Error deleting task: ${response.statusText}`);
      }
      const key = `${userId}:${itemId}`;
      delete taskCache[key];
      return true;
    } catch (error) {
      console.error(`Error deleting task ${itemId}:`, error);
      throw error;
    }
  }
};

console.log("Task client initialized");

export default taskClient;
