import unittest
from logger import Logger
from unittest.mock import patch, mock_open

class TestMain(unittest.TestCase):

    @patch('builtins.open', new_callable=mock_open, read_data="data")
    def test_init(self, mock_open):
        filename = 'test'
        expected_filepath = 'logs/test.log'
        expected_data = 'data'
        logger = Logger(filename)
        mock_open.assert_called_with()

if __name__ == '__main__':
    unittest.main()