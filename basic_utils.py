from typing import Union
# Basic Utils
def test_tester():
  return True

DOCKER_IMAGE_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"

def clean_string(str: str, charseq: str) -> str:
  for char in str:
    if not char in charseq:
      str = str.replace(char, "")
  return str

def clean_docker_str(str: str) -> str:
  return clean_string(str, DOCKER_IMAGE_CHARS)

def file_loader(path: str) -> Union[str, None]:
  try:
    f = open(path, 'r')
    data = f.read()
    f.close()
    return data
  except FileNotFoundError:
    return None

def file_saver(path: str, data: str) -> bool:
  try:
    f = open(path, 'w')
    data = f.write(data)
    f.close()
    return False
  except Exception as e:
    print(f"Error saving file: {path}")
    return True
