from threemystic_cloud_client.cloud_providers.aws.client.base import cloud_client_aws_client_base as base

class cloud_client_aws_client_sso(base):
  def __init__(self, *args, **kwargs):
    super().__init__(logger_name= "cloud_client_aws_client_sso", provider= "aws", *args, **kwargs)

    if(self.get_profile()["auth_method"].lower() != "sso"):
      raise self._main_reference.exception().exception(
          exception_type = "generic"
        ).type_error(
          logger = self.get_common().get_logger(),
          name = "Profile Authentication Invalid",
          message = f"Profile Authentication Invalid - {self.get_profile()['profile_name']}"
        )