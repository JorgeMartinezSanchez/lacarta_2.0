from flask import render_template
from .extensions import db

def register_error_handlers(app):
    """Registra los manejadores de errores personalizados de la app"""

    @app.errorhandler(404)
    def error_404(error):
        return render_template("errores/404.html"), 404

    @app.errorhandler(500)
    def error_500(error):
        db.session.rollback()
        return render_template("errores/500.html"), 500

class BusinessRuleError(Exception):
    """Una regla de negocio impide la operación. El mensaje se muestra al usuario."""


class NotFoundError(BusinessRuleError):
    """El recurso pedido no existe. La ruta puede responder con 404."""
