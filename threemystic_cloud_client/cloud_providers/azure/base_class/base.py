from threemystic_cloud_client.cloud_providers.base_class.base import cloud_client_provider_base as base
from azure.mgmt.costmanagement.models import TimeframeType, OperatorType, QueryColumnType, QueryDefinition, QueryTimePeriod, QueryDataset, QueryAggregation, QueryGrouping, QueryFilter, QueryComparisonExpression
from azure.core.exceptions import HttpResponseError, ClientAuthenticationError
import time
import math

class cloud_client_provider_azure_base(base):
  def __init__(self, *args, **kwargs):
    super().__init__(provider= "azure", *args, **kwargs)

    self.links = {
      "cli_doc_link": "https://learn.microsoft.com/en-us/cli/azure/install-azure-cli"
    }

  def check_request_too_many_requests(self, exception, *args, **kwargs):
    if not self.get_common().helper_type().general().is_type(obj= exception, type_check= HttpResponseError):
      return False       
    
    if (HttpResponseError(exception)).status_code == 429:
      return True
    
    if "too many requests" in self.get_common().helper_type().string().set_case(string_value= (HttpResponseError(exception)).message, case= "lower"):
      return True
    
    return False
  
  def check_request_error_login(self, exception, *args, **kwargs):
    if self.get_common().helper_type().general().is_type(obj= exception, type_check= HttpResponseError):    
      if (HttpResponseError(exception)).status_code is None:
        if "az login" in self.get_common().helper_type().string().set_case(string_value= (HttpResponseError(exception)).message, case= "lower"):
          return True
    
    # as I learn better exceptions I want to make sure I am trackign
    # if self.get_common().helper_type().general().is_type(obj= exception, type_check= ClientAuthenticationError): 
       
    
    return False
  def __get_backoff_time(self, count, *args, **kwargs):
    max_backoff_time = 32
    back_off_time = math.pow(2, count)
    if back_off_time > max_backoff_time:
      back_off_time = max_backoff_time
    
    return back_off_time

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
          return self.login(tenant= tenant, on_login_function= lambda: self.sdk_request(tenant= tenant, lambda_sdk_command=lambda_sdk_command, *args, **kwargs)).get("result")

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
  
  def serialize_azresource(self, resource, *args, **kwargs):
    if resource is None:
      return None

    return resource.serialize(keep_readonly= True)
    
  def deserialize_azresource(self, resource, aztype):
    if resource is None:
      return None

    return aztype.deserialize(resource)

  def get_resource_name_from_resource(self, resource, *args, **kwargs):
    if resource is None:
        return None

    return resource.name

  def get_resource_id_from_resource(self, resource, *args, **kwargs):
    if resource is None:
        return None

    return self.get_common().helper_type().string().set_case(
      string_value=resource.id, 
      case= "lower"
    )
  
  def get_resource_group_from_resource(self, resource, *args, **kwargs):
    if hasattr(resource, "resource_group"):
      return resource.resource_group 
    
    resource_id_split = self.get_common().helper_type().string().split(
      string_value= self.get_common().helper_type().string().set_case(
        string_value= self.get_resource_id_from_resource(resource= resource), 
        case= "lower"),
      separator="/",
      regex_split= False
    )
    return resource_id_split[resource_id_split.index("resourcegroups") + 1]
  
  def get_azresource_location(self, resource, *args, **kwargs):
    if resource is None:
      return None

    if not self.get_common().helper_type().general().is_type(obj= resource, type_check= str):
      if self.get_common().helper_type().general().is_type(obj= resource, type_check= dict):
          return self.get_azresource_location(resource= resource.get("extra_region") if not self.get_common().helper_type().string().is_null_or_whitespace(string_value=resource.get("extra_region")) else resource.get("location"))
      return self.get_azresource_location(resource= getattr(resource, "location"))

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
    
    name_options = ["display_name", "name"]

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
    

