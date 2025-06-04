import base64
import json
from urllib.request import urlopen

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError, DecodeError
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from starlette.authentication import (
    AuthenticationBackend,
    SimpleUser,
    AuthCredentials,
)
from fastapi import Request
from loguru import logger

from .exceptions import UnauthorizedException
from app.config import settings


class AzureBearerAuthentication(AuthenticationBackend):
    """
    Verify JWTs issued by Azure AD. Ensures the user belongs to the configured
    AD group (AZ_T_PDP_Validation).
    """

    def __init__(self):
        # JWKS and Issuer URLs
        self.jwks_url = f"https://login.microsoftonline.com/{settings.get_azure_ad_tenant()}/discovery/v2.0/keys"
        self.issuer = settings.get_azure_ad_issuer()
        self.audience = settings.get_azure_ad_audience()
        self.validation_group = settings.get_validation_ad_group()

    async def authenticate(self, request: Request):
        # Allow OPTIONS
        if request.method.lower() == "options":
            return

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.lower().startswith("bearer "):
            raise UnauthorizedException("Missing or invalid Authorization header.")

        token = auth_header.split(" ", 1)[1]
        try:
            unverified_header = jwt.get_unverified_header(token)
            jwks = json.loads(urlopen(self.jwks_url).read())
            rsa_key = self._find_rsa_key(unverified_header, jwks)
            public_key = self._rsa_pem_from_jwk(rsa_key)

            payload = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                audience=self.audience,
                issuer=self.issuer,
            )
        except (DecodeError, InvalidTokenError):
            raise UnauthorizedException("Invalid token.")
        except ExpiredSignatureError:
            raise UnauthorizedException("Token expired.")
        except Exception as e:
            logger.error(f"Azure AD authentication error: {e}")
            raise UnauthorizedException("Authentication failed.")

        # Check AD group membership in token (assumes 'groups' claim)
        groups = payload.get("groups", [])
        if self.validation_group not in groups:
            raise UnauthorizedException("User not in allowed AD group.")

        # Return AuthCredentials() (no scopes) and a SimpleUser
        username = payload.get("preferred_username", payload.get("upn", None))
        return AuthCredentials(["authenticated"]), SimpleUser(username)

    def _find_rsa_key(self, unverified_header, jwks):
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                return key
        raise UnauthorizedException("Unable to find appropriate key.")

    @staticmethod
    def _rsa_pem_from_jwk(jwk):
        e = AzureBearerAuthentication._b64_to_int(jwk["e"])
        n = AzureBearerAuthentication._b64_to_int(jwk["n"])
        public_numbers = RSAPublicNumbers(e, n)
        public_key = public_numbers.public_key(default_backend())
        pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        return pem

    @staticmethod
    def _b64_to_int(val: str) -> int:
        data = base64.urlsafe_b64decode(val + "==")
        return int.from_bytes(data, "big")
