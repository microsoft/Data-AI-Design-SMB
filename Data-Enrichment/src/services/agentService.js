// The base URL for your Python backend.
// For local development, this would be 'http://127.0.0.1:5001'
// In a real deployment, this would be your deployed backend URL.

// In the browser, we can access REACT_APP_* variables directly from process.env
// No need to use dotenv in the browser
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://127.0.0.1:5001';

// This function calls the Python backend to trigger the extraction process
// which uses Azure AI Search for the initial hotel data lookup.
export const runProcessAgent = async (userId, task) => {
    try {
        console.log(`Sending task to backend for Azure AI Search lookup: ${task.hotelName}`);
        
        const response = await fetch(`${API_BASE_URL}/trigger-process-agent`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ userId, task }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to trigger Azure AI Search lookup');
        }

        const result = await response.json();
        console.log(`Azure AI Search lookup completed for: ${task.hotelName}`);
        return result;
    } catch (error) {
        console.error('Error in Azure AI Search lookup:', error);
        // The backend is responsible for setting the error state in Cosmos DB
        throw error;
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
