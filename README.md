# Intefaz de Usuario para Sistema de Presion del INM

El presente repositorio tiene como finalidad la documentacion registro y versionamiento de todo el trabajo en realizado en el marco del trabajo de grado titulado **"Implementación de un sistema de adquisición de datos para la medición y calibración de instrumentos de vacío del laboratorio de presión y temperatura"**. El objetivo general del proyecto como trabajo de grado es la implementacion y diseño de un sistema de adquisición de datos que permita la comunicación entre sensor, controlador y reporte (PC); mediante una interfaz de usuario, para su aplicación en procesos de medición y calibración de instrumentos de vacío del INM. Como objetivos especificos para el desarrollo se realizara:

- Reconocimiento y descripcion de los elementos y estructura del sistema de presion del INM.
- Determinacion y refinamiento continuo de los requerimientos funcionales para la interfaz de usuario.
- Profundizacion en protocolos de comunicacion y funcionamiento general de controladores mediante la revision de manuales tecnicos.
- Establecimiento exitoso de comunicacion con serial entre controladores del sistema y cliente (PC).
- Desarrollar e implementacion de interfaz gráfica de usuario mediante Python para la adquisicion de datos y comando facilitado con el sistema de presion.
- Documentacion de un manual de usuario para el uso de la interfaz grafica de usuario, documentacion de diseño, procedimiento y resultados.

Este repositorio contendrá el código fuente, la documentación técnica, informes intermedios, y cualquier material de apoyo que sea necesario para la ejecución y evaluación del trabajo de grado.

## Estructura del repositorio

- `resources/` - Recursos y fuentes de documentacion
  - `Anotaciones_Ventanas.txt` - Anotaciones sobre ventanas de comunicacion para controlador 74-FSAG
  - `TwisTorr 74 FS AG Rack Controller.pdf` - Manual de usuario de Agilent del controlador 74-FSAG
  - `XGS-600 Gauge Controller.pdf` - Manual de usuario de Agilent del controlador XGS-600
- `tests/` - Scripts de preuba en python y c++ para arduino
  - `arduino_serial_tester/` - Script en carpeta requerida para simualcion de comunicacion serial con Arduino UNO a 9600 baudios
  - `gui_elements_visualizer.py` - Script de preuba de visualicacion de elementos graficos de PyQt6
  - `test_comunication_74FSAG.py` - Script de preuba de comunicacion de controlador 74-FSAG
  - `test_serial.py` - Script de preuba de comunicacion de serial general por consola de Python
-  `README.md` - Descripcion y documentacion general del proyecto

## Bitacora de trabajo

| Fecha      | Actividad Realizada 
|------------|---------------------
| 2025/04/08 | Creacion del repositorio de trabajo para el proyecto de grado. Se agrega primer script de pruebas de comunicacion. Se prepara script para simulacion de comunicacion serial mediante Arduino UNO.
| 2025/04/10 | Reunion inical con directores del proyecto del INM. Se realiza reconocimiento del sistema de presion. Se identifican algunos requerimientos clave para la interfaz de usuario. Se identifican los controladores 74FSAG y XGS600 como elementos clave para la comunicacion. Se realiza primer boceto de estructura de conexiones del sistema de presion.
| 2025/04/23 | Creacion de interfaz grafica de prueba de comunicacion para el controlador 74FSAG. Se realiza lectura de manual tecnico para la comunicacion por ventanas del controlador. Se realiza pruebas de uso de la biblioteca de PyQt6.
| 2025/04/24 | Terminacion de la programacion de prueba de comunicacion para el controlador 74FSAG. Se realiza simulacion en casa de la comunicacion serial con el controlador mediante Arduino UNO. Se realiza un reordenamiento a la estructura de archivos del repositorio. Se comaprte colaboracion a repositorio via invitacion por correo.
| 2025/04/29 | Realizacion de la primera prueba de comunicacion con el controlador 74FSAG. Se genera copia del repositorio en PC de desarrollo del INM. Se establecen los puertos de comunicacion y baudios para la comunicacion via adaptador USB a RS232. Se presenta fallo en la lectura de la respuesta del controlador. Se realiza encendido y apagado remoto de la bomba turbo de manera exitosa. Se realiza diagnostico de los fallos de la recepcion de la comunicacion. Se realiza prueba sin respuesta de comunicacion con el controlador XGS600.
| 2025/05/04 | Correccion de linea de codigo para prueba con el controlador 74FSAG. Se realiza revision en el uso de funciones de QtSerial de la biblioteca PyQt6. Se agrega script demostrativo para elementos de GUI en PyQt6.
| 2025/05/09 | Establecimiento de respuesta con el controlador 74FSAG. Se realiza lectura de parametros de la bomba incluyendo presion, temperatura, potencia. Se realiza lectura de otros parametros. Se configura via RS232 la frecuencia de operacion de la bomba. Se registra en archivo .txt las ventanas de comunicacion lectura y escritura criticas para el programa.
| 2025/05/10 | Creacion de documentacion para el repositorio. Se actualiza bitacora de trabajo. Se realiza ajustes a nombres de archivo y nombre del repositorio.

