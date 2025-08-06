// The base URL for your Python backend.
// For local development, this would be 'http://127.0.0.1:5001'
// In a real deployment, this would be your deployed backend URL.
import dotenv from 'dotenv';

// Load environment variables
dotenv.config();

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://127.0.0.1:5001';

// This function is now responsible for calling the Python backend
// to trigger the extraction process.
export const runProcessAgent = async (userId, task) => {
    try {
        const response = await fetch(`${API_BASE_URL}/trigger-process-agent`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ userId, task }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to trigger process agent');
        }

        return await response.json();
    } catch (error) {
        console.error('Error in runProcessAgent:', error);
        // We don't update Firestore from the client anymore.
        // The backend is responsible for setting the error state.
    }
};

// This function calls the Python backend to trigger the transformation process.
export const runTransformAgent = async (userId, task) => {
    try {
        const response = await fetch(`${API_BASE_URL}/trigger-transform-agent`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ userId, task }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to trigger transform agent');
        }

        return await response.json();
    } catch (error) {
        console.error('Error in runTransformAgent:', error);
        // The backend is responsible for setting the error state.
    }
};
