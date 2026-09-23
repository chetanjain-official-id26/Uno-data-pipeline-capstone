from cryptography.fernet import Fernet, InvalidToken

from app.core.config import get_settings


class CredentialEncryptionError(Exception):
    """Raised when credential encryption/decryption fails."""


class CredentialEncryptor:
    """Encrypt and decrypt external system credentials.

    The encryption key must remain stable between application
    restarts. Plaintext credentials should only exist in memory
    for the shortest possible duration.
    """

    def __init__(self) -> None:
        settings = get_settings()

        key = settings.credential_encryption_key

        if not key:
            raise CredentialEncryptionError(
                "Credential encryption key is not configured"
            )

        try:
            self.fernet = Fernet(key.encode("utf-8"))
        except Exception as exc:
            raise CredentialEncryptionError(
                "Invalid credential encryption key"
            ) from exc

    def encrypt(self, value: str) -> str:
        """Encrypt a plaintext credential."""
        if not isinstance(value, str):
            raise CredentialEncryptionError("Credential must be a string")

        try:
            encrypted = self.fernet.encrypt(value.encode("utf-8"))
            return encrypted.decode("utf-8")
        except Exception as exc:
            raise CredentialEncryptionError(
                "Failed to encrypt credential"
            ) from exc

    def decrypt(self, value: str) -> str:
        """Decrypt an encrypted credential."""
        if not value:
            raise CredentialEncryptionError("Encrypted credential is empty")

        try:
            decrypted = self.fernet.decrypt(value.encode("utf-8"))
            return decrypted.decode("utf-8")
        except InvalidToken as exc:
            raise CredentialEncryptionError(
                "Failed to decrypt credential: invalid token or encryption key"
            ) from exc
        except UnicodeDecodeError as exc:
            raise CredentialEncryptionError(
                "Failed to decrypt credential: invalid UTF-8 data"
            ) from exc
        except Exception as exc:
            raise CredentialEncryptionError(
                "Failed to decrypt credential"
            ) from exc


credential_encryptor = CredentialEncryptor()