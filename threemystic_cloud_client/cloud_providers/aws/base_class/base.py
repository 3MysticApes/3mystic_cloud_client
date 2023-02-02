from threemystic_cloud_client.cloud_providers.base_class.base import cloud_client_provider_base as base
import os
from botocore import session as botocore_session, credentials as botocore_credentials
from botocore.config import Config as botocore_config_config
from boto3 import Session as boto_session


class cloud_client_provider_aws_base(base):
  def __init__(self, *args, **kwargs):
    # https://github.com/boto/botocore/issues/2705 
    # This update should be temporary until boto version 1.28 is released
    os.environ["BOTO_DISABLE_COMMONNAME"] = "true" 

    super().__init__(*args, **kwargs)


  def _post_init(self, *args, **kwargs):
    self._set_main_account_id()
    self._set_organization_account_id()
  
  def get_default_rolename(self, *args, **kwargs):
    raise Exception("fix")
  
  def get_default_region(self, *args, **kwargs):
    raise Exception("fix")  
  
  def get_rolename(self, *args, **kwargs):
    raise Exception("fix")
  
  def get_main_account_id(self, *args, **kwargs):
    raise Exception("fix")

  def get_organization_account_id(self, *args, **kwargs):
    raise Exception("fix")

  def get_organization_account(self, *args, **kwargs):
    raise Exception("fix")

  def set_awscli_rolename(self, *args, **kwargs):
    raise Exception("fix")

  # set_main_account_id  
  def _set_main_account_id(self, *args, **kwargs):
    raise Exception("fix")


  # set_organization_account_id
  def _set_organization_account_id(self, *args, **kwargs):    
    raise Exception("fix")
  
  def _get_organization_client(self, *args, **kwargs):   
    if hasattr(self, "__org_client"):
      return self.__org_client
    
    self.__org_client = self.get_boto_client(
      client= 'organizations', 
      account=self.get_organization_account(),
      role = None, 
      region = None
    )
    self._get_organization_client()

  def get_account_name(self, account):
    if account is None:
      return None
    if self.common.is_type(account, str):
      return account

    if account.get("Name"):
      return account["Name"]
    
    if account.get("accountName"):
      self.get_logger().warning("accountName will be depreciated use Name")
      return account["accountName"]
    
    raise self.get_common().exception().exception(
      exception_type = "generic"
    ).not_implemented(
      logger = self.logger,
      name = "account",
      message = f"Unknown account object: {account}."
    )

  def get_account_id(self, account):
    if account is None:
      return None
    if self.common.is_type(account, str):
      return account
    
    if account.get("Id"):
      return account["Id"]

    if account.get("accountId"):
      self.get_logger().warning("accountId will be depreciated use Id")
      return account["accountId"]
    
    raise self.get_common().exception().exception(
      exception_type = "generic"
    ).not_implemented(
      logger = self.logger,
      name = "account",
      message = f"Unknown account object: {account}."
    )
  
  def make_account(self, **kwargs):    
    account = {}
    if not self.common.isNullOrWhiteSpace(kwargs.get("accountId")):
      self.get_logger().warning("accountId will be depreciated use Id")
      account["accountId"] = kwargs.get("accountId")
      account["Id"] = kwargs.get("accountId")

    if not self.common.isNullOrWhiteSpace(kwargs.get("Id")):
      account["Id"] = kwargs.get("Id")

    if not self.common.isNullOrWhiteSpace(kwargs.get("accountName")):
      self.get_logger().warning("accountName will be depreciated use Name")
      account["accountName"] = kwargs.get("accountName")
      account["Name"] = kwargs.get("accoNameuntId")

    if not self.common.isNullOrWhiteSpace(kwargs.get("Name")):
      account["Name"] = kwargs.get("Name")
    
    return account
  
  def get_boto_config(self, region= None, max_attempts = 10, read_timeout = 900, connect_timeout = 10, max_pool_connections = 20,   *argv, **kwargs):
    config = botocore_config_config(
      retries = {
      'max_attempts': max_attempts,
      'mode': 'standard'
      },
      read_timeout = read_timeout,
      connect_timeout = connect_timeout,
      max_pool_connections = max_pool_connections
    )

    if self.common.isNullOrWhiteSpace(region):
      return config
    
    config.region_name = region
    return config

  def get_boto_client(self, client, account=None, role = None, region = None, *argv, **kwargs):    
    if self.common.isNullOrWhiteSpace(region):
      region = self.get_default_region()

    cache_key = f"{client}{(self.get_account_id(account)) if not self.common.is_type(account, str(account)) else account}-{region}" 
    if self._created_botoclients.get(cache_key) is not None:
      return  self._created_botoclients.get(cache_key)

    session = self.get_boto_session(
        account=account,
        region=region,
        role=role
      )


    if hasattr(session, "create_client"):
       self._created_botoclients[cache_key] = session.create_client(client, config= self.get_boto_config(region= region, *argv, **kwargs))
       return self._created_botoclients[cache_key]
       
    if hasattr(session, "client"):
      self._created_botoclients[cache_key] = session.client(client, config= self.get_boto_config(region= region, *argv, **kwargs))
      return self._created_botoclients[cache_key]

  def get_boto_session_token(self, **kwargs):
    
    session_args = {
      "aws_access_key_id": kwargs.get("aws_access_key_id") if not self.common.isNullOrWhiteSpace(kwargs.get("aws_access_key_id")) else kwargs.get("AccessKeyId"),
      "aws_secret_access_key":  kwargs.get("aws_secret_access_key") if not self.common.isNullOrWhiteSpace(kwargs.get("aws_secret_access_key")) else kwargs.get("SecretAccessKey"),
      "aws_session_token":  kwargs.get("aws_session_token") if not self.common.isNullOrWhiteSpace(kwargs.get("aws_session_token")) else kwargs.get("SessionToken"),
      "region_name":  (kwargs.get("region_name") if self.common.isNullOrWhiteSpace(kwargs.get("region_name")) 
        else (kwargs.get("region") if not self.common.isNullOrWhiteSpace(kwargs.get("region")) else None))
    }
    
    return boto_session(**session_args)

  def get_boto_session_environment(self, region = None):
    if self.common.isNullOrWhiteSpace(region):
      region = os.environ["AWS_REGION"] if not self.common.isNullOrWhiteSpace(os.environ.get("AWS_REGION")) else self.get_default_region()
    session_args = {
      "aws_access_key_id": os.environ.get("AWS_ACCESS_KEY_ID"),
      "aws_secret_access_key": os.environ.get("AWS_SECRET_ACCESS_KEY"),
      "aws_session_token": os.environ.get("AWS_SESSION_TOKEN"),
      "region_name": region
    }
    
    return self.get_boto_session_token(**session_args)

  def __get_boto_session(self, role = None, region = None, profile = None, **kwargs):
    if not self.common.isNullOrWhiteSpace(profile) :
      return boto_session(profile_name= profile) if self.common.isNullOrWhiteSpace(region) else boto_session(profile_name= profile, region_name= region)
    
    if self.use_environment_botosession:
      return self.get_boto_session_environment(region= region)

    if self.common.isNullOrWhiteSpace(region) :
      region = self.credentials.default_region
    
    if self.common.isNullOrWhiteSpace(role) :
      role = self.credentials.awscli_rolename

    return botocore_session.get_session()

  def get_boto_session(self, account=None, role = None, region = None, profile = None):
    cache_key = f"{self.get_account_id(account)}-{region}"
    if self.cache_boto_session and self._created_botosessions.get(cache_key) is not None:
      return self._created_botosessions.get(cache_key)

    session = self.__get_boto_session(
      account=account, role = role, region = region, profile = profile
    )

    

    if self.use_environment_botosession:
      if account is None or self.get_main_account_id() == self.get_account_id(account):
        if not self.cache_boto_session:
          return session
        self._created_botosessions[cache_key] = session
        return self._created_botosessions[cache_key]
      
      session_token = self.get_boto_session_token(**self.assume_role(account=account, role=role))      
      if not self.cache_boto_session:
        return session_token

      self._created_botosessions[cache_key] = session_token
      return self._created_botosessions[cache_key]
      
      

    credentials = botocore_credentials.RefreshableCredentials.create_from_metadata(
      metadata=self._convert_assume_role_credentials_boto_session(self.assume_role(account=account, role=role)),
      refresh_using=lambda: self._convert_assume_role_credentials_boto_session(self.assume_role(account=account, role=role, force_refresh= True)),
      method="sts-assume-role",
    )

    session._credentials = credentials 
    session.set_config_variable("region", region)
    if not self.cache_boto_session:
      return boto_session(botocore_session= session)
      
    self._created_botosessions[cache_key] = boto_session(botocore_session= session)
    return self._created_botosessions[cache_key]
    

    

