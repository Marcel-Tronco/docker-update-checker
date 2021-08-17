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

def clean_string(str: str) -> str:
  not_implemented_yet("clean_string")
  return str

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
  def dts_to_datetime(cls, time_string: str) -> datetime.datetime:
    return datetime.datetime.strptime(time_string, DockerTimeString.DOCKER_TIME_FORMAT)
  def __new__(cls, docker_time_obj: Union[str, datetime.datetime]):
    if type(docker_time_obj) == str:
      return str.__new__(cls, cls.datetime_to_dts(cls.dts_to_datetime(docker_time_obj)))
    elif type(docker_time_obj) == cls:
      return str(docker_time_obj)
    else: # type(docker_time_obj) == datetime.datetime:
      return str.__new__(cls, cls.datetime_to_dts(docker_time_obj))
  def __lt__(self, other):
    return self.dts_to_datetime(self) < self.dts_to_datetime(other)
  def __eq__(self, other):
    return self.dts_to_datetime(self) == self.dts_to_datetime(other)
  def __le__(self, other):
    return not other.__lt__(self)
  def __ne__(self, other):
    return not self.__eq__(other)
  def __gt__(self, other):
    return other.__lt__(self)
  def __ge__(self, other):
    return other.__le__(self)

# IO

def load_running_containers() -> dict:
  # todo the loading
  not_implemented_yet("load_running_containers")
  return {
    "dockercoursemk/string-gen": {
      "image_name": "string-gen",
      "repo": "dockercoursemk",
      "image_id": "sha256:asdf68b48edc06ed8cbb006422a386fdeef8436a151170f470031b97d3d6e5db",
      "tag": "3.2.6",
      "architecture": "amd64",
      "version_date": DockerTimeString("2021-01-20T21:13:48.648135Z"),
      "open_update": {
        "tag_update": None,
        "new_tags": {}
        }
    }
  }

def save_container_data(updated_containers: List[dict]) -> None:
  # todo
  not_implemented_yet("save_container_data")
  return

## whats with selfmade/local images? Can I check the Images they build upon?

# container discovery
def container_discovery(containers: dict) -> dict:
  # todo
  not_implemented_yet("container_discovery")
  return {}

# update logic

def get_image_tags(repo: str, image: str, next: Union[ None, str ] = None, page: int = 1) -> dict:
  url = f"https://hub.docker.com/v2/repositories/{clean_string(repo)}/{clean_string(image)}/tags?page_size=100&page={clean_string(str(page))}"
  if next != None:
    url = next
  r = requests.get(url)
  json = r.json()
  return json

def image_tag_parser(image_tag_results: dict) -> dict:
  parsed_image_tag_results = {}
  for result in image_tag_results:
    parsed_image_tag_results[result["name"]] = result
  return parsed_image_tag_results

def taglist_dict_creator_translator(image_tag_results: List[dict]) -> dict:
  lookup_dict = {}
  for i in range(len(image_tag_results)):
    lookup_dict[image_tag_results[i]["name"]] = i
  return lookup_dict

def check_update(old_container_or_tag_data: dict, new_tag_data: dict) -> Union[dict, None]:
  last_container_update = DockerTimeString(old_container_or_tag_data["version_date"])
  last_image_update = None
  for image in new_tag_data["images"]:
    if image[architecture] == old_container_or_tag_data[architecture]:
      last_image_update =  DockerTimeString(image["last_pushed"])
      break
  if not last_image_update: ## check ""== none" for DTS Objects
    return None
  elif last_image_update > last_container_update:
    return last_image_update
  else:
    return None

def get_tag_update(container_data: dict, image_tags: List[dict]) -> Union[dict, None]:
  for tag_data in image_tags["results"]:
    if container_data["tag"] == tag_data["name"]:
      tag_update_data = check_update(container_data, tag_data)
      return tag_update_data
  return None

def get_tag_data(tag_name: str, image_tags: dict) -> Union[dict, None]:
  for tag in image_tags["results"]:
    if tag["name"] == tag_name:
      return tag
  return None

def get_arch_image(target_arch: str, image_list: List[dict]) -> Union[dict, None]:
  for image in image_list:
    if target_arch == image[architecture]:
      return image
  return None

