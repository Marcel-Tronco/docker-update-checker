from jsonschema import validate

CONTAINERS_SCHEMA = {
  "type": "object",
  "additionalProperties": {
    "type": "object",
    "properties": {
      "is_local": {"type": "boolean"},
      "image_name": {"type": "string"},
      "repo": {"type": ["null", "string"]},
      "image_id": {"type": "string"},
      "tag": {"type": ["null", "string"]},
      "architecture": {"type": "string"}, 
      "version_date": {"type": "string"}, 
      "open_update": {
        "type": "object",
        "properties": {
          "tag_update": {"type": ["string", "null"]},
          "new_tags": {
            "type": "object",
            "additionalProperties": {
              "type": "string"
            }
          }
        },
        "required": ["tag_update", "new_tags"]
      }
    },
    "required": ["is_local", "image_name", "repo", "image_id", "tag", "architecture", "version_date", "open_update"]
  }
}

IMAGETAGS_DH_SCHEMA = {
  "type": "object",
  "properties": {
    "count": {"type": "integer"},
    "next": {"type": ["string", "null"]},
    "previous": {"type": ["string", "null"] },
    "results": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "creator": {"type": ["null", "integer"]},
          "id": {"type": ["null", "integer"]},
          "image_id": {"type": ["string", "null"]},
          "images": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "architecture": {"type": "string"},
                "features": {},
                "digest": {"type": "string"},
                "os": {},
                "os_features": {},
                "os_version": {},
                "variant": {},
                "size": {},
                "status": {},
                "last_pulled": {"type": ["string", "null"]},
                "last_pushed": {"type": ["string", "null"]}
              },
              "additionalProperties": False,
              "minProperties": 11
            }
          },
          "last_updated": {"type": ["string", "null"]},
          "last_updater": {"type": ["null", "integer"]},
          "last_updater_username": {"type": ["string", "null"]},
          "name": {"type": ["string", "null"]},
          "repository": {"type": "integer"},
          "full_size": {"type": "integer"},
          "v2": {"type": "boolean"},
          "tag_status": {},
          "tag_last_pulled": {"type": ["string", "null"]},
          "tag_last_pushed": {"type": ["string", "null"]}
        },
        "additionalProperties": False,
        "minProperties": 14
      }
    }
  },
  "additionalProperties": False,
  "minProperties": 4
}
def containers(dict: dict) -> None:
  validate(dict, CONTAINERS_SCHEMA)
  return None

def dh_imagetags(dict: dict) -> None:
  validate(dict, IMAGETAGS_DH_SCHEMA)