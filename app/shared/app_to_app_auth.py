from msal import ConfidentialClientApplication

from app.config import settings

class GaitA2AAuthentication:

    def __init__(self) -> None:
        super().__init__()
        self.client_id = settings.get_a2a_auth_client()
        self.authority =settings.get_a2a_auth_authority()
        self.tenant_id = settings.get_a2a_auth_tenant()
        self.client_secret_value = settings.get_a2a_auth_client_secret()
        self.audience_client_id = settings.get_a2a_auth_audience()

    def get_access_token(self):
        client_app = ConfidentialClientApplication(
        self.client_id,
        authority=f"{self.authority}/{self.tenant_id}",
        client_credential=self.client_secret_value
        )
        token_response = client_app.acquire_token_for_client(scopes=[f"{self.audience_client_id}/.default"])
        if "access_token" in token_response:
            access_token = token_response['access_token']
            return access_token
        else:
            raise Exception("failed to fetch access token")

gait_a2a_auth = GaitA2AAuthentication()