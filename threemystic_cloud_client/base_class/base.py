from threemystic_common.base_class.base import base as main_base


class base(main_base): 
  """This is a library to help with the interaction with the cloud providers"""

  def __init__(self, logger_name, init_object = None, common = None,  logger = None, *args, **kwargs) -> None:
    self.__init_common(common= common)
    
    self.logger = self.get_common().helper_type().logging().get_child_logger(
      child_logger_name= logger_name,
      logger= logger if init_object is None else init_object.get_logger()
    )

  def __init_common(self, init_object = None, common = None, *args, **kwargs):
    if init_object is not None and hasattr(init_object, "get_common"):
      self._common = init_object.get_common()
      return

    if common is None:
      from threemystic_common.common import common as threemystic_common
      common = threemystic_common()
    
    self._common = common
  
  def get_common(self, *args, **kwargs):
    return self._common
  
  def get_logger(self, *args, **kwargs):
    return self.logger