import os
from abc import abstractmethod
from threemystic_cloud_client.cloud_providers.aws.base_class.base import cloud_client_provider_aws_base as base
from botocore import session as botocore_session, credentials as botocore_credentials
from botocore.config import Config as botocore_config_config
from boto3 import Session as boto_session
from botocore.exceptions import ClientError
from polling2 import TimeoutException, poll as poll2
import time
from random import randint

class cloud_client_aws_client_base(base):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.__set_profile(*args, **kwargs)
  
  @abstractmethod
  def _session_expired(self, refresh = False, *args, **kwargs):
    pass
  
  def get_resource_general_arn(cls, resource_type = None, resource_type_sub = None, account_id = None, region = None, id = None, data_item = None, **kwargs ):
    if data_item is not None:
      lower_keys = [key.lower() for key in data_item.keys()]
      if "arn" in lower_keys:
        arn_key = list(data_item.keys())[lower_keys.index("arn")]
        return data_item[arn_key]

    return f'arn:aws:{resource_type}:{region}:{account_id}:{resource_type_sub}/{id}'
  
  def _get_boto_client_key(self, client, account = None, region = None, *args, **kwargs):
    
    if self.get_common().helper_type().string().is_null_or_whitespace(string_value= region):
      region = self.get_default_region()

    if account is None or (self.get_common().helper_type().general().is_type(obj= account, type_check= str) and self.get_common().helper_type().string().is_null_or_whitespace(string_value= account)):
      account = self.get_default_account()

    return f"{client}-{(self.get_account_id(account))}-{region}" 
  
  def _get_created_boto_clients(self, *args, **kwargs):
    if(hasattr(self, "_created_boto_clients")):
      return self._created_boto_clients
    
    self._created_boto_clients = {}
    return self._get_created_boto_clients()
  
  def _get_boto_session_key(self, account = None, role = None, region = None, profile = None, *args, **kwargs):
    if self.get_common().helper_type().string().is_null_or_whitespace(string_value= role):
      role = self.get_default_rolename()
    
    if self.get_common().helper_type().string().is_null_or_whitespace(string_value= region):
      region = self.get_default_region()

    if account is None or (self.get_common().helper_type().general().is_type(obj= account, type_check= str) and self.get_common().helper_type().string().is_null_or_whitespace(string_value= account)):
      account = self.get_default_account()

    cached_key = f"{self.get_account_id(account)}-{region}-{role}"
    if not self.get_common().helper_type().string().is_null_or_whitespace(string_value= profile):
      cached_key = f"{cached_key}-{profile}"

      return cached_key
  
  def _get_created_boto_sessions(self, *args, **kwargs):
    if(hasattr(self, "_created_boto_sessions")):
      return self._created_boto_sessions
    
    self._created_boto_sessions = {}
    return self._get_created_boto_sessions()
  
  def _get_assumed_role_credentials_key(self, account, role, *args, **kwargs):    
    if self.get_common().helper_type().string().is_null_or_whitespace(string_value= role):
      role = self.get_default_rolename()

    if account is None or (self.get_common().helper_type().general().is_type(obj= account, type_check= str) and self.get_common().helper_type().string().is_null_or_whitespace(string_value= account)):
      account = self.get_default_account()

    return f'{self.get_account_id(account= account)}_{role}'

  def _get_assumed_role_credentials(self, unset = False, *args, **kwargs):
    if(hasattr(self, "_assumed_role_credentials")):
      if unset:
        current = self._assumed_role_credentials
        delattr(self, "_assumed_role_credentials")
        return current
      
      return self._assumed_role_credentials
    
    self._assumed_role_credentials = {}
    return self._get_assumed_role_credentials()
    
  def get_profile(self, *args, **kwargs):
    if(not hasattr(self, "_profile")):
      self.__set_profile()
    
    if(self._profile is None):
      raise self.get_common().exception().exception(
          exception_type = "generic"
        ).type_error(
          logger = self.get_common().get_logger(),
          name = "Cloud Client Profile",
          message = f"Profile is None"
        )
    
    return self._profile
  
  def __set_profile(self, profile_data = None, *args, **kwargs):
    if profile_data is None:
      self._profile = self.get_default_profile()
      return
      
    self._profile = profile_data

  def _post_init(self, *args, **kwargs):
    self._load_base_configs()
  
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
  def authenticate_session(self, *args, **kwargs):
    pass

  async def async_general_boto_call_array(self, *args, **kwargs):
    return self.general_boto_call_array(*args, **kwargs)
  
  async def async_general_boto_call_single(self, *args, **kwargs):
    return self.general_boto_call_single(*args, **kwargs)
  
  def general_boto_call_single(self, *args, **kwargs):
    data = self.general_boto_call_array(*args, **kwargs)
    if data is None or len(data) < 1:
      return None
    
    return data[0]

  def general_boto_call_array(self, boto_call, boto_params, boto_key, boto_nextkey, retryCount = 10, verbose = False, boto_nextkey_param = None, error_codes_return = None, error_codes_continue = None, error_codes_raise = None, logger = None):
    return_data = []

    if boto_key is not None and self.get_common().helper_type().general().is_type(obj=boto_key, type_check= str):
      local_boto_key = boto_key
      boto_key = lambda item: item[local_boto_key] if item.get(local_boto_key) is not None else []

    if boto_nextkey_param is None:
      boto_nextkey_param = boto_nextkey

    if error_codes_continue is not None:
      error_codes_continue = [self.get_common().helper_type().string().set_case(string_value= code, case= "lower") for code in error_codes_continue]

    if error_codes_return is not None:
      error_codes_return = [self.get_common().helper_type().string().set_case(string_value= code, case= "lower") for code in error_codes_return]

    if error_codes_raise is not None:
      error_codes_raise = [self.get_common().helper_type().string().set_case(string_value= code, case= "lower") for code in error_codes_raise]

    boto_response = None
    while True:
      currentAttempt = 0
      slowdown_count = 0
      
      while currentAttempt < retryCount:
        currentAttempt+=1  
        try:  
          if boto_params is not None:
            boto_response = boto_call(boto_params)  
          else:
            boto_response = boto_call()  
          break          
        except ClientError as err:
          if error_codes_raise is not None and self.get_common().helper_type().string().set_case(string_value= err.response["Error"]["Code"], case= "lower") in error_codes_raise:
            raise self.get_common().exception().exception(
              exception_type = "generic"
            ).type_error(
              logger = self.get_common().get_logger(),
              name = "General Boto Call Raise",
              message = f"Profile was not set",
              exception= err
            )

          if error_codes_continue is not None and self.get_common().helper_type().string().set_case(string_value= err.response["Error"]["Code"], case= "lower") in error_codes_continue:
            continue

          if error_codes_return is not None and self.get_common().helper_type().string().set_case(string_value= err.response["Error"]["Code"], case= "lower") in error_codes_return:
            return return_data
          
          if self.get_common().helper_type().string().set_case(string_value= err.response["Error"]["Code"], case= "lower") == "accessdeniedexception":
            raise self.get_common().exception().exception(
              exception_type = "generic"
            ).type_error(
              logger = self.get_common().get_logger(),
              name = "General Boto Call accessdeniedexception",
              message = f"accessdeniedexception - {boto_call} - {boto_params}",
              exception= err
            )
          
          if err.response['Error']["Code"] == 'SlowDown':
            time.sleep(30)
            if slowdown_count < 5:
              currentAttempt-=1
            continue

          if verbose:
            self.get_common().get_logger().exception(
              msg=f"Params:{boto_params} - err: {err}",
              extra= {
                "main_exception": err
              }
            )

          if currentAttempt >= retryCount:
            boto_response = None
            raise self.get_common().exception().exception(
              exception_type = "generic"
            ).type_error(
              logger = self.get_common().get_logger(),
              name = "General Boto Call err retry ",
              message = f"accessdeniedexception - {boto_call} - {boto_params}",
              exception= err
            )
            
          if currentAttempt > 2:
            logger.exception(msg= "Error with call: {}".format(err), exc_info= err)
            if verbose:
              self.get_common().get_logger().info(msg= "Error with call: {}".format(err))

          sleepTime = (2**currentAttempt)+randint(1,10)
          if sleepTime > 30:
            sleepTime = 30
          time.sleep(sleepTime)
          continue      

      if boto_response is None or boto_key is None:
        return [ ]
        

      if not self.get_common().helper_type().general().is_type(obj= boto_key(boto_response), type_check= list):
        return [ boto_key(boto_response) ]

      return_data += boto_key(boto_response)

      if (boto_nextkey is None) or (boto_nextkey is not None and self.get_common().helper_type().string().is_null_or_whitespace(string_value= boto_response.get(boto_nextkey))) or boto_params is None:
        return return_data

      boto_params[boto_nextkey_param] = boto_response.get(boto_nextkey)

  def get_organization_account(self, *args, **kwargs):
    if(hasattr(self, "_organization_account")):
      if not self.get_common().helper_type().string().is_null_or_whitespace(string_value= self._organization_account):
        return self._organization_account
      
    
    self._organization_account = self.make_account(Id = self.get_organization_account_id())
    return self.get_organization_account()

  def assume_role(self, *args, **kwargs):
    self.ensure_session()
    if kwargs.get("account") is not None and self.get_common().helper_type().general().is_type(obj= kwargs["account"], type_check= str):
      kwargs["account"] = self.make_account(Id= kwargs["account"]) 

    return self._assume_role(**kwargs)
  
  def session_expired(self, refresh = False, *args, **kwargs):
    return self._session_expired(refresh= refresh, *args, **kwargs)
  
  def ensure_session(self, count = 0, *args, **kwargs):
    if(not self.session_expired()):
      return True
    
    if count > 5:
      raise self.get_common().exception().exception(
        exception_type = "generic"
      ).type_error(
        logger = self.get_common().get_logger(),
        name = "NOT AUTHENTICATED",
        message = f"Error waiting for authentication"
      )
    
    if(self.is_authenticating_session()):
      poll2(
        lambda: self.is_authenticating_session(),
        ignore_exceptions=(Exception,),
        timeout=self.get_aws_poll_authenticate(),
        step=0.1
      )
      return self.ensure_session(count= count+1)
      
    self._set_authenticating_session(is_authenticating_session= True)

    try:
      self.authenticate_session()
    finally:
      self._set_authenticating_session(is_authenticating_session= False)
    
    return self.ensure_session()
  
  def is_authenticating_session(self, *args, **kwargs):
    if(hasattr(self, "_is_authenticating_session")):
      return self._is_authenticating_session
    
    return False
  
  def _set_authenticating_session(self, is_authenticating_session, *args, **kwargs):
    if not is_authenticating_session:
      self._get_assumed_role_credentials(unset= True)
      self.session_expired(refresh= True)
      
    self._is_authenticating_session = is_authenticating_session
    return self.is_authenticating_session()

  def _get_organization_client(self, *args, **kwargs):   
    if hasattr(self, "_org_client"):
      return self._org_client
    
    self._org_client = self.get_boto_client(
      client= 'organizations', 
      account=self.get_organization_account(),
      role = None,
      region = None
    )
    return self._get_organization_client()

  
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

    if self.get_common().helper_type().string().is_null_or_whitespace(string_value= region):
      return config
    
    config.region_name = region
    return config

  def get_boto_client(self, client, account=None, role = None, region = None, *argv, **kwargs):
    if self.get_common().helper_type().string().is_null_or_whitespace(string_value= region):
      region = self.get_default_region()
    
    if self.get_common().helper_type().string().is_null_or_whitespace(string_value= role):
      region = self.get_default_rolename()

    if account is None or (self.get_common().helper_type().general().is_type(obj= account, type_check= str) and self.get_common().helper_type().string().is_null_or_whitespace(string_value= account)):
      account = self.get_default_account()

    cache_key = self._get_boto_client_key(client= client, account= account, role= role, region= region)
    if self._get_created_boto_clients().get(cache_key) is not None:
      return  self._get_created_boto_clients().get(cache_key)

    session = self.get_boto_session(
        account=account,
        region=region,
        role=role
      )


    if hasattr(session, "create_client"):
       self._get_created_boto_clients()[cache_key] = session.create_client(client, config= self.get_boto_config(region= region, *argv, **kwargs))
       return self._get_created_boto_clients()[cache_key]
       
    self._get_created_boto_clients()[cache_key] = session.client(client, config= self.get_boto_config(region= region, *argv, **kwargs))
    return self._get_created_boto_clients()[cache_key]

  def _auto_parse_aws_expiration(self, expiration, *argv, **kwargs):
    if self.get_common().helper_type().general().is_type(obj= expiration, type_check= int):
      return self.get_common().helper_type().datetime().get_from_timestamp(time_delta=expiration)
    
    if self.get_common().helper_type().general().is_type(obj= expiration, type_check= str):
      return self.get_common().helper_type().datetime().parse_iso(iso_datetime_str=expiration)
    

  def convert_assume_role_credentials_export(self, credentials):
    
    outputData = f"\nexport AWS_ACCESS_KEY_ID=\"{credentials['AccessKeyId']}\"\n"
    outputData += f"export AWS_SECRET_ACCESS_KEY=\"{credentials['SecretAccessKey']}\"\n"
    outputData += f"export AWS_SESSION_TOKEN=\"{credentials['SessionToken']}\"\n"
    outputData += f"export AWS_DEFAULT_REGION=\"{self.get_default_region()}\"\n"

    return outputData
  
  def convert_assume_role_credentials_cli(self, credentials):
    # https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sourcing-external.html
    expiration = self._auto_parse_aws_expiration(
      expiration= credentials["expiration"]
    )

    return {
      "Version": 1,
      "AccessKeyId": credentials["accessKeyId"],
      "SecretAccessKey": credentials["secretAccessKey"],
      "SessionToken": credentials["sessionToken"],
      "Expiration": self.get_common().helper_type().datetime().get_iso_datetime(
        dt= expiration
      )
    }
        
  def convert_assume_role_credentials_boto_session(self, credentials):
    expiration = self._auto_parse_aws_expiration(
      expiration= credentials["expiration"]
    )
    

    return {
      "access_key": credentials["accessKeyId"],
      "secret_key": credentials["secretAccessKey"],
      "token": credentials["sessionToken"],
      "expiry_time": self.get_common().helper_type().datetime().get_iso_datetime(
        dt= expiration
      )
    }


  def __get_boto_session(self, role = None, region = None, profile = None, **kwargs):
    if not self.get_common().helper_type().string().is_null_or_whitespace(string_value= profile):
      return boto_session(profile_name= profile) if self.get_common().helper_type().string().is_null_or_whitespace(string_value= region) else boto_session(profile_name= profile, region_name= region)

    return botocore_session.get_session()

  def get_boto_session(self, account=None, role = None, region = None, profile = None, *args, **kwargs):
    
    if self.get_common().helper_type().string().is_null_or_whitespace(string_value= role):
      role = self.get_default_rolename()
    
    if self.get_common().helper_type().string().is_null_or_whitespace(string_value= region):
      region = self.get_default_region()

    if account is None or (self.get_common().helper_type().general().is_type(obj= account, type_check= str) and self.get_common().helper_type().string().is_null_or_whitespace(string_value= account)):
      account = self.get_default_account()

    cache_key = self._get_boto_session_key(account= account, role= role, region= region, profile= profile)
    if self._get_created_boto_sessions().get(cache_key) is not None:
      return self._get_created_boto_sessions().get(cache_key)

    session = self.__get_boto_session(
      account=account, role = role, region = region, profile = profile
    )     

    credentials = botocore_credentials.RefreshableCredentials.create_from_metadata(
      metadata=self.convert_assume_role_credentials_boto_session(self.assume_role(account=account, role=role)),
      refresh_using=lambda: self.convert_assume_role_credentials_boto_session(self.assume_role(account=account, role=role, refresh= True)),
      method="sts-assume-role",
    )

    session._credentials = credentials 
    session.set_config_variable("region", region)
      
    self._get_created_boto_sessions()[cache_key] = boto_session(botocore_session= session)
    return self.get_boto_session(account=account, role = role, region = region, profile = profile, *args, **kwargs)
  
  def _get_accounts(self, refresh = False, include_suspended = False):
    
    if hasattr(self, "_account_list") and not refresh:
      return_list = "active" if not include_suspended else "all"
      if self._account_list is not None and len(self._account_list) > 0:
        if return_list in self._account_list:
          return self._account_list[return_list]
    
    
    self._account_list = {
      "all": self.general_boto_call_array(
        boto_call=lambda item: self._get_organization_client().list_accounts(**item),
        boto_params={},
        boto_nextkey = "NextToken",
        boto_key="Accounts"
      )
    }
    
    self._account_list["active"] = [ acct for acct in self._account_list["all"] if self.get_common().helper_type().string().set_case(string_value= acct["Status"], case= "lower") != "suspended" ]
    return self._get_accounts(refresh= False, include_suspended= include_suspended) 

  def get_accountids_by_ou(self, org_ou, exclude_ous = None, **kwargs):
    if org_ou is None:
      org_ou = []
    
    if exclude_ous is None:
      exclude_ous = []
    
    if self.get_common().helper_type().general().is_type(obj= org_ou, type_check= str) and not self.get_common().helper_type().string().is_null_or_whitespace(string_value= org_ou): 
      org_ou = [ ou.strip() for ou in self.get_common().helper_type().string().split(string_value= org_ou) if not self.get_common().helper_type().string().is_null_or_whitespace(string_value= ou) ]
    
    account_list = []
    for ou in org_ou:
      child_ous = [child_ou["Id"] for child_ou in self.general_boto_call_array(
        boto_call=lambda item: self._get_organization_client().list_children(**item),
        boto_params={"ParentId": ou, "ChildType": "ORGANIZATIONAL_UNIT"},
        boto_nextkey = "NextToken",
        boto_key="Children"
      ) if f'-{self.get_common().helper_type().string().set_case(string_value= child_ou["Id"], case= "lower")}' not in exclude_ous]
      account_list += self.get_accountids_by_ou(org_ou= child_ous, exclude_ous= exclude_ous)
      account_list += [account["Id"] for account in self.general_boto_call_array(
        boto_call=lambda item: self._get_organization_client().list_children(**item),
        boto_params={"ParentId": ou, "ChildType": "ACCOUNT"},
        boto_nextkey = "NextToken",
        boto_key="Children"
      )]
    
    return list(dict.fromkeys(account_list))
  
  def get_accounts(self, account = None, refresh = False, include_suspended = False):    
    all_accounts = self._get_accounts(refresh=refresh, include_suspended=include_suspended)
    if account is None:
      return all_accounts
    
    if self.get_common().helper_type().general().is_type(obj= account, type_check= str) and not self.get_common().helper_type().string().is_null_or_whitespace(string_value= account):
      account = [ self.get_account_id(account= acct) for acct in self.get_common().helper_type().string().split(string_value= account) if not self.get_common().helper_type().string().is_null_or_whitespace(string_value= acct) ]

    if not self.get_common().helper_type().general().is_type(obj= account, type_check= list):
      self.get_common().get_logger().warning(f'unknown data type for accounts {type(account)}, when trying to get accounts')
      return all_accounts

    search_accounts = [ self.get_account_id(account= acct) for acct in account if not self.get_account_id(account= acct) .startswith("ou-") and not self.get_account_id(account= acct) .startswith("-") ]
    search_accounts_ous = [ self.get_account_id(account= acct)  for acct in account if self.get_account_id(account= acct) .startswith("ou-") ]
    exclude_accounts_ous = [ self.get_account_id(account= acct)  for acct in account if self.get_account_id(account= acct) .startswith("-ou-") ]
    exclude_accounts = [ self.get_account_id(account= acct)  for acct in account if self.get_account_id(account= acct).startswith("-") and not self.get_account_id(account= acct).startswith("-ou-") ]
    account = list(dict.fromkeys(search_accounts + self.get_accountids_by_ou(org_ou= search_accounts_ous, exclude_ous= exclude_accounts_ous)))

    return [ acct for acct in all_accounts if f'-{self.get_account_id(account= acct) }' not in exclude_accounts and  (len(account) < 1 or self.get_common().helper_type().list().find_item(data= account, filter= lambda item: self.get_account_id(account= item)  == self.get_account_id(account= acct)) is not None) ]
    
    