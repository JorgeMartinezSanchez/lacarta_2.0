CREATE IF NOT EXIST SCHEMA content;

CREATE TABLE content.restaurantes (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(120) NOT NULL,
    ciudad VARCHAR(80) NOT NULL,
    direccion VARCHAR(200) NULL,
    telefono VARCHAR(30) NULL
);

CREATE TABLE content.platos (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre VARCHAR(120) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    disponible BIT NOT NULL DEFAULT 1,
    restaurante_id INT NOT NULL,
    
    -- Restricción de verificación para el precio
    CONSTRAINT CHK_precio_mayor_cero CHECK (precio > 0),
    
    -- Restricción de clave foránea
    CONSTRAINT FK_platos_restaurantes FOREIGN KEY (restaurante_id) 
        REFERENCES restaurantes(id)
);