# --- score.py changes ---
import joblib
import pandas as pd
import json
import os
import logging

pipeline = None  # Changed from 'model' to 'pipeline'


def init():
    global pipeline
    model_dir = os.getenv("AZUREML_MODEL_DIR", ".")
    pipeline_path = os.path.join(model_dir, "model.pkl")  # Path to the saved pipeline
    logging.info(f"Loading pipeline from: {pipeline_path}")
    try:
        pipeline = joblib.load(pipeline_path)  # Load the entire pipeline
        logging.info("Pipeline loaded successfully.")
    except Exception as e:
        logging.error(f"Error loading pipeline from {pipeline_path}: {str(e)}")
        raise RuntimeError(f"Failed to load pipeline: {e}")


def run(raw_data):
    global pipeline
    logging.info(f"Received request: {raw_data}")
    if not pipeline:
        return json.dumps({"error": "Pipeline failed to load."}), 500

    try:
        input_json = json.loads(raw_data)
        if "input_data" in input_json:
            data = input_json["input_data"]
        else:
            data = input_json  # Assume list of dicts or single dict

        # Create DataFrame directly from input data dictionary or list of dictionaries
        input_df = pd.DataFrame(data if isinstance(data, list) else [data])
        logging.info(f"Created DataFrame for prediction:\n{input_df.to_string()}")

        # PREDICTION using the pipeline (handles preprocessing automatically!)
        # Ensure the input_df has columns with the *original* feature names
        # The pipeline's preprocessor step expects columns like 'age', 'hypertension' etc.
        prediction_proba = pipeline.predict_proba(input_df)
        logging.info(f"Raw prediction probabilities: {prediction_proba}")

        # Extract probability for the positive class (readmission - usually index 1)
        # *** Verify index 1 based on pipeline.classes_ ***
        positive_class_index = 1  # Default assumption
        if hasattr(pipeline, "classes_"):
            # Find index corresponding to the positive class (e.g., 1 or 'yes')
            positive_class_label = (
                1  # Or 'Yes', 'Readmitted' - depends on your target encoding
            )
            try:
                positive_class_index = list(pipeline.classes_).index(
                    positive_class_label
                )
                logging.info(
                    f"Determined positive class index: {positive_class_index} for label {positive_class_label}"
                )
            except ValueError:
                logging.warning(
                    f"Positive class label '{positive_class_label}' not found in pipeline classes: {pipeline.classes_}. Defaulting to index 1."
                )
                positive_class_index = 1

        # Handle single vs multiple predictions if input was a list
        results = []
        for i in range(len(prediction_proba)):
            readmission_probability = prediction_proba[i, positive_class_index]
            results.append({"readmission_probability": float(readmission_probability)})

        logging.info(f"Formatted results: {results}")
        # Return single result if input was single dict, list otherwise
        return json.dumps(results[0] if not isinstance(data, list) else results)

    except Exception as e:
        logging.error(f"Error during run: {str(e)}", exc_info=True)
        return json.dumps({"error": f"Prediction error: {str(e)}"}), 500
