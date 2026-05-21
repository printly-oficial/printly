**Printly** — Plataforma Automatizada de Impresión 3D bajo Demanda



Sistema completo de automatización de impresión 3D que conecta una tienda online WooCommerce con una impresora 3D física, permitiendo que un pedido realizado por un cliente se envíe automáticamente a producción sin intervención manual.



**Características principales**



* Tienda online funcional con WordPress + WooCommerce
* Automatización completa del flujo de impresión
* API REST personalizada desarrollada en Python con Flask
* Comunicación remota mediante Ngrok
* Subida automática de archivos .gcode
* Inicio automático de impresión en impresora Elegoo
* Integración entre servidor web y máquina virtual Linux
* Sistema totalmente funcional sin depender de software propietario de pago
* Arquitectura modular y escalable





**Arquitectura del sistema**



Cliente Web

&#x20;    │

&#x20;    ▼

WooCommerce (WordPress)

&#x20;    │

&#x20;    ▼

Plugin PHP personalizado

&#x20;    │

&#x20;    ▼

API Flask en Python (Equipo en red local con la impresora)

&#x20;    │

&#x20;    ├──► Subida del archivo G-code

&#x20;    │

&#x20;    ├──► Comunicación HTTP con la impresora

&#x20;    │

&#x20;    └──► Comunicación WebSocket con la impresora

&#x20;                │

&#x20;                ▼

&#x20;       Elegoo Centauri Carbon

&#x20;                │

&#x20;                ▼

&#x20;        Inicio automático

&#x20;            de impresión





**Funcionamiento del sistema**



1. El cliente realiza un pedido en la tienda WooCommerce.

2\. WooCommerce cambia el pedido al estado Procesando.

3\. El plugin PHP detecta automáticamente el cambio de estado mediante el hook:

&#x20;  *woocommerce\_order\_status\_completed*

4\. El plugin envía una petición HTTP a la API Flask alojada en el equipo en local.

5\. La API Flask:

* Recibe el nombre del archivo .gcode
* Localiza el archivo correspondiente
* Lo sube automáticamente a la impresora
* Envía el comando de inicio de impresión mediante WebSocket

6\. La impresora comienza el proceso de fabricación automáticamente.





**Tecnologías utilizadas**



|Componente|Tecnología|
|-|-|
|Frontend tienda|WordPress|
|Ecommerce|WooCommerce|
|Backend automatización|PHP|
|API intermedia|Python + Flask|
|Exposición remota|Ngrok|
|Comunicación impresora|HTTP + WebSocket|
|Sistema operativo del equipo local|Windows|
|Hardware impresión|Elegoo Centauri Carbon|
|Desarrollo local|LocalWP|

&#x09;	



**Requisitos**



*Software*

* Python 3.12+
* Flask
* Requests
* websocket-client
* Ngrok
* WordPress 6.x
* PHP
* WooCommerce
* LocalWP



*Hardware*

* Impresora Elegoo Centauri Carbon
* Equipo anfitrión o máquina virtual
* Red local estable





**Instalación**



1. *Descargar el proyecto*

https://github.com/printly-oficial/printly



2\. *Instalar dependencias*

pip install flask requests websocket-client



3\. *Ejecutar la API Flask*

python app.py

La API quedará disponible normalmente en: http://127.0.0.1:5000



4\. *Exponer la API mediante Ngrok*

ngrok http 5000

Ngrok generará una URL pública similar a:

https://xxxxxxxx.ngrok-free.dev



Esa URL será utilizada por WooCommerce para comunicarse con la API Flask.





**Integración con WooCommerce**



El plugin PHP personalizado realiza una petición POST hacia la API Flask.



Ejemplo:



$url = PRINTLY\_API\_URL . '/print';



&#x20;   $response = wp\_remote\_post($url, \[

&#x20;       'timeout' => 30,

&#x20;       'headers' => \[

&#x20;           'Content-Type'     => 'application/json',

&#x20;           'X-Printly-Secret' => PRINTLY\_API\_SECRET,

&#x20;           'ngrok-skip-browser-warning' => 'true',

&#x20;       ],

&#x20;       'body' => json\_encode(\['filename' => $filename]),



