from sklearn.model_selection import train_test_split
from ml_model.config.dynamic_config import config
from ml_model.model.data_validation import combine_clean_and_validate_wine_datasets
from ml_model.model.model_utils import save_pipeline
from ml_model.model.pipeline import wine_pipeline


def run_training() -> None:
    """Train the model."""
    # Get and clean training data
    training_df, errors = combine_clean_and_validate_wine_datasets(config.app_config.training_data_file_names)

    if errors is None:
        # divide train and test
        X_train, X_test, y_train, y_test = train_test_split(
            training_df[config.ml_model_config.features],
            training_df[config.ml_model_config.target],
            test_size=config.ml_model_config.test_size,
            # Set random seed for reproducibility
            random_state=config.ml_model_config.random_state,
        )

        # fit model
        wine_pipeline.fit(X_train, y_train)

        # persist trained model
        save_pipeline(pipeline=wine_pipeline)
    else:
        raise ValueError(f"An error occurred during the validation of the training data: {errors}")


if __name__ == "__main__":
    run_training()
