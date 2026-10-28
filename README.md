# API REST Óptica y Anteojos

Backend para plataforma de óptica y venta de anteojos de sol y recetados, desarrollado con Django 5.1+, Django REST Framework y base de datos PostgreSQL alojada en Supabase.

---

## 1. Planificación de Base de Datos y Relaciones

El sistema cuenta con 13 modelos de datos organizados en tres aplicaciones de dominio: `catalogo`, `clientes` y `ventas`.

### Diagrama Entidad - Relación (ER)

```mermaid
erDiagram
    User ||--|| Cliente : "perfil"
    Marca ||--o{ Anteojo : "fabrica"
    Categoria ||--o{ Anteojo : "clasifica"
    Material ||--o{ Anteojo : "marco de"
    Anteojo ||--o{ ImagenAnteojo : "tiene"
    Anteojo }o--o{ TipoLente : "compatible con"
    Cliente ||--o{ Receta : "tiene"
    Optometrista ||--o{ Receta : "emite"
    Cliente ||--o{ Turno : "reserva"
    Optometrista ||--o{ Turno : "atiende"
    Cliente ||--o{ Pedido : "realiza"
    Receta |o--o{ Pedido : "se usa en"
    Pedido ||--|{ DetallePedido : "contiene"
    Anteojo ||--o{ DetallePedido : "vendido en"
    TipoLente |o--o{ DetallePedido : "lente elegido"
    Cliente ||--o{ Resena : "escribe"
    Anteojo ||--o{ Resena : "recibe"
```

### Descripción de los 13 Modelos

| # | Modelo | Aplicación | Campos Principales | Relaciones |
|---|--------|------------|---------------------|------------|
| 1 | `Marca` | catalogo | `nombre`, `pais_origen`, `descripcion`, `activo` | 1:N con `Anteojo` |
| 2 | `Categoria` | catalogo | `nombre`, `slug`, `descripcion`, `activo` | 1:N con `Anteojo` |
| 3 | `Material` | catalogo | `nombre`, `descripcion`, `activo` | 1:N con `Anteojo` |
| 4 | `TipoLente` | catalogo | `nombre`, `descripcion`, `precio_adicional`, `activo` | M:N con `Anteojo`, 1:N con `DetallePedido` |
| 5 | `Anteojo` | catalogo | `nombre`, `sku`, `forma`, `genero`, `color_marco`, `color_lente`, `precio`, `stock`, `activo`, `destacado` | FK a Marca, Categoria, Material; M2M TipoLente |
| 6 | `ImagenAnteojo` | catalogo | `imagen`, `es_modelo` (foto producto vs persona usándolo), `orden` | FK a `Anteojo` |
| 7 | `Cliente` | clientes | `dni`, `telefono`, `direccion`, `fecha_nacimiento` | 1:1 con `User` de Django |
| 8 | `Optometrista` | clientes | `nombre`, `apellido`, `matricula`, `email`, `telefono`, `especialidad`, `activo` | 1:N con `Receta` y `Turno` |
| 9 | `Receta` | clientes | `fecha_emision`, `od_esfera`, `od_cilindro`, `od_eje`, `oi_esfera`, `oi_cilindro`, `oi_eje`, `adicion`, `distancia_pupilar` | FK a `Cliente` y `Optometrista` |
| 10 | `Turno` | clientes | `fecha_hora`, `motivo`, `estado` (pendiente, confirmado, completado, cancelado) | FK a `Cliente` y `Optometrista` |
| 11 | `Pedido` | ventas | `fecha`, `estado` (pendiente, pagado, enviado, entregado, cancelado), `total`, `notas` | FK a `Cliente` y `Receta` (opcional) |
| 12 | `DetallePedido` | ventas | `cantidad`, `precio_unitario`, `subtotal` | FK a `Pedido`, `Anteojo` y `TipoLente` (opcional) |
| 13 | `Resena` | ventas | `puntaje` (1 a 5), `comentario`, `fecha` | FK a `Cliente` y `Anteojo` (restricción única por cliente y anteojo) |

