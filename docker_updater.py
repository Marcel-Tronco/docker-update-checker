import requests, datetime, docker, os, json
from typing import List, Union, Tuple
import js_validate
from basic_utils import test_tester, clean_docker_str, file_saver, file_loader
from timestamp_utils import DockerTimeString
from infosender import send_info


class DockerApiError(Exception):
  def __init__(self):
    super().__init__("failed to retrieve tag data from docker hub")

# IO

PATH = os.getcwd() + "/data"
DATA_PATH = PATH + "/container_data.json"

def load_running_containers() -> Tuple[dict, bool]:
  data = file_loader(DATA_PATH)
  if not data:
    return {}, False
  else:
    try:
      containers = json.loads(data) 
      js_validate.containers(containers)
      return containers, False
    except Exception as e:
      print(f"JSONError: {e} \n\ncontinuing with no loaded containers.")
      return {}, True

def save_container_data(updated_containers: dict) -> None:
  converted_data = json.dumps(updated_containers)
  saving_succeeded = file_saver(DATA_PATH, converted_data)
  return saving_succeeded


# container discovery

def image_name_splitter(full_image_name: str) -> Tuple[str, str, str]:
  try:
    tag_sep_index = full_image_name.index(":")
    tag = full_image_name[tag_sep_index + 1:]
    full_image_name = full_image_name[0:tag_sep_index]
  except ValueError:
    tag = ""
  try:
    repo_sep_index = full_image_name.index("/")
    repo = full_image_name[0:repo_sep_index]
    full_image_name = full_image_name[repo_sep_index + 1 :]
  except ValueError:
    repo = ""
  image_name = full_image_name
  return (repo, image_name, tag)

def get_full_image_name(container: dict) -> str:
  full_name = container["repo"] + "/" if container["repo"] else ""
  full_name += container["image_name"]
  full_name += ":" + container["tag"] if container["tag"] else ""
  return full_name

def container_discovery(containers: dict) -> dict:
  new_containers = {}
  client = docker.from_env()
  d_containers = client.containers.list(all=True)
  for c in d_containers:
    parsed_c_data = {}
    c_data = c.attrs
    id = c_data["Id"]

    # move to next container if the container is already in the list
    try:
      if containers[id]:
        continue
    except KeyError:
      pass

    tmp_image = client.images.get(c_data["Image"]).attrs
    parsed_c_data["version_date"] = DockerTimeString(tmp_image["Created"])
    parsed_c_data["architecture"] = tmp_image["Architecture"]
    parsed_c_data["is_local"] = len(tmp_image["RepoDigests"]) == 0
    parsed_full_image_name = image_name_splitter(c_data["Config"]["Image"])

    parsed_c_data["image_name"] = parsed_full_image_name[1]
    if not parsed_c_data["is_local"]:
      parsed_c_data["repo"] = parsed_full_image_name[0] if parsed_full_image_name[0] != "" else "library"
    else:
      parsed_c_data["repo"] = ""
    parsed_c_data["tag"] = parsed_full_image_name[2]
    parsed_c_data["image_id"] = c_data["Image"]
  
    parsed_c_data["open_update"] = {
      "tag_update": None,
      "new_tags": {}
    }
    new_containers[id] = parsed_c_data

  return new_containers

# update logic

def get_image_tags(repo: str, image: str, next: Union[ None, str ] = None, page: int = 1) -> dict:
  url = f"https://hub.docker.com/v2/repositories/{clean_docker_str(repo)}/{clean_docker_str(image)}/tags?page_size=100&page={clean_docker_str(str(page))}"
  if next != None:
    url = next
  r = requests.get(url)
  json = r.json()
  try:
    js_validate.dh_imagetags(json)
  except Exception as e:
    print(e)
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

def check_tag_update(old_container_or_tag_data: dict, new_tag_data: dict) -> Union[dict, None]:
  last_container_update = DockerTimeString(old_container_or_tag_data["version_date"])
  last_image_update = None
  for image in new_tag_data["images"]:
    if image["architecture"] == old_container_or_tag_data["architecture"]:
      last_image_update =  DockerTimeString(image["last_pushed"])
      break
  if not last_image_update: ## check ""== none" for DTS Objects
    return None
  elif DockerTimeString(last_image_update) > DockerTimeString(last_container_update):
    return last_image_update
  else:
    return None

def get_tag_update(container_data: dict, image_tags: List[dict]) -> Union[dict, None]:
  for tag_data in image_tags["results"]:
    if container_data["tag"] == tag_data["name"]:
      tag_update_data = check_tag_update(container_data, tag_data)
      return tag_update_data
  return None

