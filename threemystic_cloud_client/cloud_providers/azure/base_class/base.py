from threemystic_cloud_client.cloud_providers.base_class.base import cloud_client_provider_base as base
from azure.mgmt.costmanagement.models import TimeframeType, OperatorType, QueryColumnType, QueryDefinition, QueryTimePeriod, QueryDataset, QueryAggregation, QueryGrouping, QueryFilter, QueryComparisonExpression
from azure.core.exceptions import HttpResponseError, ClientAuthenticationError
from azure.identity._exceptions import CredentialUnavailableError
import time
import math
from abc import abstractmethod
import jwt
from polling2 import TimeoutException, poll as poll2

class cloud_client_provider_azure_base(base):
  def __init__(self, *args, **kwargs):
    self._stop_process_login()
    super().__init__(provider= "azure", *args, **kwargs)
    
    self.links = {
      "cli_doc_link": "https://learn.microsoft.com/en-us/cli/azure/install-azure-cli"
    }

  
  @abstractmethod
  def _login(self, on_login_function = None, tenant = None, *args, **kwargs):
    pass

  def login(self, *args, **kwargs):
    if self.is_login_processing():
      poll2(
        lambda: self.is_login_processing(),
        ignore_exceptions=(Exception,),
        timeout=240,
        step=0.1
      )

    self._start_process_login()
    return_data = self._login(*args, **kwargs)
    self._stop_process_login()

    return return_data
  
  def decode_jwt_token(self, token, *args, **kwargs):
    alg = jwt.get_unverified_header(jwt= token)
    return jwt.decode(
      jwt= token,
      algorithms= [alg],
      options= {"verify_signature": False}
    )

  def is_login_processing(self, *args, **kwargs):
    return (self.__is_processing_login is True)
  
  def _start_process_login(self, *args, **kwargs):
    self.__is_processing_login = True
  
  def _stop_process_login(self, *args, **kwargs):
    self.__is_processing_login = False

  def _start_process_login(self, *args, **kwargs):
    self.__is_processing_login = True

  
  def _get_credential(self, account_id, unset = False, *args, **kwargs):
    if unset is True:
      if hasattr(self, f"_credentials_{account_id}"):
        current_value = getattr(self, f"_credentials_{account_id}")
        delattr(self, f"_credentials_{account_id}")
        return current_value
      return None
      
    if hasattr(self, f"_credentials_{account_id}"):
      return getattr(self, f"_credentials_{account_id}")
    
    setattr(self, f"_credentials_{account_id}", {})
    return self._get_credential(account_id= account_id)

  def _clear_credential(self, *args, **kwargs):
    if hasattr(self, "_credentials"):
      delattr(self, "_credentials")
  
  def check_request_too_many_requests(self, exception, *args, **kwargs):
    if not self.get_common().helper_type().general().is_type(obj= exception, type_check= HttpResponseError):
      return False       
    
    if (HttpResponseError(exception)).status_code == 429:
      return True
    
    if "too many requests" in self.get_common().helper_type().string().set_case(string_value= (HttpResponseError(exception)).message, case= "lower"):
      return True
    
    return False
  
  def check_request_error_login(self, exception, *args, **kwargs):

    if self.get_common().helper_type().general().is_type(obj= exception, type_check= CredentialUnavailableError):    
      if "az login" in self.get_common().helper_type().string().set_case(string_value= (CredentialUnavailableError(exception)).message, case= "lower"):
        return True
        
    if self.get_common().helper_type().general().is_type(obj= exception, type_check= CredentialUnavailableError):    
      if (HttpResponseError(exception)).status_code is None:
        if "az login" in self.get_common().helper_type().string().set_case(string_value= (HttpResponseError(exception)).message, case= "lower"):
          return True
    
    
    if self.get_common().helper_type().general().is_type(obj= exception, type_check= Exception):    
      if "az login" in self.get_common().helper_type().string().set_case(string_value= f'{exception}', case= "lower"):
        return True
      
    if self.get_common().helper_type().general().is_type(obj= exception, type_check= str):
      exception = self.get_common().helper_type().string().set_case(
        string_value= exception, 
        case= "lower"
      )
      for exceptions_str in ["please run 'az login' to setup account"]:
        if exceptions_str in exception:
          return True
      
    # as I learn better exceptions I want to make sure I am trackign
    # if self.get_common().helper_type().general().is_type(obj= exception, type_check= ClientAuthenticationError): 
       
    
    return False
  def __get_backoff_time(self, count, *args, **kwargs):
    return self.get_common().helper_type().requests().expodential_backoff_wait(attempt= count, auto_sleep= False)

  def sdk_request(self, tenant, lambda_sdk_command, *args, **kwargs):
    max_count = 15
    count = 0
    while True:
      try:
        return lambda_sdk_command()
      except Exception as err:
        if count >= max_count:
          raise self.get_common().exception().exception(
            exception_type = "generic"
          ).not_implemented(
            logger = self.get_common().get_logger(),
            name = "sdk_request",
            message = f"too many attempts: {lambda_sdk_command}",
            exception= err
          )
        
        if(self.check_request_too_many_requests(exception= err)):
          count += 1
          time.sleep(self.__get_backoff_time(count= count))
          continue
        
        if self.check_request_error_login(exception= err):
          return self.login(tenant= tenant, on_login_function= lambda: self.sdk_request(tenant= tenant, lambda_sdk_command=lambda_sdk_command, *args, **kwargs))

        raise err
     
  def get_default_querydefinition(self):
    return QueryDefinition(
      type= "ActualCost",
      timeframe= TimeframeType.THE_LAST_MONTH,
      dataset= QueryDataset(
      aggregation= {
        "totalCost": QueryAggregation(
          name= "Cost",
          function= "Sum"
        )
      },
      grouping= [
        QueryGrouping(
          type= QueryColumnType.DIMENSION,
          name= "SubscriptionId"
        )
      ]
      )
    )
  
  def serialize_resource(self, resource, *args, **kwargs):
    if resource is None:
      return None
    
    if self.get_common().helper_type().general().is_type(obj= resource, type_check= dict):
      return resource

    return resource.serialize(keep_readonly= True)
    
  def deserialize_resource(self, resource, aztype):
    if resource is None:
      return None

    return aztype.deserialize(resource)
  
  def get_resource_name(self, resource, *args, **kwargs):
    if resource is None:
      return None

    if self.get_common().helper_type().general().is_type(obj= resource, type_check= str):
      return resource
    
    if self.get_common().helper_type().general().is_type(obj= resource, type_check= dict):
      return self.get_resource_name(resource= resource.get("extra_name") if not self.get_common().helper_type().string().is_null_or_whitespace(string_value=resource.get("extra_name")) else resource.get("name"))

    return self.get_resource_name(resource= getattr(resource, "name"))

  def get_resource_id_short(self, resource, include_resource_group = False, *args, **kwargs):
    resource_id = self.get_resource_id(resource= resource)
    resource_id = resource_id[resource_id.rfind("/resourcegroups/"):]

    if include_resource_group:
      return resource_id

    return resource_id.append(resource_id[resource_id.rfind("/providers/"):])

  def get_resource_id(self, resource, *args, **kwargs):
    if resource is None:
        return None
    
    if self.get_common().helper_type().general().is_type(obj= resource, type_check= str):
      return resource

    if self.get_common().helper_type().general().is_type(obj= resource, type_check= dict):
      if "extra_id" in resource and resource.get("extra_id") is not None:
        return self.get_common().helper_type().string().set_case(
          string_value= resource.get("extra_id"), 
          case= "lower"
        )
      
      return self.get_common().helper_type().string().set_case(
          string_value= resource.get("id"), 
          case= "lower"
        )

    return self.get_common().helper_type().string().set_case(
      string_value=resource.id, 
      case= "lower"
    )
  
  def get_resource_group_from_resource(self, resource, *args, **kwargs):
    if resource is None:
        return None

    if self.get_common().helper_type().general().is_type(obj= resource, type_check= str):
      return resource

    if self.get_common().helper_type().general().is_type(obj= resource, type_check= dict):
      if "extra_resourcegroups" in resource and resource.get("extra_resourcegroups") is not None:
        return resource.get("extra_resourcegroups")[0]
      
      return resource.get("resource_group")
      
    if hasattr(resource, "resource_group"):
      return resource.resource_group 
    
    resource_id_split = self.get_common().helper_type().string().split(
      string_value= self.get_common().helper_type().string().set_case(
        string_value= self.get_resource_id(resource= resource), 
        case= "lower"),
      separator="/",
      regex_split= False
    )
    return resource_id_split[resource_id_split.index("resourcegroups") + 1]
  
  def get_resource_location(self, resource, *args, **kwargs):
    if resource is None:
      return None

    if not self.get_common().helper_type().general().is_type(obj= resource, type_check= str):
      if self.get_common().helper_type().general().is_type(obj= resource, type_check= dict):
          return self.get_resource_location(resource= resource.get("extra_region") if not self.get_common().helper_type().string().is_null_or_whitespace(string_value=resource.get("extra_region")) else resource.get("location"))
      return self.get_resource_location(resource= getattr(resource, "location"))

    return resource
  
  def get_tenant_prefix(self, *args, **kwargs):
    return "/tenants/"

  def get_account_prefix(self, *args, **kwargs):
    return "/subscriptions/"
  
  def get_account_name(self, account, *args, **kwargs):
    if account is None:
      return None
    if self.get_common().helper_type().general().is_type(obj= account, type_check= str):
      return account.strip()
    
    name_options = ["display_name", "displayname", "name"]

    if self.get_common().helper_type().general().is_type(obj= account, type_check= dict):
      for key, value in account.items():
        if self.get_common().helper_type().string().set_case(string_value= key, case= "lower") in name_options:
          return value.strip()
    
    for att in dir(account):
      if self.get_common().helper_type().string().set_case(string_value= att, case= "lower") in name_options:
        return getattr(account, att).strip()
    
    raise self.get_common().exception().exception(
      exception_type = "generic"
    ).not_implemented(
      logger = self.get_common().get_logger(),
      name = "account",
      message = f"Unknown account object: {account}."
    )

  def get_account_id(self, account, *args, **kwargs):
    if account is None:
      return None
    if self.get_common().helper_type().general().is_type(obj= account, type_check= str):
      return self.get_common().helper_type().string().set_case(string_value= account, case= "lower").strip()
    
    id_options = ["subscriptionid", "subscription_id", "id"]
    
    if self.get_common().helper_type().general().is_type(obj= account, type_check= dict):
      for key, value in account.items():
        if self.get_common().helper_type().string().set_case(string_value= key, case= "lower") in id_options:
          return self.get_common().helper_type().string().set_case(string_value= value, case= "lower").strip() if not self.get_common().helper_type().string().set_case(string_value= value, case= "lower").startswith(self.get_account_prefix()) else self.get_common().helper_type().string().split(string_value= value, separator= "/")[-1]

    for att in dir(account):
      if self.get_common().helper_type().string().set_case(string_value= att, case= "lower") in id_options:
        account_id = getattr(account, att)
        return self.get_common().helper_type().string().set_case(string_value= account_id, case= "lower").strip() if not self.get_common().helper_type().string().set_case(string_value= account_id, case= "lower").startswith(self.get_account_prefix()) else self.get_common().helper_type().string().split(string_value= account_id, separator= "/")[-1]
    
    raise self.get_common().exception().exception(
      exception_type = "generic"
    ).not_implemented(
      logger = self.get_common().get_logger(),
      name = "account",
      message = f"Unknown account object: {account}."
    )
  
  def make_account(self, **kwargs):    
    account = {}

    for key, value in kwargs.items():
      if self.get_common().helper_type().string().set_case(string_value= key, case= "lower") == "id":
        account["Id"] = self.get_common().helper_type().string().set_case(string_value= value, case= "lower").strip()
        continue
      if self.get_common().helper_type().string().set_case(string_value= key, case= "lower") == "name":
        account["Name"] = value.strip()
        continue
        
    
    return account
  
  
  def get_tenant_id(self, tenant, is_account = False, *args, **kwargs):
    if tenant is None:
      return None
    if self.get_common().helper_type().general().is_type(obj= tenant, type_check= str):
      return self.get_common().helper_type().string().set_case(string_value= tenant, case= "lower")
    
    id_options = ["tenantid", "tenant_id", "id"] if not is_account else ["tenantid", "tenant_id"]
    
    if self.get_common().helper_type().general().is_type(obj= tenant, type_check= dict):
      for key, value in tenant.items():
        if self.get_common().helper_type().string().set_case(string_value= key, case= "lower") in id_options:
          return self.get_common().helper_type().string().set_case(string_value= value, case= "lower") if not self.get_common().helper_type().string().set_case(string_value= value, case= "lower").startswith(self.get_tenant_prefix()) else self.get_common().helper_type().string().split(string_value= value, separator= "/")[-1]

    for att in dir(tenant):
      if self.get_common().helper_type().string().set_case(string_value= att, case= "lower") in id_options:
        tenant_id = getattr(tenant, att)
        return self.get_common().helper_type().string().set_case(string_value= tenant_id, case= "lower") if not self.get_common().helper_type().string().set_case(string_value= tenant_id, case= "lower").startswith(self.get_tenant_prefix()) else self.get_common().helper_type().string().split(string_value= tenant_id, separator= "/")[-1]
    
    raise self.get_common().exception().exception(
      exception_type = "generic"
    ).not_implemented(
      logger = self.get_common().get_logger(),
      name = "tenant",
      message = f"Unknown tenant object: {tenant}."
    )
  
  def make_tenant(self, **kwargs):    
    tenant = {}

    for key, value in kwargs.items():
      if self.get_common().helper_type().string().set_case(string_value= key, case= "lower") == "id":
        tenant["Id"] = self.get_common().helper_type().string().set_case(string_value= value, case= "lower")
        continue
      
      if self.get_common().helper_type().string().set_case(string_value= key, case= "lower") == "name":
        tenant["Name"] = value
        continue
        
    
    return tenant
    

