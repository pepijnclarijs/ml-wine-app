""" 
This file contains the logic for loading, parsing, and validating the configuration data. Pydantics 
BaseModel is used to define the structure and validate the structure of the configuration data.
"""

from pathlib import Path
from pydantic import BaseModel
from strictyaml import YAML, load
from typing import List, Optional, Sequence
import ml_model


# Project Directories
PACKAGE_ROOT = Path(ml_model.__file__).resolve().parent
ROOT = PACKAGE_ROOT.parent
STATIC_CONFIG_FILE_PATH = PACKAGE_ROOT / "config" / "static_config.yml"
DATASET_DIR = ROOT / "datasets"
TRAINED_MODEL_DIR = PACKAGE_ROOT / "trained_models"


class AppConfig(BaseModel):
    """
    Application-level config.
    """

    package_name: str
    training_data_file_names: List[str]
    pipeline_save_file: str


class MLModelConfig(BaseModel):
    """
    Configuration relevant to model training and feature engineering.
    """

    target: str
    features: List[str]
    categorical_vars: Sequence[str]
    numerical_vars: Sequence[str]
    test_size: float
    random_state: int
    n_estimators: int


class Config(BaseModel):
    """Class containing configurations for the application as well as the ML model."""

    app_config: AppConfig
    ml_model_config: MLModelConfig


def validate_static_config_file_path() -> Path:
    if STATIC_CONFIG_FILE_PATH.is_file():
        return STATIC_CONFIG_FILE_PATH
    raise Exception(f"No file found at {STATIC_CONFIG_FILE_PATH!r}")


def get_config_from_yaml(cfg_path: Optional[Path] = None) -> YAML:
    """Get the static configurations from the YAML config file."""

    if not cfg_path:
        cfg_path = validate_static_config_file_path()

    if cfg_path:
        with open(cfg_path, "r") as conf_file:
            parsed_config = load(conf_file.read())
            return parsed_config

    raise OSError(f"Did not find config file at path: {cfg_path}")


def create_and_validate_config(parsed_config: YAML = None) -> Config:
    """Run validation on config values."""
    if parsed_config is None:
        parsed_config = get_config_from_yaml()

    # specify the data attribute from the strictyaml YAML type.
    cfg = Config(
        app_config=AppConfig(**parsed_config.data),
        ml_model_config=MLModelConfig(**parsed_config.data),
    )

    return cfg


config = create_and_validate_config()
