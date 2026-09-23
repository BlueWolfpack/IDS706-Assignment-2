"""Reusable functions for the Agrofood CO2 emissions analysis."""

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import PolynomialFeatures


def workingfxns():
    """Return a short confirmation that the module imported successfully."""
    return "fxns_for_ACE is working"


def load_data(file_path):
    """Load the Agrofood CO2 emissions CSV into a dataframe."""
    return pd.read_csv(os.path.expanduser(file_path))


def preprocess_data(dataframe):
    """Copy the data and convert all non-area columns to numeric values."""
    cleaned_data = dataframe.copy()
    numeric_columns = cleaned_data.columns.difference(['Area'])
    cleaned_data[numeric_columns] = cleaned_data[numeric_columns].apply(
        pd.to_numeric,
        errors='coerce'
    )
    return cleaned_data


def new_df(og_df, col_list, new_col):
    """
    This function takes in a dataframe, a list of columns to keep, and a new column name. 
    It returns a new dataframe with only the specified columns and a new column with NONE type.
    
    Parameters:
    og_df (pd.DataFrame): The original dataframe
    col_list (list): A list of columns to keep
    new_col (str): The name of the new column
    new_df (str): The name of the new dataframe to be returned
    
    Returns:
    pd.DataFrame: A new dataframe with only the specified columns and a new column that is the sum of the specified columns
    """
    new_df = og_df[col_list].copy()
    new_df[new_col] = None
    return new_df


def add_columns(og_df, df, col1, col2, sum_col):
    """
    This function takes in a dataframe and two column names. It adds the values in the two columns together and adds them to a new column in the dataframe.
    
    Parameters:
    og_df (pd.DataFrame): The original dataframe
    df (pd.DataFrame): The dataframe to add the columns to
    col1 (str): The name of the first column to add
    col2 (str): The name of the second column to add
    sum_col (str): The name of the new column to add the sum to
    
    Returns:
    pd.DataFrame: The original dataframe with the new column added
    """
    result = df.copy()
    result[sum_col] = og_df[col1] + og_df[col2]
    return result


def create_fire_features(dataframe):
    """Create fire and emissions features for the forest-fire analysis."""
    columns = ['Area', 'Year', 'total_emission', 'Forestland']
    fire_data = dataframe[columns].copy()
    fire_data['total_fires'] = (
        dataframe['Forest fires']
        + dataframe['Fires in humid tropical forests']
    )
    return fire_data


def create_population_features(dataframe):
    """Create total population and urban-to-rural ratio features."""
    population_data = dataframe[
        ['Area', 'Year', 'total_emission']
    ].copy()
    population_data['total_population'] = (
        dataframe['Total Population - Male']
        + dataframe['Total Population - Female']
    )
    population_data['urban_to_rural'] = (
        dataframe['Urban population'] / dataframe['Rural population']
    )
    return population_data


def train_and_evaluate_models(dataframe, target='total_emission'):
    """Train four regressors for each area and predictor, returning metrics."""
    results = []
    predictor_columns = dataframe.columns[2:31]

    for area, area_data in dataframe.groupby('Area'):
        for column in predictor_columns:
            if column == target:
                continue

            model_data = (
                area_data[[column, target]]
                .apply(pd.to_numeric, errors='coerce')
                .dropna()
                .sort_index()
            )

            if len(model_data) < 8 or model_data[column].nunique() < 2:
                continue

            split_index = int(len(model_data) * 0.8)
            if split_index == len(model_data):
                continue

            X = model_data[[column]]
            y = model_data[target]
            X_train, X_test = X.iloc[:split_index], X.iloc[split_index:]
            y_train, y_test = y.iloc[:split_index], y.iloc[split_index:]
            models = {
                'linear': LinearRegression(),
                'polynomial_degree_2': make_pipeline(
                    PolynomialFeatures(degree=2),
                    LinearRegression()
                ),
                'polynomial_degree_3': make_pipeline(
                    PolynomialFeatures(degree=3),
                    LinearRegression()
                ),
                'random_forest': RandomForestRegressor(
                    n_estimators=200,
                    random_state=42,
                    min_samples_leaf=2
                )
            }

            for model_name, model in models.items():
                model.fit(X_train, y_train)
                predictions = model.predict(X_test)
                results.append({
                    'Area': area,
                    'predictor': column,
                    'model': model_name,
                    'MAE': mean_absolute_error(y_test, predictions),
                    'RMSE': np.sqrt(mean_squared_error(y_test, predictions)),
                    'R2': r2_score(y_test, predictions)
                })

    return pd.DataFrame(results)


def select_best_models(results_dataframe):
    """Select the lowest-RMSE model for each area and predictor."""
    return (
        results_dataframe
        .sort_values(['Area', 'predictor', 'RMSE'])
        .groupby(['Area', 'predictor'])
        .first()
        .reset_index()
    )


def plot_fire_emissions(fire_data, area):
    """Plot total fires and total emissions for one area."""
    area_data = fire_data[fire_data['Area'] == area]
    axis = area_data.plot(
        x='Year',
        y='total_fires',
        color='blue',
        label='total_fires'
    )
    area_data.plot(
        x='Year',
        y='total_emission',
        color='red',
        label='total_emission',
        ax=axis,
        secondary_y=True
    )
    axis.set_ylabel('Total Fires')
    axis.right_ax.set_ylabel('Total Emission')
    axis.set_xlabel('Year')
    return axis


def plot_population_ratio(population_data, max_ratio=200):
    """Plot a hexbin visualization of population ratio and emissions."""
    filtered_data = population_data[
        population_data['urban_to_rural'] < max_ratio
    ]
    figure, axis = plt.subplots(figsize=(8, 6))
    plot = axis.hexbin(
        filtered_data['urban_to_rural'],
        filtered_data['total_emission'],
        gridsize=35,
        bins='log',
        mincnt=1,
        cmap='viridis'
    )
    figure.colorbar(plot, ax=axis, label='Observation density')
    axis.set_xlabel(f'Urban-to-rural population ratio < {max_ratio}')
    axis.set_ylabel('Total emissions')
    axis.set_title('Density of Urban-to-Rural Ratio vs. Total Emissions')
    return figure, axis

