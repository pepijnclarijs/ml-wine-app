import os
import joblib
from sklearn.pipeline import Pipeline
from ml_model.config.dynamic_config import config, TRAINED_MODEL_DIR
from ml_model import __version__ as package_version


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

    # Save the new pipeline
    joblib.dump(pipeline, file_path)
    print(f"Pipeline saved as {file_name} in {save_dir}")


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

    # Check if the file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Pipeline file {file_path} does not exist.")

    # Load the pipeline
    pipeline = joblib.load(file_path)
    print(f"Pipeline loaded from {file_path}")

    return pipeline
