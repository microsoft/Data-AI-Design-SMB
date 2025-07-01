import os
import json
import requests
from flask import Flask, request, render_template, session, redirect, url_for
import openai
from openai import AzureOpenAI
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()

# Azure OpenAI Configuration
AOAI_ENDPOINT = ""
AOAI_KEY = ""
AOAI_API_VERSION = ""  # Use a stable version
AOAI_DEPLOYMENT_NAME = ""

# Azure Machine Learning Endpoint Configuration
AML_ENDPOINT_URL = ""
AML_API_KEY = ""

# --- Flask App Setup ---
app = Flask(__name__)
app.secret_key = os.urandom(24)

# --- Azure OpenAI Client Initialization ---

if not AOAI_ENDPOINT or not AOAI_KEY:
    print("ERROR: Azure OpenAI Endpoint or Key not configured.")
client = AzureOpenAI(
    azure_endpoint=AOAI_ENDPOINT, api_key=AOAI_KEY, api_version=AOAI_API_VERSION
)

# --- Tools Definition (Keep your existing tools definition) ---
tools = [
    {
        "type": "function",
        "function": {
            "name": "predict_patient_readmission",
            "description": "Predicts the probability of hospital readmission for a patient based on demographics, vital signs, lab results, medical history, clinical notes summary, and imaging summary.",
            "parameters": {
                "type": "object",
                "properties": {
                    "age": {
                        "type": "integer",
                        "description": "Patient's age in years.",
                    },
                    "systolic_bp": {
                        "type": "number",
                        "description": "Systolic blood pressure (mmHg)",
                    },
                    "diastolic_bp": {
                        "type": "number",
                        "description": "Diastolic blood pressure (mmHg)",
                    },
                    "heart_rate": {"type": "number", "description": "Heart rate (bpm)"},
                    "respiratory_rate": {
                        "type": "number",
                        "description": "Respiratory rate (breaths/min)",
                    },
                    "temperature": {
                        "type": "number",
                        "description": "Body temperature (Celsius)",
                    },
                    "oxygen_saturation": {
                        "type": "number",
                        "description": "Oxygen saturation (%)",
                    },
                    "glucose": {"type": "number", "description": "Glucose level"},
                    "hemoglobin": {"type": "number", "description": "Hemoglobin level"},
                    "white_blood_cells": {
                        "type": "number",
                        "description": "White blood cell count",
                    },
                    "platelet_count": {
                        "type": "number",
                        "description": "Platelet count",
                    },
                    "sodium": {"type": "number", "description": "Sodium level"},
                    "potassium": {"type": "number", "description": "Potassium level"},
                    "creatinine": {"type": "number", "description": "Creatinine level"},
                    "hypertension": {
                        "type": "integer",
                        "description": "History of hypertension (1 for Yes, 0 for No)",
                    },
                    "diabetes": {
                        "type": "integer",
                        "description": "History of diabetes (1 for Yes, 0 for No)",
                    },
                    "coronary_artery_disease": {
                        "type": "integer",
                        "description": "History of CAD (1 for Yes, 0 for No)",
                    },
                    "heart_failure": {
                        "type": "integer",
                        "description": "History of heart failure (1 for Yes, 0 for No)",
                    },
                    "stroke_history": {
                        "type": "integer",
                        "description": "History of stroke (1 for Yes, 0 for No)",
                    },
                    "copd": {
                        "type": "integer",
                        "description": "History of COPD (1 for Yes, 0 for No)",
                    },
                    "length_of_stay": {
                        "type": "integer",
                        "description": "Duration of the hospital stay in days",
                    },
                    "aggregated_notes": {
                        "type": "string",
                        "description": "A brief summary or key information from clinical notes relevant to readmission risk. Provide empty string if none available/mentioned.",
                    },
                    "imaging_count": {
                        "type": "integer",
                        "description": "Total count of relevant imaging scans (e.g., CT, MRI, X-ray) performed during the stay. Provide 0 if none.",
                    },
                    "has_ct": {
                        "type": "integer",
                        "description": "Flag indicating if a CT scan was performed (1 for Yes, 0 for No).",
                    },
                    "has_mri": {
                        "type": "integer",
                        "description": "Flag indicating if an MRI scan was performed (1 for Yes, 0 for No).",
                    },
                    "has_xray": {
                        "type": "integer",
                        "description": "Flag indicating if an X-ray was performed (1 for Yes, 0 for No).",
                    },
                },
                "required": [
                    "age",
                    "systolic_bp",
                    "diastolic_bp",
                    "heart_rate",
                    "respiratory_rate",
                    "temperature",
                    "oxygen_saturation",
                    "glucose",
                    "hemoglobin",
                    "white_blood_cells",
                    "platelet_count",
                    "sodium",
                    "potassium",
                    "creatinine",
                    "hypertension",
                    "diabetes",
                    "coronary_artery_disease",
                    "heart_failure",
                    "stroke_history",
                    "copd",
                    "length_of_stay",
                ],
            },
        },
    }
]


