import os
import abc
from threemystic_cloud_client.cloud_providers.aws.base_class.base import cloud_client_provider_aws_base as base
from botocore import session as botocore_session, credentials as botocore_credentials
from botocore.config import Config as botocore_config_config
from boto3 import Session as boto_session
from botocore.exceptions import ClientError
from polling2 import TimeoutException, poll
import time
from random import randint

class cloud_client_aws_client_base(base):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.__set_profile(*args, **kwargs)
  
  def _get_boto_client_key(self, client, account = None, region = None, *args, **kwargs):
    
    if self.get_common().helper_type().string().is_null_or_whitespace(string_value= region):
      region = self.get_default_region()

    if account is None or (self.get_common().helper_type().general().is_type(obj= account, type_check= str) and self.get_common().helper_type().string().is_null_or_whitespace(string_value= account)):
      account = self.get_default_account()

    return f"{client}-{(self.get_account_id(account))}-{region}" 
  
  def _get_created_boto_clients(self, *args, **kwargs):
    if(not hasattr(self, "_created_boto_clients")):
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
    if(not hasattr(self, "_created_boto_sessions")):
      return self._created_boto_sessions
    
    self._created_boto_sessions = {}
    return self._get_created_boto_sessions()
  
  def _get_assumed_role_credentials_key(self, account, role, *args, **kwargs):    
    if self.get_common().helper_type().string().is_null_or_whitespace(string_value= role):
      role = self.get_default_rolename()

    if account is None or (self.get_common().helper_type().general().is_type(obj= account, type_check= str) and self.get_common().helper_type().string().is_null_or_whitespace(string_value= account)):
      account = self.get_default_account()

    return f'{self.get_account_id(account= account)}_{role}'

  def _get_assumed_role_credentials(self, *args, **kwargs):
    if(not hasattr(self, "_assumed_role_credentials")):
      return self._assumed_role_credentials
    
    self._assumed_role_credentials = {}
    return self._get_assumed_role_credentials()
    
  def get_profile(self, *args, **kwargs):
    if(not hasattr(self, "_profile")):
      raise self._main_reference.exception().exception(
          exception_type = "generic"
        ).type_error(
          logger = self.get_common().get_logger(),
          name = "Cloud Client Profile",
          message = f"Profile was not set"
        )
    
    if(self._profile is None):
      raise self._main_reference.exception().exception(
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
  
  @abc.abstractmethod
  def _load_base_configs(self):
    pass
  
  @abc.abstractmethod
  def get_main_account_id(self, *args, **kwargs):
    pass

  @abc.abstractmethod
  def get_organization_account_id(self, *args, **kwargs):
    pass
  
  @abc.abstractmethod
  def _assume_role(self, *args, **kwargs):    
    pass
  
  @abc.abstractmethod
  def get_default_rolename(self, *args, **kwargs):
    pass
  
  @abc.abstractmethod
  def get_default_region(self, *args, **kwargs):
    pass
  
  @abc.abstractmethod
  def get_default_account(self, *args, **kwargs):
    pass
  
  @abc.abstractmethod
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
      error_codes_continue = [code.lower() for code in error_codes_continue]

    if error_codes_return is not None:
      error_codes_return = [code.lower() for code in error_codes_return]

    if error_codes_raise is not None:
      error_codes_raise = [code.lower() for code in error_codes_raise]

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
          if error_codes_raise is not None and err.response["Error"]["Code"].lower() in error_codes_raise:
            raise self.get_common().exception().exception(
              exception_type = "generic"
            ).type_error(
              logger = self.get_common().get_logger(),
              name = "General Boto Call Raise",
              message = f"Profile was not set",
              exception= err
            )

          if error_codes_continue is not None and err.response["Error"]["Code"].lower() in error_codes_continue:
            continue

          if error_codes_return is not None and err.response["Error"]["Code"].lower() in error_codes_return:
            return return_data
          
          if err.response["Error"]["Code"].lower() == "accessdeniedexception":
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
                "main_exception"= err
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
  
  def session_expired(self, *args, **kwargs):
    return self._session_expired(*args, **kwargs)
  
  def ensure_session(self, *args, **kwargs):
    if(not self.session_expired()):
      return
    
    if(self.is_authenticating_session()):
      poll(
        lambda: self.is_authenticating_session(),
        ignore_exceptions=(Exception,),
        timeout=self.get_aws_poll_authenticate(),
        step=0.1
      )
      return self.ensure_session()
      
    self._set_authenticating_session(is_authenticating_session= True)

    try:
      self.authenticate_session()
    finally:
      self._set_authenticating_session(is_authenticating_session= False)
  
  def is_authenticating_session(self, *args, **kwargs):
    if(hasattr(self, "_is_authenticating_session")):
      return self._is_authenticating_session
    
    return False
  
  def _set_authenticating_session(self, is_authenticating_session, *args, **kwargs):
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

  def _convert_assume_role_credentials_boto_session(self, credentials):
    experation = credentials["Expiration"]
    if self.get_common().helper_type().general().is_type(obj= experation, type_check= str):
      experation = self.get_common().helper_type().datetime().parse_iso(iso_datetime_str=experation)
    
    return {
        "access_key": credentials["AccessKeyId"],
        "secret_key": credentials["SecretAccessKey"],
        "token": credentials["SessionToken"],
        "expiry_time": f"{experation}+00:00" 
      }


  def __get_boto_session(self, role = None, region = None, profile = None, **kwargs):
    if not self.get_common().helper_type().string().is_null_or_whitespace(string_value= profile):
      return boto_session(profile_name= profile) if self.get_common().helper_type().string().is_null_or_whitespace(string_value= region) else boto_session(profile_name= profile, region_name= region)

    return botocore_session.get_session()

  def get_boto_session(self, account=None, role = None, region = None, profile = None):
    
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
      metadata=self._convert_assume_role_credentials_boto_session(self.assume_role(account=account, role=role)),
      refresh_using=lambda: self._convert_assume_role_credentials_boto_session(self.assume_role(account=account, role=role, force_refresh= True)),
      method="sts-assume-role",
    )

    session._credentials = credentials 
    session.set_config_variable("region", region)
      
    self._get_created_boto_sessions()[cache_key] = boto_session(botocore_session= session)
    return self._get_created_boto_sessions[cache_key]
  
  def _get_accounts(self, update_accountlist = False, include_suspended = False):
    
    if not self._account_list is None and len(self._account_list) > 0 and not update_accountlist:
      return self._account_list
    
    self._account_list = self.get_common().general_boto_call_array(
      boto_call=lambda item: self._get_organization_client().list_accounts(**item),
      boto_params={},
      boto_nextkey = "NextToken",
      boto_key="Accounts"
    )
    
    if include_suspended == False:
      self._account_list = [ acct for acct in self._account_list if acct["Status"].lower() != "suspended" ]
    
    return self._account_list 

  def get_accountids_by_ou(self, org_ou, exclude_ous = None, **kwargs):
    if org_ou is None:
      org_ou = []
    
    if exclude_ous is None:
      exclude_ous = []
    
    if self.get_common().helper_type().general().is_type(obj= org_ou, type_check= str) and not self.get_common().helper_type().string().is_null_or_whitespace(string_value= org_ou): 
      org_ou = [ ou.strip() for ou in org_ou.split(",") if not self.get_common().helper_type().string().is_null_or_whitespace(string_value= ou) ]
    
    account_list = []
    for ou in org_ou:
      child_ous = [child_ou["Id"] for child_ou in self.general_boto_call_array(
        boto_call=lambda item: self._get_organization_client().list_children(**item),
        boto_params={"ParentId": ou, "ChildType": "ORGANIZATIONAL_UNIT"},
        boto_nextkey = "NextToken",
        boto_key="Children"
      ) if f'-{child_ou["Id"].lower()}' not in exclude_ous]
      account_list += self.get_accountids_by_ou(org_ou= child_ous, exclude_ous= exclude_ous)
      account_list += [account["Id"] for account in self.general_boto_call_array(
        boto_call=lambda item: self._get_organization_client().list_children(**item),
        boto_params={"ParentId": ou, "ChildType": "ACCOUNT"},
        boto_nextkey = "NextToken",
        boto_key="Children"
      )]
    
    return list(dict.fromkeys(account_list))
  
  def get_accounts(self, account = None, update_accountlist = False, include_suspended = False):
    all_accounts = self._get_accounts(update_accountlist=update_accountlist, include_suspended=include_suspended)
    if self.get_common().helper_type().general().is_type(obj= account, type_check= str) and not self.get_common().helper_type().string().is_null_or_whitespace(string_value= account):
      account = [ acct.strip() for acct in account.split(",") if not self.get_common().helper_type().string().is_null_or_whitespace(string_value= acct) ]

    if self.get_common().helper_type().general().is_type(obj= account, type_check= list) and not None:
      search_accounts_accounts = [ acct for acct in account if not acct.lower().startswith("ou-") and not acct.lower().startswith("-") ]
      search_accounts_ous = [ acct for acct in account if acct.lower().startswith("ou-") ]
      exclude_accounts_ous = [ acct for acct in account if acct.lower().startswith("-ou-") ]
      exclude_accounts = [ acct for acct in account if acct.lower().startswith("-") and not acct.lower().startswith("-ou-") ]
      account = list(dict.fromkeys(search_accounts_accounts + self.get_accountids_by_ou(org_ou= search_accounts_ous, exclude_ous= exclude_accounts_ous)))

      return [ acct for acct in all_accounts if f'-{acct["Id"]}' not in exclude_accounts and  self.get_common().helper_type().list().find_item(data= account, filter= lambda item: item == acct["Id"]) is not None ]

    elif account is not None:
      self.get_common().get_logger().warning(f'unknown data type for accounts {type(account)}, when trying to get accounts')
      return None


    return all_accounts
    
    