from pathlib import Path
from typing import Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey, EllipticCurvePublicKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
import base64
import json
import hashlib

CURVE = ec.SECP256R1()
ADDRESS = Tuple[str, int]
PATH = Path | str


def hash_password(password: str) -> str:
    m = hashlib.sha256()
    m.update(password.encode())
    return base64.b64encode(m.digest()).decode()


def generate_b64_fernet_key() -> str:
    return base64.b64encode(Fernet.generate_key()).decode()


def get_fernet_from_b64(encoded_key: str) -> Fernet:
    return Fernet(base64.b64decode(encoded_key))


def decrypt_fernet_to_json(f: Fernet, data: bytes) -> dict:
    return json.loads(f.decrypt(data).decode())


def deserialize_public_key(key: bytes) -> EllipticCurvePublicKey:
    return serialization.load_pem_public_key(key)


def deserialize_private_key(key: bytes) -> EllipticCurvePrivateKey:
    return serialization.load_pem_private_key(key, password=None)


def serialize_public_key(key: EllipticCurvePublicKey) -> bytes:
    return key.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)


def serialize_private_key(key: EllipticCurvePrivateKey) -> bytes:
    return key.private_bytes(encoding=serialization.Encoding.PEM, format=serialization.PrivateFormat.PKCS8, encryption_algorithm=serialization.NoEncryption())


def generate_ecdh_keys() -> Tuple[EllipticCurvePrivateKey, EllipticCurvePublicKey]:
    private_key = ec.generate_private_key(CURVE)
    public_key = private_key.public_key()
    return private_key, public_key


def load_public_ecdh_key(path: PATH) -> EllipticCurvePublicKey:
    with open(path, "rb") as f:
        loaded_public_key = serialization.load_pem_public_key(
            f.read(),
        )
        return loaded_public_key


def load_private_ecdh_key(path: PATH) -> EllipticCurvePrivateKey:
    with open(path, "rb") as f:
        loaded_private_key = serialization.load_pem_private_key(
            f.read(),
            password=None,
        )
        return loaded_private_key


def get_fernet(public_key: EllipticCurvePublicKey, private_key: EllipticCurvePrivateKey) -> Fernet:
    shared_key = private_key.exchange(ec.ECDH(), public_key)
    derived_key = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=b"handshake data",
    ).derive(shared_key)
    derived_key = base64.urlsafe_b64encode(derived_key)
    return Fernet(derived_key)


def encrypt_with_fernet(f: Fernet, data: bytes) -> bytes:
    return f.encrypt(data)


def decrypt_with_fernet(f: Fernet, ciphertext: bytes) -> bytes:
    return f.decrypt(ciphertext)


def public_key_to_str(key: EllipticCurvePublicKey) -> str:
    return utils.encode_for_json(serialize_public_key(key))


def str_to_public_key(key: str) -> EllipticCurvePublicKey:
    return deserialize_public_key(utils.decode_from_json(key))
