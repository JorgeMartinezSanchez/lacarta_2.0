"""Arma los servicios con sus repositorios (equivalente a registrar servicios en
Program.cs / Startup.cs de ASP.NET). Es el único lugar de la presentación que
conoce db.session: los controladores solo piden el servicio ya armado.
"""
from ..extensions import db
from ..repositories.pedido_repository import PedidoRepository
from ..repositories.plato_repository import PlatoRepository
from ..repositories.restaurantes_repository import RestauranteRepository
from ..services.pedido_service import PedidosService
from ..services.plato_service import PlatosService
from ..services.restaurante_service import RestaurantesService


def restaurantes_service() -> RestaurantesService:
    return RestaurantesService(RestauranteRepository(db.session))


def platos_service() -> PlatosService:
    return PlatosService(PlatoRepository(db.session), RestauranteRepository(db.session))


def pedidos_service() -> PedidosService:
    return PedidosService(
        PedidoRepository(db.session),
        RestauranteRepository(db.session),
        PlatoRepository(db.session),
    )

