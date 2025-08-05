"""This file builds the Pipeline object. This object takes care of cleaning the training data, feature engineering and
training the model, all in one go."""
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from feature_engine.imputation import CategoricalImputer, MeanMedianImputer
from sklearn.preprocessing import StandardScaler
from ml_model.config.dynamic_config import config


wine_pipeline = Pipeline(
    [
        # --- IMPUTATION --- #
        # NOTE: This is not needed for this specific project. Added for demonstrating purposes only. Below code will not
        # have any effect.
        (
            "missing_imputation",
            CategoricalImputer(
                imputation_method="missing",
                variables=config.ml_model_config.categorical_vars
            ),
        ),
        # One could add a missing indicator like this. Not needed in this project though as there are no missing values
        # in the training dataset.
        # (
        #     "missing_indicator",
        #     AddMissingIndicator(variables=config.model_config.numerical_vars),
        # ),
        # impute numerical variables with the mean. Not needed in this project though as there are no missing values
        # in the training dataset. Below code will not have any effect.
        (
            "mean_imputation",
            MeanMedianImputer(
                imputation_method="mean",
                variables=config.ml_model_config.numerical_vars
            ),
        ),

        # --- Categorical encoding --- #
        # encode categorical variables using the target mean
        (
            "onehot_encoder",
            ColumnTransformer(
                transformers=[
                    ("cat", OneHotEncoder(drop='first', handle_unknown='ignore'),
                     config.ml_model_config.categorical_vars)
                ],
                remainder='passthrough'  # This will leave the other variables unchanged
            ),
        ),

        # --- Scaling --- #
        ('scaler', StandardScaler()),

        # --- Classification --- #
        ('classifier', RandomForestClassifier(n_estimators=config.ml_model_config.n_estimators,
                                              random_state=config.ml_model_config.random_state))

    ]
)

