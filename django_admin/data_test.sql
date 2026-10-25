-- ============================================================
-- Datos de prueba: restaurantes, platos, pedidos e items
-- Esquema: content (las tablas las crea `python manage.py migrate`)
-- Uso:  psql -U $POSTGRES_USER -d $POSTGRES_DB -f datos_prueba.sql
-- ============================================================

BEGIN;

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
INSERT INTO content.pedido (id, restaurante_id, estado, fecha, total) VALUES
(1,  1, 'Entregado',      '2026-09-28', NULL),
(2,  1, 'Entregado',      '2026-10-02', NULL),
(3,  1, 'Pendiente',      '2026-10-23', NULL),
(4,  2, 'Entregado',      '2026-09-30', NULL),
(5,  2, 'En preparación', '2026-10-24', NULL),
(6,  2, 'Cancelado',      '2026-10-10', NULL),
(7,  3, 'Entregado',      '2026-10-05', NULL),
(8,  3, 'Entregado',      '2026-10-12', NULL),
(9,  3, 'Pendiente',      '2026-10-24', NULL),
(10, 4, 'Entregado',      '2026-10-01', NULL),
(11, 4, 'En preparación', '2026-10-24', NULL),
(12, 4, 'Cancelado',      '2026-10-15', NULL),
(13, 5, 'Entregado',      '2026-10-08', NULL),
(14, 5, 'Entregado',      '2026-10-18', NULL),
(15, 5, 'Pendiente',      '2026-10-24', NULL);

-- ------------------------------------------------------------
-- Items de pedido
-- precio_unitario y restaurante_id se toman del plato, así
-- siempre son consistentes con el catálogo.
-- (cantidad es VARCHAR en el modelo, por eso va como texto)
-- ------------------------------------------------------------
INSERT INTO content.item_pedido (pedido_id, plato_id, cantidad, precio_unitario, restaurante_id)
SELECT v.pedido_id, v.plato_id, v.cantidad, pl.precio, pl.restaurante_id
FROM (VALUES
    (1,  1,  '2'), (1,  2,  '1'),
    (2,  3,  '1'), (2,  4,  '3'), (2,  6,  '2'),
    (3,  5,  '2'), (3,  1,  '1'),
    (4,  7,  '2'), (4,  9,  '1'),
    (5,  8,  '1'), (5,  10, '2'), (5,  11, '3'),
    (6,  7,  '1'),
    (7,  13, '2'), (7,  15, '2'),
    (8,  17, '1'), (8,  18, '4'),
    (9,  14, '2'), (9,  16, '1'),
    (10, 19, '2'), (10, 21, '1'), (10, 23, '2'),
    (11, 20, '1'), (11, 22, '2'),
    (12, 21, '1'),
    (13, 25, '2'), (13, 28, '1'), (13, 30, '2'),
    (14, 26, '1'), (14, 27, '1'), (14, 29, '2'),
    (15, 28, '2'), (15, 30, '1')
) AS v(pedido_id, plato_id, cantidad)
JOIN content.platos pl ON pl.id = v.plato_id;

-- ------------------------------------------------------------
-- Total de cada pedido = suma(cantidad * precio_unitario)
-- ------------------------------------------------------------
UPDATE content.pedido p
SET total = t.total
FROM (
    SELECT pedido_id, SUM(cantidad::int * precio_unitario) AS total
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

COMMIT;