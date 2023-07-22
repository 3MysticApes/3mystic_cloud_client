from threemystic_cloud_client.cloud_providers.base_class.base import cloud_client_provider_base as base
import os
from botocore import session as botocore_session, credentials as botocore_credentials
from botocore.config import Config as botocore_config_config
from boto3 import Session as boto_session
from botocore.exceptions import ClientError
from polling2 import TimeoutException, poll as poll2
import time
from random import randint

class cloud_client_provider_aws_base(base):
  def __init__(self, *args, **kwargs):
    # https://github.com/boto/botocore/issues/2705 
    # This update should be temporary until boto version 1.28 is released
    # os.environ["BOTO_DISABLE_COMMONNAME"] = "true"

    super().__init__(provider= "aws", *args, **kwargs)   
    self.links = {
      "cli_doc_link": "https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html",
      "ssm_doc_link": "https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html",
      "saml2aws_doc_link": "https://github.com/Versent/saml2aws"
    }

  def get_resource_name(self, resource, *args, **kwargs):
    if resource is None:
      return None

    if self.get_common().helper_type().general().is_type(obj= resource, type_check= str):
      return resource
    
    if self.get_common().helper_type().general().is_type(obj= resource, type_check= dict):
      for key in resource.keys():
        if self.get_common().helper_type().string().set_case(string_value= key, case= "lower") == "name":
          return self.get_resource_name(resource= resource.get(key))
        
      resource_tags = self.get_resource_tags_as_dictionary(resource= resource)
      if resource_tags is None:
        return None
      if len(resource_tags) < 1:
        return None
      
      return self.get_resource_name(resource= resource)

    return None
  
  def get_account_name(self, account):
    if account is None:
      return None
    if self.get_common().helper_type().general().is_type(obj= account, type_check= str):
      return account.strip()

    if account.get("Name"):
      return account["Name"].strip()
    
    if account.get("accountName"):
      self.get_common().get_logger().warning("accountName will be depreciated use Name")
      return account["accountName"].strip()
    
    raise self.get_common().exception().exception(
      exception_type = "generic"
    ).not_implemented(
      logger = self.get_common().get_logger(),
      name = "account",
      message = f"Unknown account object: {account}."
    )

  def get_account_id(self, account):
    if account is None:
      return None
    if self.get_common().helper_type().general().is_type(obj= account, type_check= str):
      return self.get_common().helper_type().string().trim(string_value=self.get_common().helper_type().string().set_case(string_value= account, case= "lower"))
    
    if account.get("Id"):
      return self.get_common().helper_type().string().trim(string_value=self.get_common().helper_type().string().set_case(string_value= account["Id"], case= "lower"))

    if account.get("accountId"):
      self.get_common().get_logger().warning("accountId will be depreciated use Id")
      return self.get_common().helper_type().string().trim(string_value=self.get_common().helper_type().string().set_case(string_value= account["accountId"], case= "lower"))
    
    raise self.get_common().exception().exception(
      exception_type = "generic"
    ).not_implemented(
      logger = self.get_common().get_logger(),
      name = "account",
      message = f"Unknown account object: {account}."
    )
  
  def make_account(self, **kwargs):    
    account = {}
    if not self.get_common().helper_type().string().is_null_or_whitespace(string_value= kwargs.get("accountId")):
      self.get_common().get_logger().warning("accountId will be depreciated use Id")
      account["accountId"] = self.get_common().helper_type().string().trim(string_value=self.get_common().helper_type().string().set_case(string_value= kwargs.get("accountId"), case= "lower"))
      account["Id"] = self.get_common().helper_type().string().trim(string_value=self.get_common().helper_type().string().set_case(string_value= kwargs.get("accountId"), case= "lower"))

    if not self.get_common().helper_type().string().is_null_or_whitespace(string_value= kwargs.get("Id")):
      account["Id"] = self.get_common().helper_type().string().trim(string_value=self.get_common().helper_type().string().set_case(string_value= kwargs.get("Id"), case= "lower"))

    if not self.get_common().helper_type().string().is_null_or_whitespace(string_value= kwargs.get("accountName")):
      self.get_common().get_logger().warning("accountName will be depreciated use Name")
      account["accountName"] = self.get_common().helper_type().string().trim(string_value=kwargs.get("accountName"))
      account["Name"] = self.get_common().helper_type().string().trim(string_value=kwargs.get("accountName"))

    if not self.get_common().helper_type().string().is_null_or_whitespace(string_value= kwargs.get("Name")):
      account["Name"] = self.get_common().helper_type().string().trim(string_value=kwargs.get("Name"))
    
    return account
  
  @property
  def default_region_resources(self):
    if hasattr(self, "_default_region_resources"):
      return self._default_region_resources
    
    return ["us-east-1"]
  
  @default_region_resources.setter
  def _set_default_region_resources(self, value):
    self._default_region_resources = value

  def get_resource_general_arn(self, resource_type = None, resource_type_sub = None, account_id = None, region = None, resource_id = None, data_item = None, **kwargs ):
    if data_item is not None:
      lower_keys = [key.lower() for key in data_item.keys()]
      if "arn" in lower_keys:
        arn_key = list(data_item.keys())[lower_keys.index("arn")]
        return self.get_common().helper_type().string().set_case(string_value= data_item[arn_key], case= "lower")

    return self.get_common().helper_type().string().set_case(string_value= f'arn:aws:{resource_type}:{region}:{account_id}:{resource_type_sub}/{resource_id}', case= "lower")
  
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
      self._set_profile()
    
    if(self._profile is None):
      raise self.get_common().exception().exception(
          exception_type = "generic"
        ).type_error(
          logger = self.get_common().get_logger(),
          name = "Cloud Client Profile",
          message = f"Profile is None"
        )
    
    return self._profile
  
  def _set_profile(self, profile_data = None, *args, **kwargs):
    if profile_data is None:
      self._profile = self.get_default_profile()
      return
      
    self._profile = profile_data
  
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
        currentAttempt += 1
        try:
          if boto_params is not None:
            boto_response = boto_call(boto_params)
            break
          
          boto_response = boto_call()
          break       
        except ClientError as err:
          if error_codes_raise is not None and self.get_common().helper_type().string().set_case(string_value= err.response["Error"]["Code"], case= "lower") in error_codes_raise:
            raise self.get_common().exception().exception(
              exception_type = "generic"
            ).type_error(
              logger = self.get_common().get_logger(),
              name = "General Boto Call Raise",
              message = f"error_codes_raise - {err.response['Error']['Code']} - {err.response['ResponseMetadata']['RequestId']} - {err.response['Error']['Message']}",
              exception= err,
              log_as_warning = True
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
              message = f"accessdeniedexception - {err.response['Error']['Code']} - {err.response['ResponseMetadata']['RequestId']} - {err.response['Error']['Message']}",
              exception= err,
              log_as_warning = True
            )
          
          if err.response['Error']["Code"] == 'SlowDown':
            time.sleep(self.get_common().helper_type().requests().expodential_backoff_wait(attempt= currentAttempt, auto_sleep= False))
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
              message = f"err_retrycount - {currentAttempt} - {retryCount}",
              exception= err,
              log_as_warning = True
            )
            
          if currentAttempt > 2:
            self.get_common().get_logger().exception(msg= "Error with call: {}".format(err), exc_info= err)
            if verbose:
              self.get_common().get_logger().info(msg= "Error with call: {}".format(err))

          time.sleep(self.get_common().helper_type().requests().expodential_backoff_wait(attempt= currentAttempt, auto_sleep= False))
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
      role = self.get_default_rolename()

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
  
  def _get_account_regions_costexplorer(self, account, services = None, *args, **kwargs ):
    
    ce_client = self.get_boto_client(
      client= "ce",
      account=account
    )

    filter = {}
    granularity = "DAILY"
    
    utc_now = self.get_common().helper_type().datetime().get()
    time_period = {
      "Start":(self.get_common().helper_type().datetime().datetime_as_string(
        dt= (utc_now + self.get_common().helper_type().datetime().time_delta(months= -1, dt= utc_now)),
        dt_format= "%Y-%m-%d"
      )),
      "End": (self.get_common().helper_type().datetime().datetime_as_string(
        dt= utc_now,
        dt_format= "%Y-%m-%d"
      ))
    }   
    metrics = ["NET_UNBLENDED_COST"]
    group_by= [{"Type":"DIMENSION", "Key":"REGION"}]

    get_cost_usage_params = {
      "Granularity":granularity,
      "TimePeriod": time_period,
      "Metrics": metrics,
      "GroupBy": group_by
    }

    if not services is None:
      filter["Dimensions"] = {
        "Key": "SERVICE",
        "Values": services,
        "MatchOptions": ["EQUALS", "CASE_SENSITIVE"]
      }
      get_cost_usage_params["Filter"] = filter


    try:
      discovered_resultsbytime = self.general_boto_call_array(
        boto_call = lambda item: ce_client.get_cost_and_usage(**item),
        boto_params = get_cost_usage_params,
        boto_nextkey = "NextToken",
        boto_key="ResultsByTime"
      )

      regions = []

      for itemTime in discovered_resultsbytime:
        for itemGroup in itemTime["Groups"]:
          for item in itemGroup["Keys"]:
            if self.get_common().helper_type().string().set_case(string_value= item, case= "lower") == "noregion":
              continue
            if not item in regions:
              regions.append(item)
      return regions
    except Exception as err:
      self.get_common().get_logger().exception(msg=f"Could not pull regions dynamically: {err}", exc_info= err)
      return self.default_region_resources
    
  def get_accounts_regions_costexplorer(self, accounts, services, role= None):     
    if role is None:
      role = self.get_default_rolename()
    regions = { }
    
    for account in accounts:      
      regions[self.get_account_id(account)] = self.get_account_regions_costexplorer(
        account=account,
        role=role,
        services= services
      )

    return regions

  def get_account_regions_costexplorer(self, account, role, services):     
    # to get a list of all services for an account
    # aws ce get-dimension-values --time-period "Start=2022-09-01,End=2022-09-11" --dimension SERVICE
    regions = { }

    return self._get_account_regions_costexplorer(
      account= account, 
      role= role,
      services= services
    )
  
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
  
  def get_resource_groups(self, account, region, filters_rg = [], rg_client = None):
    if rg_client is None:
      rg_client = self.get_boto_client(
        client= 'resource-groups', 
        account= account,
        role = None,
        region = region
      )

    boto_params = {}
    if len(filters_rg) > 0:
      boto_params["Filters"] = filters_rg

    return self.general_boto_call_array(
      boto_call=lambda item: rg_client.list_groups(**item),
      boto_params= boto_params,
      boto_nextkey = "NextToken",
      boto_key="GroupIdentifiers"
    )
  
  def get_resource_group_from_resource(self, account, region, filters_rg = [], filters_resource = [], rg_client = None, resource_groups = None, treat_badfilter_err_as_empty = True):
    if rg_client is None:
      rg_client = self.get_boto_client(
        client= 'resource-groups', 
        account= account,
        role = None,
        region = region
      )
      
    if resource_groups is None or (resource_groups is not None and len(resource_groups)<1):
      resource_groups = self.get_resource_groups(account=account, region= region,filters=filters_rg, rg_client= rg_client)

    if resource_groups is None or (resource_groups is not None and len(resource_groups)<1):
      return {}

    resources = {} 
    boto_params = {}
    if len(filters_resource) > 0:
      boto_params["Filters"] = filters_resource
    
    boto_nextkey = "NextToken"
    for rg in resource_groups:
      boto_params["Group"] = rg["GroupArn"]
      if boto_nextkey in boto_params:
        boto_params.pop(boto_nextkey)
      try:
        for resource in self.general_boto_call_array(
            boto_call=lambda item: rg_client.list_group_resources(**item),
            boto_params= boto_params,
            boto_nextkey = boto_nextkey,
            boto_key="Resources",
            error_codes_raise = ["BadRequestException"]
          ):
        
          if resource.get("Identifier").get("ResourceArn").lower() not in resources:
            resources[resource.get("Identifier").get("ResourceArn").lower()] = []
          
          resources[resource.get("Identifier").get("ResourceArn").lower()].append(rg["GroupName"])
      
      except Exception as err:
        if treat_badfilter_err_as_empty and "filters not valid" in str(err).lower():
          continue

        raise err

    return resources
  
  def get_resource_tags_as_dictionary(self, resource, *args, **kwargs):
    if resource is None:
      return None

    tags = None
    if not self.get_common().helper_type().general().is_type(obj= resource, type_check= dict):
      if hasattr(resource, "tags"):
        tags = resource.tags
        
    elif self.get_common().helper_type().general().is_type(obj= resource, type_check= dict):
      tags = resource.get("tags")

    if tags is None:
      tags = {}
    
    if self.get_common().helper_type().general().is_type(obj= tags, type_check= list ):
        tags = {tag["Key"]:tag["Value"] for tag in tags}

    return tags