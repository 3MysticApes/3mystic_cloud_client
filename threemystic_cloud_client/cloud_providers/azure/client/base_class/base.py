from threemystic_cloud_client.cloud_providers.azure.base_class.base import cloud_client_provider_azure_base as base
import abc
from io import StringIO
from knack.log import CLI_LOGGER_NAME
import logging
from azure.core.exceptions import HttpResponseError
from azure.cli.core import get_default_cli
from azure.mgmt.subscription import SubscriptionClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.subscriptions import SubscriptionClient as ResourceSubscriptionClient
from azure.mgmt.resourcegraph import ResourceGraphClient
from azure.mgmt.resourcegraph.models import QueryRequestOptions, QueryRequest

class cloud_client_azure_client_base(base):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    
  def _get_credential(self, *args, **kwargs):
    if hasattr(self, "_credentials"):
      return self._credentials
    
    self._credentials = {}
    return self._get_credential()
  
  @abc.abstractclassmethod
  def get_tenant_credential(self, tenant = None, *args, **kwargs):
    pass
  
  def get_tenants(self, refresh = False, tenant = None, *args, **kwargs):
    if tenant is None:
      return self.__get_tenants()
    
    if self.get_common().helper_type().general().is_type(obj= tenant, type_check= str) and not self.get_common().helper_type().string().is_null_or_whitespace(string_value= tenant):
      tenant = [ acct.strip() for acct in self.get_common().helper_type().string().split(string_value= tenant) if not self.get_common().helper_type().string().is_null_or_whitespace(string_value= acct) ]
    
    if not self.get_common().helper_type().general().is_type(obj= tenant, type_check= list):
      self.get_common().get_logger().warning(f'unknown data type for accounts {type(tenant)}, when trying to get tenants')
      return self.__get_tenants()
    
    search_tenants = [ acct for acct in tenant if not self.get_common().helper_type().string().set_case(string_value= acct, case= "lower").startswith("-") ]
    exclude_tenants = [ acct for acct in tenant if self.get_common().helper_type().string().set_case(string_value= acct, case= "lower").startswith("-") ]

    return [ acct for acct in self.__get_tenants() if f'-{self.get_tenant_id(tenant= acct)}' not in exclude_tenants and (len(search_tenants) < 1 or self.get_common().helper_type().list().find_item(data= search_tenants, filter= lambda item: item == self.get_tenant_id(tenant= acct)) is not None) ]
  
  def __get_tenants(self, refresh = False, *args, **kwargs):    
    if hasattr(self, "_tenants") and not refresh:
      return self._tenants
    
    bashCall = "az account tenant list --only-show-errors"
    return_result = self._az_cli(bashCall, on_login_function = lambda: self.get_tenants(refresh = refresh))

    if len(return_result["error"])>0:
      if return_result["exit_code"] != 0:
          raise Exception(return_result["error"])
      else:
          logging.warning(msg=return_result["error"])

    self._tenants = return_result["result"]
    return self.__get_tenants()
  

  def __get_raw_accounts(self, refresh = False, *args, **kwargs):    
    if hasattr(self, "_raw_accounts") and not refresh:
      return self._raw_accounts
    
    bashCall = "az account list{} --only-show-errors".format(" --refresh" if refresh else "")
    return_result = self._az_cli(bashCall, on_login_function = lambda: self.get_accounts(refresh = refresh))

    if len(return_result["error"])>0:
      if return_result["exit_code"] != 0:
          raise Exception(return_result["error"])
      else:
          logging.warning(msg=return_result["error"])

    self._raw_accounts = return_result["result"]
    return self.__get_raw_accounts()
  
  def get_raw_accounts(self, refresh = False, account = None, tenant = None, *args, **kwargs):
    if account is None and tenant is None:
      return self.__get_raw_accounts(refresh= refresh)
    
    if account is None:
      account = []
    if tenant is None:
      tenant = []

    if self.get_common().helper_type().general().is_type(obj= account, type_check= str) and not self.get_common().helper_type().string().is_null_or_whitespace(string_value= account):
      account = [ self.get_account_id(account= acct) for acct in account.split(",") if not self.get_common().helper_type().string().is_null_or_whitespace(string_value= acct) ]
    
    if self.get_common().helper_type().general().is_type(obj= tenant, type_check= str) and not self.get_common().helper_type().string().is_null_or_whitespace(string_value= tenant):
      tenant = [ self.get_tenant_id(tenant= acct) for acct in tenant.split(",") if not self.get_common().helper_type().string().is_null_or_whitespace(string_value= acct) ]
    
    if self.get_common().helper_type().general().is_type(obj= account, type_check= dict):
      tenant = [ account ]

    if self.get_common().helper_type().general().is_type(obj= tenant, type_check= dict):
      tenant = [ tenant ]
    
    if not self.get_common().helper_type().general().is_type(obj= account, type_check= list) and not self.get_common().helper_type().general().is_type(obj= tenant, type_check= list):
      if not self.get_common().helper_type().general().is_type(obj= account, type_check= list):
        self.get_common().get_logger().warning(f'unknown data type for accounts {type(account)}, when trying to get accounts')
      if not self.get_common().helper_type().general().is_type(obj= tenant, type_check= list):
        self.get_common().get_logger().warning(f'unknown data type for tenants {type(tenant)}, when trying to get tenants')
      
      return self.__get_raw_accounts()
    
    search_accounts = [ self.get_account_id(account= acct) for acct in account if not self.get_account_id(account= acct).startswith("-") ]
    exclude_accounts = [ self.get_account_id(account= acct) for acct in account if self.get_account_id(account= acct).startswith("-") ]

    search_tenants = [ self.get_tenant_id(tenant= acct) for acct in tenant if not self.get_tenant_id(tenant= acct).startswith("-") ]
    exclude_tenants = [ self.get_tenant_id(tenant= acct) for acct in tenant if self.get_tenant_id(tenant= acct).startswith("-") ]
    
    return [ acct for acct in self.__get_raw_accounts() if 
              (len(account) > 0 and (
              f'-{self.get_account_id(account= acct)}' not in exclude_accounts and 
              (len(search_accounts) < 1 or self.get_common().helper_type().list().find_item(data= search_accounts, filter= lambda item: item == self.get_account_id(account= acct)) is not None) 
              )) and
              (len(tenant) > 0 and (
              f'-{self.get_tenant_id(tenant= acct)}' not in exclude_tenants and 
              (len(search_tenants) < 1 or self.get_common().helper_type().list().find_item(data= search_tenants, filter= lambda item: item == self.get_tenant_id(tenant= acct)) is not None) 
              ))
            ] 
  
  def __get_accounts_resourcecontainers_subscriptions(self, tenant, *args, **kwargs):  
    resource_client = ResourceGraphClient(self.get_tenant_credential(tenant= tenant))
    resource_query_options = QueryRequestOptions(result_format="objectArray")
    
    subscription_query = self.get_raw_accounts(tenant= tenant)
    if(len(subscription_query) < 1):
      return None
    resource_query = QueryRequest(subscriptions=subscription_query, query="resourcecontainers | where type == 'microsoft.resources/subscriptions'", options=resource_query_options)
    try:
      return resource_client.resources(resource_query)
    except HttpResponseError as err:      
      raise self.get_common().exception().exception(
        exception_type = "generic"
      ).type_error(
        logger = self.get_common().get_logger(),
        name = "AccessDenied",
        message = f"Could not query ResourceGraphClient",
        exception= err
      )
    except Exception as err:
      raise self.get_common().exception().exception(
        exception_type = "generic"
      ).type_error(
        logger = self.get_common().get_logger(),
        name = "GeneralException",
        message = f"Could not query ResourceGraphClient",
        exception= err
      )
    
  def __get_accounts_resourcecontainers_managementgroups(self, tenant, *args, **kwargs):  
    resource_client = ResourceGraphClient(self.get_tenant_credential(tenant= tenant))
    resource_query_options = QueryRequestOptions(result_format="objectArray")
    resource_query = QueryRequest(management_groups=[self.get_tenant_id(tenant= tenant)], query="resourcecontainers | where type == 'microsoft.resources/subscriptions'", options=resource_query_options)
    try:
      return resource_client.resources(resource_query)
    except HttpResponseError as err:       
      if err.status_code == 403:
        return self.__get_accounts_resourcecontainers_subscriptions(tenant= tenant, *args, **kwargs)
      
      
      if err.status_code is None:
        if "az login" in self.get_common().helper_type().string().set_case(string_value= err.message, case= "lower"):
          return self.login(tenant= tenant, on_login_function= lambda: self.set_default_account(tenant=tenant)).get("result")

      raise self.get_common().exception().exception(
        exception_type = "generic"
      ).type_error(
        logger = self.get_common().get_logger(),
        name = "AccessDenied",
        message = f"Could not query ResourceGraphClient",
        exception= err
      )
    except Exception as err:
      raise self.get_common().exception().exception(
        exception_type = "generic"
      ).type_error(
        logger = self.get_common().get_logger(),
        name = "GeneralException",
        message = f"Could not query ResourceGraphClient",
        exception= err
      )
    
  def _get_accounts(self, refresh = False, *args, **kwargs):   
    if hasattr(self, "_subscriptions") and not refresh:
      return self._subscriptions
    
    tenants = self.get_tenants(refresh= refresh)
    
    subscriptions = {}
    for tenant in tenants:
      # pulls all subscriptions to know which ones are resourcecontainers
      resource_query_results = self.__get_accounts_resourcecontainers_managementgroups(tenant= tenant)
      
      subscription_details = {self.get_account_id(account= account):account for account in resource_query_results.data} if resource_query_results is not None else {}
      
      resource_subscription_client = ResourceSubscriptionClient(
        (self.get_tenant_credential(tenant= tenant))
      )  

      subscriptions[self.get_tenant_id(tenant= tenant)] = [resource_subscription for resource_subscription in resource_subscription_client.subscriptions.list()]

      for subscription in subscriptions[self.get_tenant_id(tenant= tenant)]:
        if subscription_details.get(subscription.id.lower()) is None:
          subscription.resource_container = False
          continue
        
        subscription.resource_container = True
    
    self._subscriptions = subscriptions
    return self._get_accounts()
            
  def get_accounts(self, tenant = None, refresh = False, *args, **kwargs):      

    if tenant is None:
      return self._get_accounts(refresh= refresh)

    if self._get_accounts().get(self.get_tenant_id(tenant= tenant)) is not None:
      return self._get_accounts().get(self.get_tenant_id(tenant= tenant))
    
    raise self.get_common().exception().exception(
      exception_type = "argument"
    ).type_error(
      logger = self.logger,
      name = "tenant",
      message = f"Tenant Not found: {tenant}"
    )
    

  @abc.abstractclassmethod
  def login(self, *args, **kwargs):
    pass

  def _az_cli(self, command, on_login_function = None, *args, **kwargs):

    az_cli = get_default_cli()
    stdout_buffer = StringIO()
    log_buffer = StringIO()

    az_cli_logger = logging.getLogger(CLI_LOGGER_NAME)
    az_cli_handler = logging.StreamHandler(stream=log_buffer)
    az_cli_handler.setLevel(logging.WARNING)
    
    try:
      az_cli_args = self.get_common().helper_type().string().split(string_value= command, separator="\\s")

      if az_cli_args[0].lower() == "az":
        az_cli_args.pop(0)

      if az_cli_args[0].lower() != "login":
        az_cli_logger.addHandler(az_cli_handler)
      
      exit_code = az_cli.invoke(
        args= az_cli_args, 
        out_file=stdout_buffer) or 0
        
    except SystemExit as ex:
      exit_code = ex.code

    if exit_code == 0:
      return {
        "exit_code": exit_code,
        "result": self.get_common().helper_json().loads(data= stdout_buffer.getvalue()) if not self.get_common().helper_type().string().is_null_or_whitespace(string_value= stdout_buffer.getvalue()) else None,
        "error": log_buffer.getvalue()
      }
    if self.error_trigger_login(log_buffer.getvalue()):
      return {
        "result": self.auto_login(on_login_function = on_login_function, require_tenant_id= self.error_login_requires_tenant(log_buffer.getvalue()))
      }
    
    return {
      "result": self.get_common().helper_json().loads(data= stdout_buffer.getvalue()) if not self.get_common().helper_type().string().is_null_or_whitespace(string_value= stdout_buffer.getvalue()) else None,
      "error": log_buffer.getvalue()
    }