import unittest
import pandas as pd
import numpy as np
import datetime
from helpers import get_room_number_optimized
from pandas._testing import assert_frame_equal

class Test_get_room_number_optimized(unittest.TestCase):
    
    def test_standard(self):
        """
        Values used during development
        """
        r1 = pd.DataFrame({'start': [datetime.datetime(2020, 8, 10), datetime.datetime(2020, 9, 22)], 
                           'end': [datetime.datetime(2020, 9, 3), datetime.datetime(2022, 12, 31)]})
        r2 = pd.DataFrame({'start': [datetime.datetime(2020, 7, 12), datetime.datetime(2020, 8, 2), datetime.datetime(2020, 10, 3)], 
                           'end': [datetime.datetime(2020, 7, 18), datetime.datetime(2020, 8, 30), datetime.datetime(2022, 12, 31)]})
        r3 = pd.DataFrame({'start': [datetime.datetime(2020, 8, 15)], 
                           'end': [datetime.datetime(2022, 12, 31)]})
        
        r1 = r1.set_index(r1['start']).rename(columns={"end": "1"}).drop('start', axis=1)
        r2 = r2.set_index(r2['start']).rename(columns={"end": "2"}).drop('start', axis=1)
        r3 = r3.set_index(r3['start']).rename(columns={"end": "3"}).drop('start', axis=1)
        
        data = pd.concat([r1, r2, r3], axis = 1, sort=False)

        start = datetime.datetime(2020, 8, 22)
        end = datetime.datetime(2020, 8, 28)
        result = get_room_number_optimized(data, start, end)
        answer = pd.DataFrame({'room': ['2', '1', '3'], 'order': [2, 6, 7]})
        # Ignore index values
        # np.array_equal(result.values,answer.values)
        assert_frame_equal(result.reset_index(drop=True), answer.reset_index(drop=True))

    def test_all_same_value(self):
        """
        Allow multiple same value
        """
        r1 = pd.DataFrame({'start': [datetime.datetime(2020, 8, 7), datetime.datetime(2020, 8, 20)], 
                           'end': [datetime.datetime(2020, 8, 12), datetime.datetime(2022, 12, 31)]})
        r2 = pd.DataFrame({'start': [datetime.datetime(2020, 8, 7), datetime.datetime(2020, 8, 20)], 
                           'end': [datetime.datetime(2020, 8, 12), datetime.datetime(2022, 12, 31)]})
        r3 = pd.DataFrame({'start': [datetime.datetime(2020, 8, 7), datetime.datetime(2020, 8, 20)], 
                           'end': [datetime.datetime(2020, 8, 12), datetime.datetime(2022, 12, 31)]})
        
        r1 = r1.set_index(r1['start']).rename(columns={"end": "1"}).drop('start', axis=1)
        r2 = r2.set_index(r2['start']).rename(columns={"end": "2"}).drop('start', axis=1)
        r3 = r3.set_index(r3['start']).rename(columns={"end": "3"}).drop('start', axis=1)
        
        data = pd.concat([r1, r2, r3], axis = 1, sort=False)
        start = datetime.datetime(2020, 8, 22)
        end = datetime.datetime(2020, 8, 28)
        result = get_room_number_optimized(data, start, end)
        answer = pd.DataFrame({'room': ['1', '2', '3'], 'order': [2, 2, 2]})

        assert_frame_equal(result.reset_index(drop=True), answer.reset_index(drop=True))


    def test_one_value(self):
        """
        One unique value each, 2/3 rooms returns
        """
        r1 = pd.DataFrame({'start': [datetime.datetime(2020, 8, 7)], 
                           'end': [datetime.datetime(2022, 12, 31)]})
        r2 = pd.DataFrame({'start': [datetime.datetime(2020, 10, 9)], 
                           'end': [datetime.datetime(2022, 12, 31)]})
        r3 = pd.DataFrame({'start': [datetime.datetime(2020, 6, 5)], 
                           'end': [datetime.datetime(2022, 12, 31)]})
        
        r1 = r1.set_index(r1['start']).rename(columns={"end": "1"}).drop('start', axis=1)
        r2 = r2.set_index(r2['start']).rename(columns={"end": "2"}).drop('start', axis=1)
        r3 = r3.set_index(r3['start']).rename(columns={"end": "3"}).drop('start', axis=1)
        
        data = pd.concat([r1, r2, r3], axis = 1, sort=False)
        start = datetime.datetime(2020, 8, 22)
        end = datetime.datetime(2020, 8, 28)
        result = get_room_number_optimized(data, start, end)
        answer = pd.DataFrame({'room': ['1', '3'], 'order': [15, 78]})
        
        assert_frame_equal(result.reset_index(drop=True), answer.reset_index(drop=True))

    def test_no_rooms(self):
        """
        No rooms found!
        """
        r1 = pd.DataFrame({'start': [datetime.datetime(2020, 8, 7), datetime.datetime(2020, 8, 20)], 
                           'end': [datetime.datetime(2020, 8, 12), datetime.datetime(2022, 12, 31)]})
        r2 = pd.DataFrame({'start': [datetime.datetime(2020, 8, 7), datetime.datetime(2020, 8, 20)], 
                           'end': [datetime.datetime(2020, 8, 12), datetime.datetime(2022, 12, 31)]})
        r3 = pd.DataFrame({'start': [datetime.datetime(2020, 8, 7), datetime.datetime(2020, 8, 20)], 
                           'end': [datetime.datetime(2020, 8, 12), datetime.datetime(2022, 12, 31)]})
        
        r1 = r1.set_index(r1['start']).rename(columns={"end": "1"}).drop('start', axis=1)
        r2 = r2.set_index(r2['start']).rename(columns={"end": "2"}).drop('start', axis=1)
        r3 = r3.set_index(r3['start']).rename(columns={"end": "3"}).drop('start', axis=1)
        
        data = pd.concat([r1, r2, r3], axis = 1, sort=False)
        start = datetime.datetime(2020, 8, 10)
        end = datetime.datetime(2020, 8, 28)
        result = get_room_number_optimized(data, start, end)
        
        self.assertTrue(result.empty)


    def test_one(self):
        """
        All start values valid, only one end value valid, 1/3 rooms returns
        """
        r1 = pd.DataFrame({'start': [datetime.datetime(2020, 7, 7)], 
                           'end': [datetime.datetime(2020, 7, 31)]})
        r2 = pd.DataFrame({'start': [datetime.datetime(2020, 6, 9)], 
                           'end': [datetime.datetime(2020, 6, 30)]})
        r3 = pd.DataFrame({'start': [datetime.datetime(2020, 8, 5)], 
                           'end': [datetime.datetime(2020, 8, 31)]})
        
        r1 = r1.set_index(r1['start']).rename(columns={"end": "1"}).drop('start', axis=1)
        r2 = r2.set_index(r2['start']).rename(columns={"end": "2"}).drop('start', axis=1)
        r3 = r3.set_index(r3['start']).rename(columns={"end": "3"}).drop('start', axis=1)
        
        data = pd.concat([r1, r2, r3], axis = 1, sort=False)
        start = datetime.datetime(2020, 8, 22)
        end = datetime.datetime(2020, 8, 28)
        result = get_room_number_optimized(data, start, end)
        answer = pd.DataFrame({'room': ['3'], 'order': [3]})
        
        assert_frame_equal(result.reset_index(drop=True), answer.reset_index(drop=True))


if __name__ == '__main__':
    unittest.main()
