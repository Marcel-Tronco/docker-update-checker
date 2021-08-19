import unittest
from docker_updater import test_tester, main, get_image_tags, update_container

class TestStringMethods(unittest.TestCase):
    def test_test(self):
      self.assertEqual(test_tester(), True)
    def test_main(self):
      main()
    def test_get_image_tags(self):
      # for inexisting repo/image data json with empty results list is returned
      taglist = get_image_tags("inexisting_repo_asdf123", "asdf")
      self.assertEqual(len(taglist["results"]), 0)
      # exiiting repo/image works
      taglist = get_image_tags("library", "mongo")
      self.assertTrue(len(taglist["results"]) > 0)
    def test_update_container(self):
      # when no new data is available the result is equal to the input
      container = {
        "image_name": "string-gen",
        "repo": "dockercoursemk",
        "image_id": "sha256:2c9e87da2df22ee5b612e8c0fabd6c0961ef17c1a7c3ce4481115adf72940774",
        "tag": "4.1.0",
        "version_date": "2021-03-10T13:37:34.734372Z",
        "open_update": {
          "tag_updates": None,
          "new_tags": []
          }
      }
      result = update_container(container)
      self.assertEqual(result, container)

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