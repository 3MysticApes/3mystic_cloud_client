from threemystic_cloud_client.cloud_providers.azure.base_class.base import cloud_client_provider_azure_base as base
from abc import abstractmethod
from io import StringIO
from knack.log import CLI_LOGGER_NAME
import logging
from azure.core.exceptions import HttpResponseError
from azure.cli.core import get_default_cli
from azure.mgmt.resource.subscriptions import SubscriptionClient as ResourceSubscriptionClient
from azure.mgmt.resourcegraph import ResourceGraphClient
from azure.mgmt.resourcegraph.models import QueryRequestOptions, QueryRequest

class cloud_client_azure_client_base(base):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  
  @abstractmethod
  def _get_tenant_credential(self, tenant = None, *args, **kwargs):
    pass
  
  def get_tenant_credential_full(self, tenant = None, *args, **kwargs):
    if self.get_common().helper_type().string().is_null_or_whitespace(string_value= self.get_tenant_id(tenant= tenant)):
      raise self.get_common().exception().exception(
        exception_type = "argument"
      ).type_error(
        logger = self.get_common().get_logger(),
        name = "tenant_id",
        message = f"tenant_id cannot be null or whitespace"
      )
    
    if (self._get_credential(account_id= self.get_tenant_id(tenant= tenant)) is not None
        and len(self._get_credential(account_id= self.get_tenant_id(tenant= tenant))) > 1):
      return self._get_credential(account_id= self.get_tenant_id(tenant= tenant))
    
    credentials = self._get_tenant_credential(tenant= tenant)
    try:
      jwt_token = self.decode_jwt_token(
        token= credentials.get_token("https://graph.microsoft.com/.default").token
      )
    except Exception as err:
      jwt_token = None
      self.get_common().get_logger().exception(
        msg= "could not generate token to decode",
        extra= {
          "exception": err
        }
      )
      if self.check_request_error_login(exception= err):      
        credentials = self._login(
          tenant = tenant,
          on_login_function = lambda: self._get_tenant_credential(tenant= tenant)
        )
        try:
          jwt_token = self.decode_jwt_token(
            token= credentials.get_token("https://graph.microsoft.com/.default").token
          )
        except Exception as reattempt_err:
          jwt_token = None
          
          self.get_common().get_logger().exception(
            msg= "reattempt: could not generate token to decode",
            extra= {
              "exception": reattempt_err
            }
          )
    
    self._get_credential(account_id= self.get_tenant_id(tenant= tenant) )["credentials"] = credentials
    self._get_credential(account_id= self.get_tenant_id(tenant= tenant) )["jwt"] = jwt_token

    return self.get_tenant_credential_full(tenant= tenant, *args, **kwargs)
  
  def get_tenant_credential(self, tenant = None, *args, **kwargs):
    return self.get_tenant_credential_full(tenant= tenant, *args, **kwargs).get("credentials")
         
  def get_tenants(self, refresh = False, tenant = None, *args, **kwargs):
    if tenant is None:
      return self.__get_tenants(refresh= refresh)
    
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
    
    bashCall = "az account tenant list"
    return_result = self._az_cli(bashCall, on_login_function = lambda: self.get_tenants(refresh = refresh))

    if len(return_result["error"])>0:
      if return_result.get("exit_code") != 0:
        raise Exception(return_result["error"])
      else:
        logging.warning(msg=return_result["error"])

    self._tenants = return_result.get("result")
    return self.__get_tenants()
  

  def __get_raw_accounts(self, refresh = False, *args, **kwargs):    
    if hasattr(self, "_raw_accounts") and not refresh:
      return self._raw_accounts
    
    bashCall = "az account list{}".format(" --refresh" if refresh else "")
    return_result = self._az_cli(bashCall, on_login_function = lambda: self.get_accounts(refresh = refresh))

    if len(return_result["error"])>0:
      if return_result["exit_code"] != 0:
          raise Exception(return_result["error"])
      else:
          logging.warning(msg=return_result["error"])

    self._raw_accounts = return_result["result"]
    
    return self.__get_raw_accounts()
  
  def get_group_accounts_by_tenant(self, accountList = None, refresh= False, *args, **kwargs):
    if accountList is None:
      accountList = self.get_raw_accounts(refresh= refresh *args, **kwargs)
    
    return_data = {}
    for account in accountList:
      if return_data.get(self.get_tenant_id(tenant= account, is_account= True)) is None:
        return_data[self.get_tenant_id(tenant= account, is_account= True)] = []
      
      return_data[self.get_tenant_id(tenant= account, is_account= True)].append(account)
    
    return return_data


  def get_raw_accounts(self, refresh = False, account = None, tenant = None, *args, **kwargs):
    if account is None and tenant is None:
      return self.__get_raw_accounts(refresh= refresh, *args, **kwargs)
    
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
  
  def __get_accounts_resourcecontainers_accounts(self, tenant, accounts,  *args, **kwargs):  
    if not self.get_common().helper_type().general().is_type(obj= accounts, type_check= list):      
      raise self.get_common().exception().exception(
        exception_type = "argument"
      ).type_error(
        logger = self.get_common().get_logger(),
        name = "accounts",
        message = f"Argument accounts is not of type list"
      )
    
    if len(accounts) < 1:
      return None

    resource_client = ResourceGraphClient(credential= self.get_tenant_credential(tenant= tenant))
    resource_query_options = QueryRequestOptions(result_format="objectArray")
    
    resource_query = QueryRequest(subscriptions=[self.get_account_id(account= acct) for acct in accounts], query="resourcecontainers | where type == 'microsoft.resources/subscriptions'", options=resource_query_options)
    try:
      return self.sdk_request(tenant= tenant, lambda_sdk_command=lambda: resource_client.resources(resource_query))
    except HttpResponseError as err:   
               
      raise self.get_common().exception().exception(
        exception_type = "generic"
      ).type_error(
        logger = self.get_common().get_logger(),
        name = "AccessDenied",
        message = f"Could not query ResourceGraphClient - {err.response.status_code}: {err.response.text}",
      )
    except Exception as err:
      raise self.get_common().exception().exception(
        exception_type = "generic"
      ).type_error(
        logger = self.get_common().get_logger(),
        name = "GeneralException",
        message = f"Could not query ResourceGraphClient - {err}",
      )
    
  def __get_accounts_resourcecontainers_managementgroups(self, tenant, *args, **kwargs):  
    resource_client = ResourceGraphClient(self.get_tenant_credential(tenant= tenant))
    resource_query_options = QueryRequestOptions(result_format="objectArray")
    resource_query = QueryRequest(management_groups=[self.get_tenant_id(tenant= tenant)], query="resourcecontainers | where type == 'microsoft.resources/subscriptions'", options=resource_query_options)
    try:
      return self.sdk_request(tenant= tenant, lambda_sdk_command=lambda: resource_client.resources(resource_query))
    except HttpResponseError as err:       
      if err.status_code == 403:
        return self.__get_accounts_resourcecontainers_accounts(tenant= tenant, accounts= self.get_raw_accounts(tenant= tenant), *args, **kwargs)

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
    
  def __get_accounts(self, refresh = False, *args, **kwargs):   
    
    accounts = self.get_group_accounts_by_tenant(refresh= refresh, *args, **kwargs)
    subscriptions = {}
    for tenant_id, tenant_accounts in accounts.items():
      # pulls all subscriptions to know which ones are resourcecontainers
      resource_query_results = self.__get_accounts_resourcecontainers_accounts(tenant= tenant_id, accounts= tenant_accounts)

      subscription_details = {self.get_account_id(account= account):account for account in resource_query_results.data} if resource_query_results is not None else {}
      
      resource_subscription_client = ResourceSubscriptionClient(
        (self.get_tenant_credential(tenant= tenant_id))
      )  

      subscriptions[self.get_tenant_id(tenant= tenant_id)] = [resource_subscription for resource_subscription in self.sdk_request(tenant= tenant_id, lambda_sdk_command=lambda: resource_subscription_client.subscriptions.list())]

      for subscription in subscriptions[self.get_tenant_id(tenant= tenant_id)]:
        if subscription_details.get(self.get_account_id(account= subscription)) is None:
          subscription.resource_container = False
          continue
        
        subscription.resource_container = True
    
    return self.get_common().helper_type().list().flatten(data= list(subscriptions.values()))
            
  def get_accounts(self, account= None, tenant= None, refresh= False, *args, **kwargs):      
    return self.__get_accounts(account= account, tenant= tenant, refresh= refresh, *args, **kwargs)


  def _az_cli(self, command, on_login_function = None, *args, **kwargs):

    az_cli = get_default_cli()
    stdout_buffer = StringIO()
    log_buffer = StringIO()

    az_cli_logger = logging.getLogger(CLI_LOGGER_NAME)
    az_cli_handler = logging.StreamHandler(stream=log_buffer)
    az_cli_handler.setLevel(logging.WARNING)
    
    try:
      az_cli_args = self.get_common().helper_type().string().split(string_value= command, separator="\\s")
      az_cli_args.append("--only-show-errors")

      if az_cli_args[0].lower() == "az":
        az_cli_args.pop(0)

      if az_cli_args[0].lower() != "login":
        az_cli_logger.addHandler(az_cli_handler)
      
      exit_code = az_cli.invoke(
        args= az_cli_args, 
        out_file=stdout_buffer) or 0
        
    except SystemExit as ex:
      exit_code = ex.code
    
    error_message = log_buffer.getvalue()
    if exit_code == 0:
      if az_cli_args[0].lower() == "login":
        self._clear_credential()
        if on_login_function is not None:
          # look to update this to pull a page of subscriptions and put this in some sort of loop to retry
          # thought create a validate login method.
          return on_login_function()
    
      return {
        "exit_code": exit_code,
        "result": self.get_common().helper_json().loads(data= stdout_buffer.getvalue()) if not self.get_common().helper_type().string().is_null_or_whitespace(string_value= stdout_buffer.getvalue()) else None,
        "error": error_message
      }
    
    
    
    if self.check_request_error_login(exception= error_message):
      return self._az_cli("az login", on_login_function = on_login_function)
    
    return {
      "exit_code": exit_code,
      "result": self.get_common().helper_json().loads(data= stdout_buffer.getvalue()) if not self.get_common().helper_type().string().is_null_or_whitespace(string_value= stdout_buffer.getvalue()) else None,
      "error": error_message
    }
  
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
      
    if "name" not in tags:
      name_options = ["display_name", "displayname", "name"]

      if not self.get_common().helper_type().general().is_type(obj= resource, type_check= dict):
        for att in dir(resource):
          if self.get_common().helper_type().string().set_case(string_value= att, case= "lower") in name_options:
            tags["name"] = getattr(resource, att).strip()
            return tags

      for att in resource.keys():
        if self.get_common().helper_type().string().set_case(string_value= att, case= "lower") in name_options:
          tags["name"] = resource.get(att).strip()
          return tags
    return tags
  