import requests
import urllib.parse
import datetime
import dateutil.parser as parser
import docker
from typing import List

class DockerApiError(Exception):
  def __init__(self):
    super().__init__("failed to retrieve tag data from docker hub")

def test_tester():
  return True

url_quote = urllib.parse.quote
open_todos = 0

def send_info(info: str) -> None:
  # todo
  not_implemented_yet("send_info")
  return

def not_implemented_yet(function_name: str) -> None:
  print(f"{function_name} not implemented yet ¯\_(ツ)_/¯")
  global open_todos
  open_todos += 1
  return

def clean_string(str: str) -> str:
  not_implemented_yet("clean_string")
  return str

def get_image_tags(repo: str, image: str, page: int = 1) -> List[dict]:

  url = f"https://hub.docker.com/v2/repositories/{clean_string(repo)}/{clean_string(image)}/tags?page_size=1&page={page}"
  print(url)
  r = requests.get(url)
  json = r.json()
  return json["results"]
  # todo: - handling for multipage cases

def load_running_containers() -> List[dict]:
  # todo the loading
  return [{
    "image_name": "string-gen",
    "repo": "dockercoursemk",
    "image_id": "sha256:2c9e87da2df22ee5b612e8c0fabd6c0961ef17c1a7c3ce4481115adf72940774",
    "tag": "4.1.0",
    "version_date": "2021-03-10T13:37:34.734372Z",
    "open_update": None
  }]

def save_container_data(updated_containers: List[dict]) -> None:
  # todo
  not_implemented_yet("save_container_data")
  return

def check_image(container_data: List[dict], image_tags: List[dict]) -> None:
  # todo
  not_implemented_yet("check_image")
  return

def update_container(container: dict) -> dict:
  # todo
  not_implemented_yet("update_container")
  try:
    image_tags = get_image_tags(container["repo"], container["image_name"])
    update_necessary = check_image(container, image_tags)
    if update_necessary == None:
      return container
    else:
      container["open_update"] = update_necessary()
  except Exception:
    raise DockerApiError #from None

def gather_update_info(old_containers: List[dict], updated_containers: List[dict]) -> str:
  # todo
  not_implemented_yet("gather_update_info")
  return

def send_info(info: str) -> None:
  # todo
  not_implemented_yet("send_info")
  return

def main():
  containers = load_running_containers()
  updated_containers = []
  for container in containers:
    updated_container = update_container(container)
    updated_containers.append(updated_container)
  info = gather_update_info(containers, updated_containers)
  send_info(info)
  save_container_data(updated_containers)
  print(f"open-todos: {open_todos}")

if __name__ == "__main__": 
  main()