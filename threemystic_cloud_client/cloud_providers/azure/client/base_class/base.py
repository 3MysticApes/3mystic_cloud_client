from threemystic_cloud_client.cloud_providers.azure.base_class.base import cloud_client_provider_azure_base as base
import abc
from io import StringIO
from knack.log import CLI_LOGGER_NAME
import logging
from azure.cli.core import get_default_cli

class cloud_client_azure_client_base(base):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    
  def _get_credential(self, *args, **kwargs):
    if hasattr(self, "_credentials"):
      return self._credentials
    
    self._credentials = {}
    return self._get_credential()
  
  @abc.abstractclassmethod
  def get_tenant_credential(self, tenant_id = None, *args, **kwargs):
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
  

  def __get_accounts(self, refresh = False, *args, **kwargs):    
    if hasattr(self, "_accounts") and not refresh:
      return self._accounts
    
    bashCall = "az account list{} --only-show-errors".format(" --refresh" if refresh else "")
    return_result = self._az_cli(bashCall, on_login_function = lambda: self.get_accounts(refresh = refresh))

    if len(return_result["error"])>0:
      if return_result["exit_code"] != 0:
          raise Exception(return_result["error"])
      else:
          logging.warning(msg=return_result["error"])

    self._accounts = return_result["result"]
    return self.__get_accounts()
  
  def get_accounts(self, refresh = False, account = None, *args, **kwargs):
    if account is None:
      return self.__get_accounts()
    
    if self.get_common().helper_type().general().is_type(obj= account, type_check= str) and not self.get_common().helper_type().string().is_null_or_whitespace(string_value= account):
      account = [ acct.strip() for acct in account.split(",") if not self.get_common().helper_type().string().is_null_or_whitespace(string_value= acct) ]
    
    if not self.get_common().helper_type().general().is_type(obj= account, type_check= list):
      self.get_common().get_logger().warning(f'unknown data type for accounts {type(account)}, when trying to get accounts')
      return self.__get_accounts()
    
    search_accounts = [ acct for acct in account if not self.get_common().helper_type().string().set_case(string_value= acct, case= "lower").startswith("-") ]
    exclude_accounts = [ acct for acct in account if self.get_common().helper_type().string().set_case(string_value= acct, case= "lower").startswith("-") ]

    return [ acct for acct in self.__get_accounts() if f'-{self.get_account_id(account= acct)}' not in exclude_accounts and  (len(search_accounts) < 1 or self.get_common().helper_type().list().find_item(data= search_accounts, filter= lambda item: item == self.get_account_id(account= acct)) is not None) ]
  
  # def get_subscriptions(self, tenant = None, refresh = False):      
  #   if self._subscriptions is None or refresh is True:
  #     self.get_accounts(refresh = True)
    
  #   if self._subscriptions is None or refresh:
  #     self._load_subscriptions(refresh= True)

  #   if tenant is None:
  #     all_subscriptions = []
  #     for _, subscriptions in self._subscriptions.items():
  #       all_subscriptions += subscriptions
      
  #     return all_subscriptions

  #   if self._subscriptions.get(tenant["tenantId"]) is None:
  #     tenants = self.get_tenants(refresh= refresh)
  #     if common.FindListItem(tenants, lambda item: item["tenantId"] == tenant["tenantId"]) is None:
  #       raise Exception("Tenant not Found")
      
  #     return self._subscriptions.get(tenant["tenantId"])    

  #   return self._subscriptions[tenant["tenantId"]]
  
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