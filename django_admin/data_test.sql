-- ============================================================
-- Datos de prueba: restaurantes, platos, pedidos e items
-- Esquema: content (las tablas las crea `python manage.py migrate`)
-- Uso:  psql -U $POSTGRES_USER -d $POSTGRES_DB -f datos_prueba.sql
-- ============================================================


-- Descomenta para limpiar los datos existentes y reiniciar los IDs:
-- TRUNCATE content.item_pedido, content.pedido, content.platos, content.restaurantes RESTART IDENTITY CASCADE;

-- ------------------------------------------------------------
-- Restaurantes
-- ------------------------------------------------------------
INSERT INTO content.restaurantes (id, nombre, ciudad, direccion, telefono) VALUES
(1, 'La Casona del Altiplano', 'La Paz',                 'Av. 16 de Julio 1234',  '+591 2 2123456'),
(2, 'Sabores de Cochabamba',   'Cochabamba',             'Calle España 456',      '+591 4 4234567'),
(3, 'El Fogón Cruceño',        'Santa Cruz de la Sierra','Av. San Martín 789',    '+591 3 3345678'),
(4, 'Pique Macho Don Lucho',   'Sucre',                  'Calle Bolívar 321',     '+591 4 6456789'),
(5, 'Rincón Tarijeño',         'Tarija',                 NULL,                    NULL);

-- ------------------------------------------------------------
-- Platos (6 por restaurante)
-- ------------------------------------------------------------
INSERT INTO content.platos (id, nombre, precio, disponible, restaurante_id) VALUES
-- Restaurante 1
(1,  'Sopa de maní',            28.00, TRUE,  1),
(2,  'Silpancho',               35.00, TRUE,  1),
(3,  'Pique macho',             55.00, TRUE,  1),
(4,  'Salteña de carne',         8.00, TRUE,  1),
(5,  'Trucha frita',            48.00, TRUE,  1),
(6,  'Api con pastel',          12.00, TRUE,  1),
-- Restaurante 2
(7,  'Pique macho',             60.00, TRUE,  2),
(8,  'Chicharrón de cerdo',     50.00, TRUE,  2),
(9,  'Charque kan',             45.00, TRUE,  2),
(10, 'Sopa de maní',            25.00, TRUE,  2),
(11, 'Anticucho',               30.00, TRUE,  2),
(12, 'Helado de canela',        15.00, FALSE, 2),
-- Restaurante 3
(13, 'Majadito',                40.00, TRUE,  3),
(14, 'Locro de gallina',        38.00, TRUE,  3),
(15, 'Sonso',                   22.00, TRUE,  3),
(16, 'Masaco',                  30.00, TRUE,  3),
(17, 'Costillar al horno',      65.00, TRUE,  3),
(18, 'Cuñapé',                  10.00, TRUE,  3),
-- Restaurante 4
(19, 'Chorizo chuquisaqueño',   42.00, TRUE,  4),
(20, 'Mondongo',                45.00, TRUE,  4),
(21, 'Picante de pollo',        38.00, TRUE,  4),
(22, 'Ranga',                   40.00, TRUE,  4),
(23, 'Chocolate caliente',      12.00, TRUE,  4),
(24, 'Empanada de queso',        9.00, FALSE, 4),
-- Restaurante 5
(25, 'Saice',                   36.00, TRUE,  5),
(26, 'Chancho a la cruz',       58.00, TRUE,  5),
(27, 'Ensalada tarijeña',       20.00, TRUE,  5),
(28, 'Pescado a la plancha',    52.00, TRUE,  5),
(29, 'Vino patero (copa)',      25.00, TRUE,  5),
(30, 'Flan de leche',           14.00, TRUE,  5);

