# La Carta 2.0

La Carta 2.0, creado por Jorge Martínez Sánchez (ISW-233 · Aplicaciones Web I · UCB Santa Cruz, Gestión II/2026).

Los clientes arman pedidos sobre la carta de los restaurantes, la cocina los prepara y el personal interno los administra. Son dos aplicaciones sobre **una sola base de datos PostgreSQL**:

- **Flask**: la carta pública, los pedidos de los clientes, la cola de la cocina y el CRUD de la carta. Inicia sesión con Auth0.
- **Django**: el admin interno (backoffice de pedidos). Usa los usuarios de Django.

---

## 1. URLs públicas

| Aplicación | URL |
|---|---|
| La Carta (Flask) | https://lacarta2.mooo.com |
| Admin (Django) | https://lacarta2-admin.mooo.com/admin/ |

Los subdominios están creados en FreeDNS (`mooo.com`). En ambos, el puerto 80 solo redirige a HTTPS.

---

## 2. Arquitectura

```
                         Navegador
                             │
                 HTTPS :443  │  (:80 solo redirige a :443)
                             ▼
┌──────────────────────── EC2 (Ubuntu) ────────────────────────────────────┐
│                                                                          │
│  /etc/letsencrypt (host) ──ro──┐                                         │
│                                ▼                                         │
│  ┌─────────────────── red interna de Docker Compose ───────────────────┐ │
│  │                                                                     │ │
│  │              ┌──────────────────────────────┐                       │ │
│  │              │ nginx  (publica 80 y 443)    │                       │ │
│  │              │  lacarta2.mooo.com       ────┼──► flask:5000         │ │
│  │              │  lacarta2-admin.mooo.com ────┼──► django:8000        │ │
│  │              │  /static/ del admin desde el │                       │ │
│  │              │  volumen admin_static (disco)│                       │ │
│  │              └──────────────────────────────┘                       │ │
│  │                                                                     │ │
│  │   ┌──────────────────┐   ┌──────────────────┐                       │ │
│  │   │ flask (Gunicorn) │   │ django (Gunicorn)│                       │ │
│  │   │ :5000, sin ports │   │ :8000, sin ports │                       │ │
│  │   └────────┬─────────┘   └────────┬─────────┘                       │ │
│  │            │      db:5432         │                                 │ │
│  │            ▼                      ▼                                 │ │
│  │   ┌─────────────────────────────────────────┐   ┌────────────────┐  │ │
│  │   │ db · PostgreSQL 16 · sin ports          │◄──│ migrate        │  │ │
│  │   │ volumen pg_data (esquema "content")     │   │ (corre y       │  │ │
│  │   └─────────────────────────────────────────┘   │  termina)      │  │ │
│  │                                                 └────────────────┘  │ │
│  └─────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────┘
        ▲
        │ login (Authorization Code) y claves públicas (JWKS)
     Auth0 ── roles y permisos
```

### Servicios de `docker-compose.yml` (producción)

| Servicio | Imagen / proceso | Puertos | Notas |
|---|---|---|---|
| `db` | `postgres:16-alpine` | **ninguno publicado** | Volumen con nombre `pg_data` y `healthcheck` con `pg_isready` |
| `migrate` | imagen de Django, ejecuta `entrypoint.sh` | — | Migra, crea el superusuario, ejecuta `collectstatic` y carga los datos de prueba. **Termina** |
| `flask` | Gunicorn | solo red interna (`5000`) | Arranca cuando `migrate` terminó bien (`service_completed_successfully`) |
| `django` | Gunicorn | solo red interna (`8000`) | Igual que `flask` |
| `nginx` | `nginx:alpine` | **80 y 443** | Único servicio accesible desde internet; certificados de Let's Encrypt montados desde el host |

Orden de arranque: `db` (healthy) → `migrate` (termina con código 0) → `flask` + `django` (healthy) → `nginx`.
Todos menos `migrate` tienen `restart: unless-stopped`.

`docker-compose.dev.yml` es solo para desarrollo local: `flask run --debug`, `runserver` y puertos publicados.

### Flask por capas

```
flask/app/
├── routes/        presentación: leen la petición, llaman al servicio y responden
│                  (restaurantes.py, platos.py, pedidos.py, cocina.py, dependencias.py)
├── services/      reglas de negocio y transacciones (un método por caso de uso)
├── repositories/  todas las consultas a la base (superclase Repository)
├── state/pedidos/ patrón State: estados del pedido y transiciones permitidas
├── dtos/          datos simples entre capas (sin objetos de SQLAlchemy)
├── auth/          login con Auth0, verificación del token y decorador @requires_auth
└── models.py      tablas (las crea Django; Flask solo las usa)
```