**API Flask**



*Endpoint principal*

POST /print



*Body JSON*

&#x20;message = json.dumps({

&#x20;       'Id': '',

&#x20;       'Data': {

&#x20;           'Cmd': 128,

&#x20;           'Data': {

&#x20;               'Filename':           '/local/' + filename,

&#x20;               'StartLayer':         0,

&#x20;               'Calibration\_switch': 0,

&#x20;               'PrintPlatformType':  1,

&#x20;               'Tlp\_Switch':         0,

&#x20;           },

&#x20;           'From':        1,

&#x20;           'MainboardID': '',

&#x20;           'RequestID':   str(uuid.uuid4()),

&#x20;           'TimeStamp':   int(time.time() \* 1000),

&#x20;       }

&#x20;   })



*Respuesta*

print\_ok = start\_print(filename)

&#x20;   if not print\_ok:

&#x20;       return jsonify({'success': False, 'error': 'Error al lanzar impresión'}), 500



&#x20;   print(f'\[INFO] Impresión lanzada correctamente')

&#x20;   return jsonify({'success': True})





**Comunicación con la impresora**



*Subida del archivo G-code*

La API Flask realiza una subida multipart HTTP directamente a la impresora:

POST http://192.168.0.150/uploadFile/upload



*Parámetros utilizados*

|Campo|Descripción|
|-|-|
|TotalSize|Tamaño del archivo|
|Uuid|Identificador único|
|Offset|Offset de subida|
|Check|Checksum|
|S-File-MD5|Hash MD5|
|File|Archivo .gcode|





**Inicio automático de impresión**



Una vez subido el archivo, la API abre una conexión WebSocket a ws://192.168.0.150:3030/websocket



Y envía el comando de inicio:



'Cmd': 128,

&#x20;           'Data': {

&#x20;               'Filename':           '/local/' + filename,

&#x20;               'StartLayer':         0,

&#x20;               'Calibration\_switch': 0,

&#x20;               'PrintPlatformType':  1,

&#x20;               'Tlp\_Switch':         0,

&#x20;           },





**Ingeniería inversa del protocolo Elegoo**



La impresora Elegoo Centauri Carbon no dispone de documentación oficial pública para automatización remota.

El protocolo fue analizado mediante:



* Herramientas de desarrollo del navegador
* Captura de tráfico HTTP
* Inspección de WebSockets
* Análisis del funcionamiento interno de Elegoo Slicer



Gracias a ello fue posible descubrir:



* Endpoints HTTP internos
* Formato de subida de archivos
* Comandos WebSocket
* Estructura del protocolo de impresión





**Seguridad**



*Ngrok*

* La API Flask no se expone directamente a Internet.
* Ngrok actúa como túnel seguro HTTPS entre:

  * &#x09;WooCommerce
  * &#x09;Equipo local



*Validaciones implementadas*

* Verificación de existencia del archivo
* Manejo de errores HTTP
* Control de excepciones WebSocket
* Validación de nombres de archivo





**Pruebas realizadas**



* Subida automática de archivos .gcode
* Comunicación HTTP con la impresora
* Inicio automático mediante WebSocket
* Integración completa WooCommerce → API → Impresora
* Funcionamiento remoto mediante Ngrok





**Problemas encontrados**



*Restricciones de API propietaria*

Inicialmente se investigó el uso de la API oficial de SimplyPrint/Elegoo, pero:

* El acceso a la API requiere planes de pago
* Las API Keys dejan de funcionar en planes gratuitos
* La documentación pública es limitada



Por ello se optó por una solución basada en:

* Ingeniería inversa
* Comunicación directa con la impresora
* API Flask personalizada





**Posibles mejoras futuras**



* Sistema de cola de impresión
* Panel de control en tiempo real
* Monitorización del progreso de impresión
* Notificaciones automáticas
* Integración con múltiples impresoras
* Sistema de autenticación para la API





**Autor**



Adrián Cruz Recio - Proyecto Intermodular de 2º Sistemas Microinformáticos y Redes A, curso 2025-2026, IES Fidiana





**Licencia**



Proyecto desarrollado con fines educativos y académicos.

