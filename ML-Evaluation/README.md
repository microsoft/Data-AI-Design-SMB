# Healthcare Readmission Prediction App

This application demonstrates an integration between Azure OpenAI and Azure Machine Learning to predict the probability of patient hospital readmission based on various health metrics. The app provides a chat interface where healthcare professionals can input patient information and receive readmission risk assessments.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Technical Components](#technical-components)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Environment Setup](#environment-setup)
  - [Running the Application](#running-the-application)
- [Model Training and Evaluation](#model-training-and-evaluation)
- [Docker Deployment](#docker-deployment)
- [Azure Deployment](#azure-deployment)
- [API Reference](#api-reference)
- [Contributing](#contributing)

## Overview

This application combines a Flask-based web interface with Azure OpenAI services and a machine learning model deployed on Azure ML. The system enables healthcare professionals to interact with a chat interface, where they can provide patient information. Azure OpenAI processes these inputs and uses function calling to trigger a prediction from an Azure ML endpoint that assesses patient readmission risk.

## Architecture

```
                                        ┌───────────────────┐
                                        │                   │
                ┌───────────────────────┤   Flask Web App   │
                │                       │                   │
                │                       └───────────────────┘
                │                                │
                │                                │
┌───────────────▼───────┐              ┌─────────▼────────┐
│                       │              │                  │
│   Azure OpenAI API    │◄─────────────┤   Chat Interface │
│                       │              │                  │
└───────────────┬───────┘              └──────────────────┘
                │
                │  Function Call
                │
┌───────────────▼───────┐
│                       │
│   Azure ML Endpoint   │
│   (Readmission Model) │
│                       │
└───────────────────────┘
```

## Features

- **Interactive Chat Interface**: User-friendly web interface for healthcare professionals
- **Natural Language Processing**: Leverages Azure OpenAI to understand and process natural language requests
- **Patient Readmission Prediction**: Integrates with an Azure ML endpoint to predict readmission risk
- **Error Handling**: Robust error handling for API communication and prediction failures
- **Session Management**: Maintains conversation history for context-aware interactions

## Technical Components

### App Components

1. **Flask Web Application (`app.py`)**: 
   - Serves the web interface and handles HTTP requests
   - Manages sessions and communication with Azure services
   - Processes form inputs and displays results

2. **HTML Template (`templates/chat.html`)**:
   - Responsive chat interface with message history
   - Input form for user messages
   - Styled display of assistant responses and prediction results

3. **Azure OpenAI Integration**:
   - Uses Azure OpenAI SDK for Python
   - Implements function calling to trigger ML predictions
   - Processes natural language to extract relevant patient information

4. **Azure ML Integration**:
   - Sends structured patient data to an Azure ML endpoint
   - Processes prediction results
   - Handles error scenarios and edge cases

### Machine Learning Model

The system uses a RandomForestClassifier model trained on patient health data to predict readmission risk. The model considers:

- **Demographic Information**: Age
- **Vital Signs**: Blood pressure, heart rate, respiratory rate, temperature, oxygen saturation
- **Lab Results**: Glucose, hemoglobin, white blood cell count, platelet count, electrolytes
- **Medical History**: Hypertension, diabetes, coronary artery disease, heart failure, stroke history, COPD
- **Hospital Stay Info**: Length of stay
- **Clinical Notes**: Aggregated information from patient notes
- **Imaging Data**: CT scans, MRIs, X-rays performed

## Getting Started

### Prerequisites

- Python 3.9+
- Azure OpenAI service account
- Azure Machine Learning workspace with deployed model
- Docker (for containerized deployment)

### Environment Setup

1. Clone this repository
2. Create a `.env` file in the root directory with the following variables:

```
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
AZURE_OPENAI_API_KEY=your_azure_openai_key
AZURE_OPENAI_API_VERSION=your_api_version
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name

# Azure Machine Learning Endpoint Configuration
AZURE_ML_ENDPOINT_URL=your_azure_ml_endpoint_url
AZURE_ML_API_KEY=your_azure_ml_api_key

# Flask Configuration
FLASK_HOST=127.0.0.1
FLASK_PORT=5001
FLASK_DEBUG=False
```

3. Install required packages:

```bash
pip install -r requirements.txt
```

### Running the Application

1. Start the Flask application:

```bash
python app.py
```

2. Open a web browser and navigate to `http://127.0.0.1:5001`

## Model Training and Evaluation

The project includes Jupyter notebooks for model training and evaluation:

1. **Training.ipynb**: 
   - Data preparation and preprocessing
   - Model selection and hyperparameter tuning
   - Training a RandomForestClassifier
   - Model evaluation and validation

2. **Evals.ipynb**:
   - Synthetic data generation for testing
   - Model performance evaluation
   - Analysis of feature importance
   - Testing with various patient profiles

## Docker Deployment

The application can be containerized using Docker:

1. Build the Docker image:

```bash
docker build -t healthcare-readmission-app .
```

2. Run the container:

```bash
docker run -p 5001:5000 --env-file .env healthcare-readmission-app
```

Alternatively, use Docker Compose:

```bash
docker-compose up
```

## Azure Deployment

The application is designed to be deployed to Azure using Azure Container Apps or App Service:

1. **Using Azure Container Registry**:
   - Build and push the Docker image to ACR
   - Deploy to Azure Container Apps or App Service

2. **Using App Service**:
   - Configure deployment settings in Azure Portal
   - Set up environment variables from `.env` file
   - Deploy directly from source code

## API Reference

### Azure OpenAI Function

The application defines a function for Azure OpenAI to call:

```json
{
  "name": "predict_patient_readmission",
  "description": "Predicts the probability of hospital readmission for a patient",
  "parameters": {
    "type": "object",
    "properties": {
      "age": {
        "type": "integer",
        "description": "Patient's age in years."
      },
      "systolic_bp": {
        "type": "number",
        "description": "Systolic blood pressure (mmHg)"
      },
      // Additional parameters omitted for brevity
    },
    "required": [
      "age",
      "systolic_bp",
      // Additional required fields omitted for brevity
    ]
  }
}
```

### Azure ML Endpoint

The Azure ML endpoint expects a JSON payload with patient data:

```json
{
  "input_data": [
    {
      "age": 65,
      "systolic_bp": 140,
      "diastolic_bp": 90,
      // Additional fields omitted for brevity
    }
  ]
}
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Submit a pull request