### Roles y permisos (Auth0)

| Permiso | Para qué | cliente | cocina | admin |
|---|---|:-:|:-:|:-:|
| `create:pedidos` | Hacer un pedido | ✓ | | |
| `read:mis-pedidos` | Ver y cancelar los propios | ✓ | | |
| `read:pedidos` | Ver la cola de la cocina | | ✓ | ✓ |
| `update:pedidos` | Avanzar el estado | | ✓ | |
| `write:carta` | Crear y editar restaurantes y platos | | | ✓ |
| `delete:carta` | Borrar restaurantes y platos | | | ✓ |

| Ruta | Permiso |
|---|---|
| `GET /restaurantes/`, `GET /restaurantes/<id>` | público |
| `GET/POST /restaurantes/<id>/pedir` | `create:pedidos` |
| `GET /pedidos/`, `GET /pedidos/<id>`, `POST /pedidos/<id>/cancelar` | `read:mis-pedidos` |
| `GET /cocina/` | `read:pedidos` |
| `POST /cocina/<id>/avanzar` | `update:pedidos` |

---

## 3. Cómo levantarlo desde cero

### Requisitos previos (una sola vez)

1. **Auth0**:
   - Una *Regular Web Application*.
   - Una API con **Enable RBAC** y **Add Permissions in the Access Token**, con la aplicación autorizada en *API Access*.
   - Los 6 permisos de la tabla anterior, los roles `cliente`, `cocina` y `admin`, y un usuario de prueba por rol.
   - *Allowed Callback URLs*: `https://lacarta2.mooo.com/auth/callback`.
   - *Allowed Logout URLs*: `https://lacarta2.mooo.com/restaurantes/`.
2. **FreeDNS**: los registros A de `lacarta2` y `lacarta2-admin` apuntan a la IP pública de la instancia. Compruébalo con `dig +short +norecurse lacarta2.mooo.com @ns1.afraid.org` antes de pedir certificados.
3. **AWS**: el Security Group de la instancia permite la entrada por los puertos 22, 80 y 443.

### En una instancia EC2 nueva (PRODUCCIÓN)

crear los scripts con los siguientes comandos

```bash
nano setup1.sh
```

`setup1.sh`
```bash
set -euo pipefail

verde()  { echo -e "\033[32m$*\033[0m"; }

# --- Docker ------------------------------------------------------------------
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg git docker.io
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"     # usar docker sin sudo (tras volver a entrar)
verde "== Docker instalado =="

# --- Docker Compose (plugin oficial: "docker compose") ------------------------
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
    | sudo gpg --dearmor --yes -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
    | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update
sudo apt-get install -y docker-compose-plugin
verde "== Docker Compose instalado: $(docker compose version) =="

echo
verde "== Paso 1 completo =="
echo "Escribe \"exit\", vuelve a entrar por SSH y ejecuta: bash ec2_2_desplegar.sh"
```

