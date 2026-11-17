from flask import jsonify
from werkzeug.exceptions import HTTPException

from .extensions import db


def error_json(codigo: str, mensaje: str, status: int, **extra):
    """Forma única de todas las respuestas de error: {"error": ..., "mensaje": ...}."""
    return jsonify(error=codigo, mensaje=mensaje, **extra), status

def register_error_handlers(app):
    """Registra los manejadores de errores: todos responden JSON.

    Gracias a esto los controladores no necesitan try/except: si el servicio
    lanza NotFoundError la respuesta es 404, y si lanza BusinessRuleError, 400.
    """

    @app.errorhandler(NotFoundError)
    def no_encontrado(error):
        return error_json("no_encontrado", str(error), 404)

    @app.errorhandler(BusinessRuleError)
    def regla_de_negocio(error):
        return error_json("regla_de_negocio", str(error), 400)

    @app.errorhandler(HTTPException)
    def error_http(error):
        # 404 de una URL que no existe, 405 de un método no permitido, etc.
        codigo = (error.name or "error").lower().replace(" ", "_")
        return error_json(codigo, error.description, error.code)

    @app.errorhandler(500)
    def error_500(error):
        db.session.rollback()
        return error_json("error_interno", "Ocurrió un error inesperado.", 500)


class BusinessRuleError(Exception):
    """Una regla de negocio impide la operación. El mensaje se muestra al usuario."""


class NotFoundError(BusinessRuleError):
    """El recurso pedido no existe. Se responde con 404."""