# --- Helper Function to Call Azure ML Endpoint ---


def call_azure_ml_endpoint(arguments):
    """Calls the deployed Azure ML endpoint, ensuring required fields have defaults."""
    if not AML_ENDPOINT_URL or not AML_API_KEY:
        return {
            "error": "Azure ML endpoint configuration missing on server.",
            "details": "Admin action required.",
        }

    headers = {
        "Authorization": f"Bearer {AML_API_KEY}",
        "Content-Type": "application/json",
    }

    # Ensure defaults match the model's expected input schema
    arguments.setdefault("aggregated_notes", arguments.get("aggregated_notes", ""))
    arguments.setdefault("imaging_count", arguments.get("imaging_count", 0))
    arguments.setdefault("has_ct", arguments.get("has_ct", 0))
    arguments.setdefault("has_mri", arguments.get("has_mri", 0))
    arguments.setdefault("has_xray", arguments.get("has_xray", 0))

    # Basic type validation/conversion
    for key in [
        "age",
        "systolic_bp",
        "diastolic_bp",
        "heart_rate",
        "respiratory_rate",
        "temperature",
        "oxygen_saturation",
        "glucose",
        "hemoglobin",
        "white_blood_cells",
        "platelet_count",
        "sodium",
        "potassium",
        "creatinine",
        "length_of_stay",
        "imaging_count",
    ]:
        if key in arguments:
            try:
                arguments[key] = (
                    float(arguments[key]) if arguments[key] is not None else None
                )
            except (ValueError, TypeError):
                print(
                    f"Warning: Could not convert argument '{key}' value '{arguments[key]}' to float. Setting to None."
                )
                arguments[key] = None

    for key in [
        "hypertension",
        "diabetes",
        "coronary_artery_disease",
        "heart_failure",
        "stroke_history",
        "copd",
        "has_ct",
        "has_mri",
        "has_xray",
    ]:
        if key in arguments:
            val = arguments[key]
            arguments[key] = 1 if str(val).lower() in ["true", "1", "yes"] else 0

    payload_data = {"input_data": [arguments]}
    payload = json.dumps(payload_data)
    print(f"--- Sending to AML endpoint: {payload}")

    try:
        response = requests.post(
            AML_ENDPOINT_URL, headers=headers, data=payload, timeout=30
        )
        response.raise_for_status()
        result = response.json()
        print(f"--- Received from AML endpoint: {result}")

        if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict):
            return result[0]
        elif isinstance(result, dict):
            return result
        else:
            return {
                "error": "Prediction model returned an unexpected result format.",
                "details": str(result),
            }

    except requests.exceptions.Timeout:
        print(f"--- ERROR calling AML endpoint: Timeout")
        return {
            "error": "Prediction model timed out.",
            "details": "The request took too long to complete.",
        }
    except requests.exceptions.HTTPError as e:
        print(f"--- ERROR calling AML endpoint: HTTPError {e.response.status_code}")
        error_detail = f"HTTP Error {e.response.status_code}."
        try:
            error_detail += f" Response: {e.response.text}"
        except Exception:
            pass
        return {"error": "Prediction model failed.", "details": error_detail}
    except requests.exceptions.RequestException as e:
        print(f"--- ERROR calling AML endpoint: RequestException {e}")
        return {"error": "Failed to connect to prediction model.", "details": str(e)}
    except json.JSONDecodeError:
        print(
            f"--- ERROR: Could not decode JSON response from AML endpoint: {response.text}"
        )
        return {
            "error": "Prediction model returned invalid data.",
            "details": "Non-JSON response received.",
        }