`setup2.sh`
```bash
set -euo pipefail

REPO="git@github.com:JorgeMartinezSanchez/lacarta_2.0.git"
RAMA="refactorizacion_capas"   # rama que se despliega
PROYECTO="$HOME/lacarta_2.0"
DOMINIOS=(lacarta2.mooo.com lacarta2-admin.mooo.com)   # carta y admin

verde()    { echo -e "\033[32m$*\033[0m"; }
amarillo() { echo -e "\033[33m$*\033[0m"; }
rojo()     { echo -e "\033[31m$*\033[0m"; }

# --- 1. Llave SSH para clonar el repositorio privado -------------------------
if [ ! -f "$HOME/.ssh/id_ed25519" ]; then
    ssh-keygen -t ed25519 -N "" -C "lacarta-ec2" -f "$HOME/.ssh/id_ed25519"
fi

# GitHub responde "Hi <usuario>! You've successfully authenticated..." pero
# SIEMPRE sale con código 1 (no da shell). Por eso se guarda la salida en una
# variable y se revisa el texto, en vez de usar el código de salida.
github_ok() {
    local salida
    salida=$(ssh -T -o StrictHostKeyChecking=accept-new git@github.com 2>&1 || true)
    [[ "$salida" == *"successfully authenticated"* ]]
}

if ! github_ok; then
    amarillo "== Agrega esta llave pública en GitHub (Settings → SSH keys o Deploy keys) =="
    echo; cat "$HOME/.ssh/id_ed25519.pub"; echo
    read -r -p "Presiona Enter cuando la hayas agregado... " _
    if ! github_ok; then
        rojo "== Error de autenticación con GitHub =="
        ssh -T git@github.com 2>&1 || true   # muestra el mensaje real de GitHub
        exit 1
    fi
fi
verde "== Autenticación con GitHub correcta =="

# --- 2. Clonar o actualizar ---------------------------------------------------
if [ -d "$PROYECTO/.git" ]; then
    git -C "$PROYECTO" fetch origin "$RAMA"
    git -C "$PROYECTO" checkout "$RAMA"
    git -C "$PROYECTO" pull --ff-only origin "$RAMA"
else
    git clone --branch "$RAMA" "$REPO" "$PROYECTO"
fi
verde "== Código en $PROYECTO (rama $(git -C "$PROYECTO" branch --show-current)) =="

# --- 3. El .env NO está en el repositorio: se copia desde tu computadora ------
if [ ! -f "$PROYECTO/.env" ]; then
    IP=$(curl -s --max-time 3 https://checkip.amazonaws.com || echo "<ip-de-la-instancia>")
    rojo "== Falta $PROYECTO/.env =="
    echo "Desde TU computadora (en la carpeta del proyecto) ejecuta:"
    echo "    scp -i clave.pem .env ubuntu@${IP}:~/lacarta_2.0/.env"
    echo "Usa .env.example como plantilla. Luego vuelve a ejecutar este script."
    exit 1
fi
chmod 600 "$PROYECTO/.env"
verde "== .env presente (permisos 600) =="

# --- 4. Certificados de Let's Encrypt -----------------------------------------
sudo apt-get install -y certbot
sudo resolvectl flush-caches || true

CERT="/etc/letsencrypt/live/${DOMINIOS[0]}/fullchain.pem"
if sudo test -f "$CERT"; then
    verde "== Certificado ya existe, se omite =="
else
    # --standalone levanta un servidor temporal en el puerto 80, así que Nginx
    # todavía no debe estar corriendo. Un solo certificado cubre ambos dominios
    # y queda en /etc/letsencrypt/live/<primer dominio>/.
    ARGS=()
    for d in "${DOMINIOS[@]}"; do ARGS+=(-d "$d"); done
    sudo docker compose -f "$PROYECTO/docker-compose.yml" stop nginx 2>/dev/null || true
    sudo certbot certonly --standalone "${ARGS[@]}" \
        || { rojo "Error: Certbot no pudo obtener el certificado."; exit 1; }
    verde "== Certificado obtenido =="
fi

# --- 5. Renovación automática (R5.2) ------------------------------------------
# El timer de certbot renueva solo, pero --standalone necesita el puerto 80,
# que Nginx ocupa. Estos hooks detienen Nginx justo antes y lo reinician después.
COMPOSE="docker compose -f $PROYECTO/docker-compose.yml"
sudo install -d /etc/letsencrypt/renewal-hooks/pre /etc/letsencrypt/renewal-hooks/post
printf '#!/bin/sh\n%s stop nginx\n'  "$COMPOSE" | sudo tee /etc/letsencrypt/renewal-hooks/pre/detener-nginx.sh  > /dev/null
printf '#!/bin/sh\n%s start nginx\n' "$COMPOSE" | sudo tee /etc/letsencrypt/renewal-hooks/post/iniciar-nginx.sh > /dev/null
sudo chmod +x /etc/letsencrypt/renewal-hooks/pre/detener-nginx.sh /etc/letsencrypt/renewal-hooks/post/iniciar-nginx.sh
sudo systemctl enable --now certbot.timer
verde "== Renovación automática configurada =="

# --- 6. Levantar la aplicación ------------------------------------------------
cd "$PROYECTO"
docker compose up -d --build
docker compose ps

# --- 7. Comprobar la renovación (con Nginx ya corriendo) ----------------------
sudo certbot renew --dry-run \
    && verde "== Renovación de prueba correcta ==" \
    || amarillo "== La renovación de prueba falló: revisa 'sudo certbot renew --dry-run' =="
systemctl list-timers certbot.timer --no-pager

echo
verde "== Paso 2 completo =="
echo "Carta:  https://${DOMINIOS[0]}"
echo "Admin:  https://${DOMINIOS[1]}/admin/"
```

```bash
chmod +x setup*.sh
# importante antes de ejecutar
```

`setup1.sh` instala docker y docker compose, que los cambios del usuario docker se aplique, se tiene que salir de la sesion.