---

## 2. Endpoints de la API REST

Todos los endpoints se encuentran unificados bajo el prefijo `/api/`.

### Catálogo
- `GET/POST /api/marcas/` - Listado y creación de marcas.
- `GET/PUT/PATCH/DELETE /api/marcas/{id}/` - Detalle y gestión de marca.
- `GET /api/categorias/` - Listado de categorías (solo lectura).
- `GET /api/categorias/{slug}/` - Detalle de categoría.
- `GET /api/materiales/` - Listado de materiales (solo lectura).
- `GET /api/tipos-lente/` - Listado de tratamientos y tipos de lente (solo lectura).
- `GET /api/anteojos/` - Listado paginado con **Nested Serializers** (marca, categoría, material, imágenes anidadas).
- `POST /api/anteojos/` - Creación de anteojo con IDs planos para fácil integración.
- `GET/PUT/PATCH/DELETE /api/anteojos/{id}/` - Consulta individual y edición.
- `GET /api/anteojos/destacados/` - Acción personalizada (`@action`) para anteojos en portada.
- `GET /api/anteojos/{id}/resenas/` - Acción personalizada (`@action`) que lista opiniones del producto.
- `GET/POST /api/imagenes-anteojo/` - Carga y consulta de imágenes asociadas.

### Clientes y Consultas
- `GET /api/optometristas/` - Listado de profesionales habilitados.
- `GET/POST /api/clientes/` - Gestión de clientes (restringido a dueño o admin).
- `GET/PATCH /api/clientes/me/` - Acción personalizada (`@action`) para consultar y editar el perfil propio.
- `GET/POST /api/recetas/` - Historial y registro de graduaciones oftalmológicas.
- `GET/POST /api/turnos/` - Gestión de turnos.
- `POST /api/turnos/{id}/cancelar/` - Acción personalizada (`@action`) para cancelar un turno.

### Ventas y Pedidos
- `GET /api/pedidos/` - Listado paginado con **Nested Serializers** (detalles anidados con anteojos y cliente).
- `POST /api/pedidos/` - Creación de pedidos con cálculo automático de totales.
- `POST /api/pedidos/{id}/confirmar/` - Acción personalizada (`@action`) que descuenta stock en transacción atómica (`transaction.atomic`).
- `POST /api/pedidos/{id}/cancelar/` - Acción personalizada (`@action`) que cancela el pedido y restituye el stock al inventario.
- `GET/POST /api/resenas/` - Reseñas de clientes para anteojos.

### Autenticación y Documentación
- `POST /api/token/` - Obtención de par de tokens JWT (`access` y `refresh`).
- `POST /api/token/refresh/` - Renovación del token de acceso JWT.
- `GET /api/schema/` - Esquema OpenAPI 3.0 en formato YAML/JSON.
- `GET /api/docs/` - Interfaz interactiva Swagger UI.
- `GET /api/redoc/` - Documentación técnica ReDoc.
- `GET /api-auth/login/` - Autenticación por sesión para la API navegable de DRF.
- `GET /` - Vista principal de bienvenida interactiva.
- `GET /admin/` - Panel de administración de Django.

---

## 3. Filtros y Búsquedas

El endpoint `/api/anteojos/` admite filtros avanzados combinables:
- Rango de precios: `?precio_min=20000&precio_max=35000`
- Disponibilidad: `?en_stock=true`
- Marca, categoría o material: `?marca=1&categoria=1`
- Forma y género: `?forma=wayfarer&genero=unisex`
- Destacados: `?destacado=true`
- Búsqueda textual: `?search=luz+azul` (busca en nombre, SKU, marca y color)
- Ordenamiento: `?ordering=-precio` o `?ordering=nombre`

---

## 4. Requisitos y Tecnologías

