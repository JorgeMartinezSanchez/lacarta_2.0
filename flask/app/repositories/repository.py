from sqlalchemy import func, select


class Repository:
    """Superclase con las operaciones comunes a todos los repositorios.

    Cada subclase solo indica su modelo (y opcionalmente su orden por
    defecto) y agrega las consultas propias de su entidad.
    """

    model = None        # la subclase lo define, p. ej. model = Restaurante
    default_order = ()  # columnas para ordenar getAll(), p. ej. (Restaurante.nombre,)

    def __init__(self, session):
        if self.model is None:
            raise TypeError(f"{type(self).__name__} debe definir 'model'.")
        self.session = session

    # --- lectura ---------------------------------------------------------

    def getAll(self):
        query = select(self.model).order_by(*self.default_order)
        return self.session.scalars(query).all()

    def getOne(self, entity_id):
        """Devuelve la entidad o None si no existe."""
        return self.session.get(self.model, entity_id)

    def count(self):
        return self.session.scalar(select(func.count()).select_from(self.model))

    # --- escritura (no confirma: eso lo decide el servicio) --------------

    def create(self, entity):
        self.session.add(entity)
        self.session.flush()  # envía el INSERT sin confirmar: asigna entity.id
        return entity

    def update(self, entity, **campos):
        """Asigna los campos indicados y envía el UPDATE sin confirmar."""
        for nombre, valor in campos.items():
            if not hasattr(entity, nombre):
                raise AttributeError(f"{self.model.__name__} no tiene el campo '{nombre}'.")
            setattr(entity, nombre, valor)
        self.session.flush()
        return entity

    def delete(self, entity):
        self.session.delete(entity)
        self.session.flush()

    # --- transacción -----------------------------------------------------

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
