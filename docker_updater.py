import requests
import urllib.parse
import datetime
import dateutil.parser as parser
import docker
from typing import List, Type, Union, Tuple


# Errors

class DockerApiError(Exception):
  def __init__(self):
    super().__init__("failed to retrieve tag data from docker hub")

# Basic Utils
def test_tester():
  return True


def not_implemented_yet(function_name: str) -> None:
  print(f"{function_name} not implemented yet ¯\_(ツ)_/¯")
  global open_todos
  open_todos += 1
  return

url_quote = urllib.parse.quote
open_todos = 0
architecture = "architecture"



# timestamp utils

class DockerTimeString(str):
  DOCKER_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'
  @classmethod
  def datetime_to_dts(cls, datetime: datetime.datetime) -> str:
    return datetime.strftime(DockerTimeString.DOCKER_TIME_FORMAT)
  @classmethod
  def time_string_parser(cls, time_string: str) -> datetime.datetime:
    return datetime.datetime.strptime(time_string, DockerTimeString.DOCKER_TIME_FORMAT)
  def __new__(cls, docker_time_obj: Union[str, datetime.datetime]):
    if type(docker_time_obj) == str:
      return str.__new__(cls, cls.datetime_to_dts(cls.time_string_parser(docker_time_obj)))
    elif type(docker_time_obj) == cls:
      return str(docker_time_obj)
    else: # type(docker_time_obj) == datetime.datetime:
      return str.__new__(cls, cls.datetime_to_dts(docker_time_obj))
#   Must throw error in case no data is provided...    
#    else:
#      return str.__new__(cls, cls.datetime_to_dts(datetime.datetime.now()))
  def __lt__(self, other):
    return self.time_string_parser(self) < self.time_string_parser(other)
  def __eq__(self, other):
    return self.time_string_parser(self) == self.time_string_parser(other)
  def __le__(self, other):
    return not other.__lt__(self)
  def __ne__(self, other):
    return not self.__eq__(other)
  def __gt__(self, other):
    return other.__lt__(self)
  def __ge__(self, other):
    return other.__le__(self)


def send_info(info: str) -> None:
  # todo
  not_implemented_yet("send_info")
  return

def clean_string(str: str) -> str:
  not_implemented_yet("clean_string")
  return str

def get_image_tags(repo: str, image: str, next: Union[ None, str ] = None, page: int = 1) -> dict:
  url = f"https://hub.docker.com/v2/repositories/{clean_string(repo)}/{clean_string(image)}/tags?page_size=100&page={clean_string(str(page))}"
  if next != None:
    url = next
  r = requests.get(url)
  json = r.json()
  return json

def load_running_containers() -> List[dict]:
  # todo the loading
  return [{
    "image_name": "string-gen",
    "repo": "dockercoursemk",
    "image_id": "sha256:2c9e87da2df22ee5b612e8c0fabd6c0961ef17c1a7c3ce4481115adf72940774",
    "tag": "4.1.0",
    "architecture": "amd64",
    "version_date": DockerTimeString("2021-03-10T13:37:34.734372Z"),
    "open_update": {
      "tag_updates": None,
      "new_tags": {}
      }
  }]

def save_container_data(updated_containers: List[dict]) -> None:
  # todo
  not_implemented_yet("save_container_data")
  return

def get_tag_data(tag_name: str, image_tags) -> Union[dict, None]:
  for tag in image_tags["results"]:
    if tag["name"] == tag_name:
      return tag
  return None

def check_update(old_container_or_tag_data: dict, new_tag_data: dict) -> Union[dict, None]:
  last_container_update = DockerTimeString(old_container_or_tag_data["version_date"])
  for image in new_tag_data:
    if image[architecture] == old_container_or_tag_data[architecture]:
      last_image_update =  DockerTimeString(image["last_pushed"])
      break
  if not last_image_update: ## check ""== none" for DTS Objects
    return last_container_update
  else:
    return max(last_container_update, last_image_update)

def get_tag_updates(container_data: dict, image_tags: dict) -> Union[dict, None]:
  try:
    tag_data = image_tags["result"][container_data["tag"]]
  except KeyError:
    return None
  tag_update_data = check_update(container_data, tag_data)
  return tag_update_data

def get_arch_image(target_arch: str, image_list: List[dict]) -> Union[dict, None]:
  for image in image_list:
    if target_arch == image_list[architecture]:
      return image
  return None

def get_new_tags(container_data: dict, parsed_image_tags: dict) -> Tuple[Union[dict, None], bool]:
  updated_tag_data = {}
  got_relevant_tags = False
  # first update all present tags in the container data or erase them
  for tag_name, version_date in container_data["open_update"]["new_tags"].items():
    # if tags disappear on docker hub/ if theres, no push data they will be erased here too
    try:
      image_list = parsed_image_tags[tag_name]["images"]
      arch_image = get_arch_image(container_data[architecture], image_list)
      updated_tag_data[tag_name] = max(version_date, DockerTimeString(arch_image["last_pushed"])) # in case last_pushed is None max() throws error        
    except (KeyError, TypeError): # in case the tag_name isn't present
      pass
  # then look if there are new ones.
  existing_tags_set = updated_tag_data.keys()
  for tag_name, tag in parsed_image_tags.items():
    try:
      image_list = tag["images"]
      arch_image = get_arch_image(container_data[architecture], image_list)
      tag_date = DockerTimeString(arch_image["last_pushed"]) # Throws Type error if 
      if ( not tag_name in existing_tags_set):
        if( tag_date > container_data["version_date"]): 
          updated_tag_data[tag_name] = tag_date
      if container_data["version_date"] > DockerTimeString(tag["tag_last_pushed"]):
        got_relevant_tags = True
    except TypeError:
      # if we reached a point where no push dates are given, we stop looking for older ones
      got_relevant_tags = True
    except (KeyError):
      pass
  return updated_tag_data, got_relevant_tags

def image_tag_parser(image_tag_results: dict) -> dict:
  parsed_image_tag_results = {}
  for result in image_tag_results:
    parsed_image_tag_results[result["name"]] = result
  return parsed_image_tag_results

def update_container(container: dict) -> dict:
  current_tag_done = False
  new_tags_done = False
  new_tags = []
  tag_updates = None
  image_tags = {
    "next" : None
  }

  while True:
    try:
      image_tags = get_image_tags(container["repo"], container["image_name"], image_tags["next"])
      image_tags["results"] = image_tag_parser(image_tags["results"])
    except Exception:
      raise DockerApiError ## from None
    if not current_tag_done:
      tag_updates = get_tag_updates(container, image_tags)
      if tag_updates:
        current_tag_done = True
    if not new_tags_done:
      tmp, new_tags_done = get_new_tags(container, image_tags)
      if tmp:
        new_tags += tmp
    next_image_tag_url = image_tags["next"]
    if (new_tags_done and current_tag_done) or next_image_tag_url == None:
      break
  container["open_update"] = {
    "tag_updates": tag_updates,
    "new_tags": new_tags
  }
  return container


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