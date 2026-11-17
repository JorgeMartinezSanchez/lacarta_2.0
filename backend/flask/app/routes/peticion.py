"""Lectura del cuerpo JSON de las peticiones (capa de presentación).

Los servicios esperan texto (hacen .strip()) y validan las reglas de negocio.
Aquí solo se comprueba que cada campo tenga el TIPO correcto, para que un
número o una lista donde va texto responda 400 y no un 500.
"""
from flask import request

from ..errors import BusinessRuleError


def cuerpo_json() -> dict:
    """El cuerpo de la petición como dict. Exige Content-Type: application/json."""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise BusinessRuleError("El cuerpo de la petición debe ser un objeto JSON.")
    return data


def texto(data: dict, campo: str, default: str | None = "") -> str | None:
    valor = data.get(campo)
    if valor is None:
        return default
    if isinstance(valor, bool) or not isinstance(valor, (str, int, float)):
        raise BusinessRuleError(f"El campo '{campo}' debe ser texto.")
    return str(valor)


def entero(data: dict, campo: str) -> int:
    valor = data.get(campo)
    if isinstance(valor, int) and not isinstance(valor, bool):
        return valor
    if isinstance(valor, str) and valor.strip().isdigit():
        return int(valor)
    raise BusinessRuleError(f"El campo '{campo}' debe ser un número entero.")


def booleano(data: dict, campo: str, default: bool) -> bool:
    if campo not in data:
        return default
    valor = data[campo]
    if not isinstance(valor, bool):
        raise BusinessRuleError(f"El campo '{campo}' debe ser true o false.")
    return valor
