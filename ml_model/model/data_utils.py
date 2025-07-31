from pathlib import Path
from typing import List
from ml_model.config.dynamic_config import DATASET_DIR
import pandas as pd


def load_dataset(file_name: str = None, full_path: str = None) -> pd.DataFrame:
    if file_name is None and full_path is None:
        raise ValueError("Either 'file_name' or 'full_path' must be provided.")

    # Determine the file path
    if full_path:
        file_path = Path(full_path)
    else:
        file_path = Path(DATASET_DIR) / file_name

    # Check if the file exists
    if not file_path.exists():
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    # Read the dataset
    try:
        df = pd.read_csv(file_path, sep=';')
    except pd.errors.EmptyDataError:
        raise ValueError(f"The file {file_path} is empty or cannot be read.")
    except pd.errors.ParserError:
        raise ValueError(f"Error parsing the file {file_path}. Check the file format.")
    except Exception as e:
        raise RuntimeError(f"An error occurred while reading the file {file_path}: {e}")

    return df


def load_wine_datasets_and_add_color_col(file_names: List[str]) -> List[pd.DataFrame]:
    dfs = []
    for name in file_names:
        df = load_dataset(name)

        # Add color column
        if 'red' in name:
            df['color'] = 'red'
        else:
            df['color'] = 'white'

        dfs.append(df)

    return dfs


# Custom function to format column names
def format_feature_names(input_string: str) -> str:
    # Split the string by whitespace and capitalize each word
    words = input_string.split()
    capitalized_words = [word[0].upper() + word[1:] for word in words]

    # Join the capitalized words without spaces
    formatted_string = ''.join(capitalized_words)

    return formatted_string


def clean_raw_data(df: pd.DataFrame) -> pd.DataFrame:
    """Gets rid of rows containing missing values and formats the feature names."""
    clean_df = df.copy()

    # Get rid of rows containing missing values
    clean_df.dropna(inplace=True)

    # Get rid of spaces in features in order to use pydantic schema for validation
    clean_df.columns = [format_feature_names(col) for col in clean_df.columns]

    return clean_df
