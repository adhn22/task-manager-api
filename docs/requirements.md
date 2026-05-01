# Funcionalidades

## El usuario puede:
- Registrarse con email y contraseña
- Iniciar y cerrar sesión (JWT)
- Crear una tarea
- Ver todas sus tareas
- Ver el detalle de una tarea
- Editar una tarea
- Eliminar una tarea
- Filtrar tareas por estado y prioridad
- Marcar una tarea como completada

## Reglas de negocio
- Un usuario solo puede ver y modificar sus propias tareas
- Una tarea debe tener al menos un título
- La fecha límite no puede ser una fecha pasada al crearla
- Una tarea completada no puede editarse

## Requisitos no funcionales
- Autenticación con JWT
- Respuestas de error claras y consistentes
- Paginación en el listado de tareas
- Documentación automática con Swagger