# Gestión de Clan Clash Royale
### Descripcción y utilidad de carpetas
* daemon: Se trata de un demonio que carga datos en nuestro MongoDB
* telegram: Bot para dar informes de datos recogidos. Además tendrá la función de dar alertas y demás.

### Funcionalidad de procesos
#### Daemon
Engargado de recoger estadísicas de combates y donaciones sobre los miembros del clan establecido en los ficheros de configuración.
Realizará un tratamiento de dichos datos y guardará la información de interés ya tratada en MongoDB.

#### Telegram
Proceso en continua ejecución en Telegram el cual mostrará los avances sobre los miembros del clan (Información con mas detalle para administradores del mismo), generación de alertas por inactividad de miembros, etc.
