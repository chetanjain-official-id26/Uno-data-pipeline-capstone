from cryptography.fernet import Fernet, InvalidToken

from app.core.config import get_settings


class CredentialEncryptionError(Exception):
    """Raised when credential encryption/decryption fails."""


class CredentialEncryptor:
    """Encrypts and decrypts external system credentials.

    Plaintext credentials should only exist in application memory
    for the shortest possible duration.
    """

    def __init__(self) -> None:
        settings = get_settings()

        try:
            self.fernet = Fernet(
                settings.credential_encryption_key.encode()
            )
        except Exception as exc:
            raise CredentialEncryptionError(
                "Invalid credential encryption key"
            ) from exc

    def encrypt(self, value: str) -> str:
        try:
            return self.fernet.encrypt(
                value.encode("utf-8")
            ).decode("utf-8")
        except Exception as exc:
            raise CredentialEncryptionError(
                "Failed to encrypt credential"
            ) from exc

    def decrypt(self, value: str) -> str:
        try:
            return self.fernet.decrypt(
                value.encode("utf-8")
            ).decode("utf-8")
        except InvalidToken as exc:
            raise CredentialEncryptionError(
                "Failed to decrypt credential"
            ) from exc


credential_encryptor = CredentialEncryptor()