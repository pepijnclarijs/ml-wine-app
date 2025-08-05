import logging
import os
import pandas as pd
import threading
from dataclasses import dataclass
from typing import Union
from ml_model.config.dynamic_config import config
from ml_model import __version__ as package_version
from ml_model.model.data_utils import clean_raw_data, load_dataset
from ml_model.model.data_validation import validate_data
from ml_model.model.model_utils import load_pipeline


logging.basicConfig(level=logging.INFO)


def predict(input_data: Union[pd.DataFrame, dict]) -> dict:
    """Make prediction using a saved ML model given input data."""

    logging.info("converting input data into pd dataframe...")
    # Convert input data to dataframe
    if not isinstance(input_data, pd.DataFrame):
        input_data = pd.DataFrame(input_data)
    logging.info("converting input data into pd dataframe -- DONE")

    # Make predictions
    logging.info("loading the pipeline...")
    pipeline = load_pipeline()
    logging.info("loading the pipeline -- DONE")
    logging.info("Making predictions...")
    predictions = pipeline.predict(
        X=input_data[config.ml_model_config.features]
    )
    logging.info("Making predictions -- DONE")

    results = {
        "predictions": predictions.tolist(),
        "version": package_version,
    }

    return results


@dataclass
class TaskContext:
    """Object containing information related to a task initiated by the API user."""
    task_id: str
    status_lock: threading.Lock
    processing_status: dict
    task_results: dict
    task_results_lock: threading.Lock
    temp_file_name: str


def handle_context_errors(context: TaskContext, errors: dict) -> dict:
    with context.status_lock:
        context.processing_status[context.task_id] = f"failed: {str(errors)}"
    with context.task_results_lock:
        context.task_results[context.task_id] = {"status": "failed", "error": str(errors)}

    return {"errors": errors}


def make_predictions(context: TaskContext, valid_data: pd.DataFrame) -> dict:
    results = predict(valid_data)
    logging.info(f"Results gathered for task {context.task_id}")
    with context.status_lock:
        context.processing_status[context.task_id] = "completed"
    with context.task_results_lock:
        context.task_results[context.task_id] = results

    return results


def clean_validate_and_predict(context: TaskContext, file_path: str) -> dict:
    # Gather data
    input_data = load_dataset(full_path=file_path)
    cleaned_data = clean_raw_data(input_data)
    valid_data, errors = validate_data(cleaned_data)

    if errors:
        return handle_context_errors(context, errors)

    logging.info(f"Input data valid for task {context.task_id}. Making predictions.")
    results = make_predictions(context, valid_data)
    logging.info(f"predictions made! {results}")

    # Ensure temporary file is deleted
    if os.path.exists(file_path):
        os.remove(file_path)

    return results
