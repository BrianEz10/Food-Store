## ADDED Requirements

### Requirement: Middleware de errores RFC 7807
El sistema SHALL capturar todas las excepciones no manejadas y retornar respuestas de error siguiendo el estándar RFC 7807 (Problem Details for HTTP APIs).

#### Scenario: Formato de error estándar
- **WHEN** ocurre cualquier error HTTP en la aplicación
- **THEN** la respuesta tiene Content-Type `application/problem+json` y contiene los campos: `type` (URI de referencia o "about:blank"), `title` (descripción corta del error), `status` (código HTTP numérico), `detail` (mensaje específico del error), `instance` (ruta del request que falló)

#### Scenario: Error de validación Pydantic
- **WHEN** un request tiene datos inválidos que Pydantic rechaza
- **THEN** se retorna HTTP 422 con `detail` que incluye los errores por campo en formato `[{"field": "email", "message": "invalid email format"}]`

#### Scenario: Error 500 no expone internals
- **WHEN** ocurre un error interno no manejado
- **THEN** se retorna HTTP 500 con `detail` genérico ("Error interno del servidor") sin exponer stack trace ni detalles de implementación al cliente, y se loguea el error completo en el servidor

### Requirement: Excepciones custom con mapeo a HTTP
El sistema SHALL definir clases de excepción custom que mapean a códigos HTTP específicos, permitiendo lanzar errores semánticos desde cualquier capa.

#### Scenario: Excepciones disponibles
- **WHEN** se consulta las excepciones custom disponibles
- **THEN** existen: `NotFoundError` (404), `ValidationError` (422), `UnauthorizedError` (401), `ForbiddenError` (403), `ConflictError` (409), `RateLimitError` (429)

#### Scenario: Lanzar excepción desde service
- **WHEN** un service lanza `NotFoundError("Producto con id 99 no encontrado")`
- **THEN** el middleware captura la excepción y retorna HTTP 404 con el mensaje como `detail` en formato RFC 7807

### Requirement: Rate limiting en endpoints sensibles
El sistema SHALL implementar rate limiting global con slowapi para proteger endpoints sensibles contra abuso.

#### Scenario: Configuración de slowapi
- **WHEN** la aplicación arranca
- **THEN** slowapi está configurado como middleware global con limiter disponible para decorar endpoints individuales

#### Scenario: Respuesta al exceder límite
- **WHEN** un cliente excede el límite de rate configurado para un endpoint
- **THEN** el servidor responde HTTP 429 Too Many Requests con header `Retry-After` indicando segundos de espera

### Requirement: CORS configurado para desarrollo
El sistema SHALL configurar CORS middleware para permitir requests cross-origin desde el frontend de desarrollo.

#### Scenario: Origen permitido
- **WHEN** un request llega desde `http://localhost:5173` (Vite dev server)
- **THEN** los headers CORS permiten el request (Access-Control-Allow-Origin, Access-Control-Allow-Methods, Access-Control-Allow-Headers, Access-Control-Allow-Credentials)

#### Scenario: Orígenes desde variable de entorno
- **WHEN** se configura `CORS_ORIGINS=["http://localhost:5173", "https://midominio.com"]`
- **THEN** ambos orígenes son permitidos por el middleware CORS

### Requirement: Servidor arrancable con documentación automática
El sistema SHALL arrancar con `uvicorn` y generar documentación OpenAPI automáticamente.

#### Scenario: Arranque exitoso
- **WHEN** se ejecuta `uvicorn app.main:app --reload`
- **THEN** el servidor arranca sin errores en el puerto 8000

#### Scenario: Swagger UI accesible
- **WHEN** se accede a `http://localhost:8000/docs`
- **THEN** se muestra Swagger UI con la documentación interactiva de la API

#### Scenario: ReDoc accesible
- **WHEN** se accede a `http://localhost:8000/redoc`
- **THEN** se muestra la documentación en formato ReDoc
