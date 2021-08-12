import requests
import urllib.parse
import datetime
import dateutil.parser as parser

url_quote = urllib.parse.quote
open_todos = 0

def send_info(info):
  # todo
  not_implemented_yet("send_info")
  return

def not_implemented_yet(function_name):
  print(f"{function_name} not implemented yet ¯\_(ツ)_/¯")
  global open_todos
  open_todos += 1
  return

def get_image_tags(repo, image, page="1"):
  url = f"https://hub.docker.com/v2/repositories/{url_quote(repo)}/{url_quote(image)}/tags?page_size=1&page={page}"
  r = requests.get(url)
  return r.json()
  # todo: - modify the error message here to make clear what happened if the api doesn't work
  #       - handling for multipage cases

def load_running_containers():
  # todo the loading
  return [{
    "image": "string-gen",
    "repo": "dockercoursemk",
    "digest": "sha256:2c9e87da2df22ee5b612e8c0fabd6c0961ef17c1a7c3ce4481115adf72940774",
    "tag": "4.1.0",
    "version_date": "2021-03-10T13:37:34.734372Z",
    "open_update": None
  }]

def save_container_data(updated_containers):
  # todo
  not_implemented_yet("sace_container_data")
  return

def check_image(container_data, image_tags):
  # todo
  not_implemented_yet("check_image")
  return

def update_container(container):
  # todo
  not_implemented_yet("update_container")
  try:
    image_tags = get_image_tags(container["repo"], container["image"])
    update_necessary = check_image(container, image_tags)
    if update_necessary == None:
      return container
    else:
      container["open_update"] = update_necessary()

  except Exception as e:
    print(e)

def gather_update_info(old_containers, updated_containers):
  # todo
  not_implemented_yet("gather_update_info")
  return

def send_info(info):
  # todo
  not_implemented_yet("send_info")
  return

def __main__():
  containers = load_running_containers()
  updated_containers = []
  for container in containers:
    updated_container = update_container(container)
    updated_containers.append(updated_container)
  info = gather_update_info(containers, updated_containers)
  send_info(info)
  save_container_data(updated_containers)
  print(f"open-todos: {open_todos}")


__main__()