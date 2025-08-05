import logging
import os
import joblib
from sklearn.pipeline import Pipeline
from ml_model.config.dynamic_config import config, TRAINED_MODEL_DIR
from ml_model import __version__ as package_version
from azure.storage.blob import BlobServiceClient
from pathlib import Path


def upload_to_blob(file_path: Path, container_name: str) -> None:
    """Upload a file to Azure Blob Storage."""

    connect_str = config.secrets.ml_models_storage_connection_string
    if not connect_str:
        raise ValueError("Azure Storage connection string not found in environment variables.")

    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_path.name)

    with open(file_path, "rb") as data:
        blob_client.upload_blob(data, overwrite=True)

    logging.info(f"Uploaded model to Azure Blob Storage: {container_name}/{file_path.name}")

def save_pipeline(pipeline: Pipeline):
    """
    Save the fitted pipeline to a directory specified in the configuration file.

    Parameters:
    - pipeline: The fitted pipeline object to save.

    The function will check if a pipeline file already exists in the directory.
    If it does, the existing file will be replaced with the new pipeline.
    """

    # Fetch the directory from the configuration
    file_name = config.app_config.pipeline_save_file + '_' + package_version + '.pkl'
    file_path = TRAINED_MODEL_DIR / file_name
    save_dir = file_path.parent

    # Check if there is already a pipeline file in the directory
    if os.path.exists(save_dir):
        for file in os.listdir(save_dir):
            if file.endswith(".pkl"):
                # Remove the existing pipeline file
                os.remove(os.path.join(save_dir, file))

    # Save the new pipeline locally
    joblib.dump(pipeline, file_path)
    logging.info(f"Pipeline saved as {file_name} in {save_dir}")

    # Save the pipeline in a blob container
    try:
        upload_to_blob(file_path, container_name="ml-models")
    except Exception as e:
        logging.error(f"Failed to upload model to blob storage: {e}")


def download_model_if_missing(model_path: Path) -> None:
    if model_path.exists():
        return

    logging.info("Model not found locally. Downloading from blob storage...")

    blob_service_client = BlobServiceClient.from_connection_string(
        config.secrets.ml_models_storage_connection_string
    )
    container_client = blob_service_client.get_container_client("ml-models")
    blob_client = container_client.get_blob_client(model_path.name)

    # Ensure the directory exists before saving
    model_path.parent.mkdir(parents=True, exist_ok=True)

    with open(model_path, "wb") as f:
        blob_data = blob_client.download_blob()
        content = blob_data.readall()
        logging.info(f"Downloaded blob content size: {len(content)} bytes")
        f.write(content)
        f.flush()
        os.fsync(f.fileno())  # Make sure everything is flushed to disk

    logging.info("Model downloaded.")


def load_pipeline() -> Pipeline:
    """
    Load a fitted pipeline from a directory specified in the configuration file.

    The function will look for a pipeline file with the version suffix in the directory.
    If the file does not exist, an exception will be raised.

    Returns:
    - The loaded pipeline object.
    """

    # Fetch the directory and file name from the configuration
    file_name = config.app_config.pipeline_save_file + '_' + package_version + '.pkl'
    file_path = TRAINED_MODEL_DIR / file_name

    download_model_if_missing(file_path)

    # Load the pipeline
    logging.info("Loading model from the given filepath...")
    pipeline = joblib.load(file_path)
    logging.info(f"Pipeline loaded from {file_path}")

    return pipeline