-- ------------------------------------------------------------
-- Pedidos (el total se calcula más abajo a partir de los items)
-- ------------------------------------------------------------
-- cliente = el 'sub' del token de Auth0 (aquí, valores de ejemplo).
-- Reemplázalos por el sub real de tus usuarios de prueba para verlos en "mis pedidos".
INSERT INTO content.pedido (id, cliente, restaurante_id, estado, fecha, total) VALUES
(1,  'auth0|cliente-demo-1', 1, 'entregado',      '2026-09-28', 0),
(2,  'auth0|cliente-demo-2', 1, 'entregado',      '2026-10-02', 0),
(3,  'auth0|cliente-demo-3', 1, 'pendiente',      '2026-10-23', 0),
(4,  'auth0|cliente-demo-1', 2, 'entregado',      '2026-09-30', 0),
(5,  'auth0|cliente-demo-2', 2, 'en_preparacion', '2026-10-24', 0),
(6,  'auth0|cliente-demo-3', 2, 'cancelado',      '2026-10-10', 0),
(7,  'auth0|cliente-demo-1', 3, 'entregado',      '2026-10-05', 0),
(8,  'auth0|cliente-demo-2', 3, 'entregado',      '2026-10-12', 0),
(9,  'auth0|cliente-demo-3', 3, 'pendiente',      '2026-10-24', 0),
(10, 'auth0|cliente-demo-1', 4, 'entregado',      '2026-10-01', 0),
(11, 'auth0|cliente-demo-2', 4, 'en_preparacion', '2026-10-24', 0),
(12, 'auth0|cliente-demo-3', 4, 'cancelado',      '2026-10-15', 0),
(13, 'auth0|cliente-demo-1', 5, 'entregado',      '2026-10-08', 0),
(14, 'auth0|cliente-demo-2', 5, 'entregado',      '2026-10-18', 0),
(15, 'auth0|cliente-demo-3', 5, 'pendiente',      '2026-10-24', 0);

-- ------------------------------------------------------------
-- Items de pedido
-- precio_unitario y restaurante_id se toman del plato, así
-- siempre son consistentes con el catálogo.
-- ------------------------------------------------------------
INSERT INTO content.item_pedido (pedido_id, plato_id, cantidad, precio_unitario, restaurante_id)
SELECT v.pedido_id, v.plato_id, v.cantidad, pl.precio, pl.restaurante_id
FROM (VALUES
    (1,  1,  2), (1,  2,  1),
    (2,  3,  1), (2,  4,  3), (2,  6,  2),
    (3,  5,  2), (3,  1,  1),
    (4,  7,  2), (4,  9,  1),
    (5,  8,  1), (5,  10, 2), (5,  11, 3),
    (6,  7,  1),
    (7,  13, 2), (7,  15, 2),
    (8,  17, 1), (8,  18, 4),
    (9,  14, 2), (9,  16, 1),
    (10, 19, 2), (10, 21, 1), (10, 23, 2),
    (11, 20, 1), (11, 22, 2),
    (12, 21, 1),
    (13, 25, 2), (13, 28, 1), (13, 30, 2),
    (14, 26, 1), (14, 27, 1), (14, 29, 2),
    (15, 28, 2), (15, 30, 1)
) AS v(pedido_id, plato_id, cantidad)
JOIN content.platos pl ON pl.id = v.plato_id;

-- ------------------------------------------------------------
-- Total de cada pedido = suma(cantidad * precio_unitario)
-- ------------------------------------------------------------
UPDATE content.pedido p
SET total = t.total
FROM (
    SELECT pedido_id, SUM(cantidad * precio_unitario) AS total
    FROM content.item_pedido
    GROUP BY pedido_id
) t
WHERE t.pedido_id = p.id;

-- ------------------------------------------------------------
-- Sincronizar secuencias (insertamos IDs explícitos)
-- ------------------------------------------------------------
SELECT setval(pg_get_serial_sequence('content.restaurantes', 'id'), (SELECT MAX(id) FROM content.restaurantes));
SELECT setval(pg_get_serial_sequence('content.platos',       'id'), (SELECT MAX(id) FROM content.platos));
SELECT setval(pg_get_serial_sequence('content.pedido',       'id'), (SELECT MAX(id) FROM content.pedido));
SELECT setval(pg_get_serial_sequence('content.item_pedido',  'id'), (SELECT COALESCE(MAX(id), 1) FROM content.item_pedido));
