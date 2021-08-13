import unittest
from docker_updater import test_tester, main

class TestStringMethods(unittest.TestCase):

    def test_test(self):
      self.assertEqual(test_tester(), True)
    def test_main(self):
      main()

'''
    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)
'''

if __name__ == '__main__':
    unittest.main()