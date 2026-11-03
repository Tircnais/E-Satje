# Puesta en producción

Al momento el sitio esta abajo puesto la app y el sitio apuntan al mismo puerto lo que ocasiona un conflicto (el de waitress-serve 8080)

## Configuracion IIS

Para configurar IIS en Windows para servir una aplicación Flask utilizando Waitress, sigue estos pasos:

1. Asegúrate de tener Python y la biblioteca de Waitress instaladas en tu máquina.
2. Crea una nueva carpeta para tu aplicación Flask en la ruta de acceso que desees.
3. Copia todos los archivos relacionados con la aplicación Flask en la carpeta que acabas de crear.
4. Abre el Administrador de IIS desde el menú Inicio de Windows.
5. Haz clic en el nodo de tu servidor en el panel izquierdo y selecciona "Módulos" en el panel central.
6. Haz clic en "Agregar módulo" en el panel de acciones.
7. Asigna un nombre al nuevo módulo y asegúrate de que el "Tipo de entrada" esté establecido en "Código gestionado" y el "Paso de solicitud" en "Integrado".
8. Haz clic en "Añadir" en el campo "Ensamblado".
9. Busca la biblioteca de Waitress en tu máquina y selecciona el archivo "waitress.dll". Haz clic en "Aceptar".
10. En la sección de "Restricciones de acceso", establece "Permitir acceso" para todos los verbos HTTP.
11. Guarda la configuración y cierra el Administrador de IIS.
12. Abre el Panel de control de Windows y haz clic en "Herramientas administrativas".
13. Selecciona "Administrador de servicios de Internet (IIS)".
14. Haz clic en el nodo de tu servidor en el panel izquierdo y selecciona "Sitios".
15. Haz clic en "Agregar sitio web" en el panel de acciones.
16. Asigna un nombre a tu sitio web y selecciona la carpeta que creaste anteriormente como "Ruta de acceso física".
17. Haz clic en "Aceptar" para guardar la configuración del sitio.
18. Abre el archivo de configuración de Nginx y agrega una nueva entrada de servidor que apunte al sitio web que acabas de crear en IIS.
19. Reinicia IIS y Nginx para aplicar los cambios.
20. Accede a tu sitio web en el navegador para asegurarte de que la configuración se ha aplicado correctamente.

## Resumen

Se recomienda que para desplegar una aplicación Flask con Waitress en IIS, configuremos el "Tipo de entrada" en "Código gestionado" y el "Paso de solicitud" en "Integrado". Esto se puede hacer siguiendo los siguientes pasos:

1. Abrir IIS Manager
2. Seleccionar el sitio web donde deseas desplegar la aplicación Flask
3. Seleccionar "Configuración de controlador" en el panel derecho
4. Seleccionar "Controlador de solicitudes" en el menú desplegable
5. En la sección "Controlador de solicitudes", seleccionar "Agregar"
6. Seleccionar "Integrado" como "Paso de solicitud"
7. Seleccionar ".NET CLR" como "Tipo de entrada"
8. Hacer clic en "Aceptar" para guardar los cambios.

## Verificacion de la configuracion

Para verificar que el sitio web de IIS esté configurado correctamente para manejar solicitudes para la aplicación Flask, puedes seguir estos pasos:

1. Asegúrate de que la aplicación Flask se esté ejecutando correctamente en el servidor web (por ejemplo, usando Waitress).
2. Abre el Administrador de Internet Information Services (IIS Manager) en el servidor.
3. En el panel de navegación izquierdo, expande el nodo del servidor y luego expande el nodo de Sitios.
4. Busca el sitio web que aloja la aplicación Flask y selecciónalo.
5. En el panel central, haz clic en la opción "Probar configuración" en el panel Acciones.
6. Ingresa la URL de la aplicación Flask en el campo de URL de prueba y haz clic en el botón "Probar".

Espera a que se complete la prueba y verifica que se muestre un mensaje de "Prueba exitosa" y que la respuesta del servidor sea "200 OK".

Si la prueba es exitosa, significa que el sitio web de IIS está configurado correctamente para manejar solicitudes para la aplicación Flask. De lo contrario, es posible que debas revisar la configuración de IIS y asegurarte de que se haya seguido correctamente cada uno de los pasos necesarios para configurar el sitio web y la aplicación.