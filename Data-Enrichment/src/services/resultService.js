// resultService.js
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000';
console.log('API_BASE_URL:', API_BASE_URL); // Debug log to verify the URL

/**
 * Fetch all agent results
 */
export const getAllAgentResults = async () => {
  try {
    // Normal endpoint
    console.log('Fetching all agent results from:', `${API_BASE_URL}/api/agent-results`);
    const response = await axios.get(`${API_BASE_URL}/api/agent-results`);
    console.log('Received agent results:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error fetching agent results:', error);
    throw error;
  }
};

/**
 * Fetch test data for debugging
 */
export const getTestData = async () => {
  try {
    console.log('Fetching test data from:', `${API_BASE_URL}/debug/token-test-data`);
    const response = await axios.get(`${API_BASE_URL}/debug/token-test-data`);
    console.log('Received test data:', response.data);
    return response.data;
  } catch (error) {
    console.error('Error fetching test data:', error);
    throw error;
  }
};

/**
 * Fetch agent results for a specific task
 * @param {string} taskId - The ID of the task to fetch results for
 */
export const getAgentResultsByTaskId = async (taskId) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/agent-results?task_id=${taskId}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching agent results for task ${taskId}:`, error);
    throw error;
  }
};
