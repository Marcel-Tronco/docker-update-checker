import unittest
from docker_updater import test_tester, main, get_image_tags

class TestStringMethods(unittest.TestCase):

    def test_test(self):
      self.assertEqual(test_tester(), True)
    def test_main(self):
      main()
    def test_get_image_tags(self):
      # testing if escaping characters works
      taglist = get_image_tags("escaping chars works /?=)(/&", "asdf")
      self.assertEqual(len(taglist), 0)

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