`setup2.sh` realiza lo siguiente:
1. Genera la llave para que ingreses a **Repositorio lacarta_2.0 -> Settings -> Deploy keys -> Add Deploy Key** y copies la clave ssh en el campo de key.
2. Clona el repositorio
3. Te pedira que copies el .env desde la maquina local
4. Instala los certificados de Lets Encrypt
5. El timer de certbot renueva solo, pero --standalone necesita el puerto 80 para nginx.
6. Levanta el proyecto
7. Comprueba la renovacion

### Comandos manuales equivalentes

```bash
cp .env.example .env          # y completar los valores
docker compose up -d --build  # db → migrate → flask/django → nginx
docker compose ps             # migrate: Exited (0); el resto: healthy
```

### Desarrollo local

```bash
cp .env.example .env          # con BEHIND_PROXY y SESSION_COOKIE_SECURE vacíos y DJANGO_DEBUG=1
docker compose -f docker-compose.dev.yml up --build
```

### Pruebas automáticas

```bash
cd flask
pip install -r requirements-dev.txt
pytest -q
```

No necesitan Docker, Postgres ni Auth0. Usan SQLite en memoria y simulan la sesión con un usuario y sus permisos (`tests/conftest.py`). Las seis pruebas obligatorias de R6 están en `tests/test_r6_obligatorias.py`.

---

## 4. Decisiones justificadas

### 4.1 Una sola base, y solo Django migra

Los cuatro modelos (`Restaurante`, `Plato`, `Pedido`, `ItemPedido`) viven en `django_admin/django_admin/models.py`, con `db_table` apuntando al esquema `content` (por ejemplo, `content.pedido`). Las restricciones `CHECK` también se declaran ahí (`Meta.constraints`). En Flask, `app/models.py` declara las mismas tablas con `__tablename__` y `__table_args__ = {"schema": "content"}`, y las mismas columnas.

**Solo Django migra** (servicio `migrate`, con migraciones versionadas en `migrations/`). Flask nunca ejecuta `create_all()` ni Flask-Migrate. Si los dos migraran, cada uno podría alterar la misma tabla de forma distinta, y el esquema dependería de cuál arrancó último.

### 4.2 El pedido de otro cliente responde 404, no 403

Un 403 confirmaría que el pedido **existe** y que es de otra persona. Con eso, cualquiera podría recorrer los IDs para saber cuántos pedidos hay. Por eso la consulta busca el pedido **y** su dueño a la vez (`WHERE id = :id AND cliente = :sub`, en `PedidoRepository.get_de_cliente`). Un pedido ajeno y uno inexistente producen la misma respuesta.

### 4.3 Dónde se aplica cada regla

Todas las reglas se aplican en el servidor. Ocultar botones en los templates es solo una ayuda visual.

| Regla | Archivo y función |
|---|---|
| R1.2 El cliente es el `sub` del token | `flask/app/routes/restaurantes.py` → `pedir` (`cliente=payload["sub"]`) |
| R1.3 Precio congelado | `flask/app/services/pedido_service.py` → `create_pedido` (`precio_unitario=plato.precio`) |
| R1.4 El total lo calcula el servidor | `pedido_service.py` → `create_pedido` (`total += plato.precio * cantidad`). Del formulario solo se leen `cantidad_<plato_id>` (`restaurantes.py` → `_items_desde_form`) |
| R1.5 Pedido atómico (existe, está disponible, es del mismo restaurante) | `pedido_service.py` → `create_pedido`: valida **todos** los ítems antes de escribir, hace un único `commit()` y `rollback()` ante cualquier error |
| R1.5 Cantidad entera entre 1 y 20 | `pedido_service.py` → `_validar_cantidad` |
| R1.6 `CHECK` en la base | `django_admin/django_admin/models.py`: `pedido_estado_valido`, `pedido_total_no_negativo`, `item_cantidad_1_a_20`, `item_precio_no_negativo` (migración `0002`) |
| R1.7 404, 400 y Post/Redirect/Get | `routes/restaurantes.py` → `pedir`; `routes/pedidos.py`; `routes/cocina.py` (`abort(404)`, 400 con el formulario y `redirect` después de cada POST) |
| R2.4 Un permiso por ruta | Decorador `@requires_auth("…")` en cada ruta protegida (`flask/app/auth/decorators.py`) |
| R2.5 Sin sesión: 401; sin permiso: 403 | `auth/decorators.py` → `requires_auth` y `check_permissions`; páginas en `auth/handlers.py` |
| R2.6 Nadie ve pedidos ajenos | `repositories/pedido_repository.py` → `listar_por_cliente` y `get_de_cliente`; `services/pedido_service.py` → `_find_de_cliente` |
| Estados: `pendiente → en_preparacion → listo → entregado` (cocina) | `flask/app/state/pedidos/` (patrón State): cada estado solo permite sus transiciones. `routes/cocina.py` → `avanzar` y `pedido_service.py` → `avanzar` (solo acepta destinos de cocina) |
| Estados: `pendiente → cancelado` (cliente dueño) | `state/pedidos/pendiente.py` → `cancelar`; `en_preparacion.py` → `cancelar` lo rechaza. `pedido_service.py` → `cancelar` busca el pedido por `sub` |

