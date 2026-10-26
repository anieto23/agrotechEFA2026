"""Hash de contraseñas y de claves de los aparatos. Solo librería estándar de Python."""
import hashlib
import hmac
import secrets

ITERACIONES = 600_000  # recomendación de OWASP para PBKDF2-SHA256


def hash_password(password: str) -> str:
    """Devuelve `pbkdf2_sha256$iteraciones$sal$hash`, que se puede guardar en la base de datos."""
    sal = secrets.token_hex(16)
    calculado = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(sal), ITERACIONES)
    return f"pbkdf2_sha256${ITERACIONES}${sal}${calculado.hex()}"


def verificar_password(password: str, guardado: str) -> bool:
    try:
        algoritmo, iteraciones, sal, esperado = guardado.split("$")
    except ValueError:
        return False
    if algoritmo != "pbkdf2_sha256":
        return False
    calculado = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(sal), int(iteraciones))
    # compare_digest tarda lo mismo acierte o no, para no dar pistas a un atacante
    return hmac.compare_digest(calculado.hex(), esperado)


def generar_api_key() -> str:
    return secrets.token_urlsafe(24)


def hash_api_key(clave: str) -> str:
    # Las claves son largas y aleatorias, así que basta un SHA-256 sin sal
    return hashlib.sha256(clave.encode()).hexdigest()