def get_tag_data(tag_name: str, image_tags: dict) -> Union[dict, None]:
  for tag in image_tags["results"]:
    if tag["name"] == tag_name:
      return tag
  return None

def get_arch_image(target_arch: str, image_list: List[dict]) -> Union[dict, None]:
  for image in image_list:
    if target_arch == image["architecture"]:
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
      arch_image = get_arch_image(container_data["architecture"], image_list)
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
      arch_image = get_arch_image(container_data["architecture"], image_list)
      tag_date = DockerTimeString(arch_image["last_pushed"]) # Throws Type error if 
      if( DockerTimeString(tag_date) > DockerTimeString(container_data["version_date"])): 
          updated_tag_data[tag_name] = tag_date
      if DockerTimeString(container_data["version_date"]) > DockerTimeString(tag["tag_last_pushed"]):
        got_relevant_tags = True
    except (TypeError, AttributeError):
      # Trigered by DTS creator.
      # if we reached a point where no push dates are given, we stop looking for older ones
      got_relevant_tags = True
    except (KeyError):
      pass
  return updated_tag_data, got_relevant_tags

def get_container_update(container: dict) -> dict:
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
  for container_name, u in updates.items():
    image_name = get_full_image_name(old_containers[container_name])
    container_dif = {
      "any_update": False,
      "tag_update": None,
      "new_tags": []
      }
    if not u["tag_update"]:
      pass
    elif ( 
      not old_containers[container_name]["open_update"]["tag_update"] or
      DockerTimeString(u["tag_update"]) != DockerTimeString(old_containers[container_name]["open_update"]["tag_update"])
      ):
      container_dif["container_name"] = container_name
      container_dif["image_name"] = image_name
      container_dif["any_update"] = True
      container_dif["tag_update"] = u["tag_update"]
    for tag_name, version_date in u["new_tags"].items():
      try:
        if DockerTimeString(version_date) > DockerTimeString(old_containers[container_name]["open_update"]["new_tags"][tag_name]):
          container_dif["container_name"] = container_name
          container_dif["image_name"] = image_name
          container_dif["any_update"] = True
          container_dif["new_tags"] += (tag_name, version_date) 
      except KeyError:
        container_dif["container_name"] = container_name
        container_dif["image_name"] = image_name
        container_dif["any_update"] = True
        container_dif["new_tags"] += [(tag_name, version_date)]

    dif += [container_dif] if container_dif["any_update"] else []
  return dif

def create_info(dif_list: List[dict]) -> Union[str, None]:
  info = ""
  for dif in dif_list:
    if not dif["any_update"]:
      continue
    else:
      info += f"Updates for {dif['image_name']} ({dif['container_name']}):\n"
      if dif["tag_update"]:
        info += f"\nTag update: new version from {dif['tag_update']}.\n"
      if len(dif["new_tags"]) > 0:
        info += "\nNew Tags:\n"
        for tuple in dif["new_tags"]:

          info += f"\n- {tuple[0]}:   {tuple[1]}"
    info += "\n-----------------------------\n"
  return info

def main():
  errors = []
  print(f"\n##################################################\n\nDocker-Updater run at: {datetime.datetime.now()} ")

  # Load Containers
  containers, io_loading_error = load_running_containers()
  if io_loading_error:
    errors += ["io_loading_error"]
  
  # Discover newly launched/changed containers and remove deleted ones
  newly_discovered_containers = container_discovery(containers)
  containers.update(newly_discovered_containers)
  container_updates = {}

  # Get Updates
  for name, container in containers.items():
    if container["is_local"]:
      continue
    try:
      container_update = get_container_update(container)
      container_updates.update({name: container_update})
    except DockerApiError as e:
      print(e)
      errors += ["DockerApiError"]
      container_updates.update({name: container["open_update"]})

  #Get dif
  dif = dif_parser(containers, container_updates)
  # Create info message
  info = create_info(dif)

  # Save updates
  for update in dif:
    new_tags = {}
    for tag_name, date in update["new_tags"]:
      new_tags[tag_name] = date
    containers[update["container_name"]].update({
      "open_update": {
        "tag_update": update["tag_update"],
        "new_tags": new_tags
      }
      })
  io_saving_error = save_container_data(containers)
  if io_saving_error:
    errors += ["io_saving_error"]

  # add errors to info
  if errors:
    info += "\nErrors:\n"
    for error in errors:
      info += error + " "
  
  # send info
  if info:
    print(info)
    send_info(info)
  else:  
    print("no updates.")

if __name__ == "__main__":
  main()