Verificación del token: Auth0 lo firma con **RS256**. Flask descarga la clave pública de Auth0 (JWKS) y verifica la firma, la expiración, la audiencia y el emisor en `flask/app/auth/tokens.py` → `verify_decode_jwt`.

### 4.4 Dónde están los secretos y quién puede leerlos

- **`.env`** en la raíz del proyecto: contraseña de Postgres, `SECRET_KEY` (firma la sesión de Flask; Django también lo lee), `AUTH0_CLIENT_SECRET` y contraseña del superusuario.
  - **No está en el repositorio** (está en `.gitignore`). `.env.example` documenta las variables con valores de ejemplo.
  - En el servidor tiene permisos `600`: solo lo lee el usuario `ubuntu`.
  - Lo leen los contenedores que lo declaran en `env_file`: `migrate`, `flask` y `django`. **Nginx no lo recibe.**
  - Se copia desde mi computadora con `scp` y no viaja por Git.
- **Certificados** de Let's Encrypt: en `/etc/letsencrypt` del host (solo `root`). Nginx los monta en modo solo lectura.
- **Llaves SSH** de las instancias: solo en mi computadora (`.ec2_keys/`, en `.gitignore`).
- **Contraseñas de los usuarios de prueba**: no están en el repositorio. Se entregan en papel el día de la defensa.

---

## 5. Qué quedó incompleto o haría distinto

- **Secretos en el historial de Git.**
  - Una llave SSH privada de una instancia EC2 (`.ec2_keys/lacarta2_1.pem`) se subió en el commit `d505260` y se eliminó en `7fc5a75`. Sigue en el historial. Esa instancia ya no existe, y el par de llaves debe eliminarse en AWS (EC2 → Key Pairs).
  - Una contraseña de PostgreSQL estuvo como valor por defecto en `flask/app/config.py` (commits `cd5dd4f` a `0eed722`). Se debe cambiar `POSTGRES_PASSWORD` en el `.env` del servidor.
  - Lo correcto habría sido no versionar nunca esos archivos.
- **Botones de la carta en `platos/`.** En `restaurantes/detalle.html` los botones se ocultan según los permisos, pero en `platos/index.html` y `platos/detalle.html` todavía se muestran "Editar" y "Eliminar" a todos. La protección real está en el servidor (`@requires_auth("write:carta")` y `@requires_auth("delete:carta")`).
- **Código sin uso** que conviene borrar:
  - `flask/app/api.py`: no está registrado e importa `require_auth`, que no existe.
  - `flask/app/services/item_pedido.py`, `flask/app/repositories/item_pedido.py` e `ItemPedidosDTO_Input`: quedaron del CRUD de ítems sueltos, que se eliminó porque contradecía el pedido atómico.
- **WhiteNoise** sigue en el `MIDDLEWARE` de Django. En producción, Nginx sirve los estáticos antes de que la petición llegue a Django, así que ya no hace falta.
- **`ItemPedido.restaurante_id`** es redundante: el restaurante se obtiene del pedido. Se mantiene por compatibilidad con la base existente.
- **Las pruebas usan SQLite, no PostgreSQL.** Las restricciones `CHECK` las define Django, así que no se prueban con pytest; se comprueban con un `INSERT` en `psql`.
- **Doble avance concurrente.** `avanzar` usa `SELECT … FOR UPDATE` (`PedidoRepository.get_para_actualizar`), pero no hay una prueba que lo demuestre, porque SQLite ignora `FOR UPDATE`. Por eso no lo presento como el extra de la sección 9.
- **La IP cambia en cada instancia nueva**, y hay que actualizar a mano los registros A en FreeDNS antes de pedir certificados. Lo haría distinto con una Elastic IP, o con la URL de actualización dinámica de FreeDNS llamada desde el script de despliegue.