- **Python**: 3.13+
- **Gestor de paquetes y entornos**: [uv](https://docs.astral.sh/uv/)
- **Framework Web**: Django 5.1+ / 6.1
- **API REST**: Django REST Framework 3.15+
- **Base de datos**: PostgreSQL en [Supabase](https://supabase.com/) vía Session Pooler (puerto 5432)
- **Autenticación**: JWT (`djangorestframework-simplejwt`) + Sesión de Django
- **CORS**: `django-cors-headers` configurado para orígenes frontend
- **Documentación**: OpenAPI 3.0 con `drf-spectacular` (Swagger y ReDoc)

---

## 5. Instalación y Puesta en Marcha

### Paso 1: Clonar el repositorio
```bash
git clone git@github.com:lneira1754/EFI_ING_API.git
cd EFI_ING_API
```

### Paso 2: Instalar dependencias con uv
```bash
uv sync
```

### Paso 3: Configurar variables de entorno
Copie el archivo de ejemplo:
```bash
cp .env.example .env
```
Complete las variables en `.env`:
```ini
SECRET_KEY=su-clave-secreta
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,testserver
DATABASE_URL=postgresql://postgres.PROYECTO:PASSWORD@aws-0-us-east-1.pooler.supabase.com:5432/postgres
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173
```

### Paso 4: Aplicar migraciones
```bash
uv run python src/manage.py migrate
```

### Paso 5: Cargar datos iniciales de prueba (con imágenes de anteojos)
```bash
uv run python src/manage.py cargar_datos
```

### Paso 6: Iniciar el servidor de desarrollo
```bash
uv run python src/manage.py runserver
```

El servidor quedará disponible en `http://127.0.0.1:8000/`.

---

## 6. Ejecución con Docker

Alternativa a la instalación manual: levanta la API junto con una base PostgreSQL local, sin necesidad de credenciales externas.

### Paso 1: Requisitos
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (incluye Docker Compose) en ejecución.
- El puerto `8000` libre en el equipo.

### Paso 2: Construir e iniciar los servicios
```bash
docker compose up --build
```

El archivo `docker-compose.yml` define dos servicios:
- **db**: PostgreSQL 17 con los datos persistidos en un volumen.
- **web**: la API servida con Gunicorn. Al iniciar espera a que la base esté disponible, aplica las migraciones (`migrate`) y, solo en el primer arranque, ejecuta `cargar_datos` con los datos de prueba e imágenes.

La configuración de Docker es independiente del archivo `.env`: no lo lee ni lo copia a la imagen, por lo que nunca modifica la base de datos de Supabase.

### Paso 3: Acceder a la aplicación
- Inicio: `http://localhost:8000/`
- Documentación Swagger: `http://localhost:8000/api/docs/`
- Panel de administración: `http://localhost:8000/admin/`

Usuarios disponibles (ver sección 7):
- Administrador: `admin` / `admin1234`
- Cliente: `cliente_demo` / `demo1234`

### Paso 4: Detener los servicios
```bash
docker compose down      # detiene los contenedores y conserva los datos
docker compose down -v   # detiene los contenedores y borra los volúmenes (base de datos e imágenes)
```

### Notas
- El compose usa `DEBUG=True` para que Django sirva las imágenes de `/media/`. Es una configuración pensada solo para evaluación local, no para producción.
- Para usar Supabase en lugar del PostgreSQL local, defina en el servicio `web` la variable `DATABASE_URL` con la cadena de conexión de Supabase y `DB_SSL_REQUIRE=True`.

---

## 7. Credenciales de Prueba

Tras ejecutar `cargar_datos`, los siguientes usuarios quedan disponibles:

### Administrador (Staff):
- **Usuario:** `admin`
- **Contraseña:** `admin1234`
- **Acceso:** Panel `/admin/`, endpoints completos de escritura en catálogo y gestión global.

### Cliente de Prueba:
- **Usuario:** `cliente_demo`
- **Contraseña:** `demo1234`
- **DNI:** `39485120`
- **Acceso:** Consulta de perfil propio `/api/clientes/me/`, recetas, turnos y pedidos propios.