# --- Flask Routes ---
@app.route("/", methods=["GET", "POST"])
def chat():
    if "chat_history" not in session:
        # Simplified initial history
        session["chat_history"] = [
            {
                "role": "system",
                "content": "You are a helpful AI assistant interacting with a healthcare prediction model. Use the 'predict_patient_readmission' tool when appropriate.",
            },
            {"role": "assistant", "content": "Hello! How can I assist you today?"},
        ]

    if request.method == "POST":
        if request.form.get("clear"):
            session.pop("chat_history", None)
            return redirect(url_for("chat"))

        user_message_content = request.form.get("message")
        if user_message_content:
            session["chat_history"].append(
                {"role": "user", "content": user_message_content}
            )

            try:
                max_history_len = 20
                messages_to_send = session["chat_history"][-max_history_len:]

                # === First Call to Azure OpenAI ===
                print("--- Calling Azure OpenAI (Round 1) ---")
                response = client.chat.completions.create(
                    model=AOAI_DEPLOYMENT_NAME,
                    messages=messages_to_send,
                    tools=tools,
                    tool_choice="auto",
                )

                response_message = response.choices[0].message
                tool_calls = response_message.tool_calls

                if tool_calls:
                    print(
                        f"--- Tool call requested by LLM: {tool_calls[0].function.name} ---"
                    )
                    session["chat_history"].append(
                        response_message.model_dump(exclude_unset=True)
                    )

                    available_functions = {
                        "predict_patient_readmission": call_azure_ml_endpoint,
                    }
                    function_name = tool_calls[0].function.name
                    function_to_call = available_functions.get(function_name)

                    if function_to_call:
                        try:
                            function_args = json.loads(tool_calls[0].function.arguments)
                        except json.JSONDecodeError:
                            function_response = {
                                "error": f"Invalid arguments format from LLM for {function_name}.",
                                "details": tool_calls[0].function.arguments,
                            }
                            print(
                                f"--- ERROR parsing arguments: {tool_calls[0].function.arguments}"
                            )
                        else:
                            print(
                                f"--- Calling tool '{function_name}' with args: {function_args} ---"
                            )
                            function_response = function_to_call(function_args)
                        session["chat_history"].append(
                            {
                                "tool_call_id": tool_calls[0].id,
                                "role": "tool",
                                "name": function_name,
                                "content": json.dumps(function_response),
                            }
                        )
                        print("--- Calling Azure OpenAI (Round 2) with tool result ---")
                        messages_to_send = session["chat_history"][-max_history_len:]
                        second_response = client.chat.completions.create(
                            model=AOAI_DEPLOYMENT_NAME,
                            messages=messages_to_send,
                        )
                        final_message = second_response.choices[0].message
                        session["chat_history"].append(
                            final_message.model_dump(exclude_unset=True)
                        )

                    else:
                        print(
                            f"--- ERROR: LLM requested unknown tool: {function_name} ---"
                        )
                        session["chat_history"].append(
                            {
                                "role": "assistant",
                                "content": f"Sorry, I tried to use an unknown tool: {function_name}.",
                            }
                        )
                else:
                    print("--- Regular text response from LLM ---")
                    session["chat_history"].append(
                        response_message.model_dump(exclude_unset=True)
                    )

            except openai.APIConnectionError as e:
                print(f"--- ERROR connecting to Azure OpenAI: {e} ---")
                session["chat_history"].append(
                    {"role": "assistant", "content": "Error connecting to AI service."}
                )
            except openai.RateLimitError as e:
                print(f"--- ERROR Rate limit exceeded: {e} ---")
                session["chat_history"].append(
                    {
                        "role": "assistant",
                        "content": "AI service busy. Try again later.",
                    }
                )
            except openai.APIStatusError as e:
                print(
                    f"--- ERROR Azure OpenAI API error: {e.status_code} - {e.response} ---"
                )
                session["chat_history"].append(
                    {
                        "role": "assistant",
                        "content": f"AI service error (Code: {e.status_code}).",
                    }
                )
            except Exception as e:
                print(f"--- ERROR Unexpected error: {type(e).__name__} - {e} ---")
                session["chat_history"].append(
                    {
                        "role": "assistant",
                        "content": f"An unexpected error occurred: {type(e).__name__}",
                    }
                )

            session.modified = True
            return redirect(url_for("chat"))

    render_history = [
        msg for msg in session.get("chat_history", []) if msg.get("role") != "system"
    ]
    return render_template("chat.html", chat_history=render_history)


if __name__ == "__main__":
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_PORT", 5001))
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    app.run(host=host, port=port, debug=debug_mode)