def get_new_tags(container_data: dict, image_tags: List[dict]) -> Tuple[Union[dict, None], bool]:
  updated_tag_data = {}
  got_relevant_tags = False
  # first update all present tags in the container data or erase them
  for tag_name, version_date in container_data["open_update"]["new_tags"].items():
    # if tags disappear on docker hub/ if theres, no push data they will be erased here too
    try:
      image_list = get_tag_data(tag_name, image_tags)["images"]
      arch_image = get_arch_image(container_data[architecture], image_list)
      updated_tag_data[tag_name] = max(version_date, DockerTimeString(arch_image["last_pushed"])) # in case last_pushed is None max() throws error        
    except (KeyError, TypeError): # in case the tag_name isn't present
      pass
  # then look if there are new ones.
  existing_tags_set = updated_tag_data.keys()
  for tag in image_tags["results"]:
    try:
      tag_name = tag["name"]
      if tag_name in existing_tags_set:
        continue
      image_list = tag["images"]
      arch_image = get_arch_image(container_data[architecture], image_list)
      tag_date = DockerTimeString(arch_image["last_pushed"]) # Throws Type error if 
      if( tag_date > container_data["version_date"]): 
          updated_tag_data[tag_name] = tag_date
      if container_data["version_date"] > DockerTimeString(tag["tag_last_pushed"]):
        got_relevant_tags = True
    except TypeError:
      # Trigered by DTS creator.
      # if we reached a point where no push dates are given, we stop looking for older ones
      got_relevant_tags = True
    except (KeyError):
      pass
  return updated_tag_data, got_relevant_tags

def update_container(container: dict) -> dict:
  current_tag_done = False
  new_tags_done = False
  new_tags = {}
  tag_update = None
  image_tags = {
    "next" : None
    }
  while True:
    try:
      image_tags = get_image_tags(container["repo"], container["image_name"], image_tags["next"])
      # image_tags["results"] = image_tag_parser(image_tags["results"])
    except Exception:
      raise DockerApiError ## from None
    if not current_tag_done:
      tag_update = get_tag_update(container, image_tags)
      if tag_update:
        current_tag_done = True
    if not new_tags_done:
      tmp, new_tags_done = get_new_tags(container, image_tags)
      if tmp:
        new_tags.update(tmp)
    next_image_tag_url = image_tags["next"]
    if (new_tags_done and current_tag_done) or next_image_tag_url == None:
      break

  updates = {
    "tag_update": tag_update,
    "new_tags": new_tags
    }
  return updates

def dif_parser(old_containers: dict, updates: dict) -> List[dict]:
  dif = []
  for image_name, u in updates.items():
    container_dif = {
      "any_update": False,
      "tag_update": None,
      "new_tags": []
      }
    if not u["tag_update"]:
      pass
    elif ( 
      not old_containers[image_name]["open_update"]["tag_update"] or
      u["tag_update"] != old_containers[image_name]["open_update"]["tag_update"]
      ):
      container_dif["image_name"] = image_name
      container_dif["any_update"] = True
      container_dif["tag_update"] = u["tag_update"]
    for tag_name, version_date in u["new_tags"].items():
      try:
        if version_date > old_containers[image_name]["open_update"]["new_tags"][tag_name]:
          container_dif["image_name"] = image_name
          container_dif["any_update"] = True
          container_dif["new_tags"] += (tag_name, version_date) 
      except KeyError:
        container_dif["image_name"] = image_name
        container_dif["any_update"] = True
        container_dif["new_tags"] += [(tag_name, version_date)]

    dif += [container_dif]
  return dif

def create_info(dif_list: List[dict]) -> Union[str, None]:
  # todo
  not_implemented_yet("create_info")
  info = ""
  for dif in dif_list:
    if not dif["any_update"]:
      return None
    else:
      info += f"Updates for {dif['image_name']}:\n"
      if dif["tag_update"]:
        info += f"\nTag update: new version from {dif['tag_update']}.\n"
      if len(dif["new_tags"]) > 0:
        info += "\nNew Tags:\n"
        for tuple in dif["new_tags"]:

          info += f"\n- {tuple[0]}:   {tuple[1]}"
  return info

def gather_update_info(old_containers: dict, updated_containers: dict) -> str:
  dif = dif_parser(old_containers, updated_containers)
  info = create_info(dif)
  return info

# notification logic

def send_info(info: str) -> None:
  # todo
  not_implemented_yet("send_info")
  return



def main():
  containers = load_running_containers()
  newly_discovered_containers = container_discovery(containers)
  containers.update(newly_discovered_containers)
  updated_containers = {}
  for name, container in containers.items():
    updated_container = update_container(container)
    updated_containers.update({name: updated_container})
  info = gather_update_info(containers, updated_containers)
  send_info(info)
  print(info)
  save_container_data(updated_containers)
  print(f"open-todos: {open_todos}")

if __name__ == "__main__":
  main()