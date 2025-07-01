# 1. Import necessary libraries
from azure.ai.ml import MLClient
from azure.ai.ml.entities import (
    ManagedOnlineEndpoint,
    ManagedOnlineDeployment,
    Model,
    Environment,
    CodeConfiguration,
)
from azure.identity import DefaultAzureCredential
import datetime

# 2. Configure workspace details and connect
try:
    credential = DefaultAzureCredential()
    # Check if given credential can get token successfully.
    credential.get_token("https://management.azure.com/.default")
except Exception as ex:
    # Fall back to InteractiveBrowserCredential in case DefaultAzureCredential not work
    # This will open a browser page for you to authenticate.
    print(f"DefaultAzureCredential failed: {ex}. Falling back to InteractiveBrowserCredential.")
    from azure.identity import InteractiveBrowserCredential
    credential = InteractiveBrowserCredential()

# --- Replace with your workspace details ---
subscription_id = ""
resource_group = ""
workspace = ""
# -----------------------------------------

# Get a handle to the workspace
ml_client = MLClient(credential, subscription_id, resource_group, workspace)


# 3. Register your model (assuming you have a model file)
# --- Replace with your model details ---
model_name = "HealthEvals1.0" # Choose a name for your model in Azure ML
model_local_path = "code/Evals/data/csv" # Path to the folder containing your model file(s)
# -----------------------------------------

print(f"Registering model '{model_name}' from path '{model_local_path}'...")
# If your model includes multiple files, point 'path' to the folder.
# Azure ML will automatically detect the main model file if it's standard (like .pkl)
# or you might need to specify 'type' (e.g., AssetTypes.MLFLOW_MODEL, AssetTypes.TRITON_MODEL)
model = Model(
    path=model_local_path,
    name=model_name,
    description="Chat model registered via Python SDK.",
    # type=AssetTypes.CUSTOM_MODEL # Specify type if needed, e.g. MLFLOW_MODEL, TRITON_MODEL
)
registered_model = ml_client.models.create_or_update(model)
print(f"Model registered: {registered_model.name} version {registered_model.version}")


# 4. Define the Environment
# You can use a curated environment or define your own.
# Using a curated environment (example):
# --- Choose a suitable curated environment ---
env_name = "AzureML-ACPT-pytorch-1.13-py38-cuda11.7-gpu" # Example, find suitable ones in Azure ML Studio
# -----------------------------------------
print(f"Using curated environment: {env_name}")
deployment_environment = ml_client.environments.get(name=env_name, version="latest") # Or specify a version

# Or, define a custom environment (example using a conda file):
# --- Replace with your environment details if custom ---
# custom_env_name = "your-chat-model-env"
# conda_file_path = "path/to/your/conda_env.yml"
# docker_image = "mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04" # Example base image
# -----------------------------------------
# deployment_environment = Environment(
#     name=custom_env_name,
#     description="Custom environment for the chat model.",
#     conda_file=conda_file_path,
#     image=docker_image
# )
# deployment_environment = ml_client.environments.create_or_update(deployment_environment)
# print(f"Custom environment created: {deployment_environment.name} version {deployment_environment.version}")


# 5. Create an Online Endpoint
endpoint_name = "chat-endpoint-" + datetime.datetime.now().strftime("%m%d%H%M%f")
print(f"Creating endpoint: {endpoint_name}...")

endpoint = ManagedOnlineEndpoint(
    name=endpoint_name,
    description="Online endpoint for chat model.",
    auth_mode="key", # Or "aml_token"
    # tags={'purpose': 'chat_demo'} # Optional tags
)

# This command starts endpoint creation and returns while it continues.
endpoint_job = ml_client.online_endpoints.begin_create_or_update(endpoint)
endpoint_job.wait() # Wait for endpoint creation to complete
print(f"Endpoint '{endpoint_name}' created successfully.")


# 6. Create a Deployment for the model under the endpoint
deployment_name = "blue" # Deployment name, e.g., 'blue', 'green', or a version name
print(f"Creating deployment '{deployment_name}' for endpoint '{endpoint_name}'...")

# --- Define code configuration if needed (scoring script) ---
# This tells Azure ML how to use your model. You'll likely need a scoring script.
# Create a file (e.g., score.py) in a 'src' directory.
# score_script_path = "src/score.py" # Path to your scoring script
# code_folder_path = "src"          # Path to the folder containing the script
# ------------------------------------------------------------
# code_config = CodeConfiguration(
#     code=code_folder_path,
#     scoring_script=score_script_path,
# )

# --- Adjust instance type and count as needed ---
instance_type = "Standard_DS3_v2" # Example instance type
instance_count = 1
# ---------------------------------------------

deployment = ManagedOnlineDeployment(
    name=deployment_name,
    endpoint_name=endpoint_name,
    model=registered_model, # Use the registered model object
    environment=deployment_environment, # Use the environment object
    # code_configuration=code_config, # Uncomment if using a scoring script
    instance_type=instance_type,
    instance_count=instance_count,
)

# This command starts deployment creation and returns while it continues.
deployment_job = ml_client.online_deployments.begin_create_or_update(deployment)
deployment_job.wait() # Wait for deployment creation to complete
print(f"Deployment '{deployment_name}' created successfully.")

# Optionally, set traffic allocation if this is the main deployment
endpoint.traffic = {deployment_name: 100}
ml_client.online_endpoints.begin_create_or_update(endpoint).wait()
print(f"Traffic set for deployment '{deployment_name}'.")

# 7. Get Endpoint Details for Interaction
endpoint = ml_client.online_endpoints.get(name=endpoint_name)
print(f"\nEndpoint '{endpoint.name}' provisioning state: {endpoint.provisioning_state}")
print(f"Scoring URI: {endpoint.scoring_uri}")

# Get the keys for authentication
endpoint_keys = ml_client.online_endpoints.get_keys(name=endpoint_name)
primary_key = endpoint_keys.primary_key
print(f"Primary Key: {primary_key}") # Keep this key secure!