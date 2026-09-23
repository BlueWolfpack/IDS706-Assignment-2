"""Run the Agrofood CO2 emissions analysis."""

from pathlib import Path

import matplotlib.pyplot as plt

import fxns_for_ACE as fxn


DATA_PATH = Path(__file__).with_name("Agrofood_co2_emission.csv")


def main(data_path=DATA_PATH):
    """Run data loading, transformation, modeling, and visualization."""
    ace = fxn.load_data(data_path)
    ace = fxn.preprocess_data(ace)

    fire_data = fxn.create_fire_features(ace)
    population_data = fxn.create_population_features(ace)

    results = fxn.train_and_evaluate_models(ace)
    best_models = fxn.select_best_models(results)

    print("Best models by area and predictor:")
    print(best_models.head(30))
    print("\nBest models sorted by R2:")
    print(best_models.sort_values('R2', ascending=False).head(30))

    fxn.plot_fire_emissions(fire_data, 'United States of America')
    plt.show()

    fxn.plot_fire_emissions(fire_data, 'Greece')
    plt.show()

    fxn.plot_population_ratio(population_data)
    plt.show()


if __name__ == '__main__':
    main()
