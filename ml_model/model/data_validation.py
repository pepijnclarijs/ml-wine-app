import pandas as pd
from pydantic import BaseModel, ValidationError
from typing import List, Optional, Tuple
from ml_model.model.data_utils import clean_raw_data, load_wine_datasets_and_add_color_col


def validate_data(input_df: pd.DataFrame) -> Tuple[pd.DataFrame, Optional[dict]]:
    """Validates if the input data follows the right schema"""

    # Convert df to list of dicts. Each element represents a row.
    records = input_df.to_dict(orient="records")
    validated_df = pd.DataFrame()
    try:
        # Convert the validated dataframe into WineDataInputSchema to validate its schema.
        validated_records = [WineDataInputSchema(**record) for record in records]
        schema = WineDataBatchInputSchema(inputs=validated_records)
        validated_df = convert_schema_to_dataframe(schema)
        errors = None
    except ValidationError as error:
        errors = error.json()

    return validated_df, errors


class WineDataInputSchema(BaseModel):
    FixedAcidity: float
    VolatileAcidity: float
    CitricAcid: float
    ResidualSugar: float
    Chlorides: float
    FreeSulfurDioxide: float
    TotalSulfurDioxide: float
    Density: float
    PH: float
    Sulphates: float
    Alcohol: float
    Quality: int
    Color: str  # Added to dataset


class WineDataBatchInputSchema(BaseModel):
    inputs: List[WineDataInputSchema]


# Extract data and convert to DataFrame
def convert_schema_to_dataframe(batch_schema: WineDataBatchInputSchema) -> pd.DataFrame:
    """
    This function converts a WineDataBatchInputSchema into a pandas DataFrame. This ensures that the data used by
    the model follows the right schema.
    """

    # Convert schema to list of dictionaries
    data = [item.dict() for item in batch_schema.inputs]

    # Create DataFrame
    df = pd.DataFrame(data)

    return df


def process_user_input(input_data: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    input_data = clean_raw_data(input_data)
    valid_data, errors = validate_data(input_data)

    return valid_data, errors


def combine_clean_and_validate_wine_datasets(file_names: List[str]) -> Tuple[pd.DataFrame, dict]:
    """
    Combines the white and red wine datasets, gets rid of rows containing missing values and formats the feature
    names. Please note that since there are no missing values in the training data, I have opted to remove all rows
    containing missing data.
    """
    dfs = load_wine_datasets_and_add_color_col(file_names)
    combined_df = pd.concat(dfs, ignore_index=True)
    clean_df = clean_raw_data(combined_df)
    valid_data, errors = validate_data(clean_df)

    return valid_data, errors
