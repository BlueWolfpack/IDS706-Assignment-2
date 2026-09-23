import fxns_for_ACE as fxn
import pandas as pd
import unittest
import importlib
importlib.reload(fxn)

class TestNewDf(unittest.TestCase):
    def test_new_df(self):
        '''Test the new_df function from fxns_for_ACE.py'''
        # Create a sample dataframe
        test_df = pd.read_csv("test.csv")
        # Call the new_df function
        result_df = fxn.new_df(test_df, ['Letters', 'Integers'], 'D')

        # Check if the new dataframe has the correct columns
        self.assertEqual(list(result_df.columns), ['Letters', 'Integers', 'D'])

        # Check if the new column is filled with None
        self.assertTrue(all(result_df['D'].isnull()))

    def test_add_columns(self):
        '''Test the add_columns function from fxns_for_ACE.py'''
        # Create a sample dataframe
        test_df = pd.read_csv("test.csv")
        # Call the add_columns function
        result_df = fxn.add_columns(test_df, test_df.copy(), 'Integers', 'Floats', 'Sum')

        # Check if the new column is added
        self.assertIn('Sum', result_df.columns)

        # Check if the new column has the correct values
        expected_sum = test_df['Integers'] + test_df['Floats']
        pd.testing.assert_series_equal(result_df['Sum'],expected_sum,check_names=False)

    def test_create_fire_features(self):
        '''Test the create_fire_features function from fxns_for_ACE.py'''
        # Create a sample dataframe
        test_df = pd.read_csv("test_fire.csv")
        # Call the create_fire_features function
        result_df = fxn.create_fire_features(test_df)

        # Check if the new column is added
        self.assertIn('total_fires', result_df.columns)

        # Check if the new column has the correct values
        expected_fires = test_df['Forest fires'] + test_df['Fires in humid tropical forests']
        pd.testing.assert_series_equal(result_df['total_fires'], expected_fires, check_names=False)

    def test_train_and_evaluate_models(self):
        '''Test the train_and_evaluate_models function from fxns_for_ACE.py'''
        # Create a sample dataframe
        test_df = pd.read_csv("Japan_Agrofood_co2_emission.csv")
        # Call the train_and_evaluate_models function
        results = fxn.train_and_evaluate_models(test_df)
        # Check if the result is a dataframs
        self.assertIsInstance(results, pd.DataFrame)
        self.assertTrue(len(results) > 0)
        # Verify that the expected columns are present in the results dataframe
        self.assertIn('model', results.columns)
        self.assertIn('MAE', results.columns)
        self.assertIn('RMSE', results.columns)
        self.assertIn('R2', results.columns)
        # Check that the models in the results dataframe are as expected
        expected_models = {
            'linear',
            'polynomial_degree_2',
            'polynomial_degree_3',
            'random_forest'
        }
        self.assertTrue(expected_models.issubset(set(results['model'])))

if __name__ == '__main__':
    unittest.main()