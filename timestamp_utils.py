import datetime
from typing import Union

class DockerTimeString(str):
  DOCKER_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'
  @classmethod
  def datetime_to_dts(cls, datetime: datetime.datetime) -> str:
    return datetime.strftime(DockerTimeString.DOCKER_TIME_FORMAT)
  @classmethod
  def dts_to_datetime(cls, time_string: str) -> datetime.datetime:
    time_string = time_string.rstrip("Z")
    end_index = 26 if len(time_string) >= 26 else None
    time_string = time_string[0:end_index]
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