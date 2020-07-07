#!/usr/bin/env python

import unittest
import weather

class Test_Weather(unittest.TestCase):
    """Main Unit Test class for Weather"""

    def test_grace_exit(self):
        """Ensure the grace_exit function works as expected"""
        self.assertEqual(1, 1)

    def test_debug(self):
        """Test the debug function is printing output if the WEATHER_DEBUG ENV var is set"""

if __name__ == "__main__":
    unittest.main()
