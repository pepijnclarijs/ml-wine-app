from ml_model.model.data_utils import load_dataset
import pytest
import pandas as pd
import os
import tempfile

# Sample datasets for testing
sample_red_data = pd.DataFrame({
    'fixed acidity': [7.4, 7.8],
    'volatile acidity': [0.7, 0.88],
    'citric acid': [0, 0.1]
})

sample_white_data = pd.DataFrame({
    'fixed acidity': [6.3, 6.2],
    'volatile acidity': [0.3, 0.3],
    'citric acid': [0.2, 0.2]
})


@pytest.fixture
def temp_files():
    """Fixture to create temporary CSV files for testing."""
    # Create temporary files
    red_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='w', newline='')
    white_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv', mode='w', newline='')

    try:
        # Write sample datasets to temporary CSV files
        sample_red_data.to_csv(red_file.name, sep=';', index=False)
        sample_white_data.to_csv(white_file.name, sep=';', index=False)

        # Close the files, so they can be used by other processes
        red_file.close()
        white_file.close()

        # Provide file paths to the test functions
        yield red_file.name, white_file.name

    finally:
        # Ensure temporary files are cleaned up
        os.remove(red_file.name)
        os.remove(white_file.name)


def test_load_dataset(temp_files):
    red_file_path, white_file_path = temp_files

    # Run the function
    df_red = load_dataset(full_path=red_file_path)
    df_white = load_dataset(full_path=white_file_path)

    # Perform assertions on df_combined to ensure it is as expected
    assert df_red.shape[0] == 2  # Check the number of rows
    assert df_white.shape[0] == 2
    assert 'fixed acidity' in df_red.columns  # Ensure the 'color' column is present
    assert 'fixed acidity' in df_white.columns  # Ensure the 'color' column is present


