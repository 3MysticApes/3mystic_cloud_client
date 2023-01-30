from threemystic_cloud_client.base_class.base import base


class cloud_client(base): 
  """This is a library to help with the interaction with the cloud providers"""

  def __init__(self, logger = None, common = None, *args, **kwargs) -> None: 
    super().__init__(common= common, logger_name= "cloud_client", logger= logger, *args, **kwargs)
    
  def version(self, *args, **kwargs):
    if hasattr(self, "_version"):
      return self._version
    import threemystic_cloud_client.__version__ as __version__
    self._version = __version__.__version__
    return self.version()
    
  def get_supported_providers(self, *args, **kwargs):
    return ["aws", "azure"]

  def init_client(self, provider, *args, **kwargs):
    provider = provider.lower() if provider is not None else ""

    if provider not in self.get_supported_providers():
      raise self.get_common().exception(
        exception_type = "generic"
      ).not_implemented(
        logger = self.logger,
        name = "provider",
        message = f"Unknown Cloud Provided: {provider}.\nSupported Cloud Providers{self.get_supported_providers()}"
      )

    if not hasattr(self, "_client"):
      self._client = {}

    if provider == "azure":
      from domain.azure.client import client_azure as client
      self._client[provider] = client(
        common= self.get_common()
      )
      return
    
    if provider == "aws":
      from domain.aws.controller import client_controller as client
      self._client[provider] = client(
        common= self.get_common()
      )
      return

  def client(self, provider, *args, **kwargs):
    provider = provider.lower() if provider is not None else ""

    if hasattr(self, "_client"):
      if self._client.get(provider) is not None:
        return self._client[provider]
   
    raise self.get_common().exception().exception(
      exception_type = "generic"
    ).not_implemented(
      logger = self.logger,
      name = "provider",
      message = f"Unknown Cloud Provided: {provider}.\nSupported Cloud Providers{self.get_supported_providers()}"
    )