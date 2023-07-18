import os
from abc import abstractmethod
from threemystic_cloud_client.cloud_providers.aws.base_class.base import cloud_client_provider_aws_base as base


class cloud_client_aws_client_base(base):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self._set_profile(*args, **kwargs)
  
  @abstractmethod
  def _session_expired(self, refresh = False, *args, **kwargs):
    pass

  @abstractmethod
  def _load_base_configs(self):
    pass
  
  @abstractmethod
  def get_main_account_id(self, *args, **kwargs):
    pass

  @abstractmethod
  def get_organization_account_id(self, *args, **kwargs):
    pass
  
  @abstractmethod
  def _assume_role(self, *args, **kwargs):    
    pass
  
  @abstractmethod
  def get_default_rolename(self, *args, **kwargs):
    pass
  
  @abstractmethod
  def get_default_region(self, *args, **kwargs):
    pass
  
  @abstractmethod
  def get_default_account(self, *args, **kwargs):
    pass
  
  @abstractmethod
  def authenticate_session(self, force_quiet = False, *args, **kwargs):
    pass
  
  def _post_init(self, *args, **kwargs):
    self._load_base_configs()
  
  