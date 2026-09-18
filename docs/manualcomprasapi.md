Sistema Integrado Registro Electrónico- SIRE
Compras
SERVICIOS WEB API – SIRE COMPRAS
Manual de Usuario
2
Introducción
Este documento Manual de usuario de los Servicios Web Api – SIRE Compras, ha sido
diseñado para ser usado como instructivo en la integración de los servicios Web Api
expuestos del SIRE Compras por la SUNAT con los sistemas informáticos de los declarantes,
que tienen la necesidad de integrarlos desde sus aplicaciones.
El proyecto SIRE COMPRAS que expone los servicios aquí descritos ha sido desarrollado con
la finalidad de facilitar el cumplimiento voluntario de las obligaciones tributarias de los
contribuyentes y toma como base al comprobante de pago electrónico para el control del
flujo de la transacción del IGV y la información que se genera en cada fase.
El SIRE Compras una vez autenticado le permite al contribuyente:
Servicios principales:
● Descargar la propuesta (Servicio: Descargar propuesta) con el detalle individualizado
de los comprobantes y documentos que deberían integrar el registro de compras que
genere, la cual podría ser la propuesta inicial de la SUNAT o aquella que fue
actualizada por el contribuyente.
3
● Aceptar Propuesta (Servicio: Aceptar propuesta) permite actualizar el estado del
registro libro y Control de procesos para indicar que se está registrando un preliminar
a través de la propuesta aceptada.
● Reemplazar propuesta (Servicio: Reemplazar propuesta) permite al generador,
reemplazar la propuesta SUNAT con lo considerado por el contribuyente mediante el
uso de un archivo de formato .txt.
● Registrar preliminar (Servicio: Registrar preliminar) permite registrar los
comprobantes No domiciliados y los comprobantes de la propuesta o del preliminar
según corresponda al proceso ejecutado por el generador.
Servicios complementarios al proceso:
● Descargar el resumen consolidado (Servicio: Descargar resumen de comprobantes
RCE) de todos los comprobantes de pago y documentos que le fueron emitidos
electrónicamente en su calidad de usuario o adquiriente, este resumen está separado
por tipo de comprobante o documento, mostrando respecto de cada uno la cantidad
exacta de los mismos, así como la base imponible, monto de IGV e importe total a
pagar, de acuerdo a lo registrado hasta el momento de la consulta.
● Descargar inconsistencias por montos totales (Servicio: Descargar inconsistencia por
Monto Totales), Servicio WEB API que permite descargar las inconsistencias
asociadas a los montos totales de la propuesta versus el archivo de carga de
reemplazo de la propuesta.
● Descargar inconsistencias por comprobantes de pago (Servicio : Descargar
Inconsistencias por comprobantes) este servicio WEB API permite descargar las
inconsistencias asociadas a los comprobantes que se encuentran en la fase actual de
proceso del RCE, que pueden ser 1-Propuesta o 3-Preliminar.
● Consultar el estado del ticket (Servicio: Consultar estado del ticket) permite al
generador consultar el estado del número ticket asociado al proceso que genera el
archivo de descarga o carga. Si el estado es "Terminado", devuelve el nombre del
archivo generado, si el estado del ticket es diferente, devuelve el estado del ticket.
● Descargar archivo (Servicio: Descargar archivo ticket generado) permite realizar la
descarga de los archivos generados zipeados y particionados guardados en el
fileserver.
Entre otros servicios, que se detallarán en el presente manual.
La siguiente imagen muestra el flujo mínimo para registrar el preliminar del Registro de
Compras Electrónico de un periodo:
4
Aceptar propuesta:
Reemplazar propuesta:
El manual comienza con la sección que describe el procedimiento inicial para obtener las
credenciales del token, necesarios para hacer uso de los servicios.
5
Tabla de contenido
Introducción......................................................................................................................................2
Control de cambios del documento..................................................................................................8
I. Guía de Uso .............................................................................................................................12
1. Servicio prerrequisito..............................................................................................................12
2. Secuencia de servicios mínimos para Registrar Preliminar.....................................................14
Funcionalidad 1: Aceptar Propuesta ...........................................................................................14
Funcionalidad 2: Reemplazar Propuesta.....................................................................................16
Funcionalidad 3: Registrar Preliminar.........................................................................................17
3. Secuencia de servicios interdependientes que completan funcionalidades del SIRE Compras
19
Funcionalidad 1: Registrar no domiciliados................................................................................19
Funcionalidad 2: Complementar propuesta (complementar, agregar y excluir/incluir) ............20
Funcionalidad 3: Tipo de cambio masivo....................................................................................20
Funcionalidad 4: Datos FV0621...................................................................................................21
Funcionalidad 5: Importar comprobantes en preliminar............................................................22
Funcionalidad 6: Eliminar comprobantes en preliminar.............................................................23
Funcionalidad 7: Eliminar comprobantes no domiciliados.........................................................24
Funcionalidad 8: Cargar ajustes posteriore.................................................................................25
Funcionalidad 9: Enviar ajustes posteriores................................................................................25
Funcionalidad 10: Eliminar comprobantes en ajustes posteriores.............................................26
Funcionalidad 11: Cargar ajustes posteriores no domiciliados...................................................27
Funcionalidad 12: Enviar ajustes posteriores no domiciliados...................................................28
Funcionalidad 13: Eliminar comprobantes en ajustes posteriores no domiciliados...................29
Funcionalidad 14: Cargar ajustes posteriores de periodos anteriores .......................................29
Funcionalidad 15: Enviar ajustes posteriores de periodos anteriores........................................30
Funcionalidad 16: Eliminar comprobantes en ajustes posteriores de periodos anteriores.......31
Funcionalidad 17: Cargar ajustes posteriores de periodos anteriores no domiciliados.............32
Funcionalidad 18: Enviar ajustes posteriores de periodos anteriores no domiciliados .............33
Funcionalidad 19: Eliminar comprobantes en ajustes posteriores de periodos anteriores no
domiciliados ................................................................................................................................34
Funcionalidad 20: Consultar estado de envío de ticket..............................................................35
Funcionalidad 21: Descargar archivo. .........................................................................................36
Funcionalidad 22: Eliminar preliminar registrado.......................................................................37
4. Servicios accesorios que pueden ser consumidos en el SIRE Compras ..................................38
5. Documentación Servicios Web API .........................................................................................40
6
5.1 Servicio Api Seguridad...........................................................................................................40
5.2 Servicio Web Api aceptar propuesta.....................................................................................42
5.3 Servicio Web Api importar reemplazo de la propuesta ........................................................43
5.4 Servicio Web Api registrar preliminar...................................................................................44
5.5 Servicio Web Api cargar registro de compra no domiciliados ..............................................45
5.6 Servicio Web Api importar datos complementarios de los CP de la propuesta ...................47
5.7 Servicio Web Api importar nuevos comprobantes preliminar..............................................48
5.8 Servicio Web Api incluir-excluir comprobantes de la propuesta..........................................50
5.9 Servicio Web Api importar nuevos comprobantes de pago .................................................51
5.10 Servicio Web Api importar tipo de cambio masivo.............................................................53
5.11 Servicio Web Api actualizar reintegro del crédito fiscal .....................................................54
5.12 Servicio Web Api actualizar crédito fiscal especial .............................................................55
5.13 Servicio Web Api actualizar coeficiente de prorrata...........................................................57
5.14 Servicio Web Api consultar FV0621 ....................................................................................58
5.15 Servicio Web Api eliminar comprobante de la propuesta ..................................................59
5.16 Servicio Web Api eliminar comprobante del preliminar.....................................................60
5.17 Servicio Web Api eliminar preliminar..................................................................................62
5.18 Servicio Web Api cargar ajustes posteriores.......................................................................63
5.19 Servicio Web Api enviar ajustes posteriores.......................................................................65
5.20 Servicio Web Api eliminar comprobante de ajustes posteriores........................................66
5.21 Servicio Web Api cargar ajustes posteriores no domiciliados ............................................67
5.22 Servicio Web Api enviar ajustes posteriores no domiciliados ............................................69
5.23 Servicio Web Api eliminar comprobante de ajustes posteriores no domiciliados .............71
5.24 Servicio Web Api cargar ajustes posteriores de periodos anteriores.................................72
5.25 Servicio Web Api enviar ajustes posteriores de periodos anteriores.................................74
5.26 Servicio Web Api eliminar comprobante de ajustes posteriores de periodos anteriores..75
5.27 Servicio Web Api cargar ajustes posteriores de periodos anteriores no domiciliados.......77
5.28 Servicio Web Api enviar ajustes posteriores de periodos anteriores no domiciliados.......78
5.29 Servicio Web Api eliminar comprobante de ajustes posteriores de periodos anteriores no
domiciliados ................................................................................................................................80
5.31 Servicio Web Api consultar estado de envío de ticket........................................................81
5.32 Servicio Web Api descargar archivo....................................................................................84
5.33 Servicio Web Api consultar año y mes................................................................................86
5.34 Servicio Web Api descargar propuesta ...............................................................................87
5.35 Servicio Web Api descargar resumen..................................................................................89
5.36 Servicio Web Api descargar resumen inconsistencias RCE .................................................91
7
5.37 Servicio Web Api descargar excluidos.................................................................................92
5.38 Servicio Web Api eliminar comprobante no domiciliado ...................................................94
5.39 Servicio Web Api exportar preliminar de registro de compras no domiciliados ................96
5.40 Servicio Web Api exportar preliminar de registro de compras...........................................98
5.41 Servicio Web Api descargar reporte de casillas................................................................100
5.42 Servicio Web Api descargar inconsistencias en registros preliminar registrado ..............101
5.43 Servicio Web Api descargar inconsistencias por montos totales......................................102
5.44 Servicio Web Api descargar inconsistencias por comprobante pago ...............................104
5.45 Servicio Web Api descargar ajustes posteriores...............................................................106
5.46 Servicio Web Api descargar ajustes posteriores no domiciliados.....................................107
5.47 Servicio Web Api descargar ajustes posteriores de periodos anteriores .........................108
5.48 Servicio Web Api descargar ajustes posteriores de periodos anteriores no domiciliados110
5.49 Servicio Web Api descargar constancia de recepción.......................................................111
5.50 Servicio Web Api descargar reporte consolidado registro por periodo............................112
5.51 Servicio Web Api descargar RCE por periodo ...................................................................114
5.52 Servicio Web Api descargar reporte inconsistencias por periodo ....................................115
5.53 Servicio Web Api descargar reporte CAR..........................................................................116
5.54 Servicio Web Api descargar reporte estadístico compras por proveedor por periodo ....118
5.55 Servicio Web Api descargar reporte estadístico NC-ND por proveedor y periodo...........119
5.56 Servicio Web Api descargar reporte estadístico Compras por día y periodo ...................121
5.57 Servicio Web Api descargar reporte estadístico Compras por CIIU..................................123
5.58 Servicio Web Api descargar reporte de cumplimiento .....................................................124
5.59 Servicio Web Api consultar ajustes posteriores RCE.........................................................126
5.60 Servicio Web Api eliminar preliminar registrado ..............................................................127
5.61 Servicio Web Api consultar preliminares registrados.......................................................128
6. Documentación TUS.IO .........................................................................................................129
7. Anexos...................................................................................................................................130
7.1 Anexo I: Indicador de carga masiva.....................................................................................130
7.2 Anexo II: Tipo de ajuste posterior.......................................................................................132
7.3 Anexo III: Extension del archivo a descargar......................................................................132
7.4 Anexo IV: Ejemplo cliente TUS JAVA ..................................................................................132
Clase:: TusResponseBody.java ......................................................................................................133
Clase:: Http401And403CodeException.java..................................................................................135
Clase:: Http422CodeException.java ..............................................................................................136
Clase:: HttpErrorCodeException.java............................................................................................137
Clase:: TusClientCustom.java ........................................................................................................138
8
Clase: TusUploaderCustom.java....................................................................................................148
Clase:: Demo.java..........................................................................................................................158
Control de cambios del documento
N.
°
Descripción Fecha Versión Responsable Motivo de
cambio
1
Creación del
documento 01/02/2022 1.0.0 FSW III creación
2
Actualización del
documento 31/05/2023 2.0.0 FSW Actualización
3
Actualización del
documento 03/11/2023 v19 INSI Actualización
4
Actualización del
documento 06/11/2023 V20 FSW Actualización
5
Actualización del
documento 09/01/2024 V21 INSI
Se agrega
nuevo modelo
de cliente TUS
JAVA que
permite
recuperar los
mensajes de
error 422.
6
Se actualizan mensajes
de error para los
servicios 5.4 y 5.17
05/03/2024 V22 INSI
Actualización
por el pase
PAS20241U210
800038
7
Actualizacion del
documento 18/03/2024 V23 INSI
Actualización
por el pase
PAS20241U210
800039
Se modifico el
Servicio Web
Api eliminar
preliminar 5.17
– Compras
Se incluyeron
9
los siguientes
mensajes de
error:
CATALOGO_ER
ROR_2301
CATALOGO_ER
ROR_2302
CATALOGO_ER
ROR_2297
Se modifico el
Servicio Web
Api descargar
inconsistencias
por
comprobante
pago 5.44
–
Compras
Se incluyeron
los siguientes
mensajes de
error:
CATALOGO_ER
ROR_2303
8 Se modifica el 5.32
Servicio Web Api
descargar archivo
10/01/2025 V24 INSI Se modifica la
url.
Se agrega 3
parámetros
adicionales
perTributario
-
alfanumérico
-
String
codProceso
-
alfanumérico
-
String
numTicket
-
alfanumérico
-
String
Se modifica la
fila de
Evidencias
9 Actualizacion del
documento
05/06/2025 V25 INSI Se agrega el
servicio 5.61
Servicio Web
Api consultar
preliminares
registrados
Se agregó en el
servicio 5.17
10
Servicio Web
Api eliminar
preliminar el
mensaje de
error “2009
- El
campo
'indEliminar'
enviado no es
válido”
Se modifica en
5.32 Servicio
Web Api
descargar
archivo la
descripción
general y de los
siguientes
parámetros:
nomArchivoRep
orte
-
alfanumérico
-
String
codTipoArchivo
Reporte
-
numérico
-String
codLibro
-
numérico
-String
perTributario
-
alfanumérico
-
String
codProceso
-
alfanumérico
-
String
numTicket
-
alfanumérico
-
String
10 Actualizacion del
documento
16/06/2025 V26 INSI Se modificó en
5.32 Servicio
Web Api
descargar
archivo el
parámetro de
salida por
Buffer
-binary
-
binary: Arreglo
de bits
11 Actualización del
documento
13/08/2025 V27 INSI Se actualiza el
diagrama de
Servicios
accesorios que
pueden ser
consumidos en
el SIRE
11
Compras, se
agrega el
servicio
consultar
preliminar
registrado y
eliminar
preliminar
registrado
12
I. Guía de Uso
1. Servicio prerrequisito
a) Diagrama: Esquema gráfico de la secuencia de pasos para llegar a consumir el
servicio web, a nivel de proceso para obtener el token
El contribuyente, usuario del sistema SIRE Compras, que se encuentra obligado a
generar el registro de compras de manera periódica, debe ingresar al Portal SOL de
la SUNAT (https://e-menu.sunat.gob.pe/cl-ti-itmenu/MenuInternet.htm) e iniciar
sesión con su correspondiente Clave SOL.
Ingresar a la opción “EMPRESAS / Credenciales de API SUNAT / Credenciales de API
SUNAT/ Credenciales de API SUNAT/ Gestión Credenciales de API SUNAT”
Se muestran las secciones:
● REGISTRE SU APLICACIÓN
○ Nombre de su aplicación: Alfanumérico, obligatorio y con longitud de
50 caracteres. Ejemplo: Mi Organización ABC
○ URL de su aplicación: Alfanumérico, obligatorio y con longitud de
260. Ejemplo: https://miOrganizacionAbc.com
● SECCIÓN LISTADO DE URI’S
○ Botón de acción:
■ Seleccionar Todos, permite seleccionar o marcar todas las
casillas que hacen referencia a la URI’s
■ Deseleccionar Todos, permite desmarcar todas las casillas
que han sido marcadas o seleccionadas.
○ Lista de URI’s, muestra un listado de URI´s donde el contribuyente
debe seleccionar las URI´s que va consumir para que el sistema le
brinde el acceso correspondiente.
13
○ El contribuyente deberá seleccionar la URI: “MIGE RCE y RVIE – SIRE ”
● ALCANCE
○ Desktop, indica que la(s) uri(s) seleccionada(s) van a ser consumidas
desde una interfaz de escritorio.
○ Web, indica que la(s) uri(s) seleccionada(s) van a ser consumidas
desde una interfaz web.
● BOTÓN DE ACCIÓN
○ Guardar, registrar en la base de datos la información de la empresa
del contribuyente, las uris el cual va a consumir y el alcance.
○ Si el contribuyente ya registró su aplicación y las URI´s
correspondientes
○ Seleccionar el botón Editar ubicado en la parte superior derecha
○ El usuario del SIRE, debe ingresar los datos solicitados.
○ Una vez completados los datos requeridos debe seleccionar MIGE
RCE y RVIE - SIRE y seleccionar como alcance Web.
○ Seleccionar el botón Guardar.
○ Al presionar el botón “ACEPTAR”, el sistema genera las credenciales
correspondientes:
14
El usuario del SIRE que utiliza los servicios Rest, debe almacenar estos valores para
ser utilizado mediante su Sistema de Información.
Una vez que el usuario cuente con los datos del client_id y client_secret además
de su cuenta de usuario y clave SOL, podrán generar el token del api-seguridadSUNAT con la siguiente url:
https://api-seguridad.sunat.gob.pe/v1/clientessol/{client_id}/oauth2/token/
Ejemplo:
https://api-seguridad.sunat.gob.pe/v1/clientessol/9cae24a9-10d7-48b0-bee0-
e94bd56947e3/oauth2/token/
b) Servicios Necesarios:
● 5.1 Servicio Api Seguridad
2. Secuencia de servicios mínimos para Registrar Preliminar
Funcionalidad 1: Aceptar Propuesta
a) Diagrama: Esquema gráfico de la secuencia de pasos para llegar a consumir el
servicio aceptar la propuesta
15
Nota: los servicios accesorios de “5.37 Servicio Web Api descargar excluidos”,
“5.43 Servicio Web Api descargar inconsistencias por montos totales” y “5.44
Servicio Web Api descargar inconsistencias por comprobante pago” son algunos
de los servicios que se ponen a disposición del generador. La lista de servicios
accesorios se encuentra en el punto “4. Servicios accesorios que pueden ser
consumidos en el SIRE Compras”.
Este servicio permite registrar un preliminar del RCE mediante la aceptación de
una propuesta, como resultado se obtiene un ticket asociado al proceso.
Este servicio debe contemplar dos escenarios:
● Enviar solo comprobantes de la propuesta sin incluir comprobantes con “No
Domiciliados” (ver servicios que se pueden invocar en el paso b), en este caso:
16
○ Se activa el proceso “En Generación de registro”, etapa: Preliminar
registrado
○ codTipoRegistro (1 Registro de compras)
○ Devuelve respuesta (T o F)
● Enviar comprobantes de la propuesta que incluye comprobantes con “No
Domiciliados” (se detallará más adelante), en este caso:
○ codTipoRegistro (2 Registro de compras no domiciliados)
○ Se devuelve un mensaje: “Debe completar con el envío de los
Comprobantes de pago no domiciliados”
○ Para este caso deberá hacer uso del servicio “5.5 Servicio Web Api
cargar registro de compra no domiciliados” para continuar el flujo.
b) Servicios que se pueden invocar:
● 5.1 Servicio Api Seguridad (necesario)
● 5.33 Servicio Web Api consultar año y mes del RCE (opcional)
● 5.34 Servicio Web Api descargar propuesta (opcional)
● 5.31 Servicio Web Api consultar estado ticket (opcional)
● 5.32 Servicio Web Api descargar archivo (opcional)
● 5.2 Servicio Web Api aceptar propuesta (necesario)
Funcionalidad 2: Reemplazar Propuesta
a) Diagrama: Esquema gráfico de la secuencia de pasos para llegar a consumir el
servicio reemplazar la propuesta
17
Nota: los servicios accesorios de “5.37 Servicio Web Api descargar excluidos”,
“5.43 Servicio Web Api descargar inconsistencias por montos totales” y “5.44
Servicio Web Api descargar inconsistencias por comprobante pago” son algunos
de los servicios que se ponen a disposición del generador. La lista de servicios
accesorios se encuentra en el punto “4. Servicios accesorios que pueden ser
consumidos en el SIRE Compras”.
Servicio web api que permite al generador, reemplazar la propuesta SUNAT con
lo considerado por el contribuyente mediante el uso de un archivo de formato
.txt zipeado.
Si el estado del generador es “baja definitiva”, solo se permitirá actualizar la
información correspondiente a los periodos donde estuvo activo o con
suspensión temporal (generó y/o fue omiso a la generación del registro), en caso
haya generado el registro solo se permitirá la presentación de ajustes
posteriores.
b) Servicios que se pueden invocar:
● 5.1 Servicio Api Seguridad (necesario)
● 5.33 Servicio Web Api consultar año y mes del RCE (opcional)
● 5.34 Servicio Web Api descargar propuesta (opcional)
● 5.31 Servicio Web Api consultar estado ticket (opcional)
● 5.32 Servicio Web Api descargar archivo (opcional)
● 5.3 Servicio Web Api importar reemplazo de la propuesta (necesario)
Funcionalidad 3: Registrar Preliminar
a) Diagrama: Esquema gráfico de la ejecución de servicios que mantienen
interdependencia para consumir el servicio Registrar preliminar
18
Servicio WEB API que permitirá al generador registrar el preliminar enviando con
esa acción a la opción de generación, antes de su invocación es opcional registrar
operaciones con no domiciliados utilizando el servicio “Registrar no
domiciliados”.
Si el estado del generador es baja definitiva, solo se debe permitir actualizar la
información correspondiente a los periodos donde estuvo activo (generó y/o fue
omiso a la generación). En caso haya generado el registro solo se permite la
presentación de ajustes posteriores.
b) Servicios que se pueden invocar:
● 5.1 Servicio Api Seguridad (necesario)
● 5.7 Servicio Web Api importar nuevos comprobantes preliminar (opcional)
● 5.16 Servicio Web Api eliminar comprobante del preliminar (opcional)
● 5.17 Servicio Web Api eliminar preliminar(opcional)
● 5.4 Servicio Web Api registrar preliminar (necesario)
19
3. Secuencia de servicios interdependientes que completan
funcionalidades del SIRE Compras
Funcionalidad 1: Registrar no domiciliados
a) Diagrama: Esquema gráfico de la ejecución de servicios que mantienen
interdependencia para consumir el servicio registrar no domiciliados
Para poder consumir el servicio Registrar No Domiciliados con Propuesta o con
Preliminar, previamente debe haberse aceptado la Propuesta o Registrado el
preliminar y en cualquiera de los casos debe haberse elegido que “si” desea
agregar comprobantes No domiciliados.
b) Servicios que se pueden invocar:
● 5.1 Servicio Api Seguridad (necesario)
● 5.33 Servicio Web Api consultar año y mes del RCE (necesario)
● 5.5 Servicio Web Api cargar registro de compra no domiciliados (necesario)
● 5.17 Servicio Web Api eliminar preliminar (opcional)
● 5.38 Servicio Web Api eliminar comprobante no domiciliado (opcional)
● 5.4 Servicio Web Api registrar preliminar (necesario)
20
Funcionalidad 2: Complementar propuesta (complementar, agregar y
excluir/incluir)
a) Diagrama: Esquema gráfico de la ejecución de servicios que mantienen
interdependencia para consumir el servicio complementar propuesta
(complementar, agregar y excluir/incluir)
Servicio web api que permite al generador, complementar la propuesta
mediante el uso de un archivo de formato .txt zipeado.
b) Servicios que se pueden invocar:
● 5.1 Servicio Api Seguridad (necesario)
● 5.33 Servicio Web Api consultar año y mes del RCE (necesario)
● 5.6 Servicio Web Api importar datos complementarios de los CP de la
propuesta
● 5.8 Servicio Web Api incluir-excluir comprobantes de la propuesta
● 5.9 Servicio Web Api importar nuevos comprobantes de pago
Funcionalidad 3: Tipo de cambio masivo
a) Diagrama: Esquema gráfico de la ejecución de servicios que mantienen
interdependencia para consumir el servicio Tipo de cambio masivo
21
Servicio web api que permite al generador, importar el tipo de cambio masivo
mediante el uso de un archivo de formato .txt
b) Servicios que se pueden invocar:
● 5.1 Servicio Api Seguridad (necesario)
● 5.33 Servicio Web Api consultar año y mes del RCE (necesario)
● 5.34 Servicio Web Api descargar propuesta (opcional)
● 5.10 Servicio Web Api importar tipo de cambio masivo (necesario)
Funcionalidad 4: Datos FV0621
a) Diagrama: Esquema gráfico de la ejecución de servicios que mantienen
interdependencia para consumir los servicios asociados a los datos de FV0621.
22
b) Servicios que se pueden invocar:
● 5.1 Servicio Api Seguridad (necesario).
● 5.33 Servicio Web Api consultar año y mes del RCE (necesario)
● 5.11 Servicio Web Api actualizar reintegro del crédito fiscal
● 5.12 Servicio Web Api actualizar crédito fiscal especial
● 5.13 Servicio Web Api actualizar coeficiente de prorrata
● 5.14 Servicio Web Api consultar FV0621
Funcionalidad 5: Importar comprobantes en preliminar
a) Diagrama: Esquema gráfico de la ejecución de servicios que mantienen
interdependencia para consumir el servicio importar comprobantes en
preliminar
23
Para poder consumir el servicio importar comprobantes en preliminar,
previamente debe haber reemplazado la propuesta.
b) Servicios que se pueden invocar:
● 5.1 Servicio Api Seguridad (necesario)
● 5.33 Servicio Web Api consultar año y mes del RCE (necesario)
● 5.3 Servicio Web Api importar reemplazo de la propuesta(necesario)
● 5.7 Servicio Web Api importar nuevos comprobantes preliminar (necesario)
Funcionalidad 6: Eliminar comprobantes en preliminar
a) Diagrama: Esquema gráfico de la ejecución de servicios que mantienen
interdependencia para consumir el servicio Eliminar comprobantes en preliminar
24
Para poder consumir el servicio Eliminar comprobantes en preliminar,
previamente debe haber reemplazado la propuesta.
b) Servicios que se pueden invocar:
● 5.1 Servicio Api Seguridad (necesario)
● 5.7 Servicio Web Api importar nuevos comprobantes preliminar (opcional)
● 5.16 Servicio Web Api eliminar comprobante del preliminar (necesario)
● 5.17 Servicio Web Api eliminar preliminar
Funcionalidad 7: Eliminar comprobantes no domiciliados
a) Diagrama: Esquema gráfico de la ejecución de servicios que mantienen
interdependencia para consumir el servicio Eliminar comprobantes no
domiciliados
25
Para poder consumir el servicio Eliminar comprobantes no domiciliados,
previamente debe haberse ejecutado el servicio de Cargar no domiciliados,
habiendo aceptado o reemplazado la propuesta.
b) Servicios que se pueden invocar:
● 5.1 Servicio Api Seguridad (necesario)
● 5.2 Servicio Web Api aceptar propuesta (o se acepta o se reemplaza)
● 5.5 Servicio Web Api cargar registro de compra no domiciliados (necesario)
● 5.38 Servicio Web Api eliminar comprobante no domiciliado (necesario)
Funcionalidad 8: Cargar ajustes posteriore
a) Diagrama: Esquema gráfico de la ejecución de servicios que mantienen
interdependencia para consumir el servicio Cargar Ajustes Posteriores RCE
Para poder consumir el servicio Cargar Ajustes Posteriores RCE, debe primero
haber generado el periodo que desea ajustar y el registro de operaciones del
RCE debe tener información. Opcionalmente y antes de cargar los ajustes
posteriores del RCE puede descargar los ajustes posteriores propuestos por
SUNAT para utilizarlos en su archivo de carga.
b) Servicios que se pueden invocar:
● 5.1 Servicio Api Seguridad (necesario)
● 5.33 Servicio Web Api consultar año y mes del RCE (necesario)
● 5.45 Servicio Web Api descargar ajustes posteriores (opcional)
● 5.18 Servicio Web Api cargar ajustes posteriores (necesario)
● 5.31 Servicio Web Api consultar estado ticket
● 5.32 Servicio Web Api descargar archivo
Funcionalidad 9: Enviar ajustes posteriores
a) Diagrama: Esquema gráfico de la ejecución de servicios que mantienen
interdependencia para consumir el servicio Enviar Ajustes Posteriores no
domiciliados
26
Para poder consumir el servicio Enviar Ajustes Posteriores RCE, previamente debe
haberse ejecutado el servicio de Cargar Ajustes Posteriores RCE.
b) Servicios que se pueden invocar:
● 5.1 Servicio Api Seguridad (necesario)
● 5.33 Servicio Web Api consultar año y mes del RCE (necesario)
● 5.31 Servicio Web Api consultar estado ticket
● 5.32 Servicio Web Api descargar archivo
● 5.18 Servicio Web Api cargar ajustes posteriores (Necesario)
● 5.20 Servicio Web Api eliminar comprobante de ajustes posteriores
(opcional)
● 5.45 Servicio Web Api descargar ajustes posteriores (opcional)
● 5.19 Servicio Web Api enviar ajustes posteriores (Necesario)
Funcionalidad 10: Eliminar comprobantes en ajustes posteriores
a) Diagrama: Esquema gráfico de la ejecución de servicios que mantienen
interdependencia para consumir el servicio Eliminar comprobantes Ajustes
Posteriores RCE
27
Para poder consumir el servicio Eliminar comprobantes en Ajustes Posteriores
RCE, previamente debe haberse ejecutado el servicio de Cargar Ajustes
Posteriores RCE.
b) Servicios que se pueden invocar:
● 5.1 Servicio Api Seguridad (necesario)
● 5.33 Servicio Web Api consultar año y mes del RCE (necesario)
● 5.18 Servicio Web Api cargar ajustes posteriores (necesario)
● 5.20 Servicio Web Api eliminar comprobante de ajustes posteriores
(necesario)
Funcionalidad 11: Cargar ajustes posteriores no domiciliados
a) Diagrama: Esquema gráfico de la ejecución de servicios que mantienen
interdependencia para consumir el servicio Cargar Ajustes Posteriores no
domiciliados
28
Para poder consumir el servicio Cargar Ajustes Posteriores no domiciliados,
debe primero haber generado el periodo que desea ajustar y el registro de
operaciones con no domiciliados debe tener información.
b) Servicios que se pueden invocar:
● 5.1 Servicio Api Seguridad (necesario)
● 5.33 Servicio Web Api consultar año y mes del RCE (necesario)
● 5.21 Servicio Web Api cargar ajustes posteriores no domiciliados (necesario)
● 5.31 Servicio Web Api consultar estado ticket
● 5.32 Servicio Web Api descargar archivo
● 5.46 Servicio Web Api descargar ajustes posteriores no domiciliados
Funcionalidad 12: Enviar ajustes posteriores no domiciliados
a) Diagrama: Esquema gráfico de la ejecución de servicios que mantienen
interdependencia para consumir el servicio Enviar Ajustes Posteriores no
domiciliados
Para poder consumir el servicio Enviar Ajustes Posteriores no domiciliados,
previamente debe haberse ejecutado el servicio de Cargar Ajustes Posteriores no
domiciliados.
b) Servicios que se pueden invocar:
● 5.1 Servicio Api Seguridad (necesario)
● 5.33 Servicio Web Api consultar año y mes del RCE (necesario)
● 5.31 Servicio Web Api consultar estado ticket
● 5.32 Servicio Web Api descargar archivo
● 5.21 Servicio Web Api cargar ajustes posteriores no domiciliados (necesario)
● 5.22 Servicio Web Api enviar ajustes posteriores no domiciliados (necesario)
29
Funcionalidad 13: Eliminar comprobantes en ajustes posteriores no
domiciliados
a) Diagrama: Esquema gráfico de la ejecución de servicios que mantienen
interdependencia para consumir el servicio Eliminar comprobantes Ajustes
Posteriores no domiciliados
Para poder consumir el servicio Eliminar comprobantes en Ajustes Posteriores
de no domiciliados, previamente debe haberse ejecutado el servicio de Cargar
Ajustes Posteriores no domiciliados.
b) Servicios que se pueden invocar:
● 5.1 Servicio Api Seguridad (necesario)
● 5.33 Servicio Web Api consultar año y mes del RCE (necesario)
● 5.21 Servicio Web Api cargar ajustes posteriores no domiciliados (necesario)
● 5.23 Servicio Web Api eliminar comprobante de ajustes posteriores no
domiciliados (necesario)
Funcionalidad 14: Cargar ajustes posteriores de periodos anteriores
a) Diagrama: Esquema gráfico de la ejecución de servicios que mantienen
interdependencia para consumir el servicio Cargar Ajustes Posteriores de
periodos anteriores
30
Para poder consumir el servicio Cargar Ajustes Posteriores de periodos
anteriores, debe hacerlo referenciando al último periodo generado en el SIRE.
b) Servicios que se pueden invocar:
● 5.1 Servicio Api Seguridad (necesario)
● 5.33 Servicio Web Api consultar año y mes del RCE (necesario)
● 5.24 Servicio Web Api cargar ajustes posteriores de periodos anteriores
(necesario)
● 5.31 Servicio Web Api consultar estado ticket
● 5.32 Servicio Web Api descargar archivo
● 5.47 Servicio Web Api descargar ajustes posteriores de periodos anteriores
Funcionalidad 15: Enviar ajustes posteriores de periodos anteriores
a) Diagrama: Esquema gráfico de la ejecución de servicios que mantienen
interdependencia para consumir el servicio Enviar Ajustes Posteriores de
periodos anteriores
31
Para poder consumir el servicio Enviar Ajustes Posteriores de periodos
anteriores, previamente debe haberse ejecutado el servicio de Cargar Ajustes
Posteriores de periodos anteriores.
b) Servicios que se pueden invocar:
● 5.1 Servicio Api Seguridad (necesario)
● 5.33 Servicio Web Api consultar año y mes del RCE (necesario)
● 5.31 Servicio Web Api consultar estado ticket
● 5.32 Servicio Web Api descargar archivo
● 5.24 Servicio Web Api cargar ajustes posteriores de periodos anteriores
(necesario)
● 5.25 Servicio Web Api enviar ajustes posteriores de periodos anteriores
(necesario)
● 5.47 Servicio Web Api descargar ajustes posteriores de periodos anteriores
Funcionalidad 16: Eliminar comprobantes en ajustes posteriores de
periodos anteriores
a) Diagrama: Esquema gráfico de la ejecución de servicios que mantienen
interdependencia para consumir el servicio Eliminar comprobantes Ajustes
Posteriores de periodos anteriores
32
Para poder consumir el servicio Eliminar comprobantes en Ajustes Posteriores
de periodos anteriores, previamente debe haberse ejecutado el servicio de
Cargar Ajustes Posteriores de periodos anteriores.
b) Servicios que se pueden invocar:
● 5.1 Servicio Api Seguridad (necesario)
● 5.33 Servicio Web Api consultar año y mes del RCE (necesario)
● 5.24 Servicio Web Api cargar ajustes posteriores de periodos anteriores
(necesario)
● 5.26 Servicio Web Api eliminar comprobante de ajustes posteriores de
periodos anteriores (necesario)
Funcionalidad 17: Cargar ajustes posteriores de periodos anteriores no
domiciliados
a) Diagrama: Esquema gráfico de la ejecución de servicios que mantienen
interdependencia para consumir el servicio Cargar Ajustes Posteriores de
periodos anteriores no domiciliados
33
Para poder consumir el servicio Cargar Ajustes Posteriores de periodos
anteriores no domiciliados, debe hacerlo referenciando al último periodo
generado en el SIRE.
b) Servicios que se pueden invocar:
● 5.1 Servicio Api Seguridad (necesario)
● 5.33 Servicio Web Api consultar año y mes del RCE (necesario)
● 5.27 Servicio Web Api cargar ajustes posteriores de periodos anteriores no
domiciliados (necesario)
● 5.31 Servicio Web Api consultar estado ticket
● 5.32 Servicio Web Api descargar archivo
● 5.48 Servicio Web Api descargar ajustes posteriores de periodos anteriores
no domiciliados
Funcionalidad 18: Enviar ajustes posteriores de periodos anteriores no
domiciliados
a) Diagrama: Esquema gráfico de la ejecución de servicios que mantienen
interdependencia para consumir el servicio Enviar Ajustes Posteriores de
periodos anteriores no domiciliados
34
Para poder consumir el servicio Enviar Ajustes Posteriores de periodos anteriores
no domiciliados, previamente debe haberse ejecutado el servicio de Cargar
Ajustes Posteriores de periodos anteriores no domiciliados.
b) Servicios que se pueden invocar:
● 5.1 Servicio Api Seguridad (necesario)
● 5.33 Servicio Web Api consultar año y mes del RCE (necesario)
● 5.31 Servicio Web Api consultar estado ticket
● 5.32 Servicio Web Api descargar archivo
● 5.27 Servicio Web Api cargar ajustes posteriores de periodos anteriores no
domiciliados (necesario)
● 5.28 Servicio Web Api enviar ajustes posteriores de periodos anteriores no
domiciliados (necesario)
● 5.48 Servicio Web Api descargar ajustes posteriores de periodos anteriores
no domiciliados
Funcionalidad 19: Eliminar comprobantes en ajustes posteriores de
periodos anteriores no domiciliados
a) Diagrama: Esquema gráfico de la ejecución de servicios que mantienen
interdependencia para consumir el servicio Eliminar comprobantes en Ajustes
Posteriores de periodos anteriores no domiciliados
35
Para poder consumir el servicio Eliminar comprobantes en Ajustes Posteriores
de periodos anteriores no domiciliados, previamente debe haberse ejecutado el
servicio de Cargar Ajustes Posteriores de periodos anteriores no domiciliados.
b) Servicios que se pueden invocar:
● 5.1 Servicio Api Seguridad (necesario)
● 5.33 Servicio Web Api consultar año y mes del RCE (necesario)
● 5.27 Servicio Web Api cargar ajustes posteriores de periodos anteriores no
domiciliados (necesario)
● 5.29 Servicio Web Api eliminar comprobante de ajustes posteriores de
periodos anteriores no domiciliados (necesario)
Funcionalidad 20: Consultar estado de envío de ticket
a) Diagrama: Esquema gráfico de la ejecución de servicios que mantienen
interdependencia para consumir el servicio consultar estado de envío de ticket
Para poder consumir el servicio consulta de estado de envío de ticket,
previamente debe haberse ejecutado al menos un proceso que genere ticket,
por ejemplo, aceptar propuesta, reemplazar propuesta, generar RCE, descargar
propuesta, entre otros.
b) Servicios que se pueden invocar:
● 5.1 Servicio Api Seguridad (necesario)
36
● 5.2 Servicio Web Api aceptar propuesta
● 5.3 Servicio Web Api importar reemplazo de la propuesta
● 5.5 Servicio Web Api cargar registro de compra no domiciliados
● 5.7 Servicio Web Api importar nuevos comprobantes preliminar
● 5.18 Servicio Web Api cargar ajustes posteriores
● 5.19 Servicio Web Api enviar ajustes posteriores
● 5.20 Servicio Web Api eliminar comprobante de ajustes posteriores
● 5.21 Servicio Web Api cargar ajustes posteriores no domiciliados
● 5.22 Servicio Web Api enviar ajustes posteriores no domiciliados
● 5.24 Servicio Web Api cargar ajustes posteriores de periodos anteriores
● 5.25 Servicio Web Api enviar ajustes posteriores de periodos anteriores
● 5.27 Servicio Web Api cargar ajustes posteriores de periodos anteriores no
domiciliados
● 5.28 Servicio Web Api enviar ajustes posteriores de periodos anteriores no
domiciliados
● 5.29 Servicio Web Api eliminar comprobante de ajustes posteriores de
periodos anteriores no domiciliados
● 5.34 Servicio Web Api descargar propuesta
● 5.41 Servicio Web Api descargar reporte de casillas
● 5.53 Servicio Web Api descargar reporte CAR por periodo y fase
● 5.45 Servicio Web Api descargar ajustes posteriores
● 5.46 Servicio Web Api descargar ajustes posteriores no domiciliados
● 5.47 Servicio Web Api descargar ajustes posteriores de periodos anteriores
● 5.48 Servicio Web Api descargar ajustes posteriores de periodos anteriores no
domiciliados
● 5.39 Servicio Web Api exportar preliminar de registro de compras no
domiciliados
● 5.31 Servicio Web Api consultar estado ticket (opcional)
● 5.50 Servicio Web Api descargar reporte consolidado registro por periodo
● 5.51 Servicio Web Api descargar RCE por periodo.
Funcionalidad 21: Descargar archivo.
a) Diagrama: Esquema gráfico de la ejecución de servicios que mantienen
interdependencia para consumir el servicio descargar archivo
37
Para poder consumir el servicio “Descargar archivo”, previamente debe haberse
ejecutado algún proceso que genere un archivo o más, por ejemplo: “Generar
RCE”, “Descargar propuesta”, entre otros. Es recomendable verificar el estado
del ticket haciendo uso del servicio “Consultar estado de envío de ticket”. El
estado debe encontrarse “Terminado”.
b) Servicios que se pueden invocar:
● 5.1 Servicio Api Seguridad (necesario)
● 5.2 Servicio Web Api aceptar propuesta
● 5.3 Servicio Web Api importar reemplazo de la propuesta
● 5.5 Servicio Web Api cargar registro de compra no domiciliados
● 5.7 Servicio Web Api importar nuevos comprobantes preliminar
● 5.18 Servicio Web Api cargar ajustes posteriores
● 5.19 Servicio Web Api enviar ajustes posteriores
● 5.20 Servicio Web Api eliminar comprobante de ajustes posteriores
● 5.21 Servicio Web Api cargar ajustes posteriores no domiciliados
● 5.22 Servicio Web Api enviar ajustes posteriores no domiciliados
● 5.24 Servicio Web Api cargar ajustes posteriores de periodos anteriores
● 5.25 Servicio Web Api enviar ajustes posteriores de periodos anteriores
● 5.27 Servicio Web Api cargar ajustes posteriores de periodos anteriores no
domiciliados
● 5.28 Servicio Web Api enviar ajustes posteriores de periodos anteriores no
domiciliados
● 5.29 Servicio Web Api eliminar comprobante de ajustes posteriores de
periodos anteriores no domiciliados
● 5.34 Servicio Web Api descargar propuesta
● 5.41 Servicio Web Api descargar reporte de casillas
● 5.53 Servicio Web Api descargar reporte CAR por periodo y fase
● 5.45 Servicio Web Api descargar ajustes posteriores
● 5.46 Servicio Web Api descargar ajustes posteriores no domiciliados
● 5.47 Servicio Web Api descargar ajustes posteriores de periodos anteriores
● 5.48 Servicio Web Api descargar ajustes posteriores de periodos anteriores no
domiciliados
● 5.39 Servicio Web Api exportar preliminar de registro de compras no
domiciliados
● 5.31 Servicio Web Api consultar estado ticket (opcional)
● 5.50 Servicio Web Api descargar reporte consolidado registro por periodo
● 5.51 Servicio Web Api descargar RCE por periodo.
Funcionalidad 22: Eliminar preliminar registrado
a) Diagrama: Esquema gráfico de la ejecución de servicios que mantienen
interdependencia para consumir el servicio eliminar preliminar registrado.
38
Servicio WEB API que permitirá al generador eliminar los preliminares
registrados del RCE, siempre y cuando haya registrado el preliminar. Si el estado
del generador es baja definitiva, solo se debe permitir eliminar la información
correspondiente a los periodos donde estuvo activo o con suspensión temporal.
b) Servicios que se pueden invocar:
● 5.1 Servicio Api Seguridad (necesario)
● 5.33 Servicio Web Api consultar año y mes del RCE (opcional)
● 5.4 Servicio Web Api registrar preliminar (necesario)
● 5.16 Servicio Web Api eliminar comprobante del preliminar (necesario)
4. Servicios accesorios que pueden ser consumidos en el SIRE Compras
a) Diagrama: Esquema gráfico de la secuencia de todos los servicios que SUNAT
pone a disposición de los contribuyentes.
39
40
b) Servicios que se pueden invocar (servicios opcionales):
● 5.58 Servicio Web Api descargar reporte de cumplimiento
● 5.49 Servicio Web Api descargar constancia de recepción.
● 5.35 Servicio Web Api descargar resumen
● 5.36 Servicio Web Api Descargar resumen de inconsistencias RCE
● 5.41 Servicio Web Api descargar reporte de casillas.
● 5.42 Servicio Web Api descargar inconsistencias en registros del preliminar
registrado.
● 5.53 Servicio Web Api descargar reporte CAR por periodo y fase
● 5.33 Servicio Web Api consultar año y mes del RCE
● 5.34 Servicio Web Api descargar propuesta
● 5.14 Servicio Web Api consultar FV0621
● 5.45 Servicio Web Api descargar ajustes posteriores
● 5.46 Servicio Web Api descargar ajustes posteriores no domiciliados
● 5.47 Servicio Web Api descargar ajustes posteriores de periodos anteriores
● 5.48 Servicio Web Api descargar ajustes posteriores de periodos anteriores no
domiciliados
● 5.31 Servicio Web Api consultar estado ticket
● 5.39 Servicio Web Api exportar preliminar de registro de compras no
domiciliados
● 5.47 Servicio Web Api descargar ajustes posteriores de periodos anteriores
● 5.50 Servicio Web Api descargar reporte consolidado registro por periodo
● 5.51 Servicio Web Api descargar RCE por periodo.
● 5.52 Servicio Web Api Descargar Reporte de Inconsistencias por Periodo.
● 5.54 Servicio Web Api Descargar Reporte estadísticos de compras por
proveedor por Periodo.
● 5.55 Servicio Web Api Descargar Reporte estadísticos de notas de créditos y
notas de débito por proveedor por Periodo.
● 5.56 Servicio Web Api Descargar Reporte estadísticos de compras por día por
Periodo.
● 5.57 Servicio Web Api Descargar Reporte estadísticos de compras por CIIU de
proveedor por Periodo.
5. Documentación Servicios Web API
Importante: los servicios del API SIRE no deben ser consumidos desde un cliente Web,
en caso de utilizar un cliente Web se producirá error de CORS. Así mismo los servicios
API REST que impliquen el desarrollo de un cliente TUS (Open Protocol for Resumable
File Uploads) deben ser desarrollados en el lenguaje JAVA (Ver Anexo 7.4)
5.1 Servicio Api Seguridad
Nombre Web
Services
Api Seguridad
Descripción Permite generar el token para consumo de API’s expuestas por SUNAT.
41
Url https://api-seguridad.sunat.gob.pe/v1/clientessol/9cae24a9-10d7-48b0-bee0-
e94bd56947e3/oauth2/token/
Parámetros[body] Descripción:
grant_type: password
 (credenciales del cliente - usar por defecto: password)
scope: https://api-sire.sunat.gob.pe
 (uri que permitirá el acceso con el token - por defecto:
 https://api-sire.sunat.gob.pe )
client_id: ababababa-9abc-453s-s5s4s4-s457555
 (se obtiene desde la opción Credenciales de API SUNAT)
client_secret: CSCSSKSJDSKSNSKSKSSKSJDDN
 (se obtiene desde la opción Credenciales de API SUNAT)
username: {RUC} {USUARIO} (RUC y Usuario del generador)
password: {CLAVESOL} (Clave sol del generador)
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Content-type: application/x-www-form-urlencoded (opcional)
Método: POST
Evidencias URL
https://api-seguridad.sunat.gob.pe/v1/clientessol/9cae24a9-10d7-48b0-bee0-
e94bd56947e3/oauth2/token/
Headers
(No aplica)
Body
Result OK
Result Fail
42
5.2 Servicio Web Api aceptar propuesta
Nombre Web
Services
Aceptar Propuesta
Descripción Actualiza el estado del registro libro y Control de procesos para indicar que se está
registrando un preliminar a través de la propuesta aceptada
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/propuesta/web/registroslibros/{perTr
ibutario}/aceptarpropuesta
Parámetros[URL] Param-formato-tipo Descripción
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
Parámetros[body] No aplica
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Parámetros valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: POST
Parámetros[salida] Parámetros
de Salida Descripcion Formato Tipo
dato
numTicket
Número de ticket de envío [AAAA99999999]
AAAA: Año
99: Tipo de correlativo
99999999: Número correlativo de envío
alfanumerico String
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/propuesta/web/registroslibros/20230
1/aceptarpropuesta
Headers
Body
(No aplica)
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
• 1005 – El campo “perTributario” no enviado o es vacío
• 1006 – Formato de perTributario no cumple con el formato “yyyymm”
• 1007 – El perTributario de búsqueda no debe ser mayor a la fecha actual
43
5.3 Servicio Web Api importar reemplazo de la propuesta
Nombre Web
Services
Servicio Web Api importar reemplazo de la propuesta
Descripción Servicio web api que permite al generador, reemplazar la propuesta SUNAT con lo
considerado por el contribuyente mediante el uso de un archivo de formato .txt
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/receptorpropuesta/web/propues
ta/upload
Parámetros[body] No aplica
Parámetros[header] Valores:
Content-type: application/x-www-form-urlencoded
Metadata Cliente TUS
Param-formato-tipo Descripción
filename-alfanumérico-string Nombre de archivo (Obligatorio)
filetype-alfanumérico-string Tipo de archivo (Obligatorio)
numRuc-alfanumérico-string Número de RUC del contribuyente (Obligatorio)
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
codOrigenEnvio-alfanuméricostring
Código de origen de envío: 2 Servicio web
(Obligatorio)
codProceso-alfanumérico-String Código del indicador de carga masiva: 61 Reemplazo
de la Propuesta (Ver Anexo I: Indicador de carga
masiva) (Obligatorio)
codTipoCorrelativo-alfanuméricostring
Tipo de correlativo: 01: Tipo envíos masivos (Ver
Anexo II: Tipo de correlativo) (Obligatorio)
nomArchivoImportacionalfanumérico-String
Nombre del archivo utilizado para la importación o
nombre de archivo generado (Obligatorio)
codLibro-alfanumérico-String Código de libro: 080000 RCE (Obligatorio)
Parámetros[salida] Parámetros de
Salida Descripción Formato Tipo
dato
numTicket
Número de ticket de envío [AAAA99999999]
AAAA: Año
99: Tipo de correlativo
99999999: Número correlativo de envío
alfanumerico String
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/receptorpropuesta/web/propues
ta/upload
Headers (metadata)
filename
TEUyMDEwMDE3NjQ1MDIwMjMwMjAwMTQwNDAwMDMxMTEwMi56aXA=,filetype
YXBwbGljYXRpb24vemlw,numRuc MjAxMDAxNzY0NTA=,perTributario
MjAyMzAy,codOrigenEnvio MQ==,codProceso ODc=,codTipoCorrelativo
MQ==,nomArchivoImportacion
TEUyMDEwMDE3NjQ1MDIwMjMwMjAwMTQwNDAwMDMxMTEwMi56aXA=,codLibro
MTQwMDAw
Body
(No aplica)
Result OK
Result Fail
{ “cod”:”500”, “msg”:”Internal Server Error – Se presento una condicion inesperada que
impidio completar el Request”, “exc”:”java.lang.NullPointerException at …” }
Mensaje Error { “cod”:”422”, “msg”:”Unprocessable Entity – Se presentaron errores de validacion que
impidieron completar el Request”, “errors”:[ { “cod”:”1001”, “msg”:”El campo “numRuc” no
enviado o es vacío” }] }
Lista de errores 422:
44
● 1001 - El campo “numRuc” no enviado o es vacío
● 1002 - Solo se permite dato numérico de 11 dígitos para el número de RUC.
● 1003 - El RUC ingresado no existe o no es válido
● 1005 - El campo “perTributario” no enviado o es vacío
● 1006 - Formato de perTributario no cumple con el formato “yyyymm”
● 1007 - El perTributario de búsqueda no debe ser mayor a la fecha actual
● 1014 - Solo se permite dato numérico de 6 dígitos para el perTributario.
● 1064 - El periodo no debe ser mayor al periodo de la fecha actual
● 1093 - Formato de período no cumple con el formato “yyyymm”
● 1028 - El campo “codOrigenEnvio” no enviado o es vacío
● 1029 - Código tipo de Origen de Envio no permitido o no valido
● 1030 - Solo se permite dato numérico de 1 dígito para el codOrigenEnvio
● 1025 - El campo “codProceso” no enviado o es vacío
● 1026 - Código Proceso no permitido o no valido
● 1027 - Solo se permite dato numérico para el codProceso
● 1138 - El campo "codProceso" es nulo o vacío
● 1139 - Código de Proceso no permitido o no valido
● 1048 - Solo se permite dato numérico de 1 dígito para el codTipoOrigen
● 1022 - nombre del archivo no enviado o es vacio.
● 1024 - El archivo <nombre del archivo txt> fue previamente enviado.
● 1044 - Error en la <<Posición - Descripción>> del nombre del archivo plano, favor
de corregir
● 1348 - La extensión del archivo es diferente a “.zip”, por favor corregir
● 1346 - El tamaño del archivo comprimido en formato “.zip” debe ser menor o igual
a 6GB.
● 1350 - El tamaño del archivo mayor a 0 Kb.
● 1351 - Se ha producido un error al realizar el envío del archivo, por favor volver a
intentar el envío
● 1048 - Solo se permite dato numérico de 2 dígitos para el codTipoCorrelativo
● 1049 - El campo “codTipoCorrelativo” no enviado o es vacio
● 1050 - Código tipo de Correlativo no permitido o no valido
● 1140 - El campo “codLibro” no enviado o es vacío
Tecnología Uso de la librería TUS.io para cliente.
5.4 Servicio Web Api registrar preliminar
Nombre Web
Services
Servicio Web Api Registrar Preliminar
Descripción Permite registrar los preliminares del registro de compras u ajustes posteriores y pueda
continuar con la Generación en el portal WEB de SUNAT.
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/preliminar/web/registroslibros/{perT
ributario}/registrapreliminares
Parámetros[URL] Param-formato-tipo Descripción
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
Parámetros[body] No aplica
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Content-type: application/x-www-form-urlencoded
Parámetros valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: POST
Parámetros[salida] Parámetros de
Salida Descripción Formato Tipo
dato
numTicket
Número de ticket de envío [AAAA99999999]
AAAA: Año
99: Tipo de correlativo
99999999: Número correlativo de envío
alfanumerico String
45
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/preliminar/web/registroslibros/2022
03/registrapreliminares
Headers
Body
(No aplica)
Result OK
Result Fail
{ “cod”:”500”, “msg”:”Internal Server Error – Se presento una condicion inesperada que
impidio completar el Request”, “exc”:”java.lang.NullPointerException at …” }
Mensaje Error { “cod”:”422”, “msg”:”Unprocessable Entity – Se presentaron errores de validacion que
impidieron completar el Request”, “errors”:[ { “cod”:”1001”, “msg”:”El campo “numRuc” no
enviado o es vacío” }] }
Lista de errores 422:
• 1005 - El campo “perTributario” no enviado o es vacío
• 1006 – Formato permitido: yyyymm
• 1007 – El PeriodoTributario no debe ser posterior al yyyymm actual
• 1008 – “El registro electrónico xxxxx ya se encuentra en el módulo de
preliminar.”
• 1009 - "El registro electrónico xxxxx ya ha sido generado."
5.5 Servicio Web Api cargar registro de compra no domiciliados
Nombre Web
Services
Servicio Web Api cargar no domiciliado
Descripción Permite importar el archivo de las operaciones con no domiciliados.
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/receptorpreliminar/web/prelimin
ar/upload
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Content-type: application/x-www-form-urlencoded
Metadata Cliente TUS
Param-formato-tipo Descripción
filename-alfanumérico-string Nombre de archivo (Obligatorio)
filetype-alfanumérico-string Tipo de archivo (Obligatorio)
numRuc-alfanumérico-string Número de RUC del contribuyente (Obligatorio)
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
codOrigenEnvio-alfanuméricostring
Código de origen de envío: 2 Servicio web
(Obligatorio)
codProceso-alfanumérico-String Código del indicador de carga masiva: 56. Cargar
no domiciliados (Ver Anexo I: Indicador de carga
masiva) (Obligatorio)
46
codTipoCorrelativo-alfanuméricostring
Tipo de correlativo: 01: Tipo envíos masivos (Ver
Anexo II: Tipo de correlativo) (Obligatorio)
nomArchivoImportacionalfanumérico-String
Nombre del archivo utilizado para la importación o
nombre de archivo generado
(Obligatorio)
codLibro-alfanumérico-String Código de libro: 080000 RCE (Obligatorio)
Parámetros[salida] Parámetros
de Salida Descripción Formato Tipo dato
numTicket
Número de ticket de envío [AAAA99999999]
AAAA: Año
99: Tipo de correlativo
99999999: Número correlativo de envío
Alfanumerico String
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/receptorpreliminar/web/prelimin
ar/upload
Headers
(No aplica)
Body
(No aplica)
Result OK
Result Fail
{ “cod”:”500”, “msg”:”Internal Server Error – Se presento una condicion inesperada que
impidio completar el Request”, “exc”:”java.lang.NullPointerException at …” }
Mensaje Error { “cod”:”422”, “msg”:”Unprocessable Entity – Se presentaron errores de validacion que
impidieron completar el Request”, “errors”:[ { “cod”:”1001”, “msg”:”El campo “numRuc” no
enviado o es vacío” }] }
Lista de errores:
• 1001 - El campo “numRuc” no enviado o es vacío
• 1002 - Solo se permite dato numérico de 11 dígitos para el número de RUC.
• 1003 - El RUC ingresado no existe o no es válido
• 1005 - El campo “perTributario” no enviado o es vacío
• 1006 - Formato de perTributario no cumple con el formato “yyyymm”
• 1007 - El perTributario de búsqueda no debe ser mayor a la fecha actual
• 1014 - Solo se permite dato numérico de 6 dígitos para el perTributario.
• 1064 - El periodo no debe ser mayor al periodo de la fecha actual
• 1093 - Formato de período no cumple con el formato “yyyymm”
• 1028 - El campo “codOrigenEnvio” no enviado o es vacío
• 1029 - Código tipo de Origen de Envio no permitido o no valido
• 1030 - Solo se permite dato numérico de 1 dígito para el codOrigenEnvio
• 1025 - El campo “codProceso” no enviado o es vacío
• 1026 - Código Proceso no permitido o no valido
• 1027 - Solo se permite dato numérico para el codProceso
• 1138 - El campo "codProceso" es nulo o vacío
• 1139 - Código de Proceso no permitido o no valido
• 1048 - Solo se permite dato numérico de 1 dígito para el codTipoOrigen
• 1022 - nombre del archivo no enviado o es vacio.
• 1024 - El archivo <nombre del archivo txt> fue previamente enviado.
• 1044 - Error en la <<Posición - Descripción>> del nombre del archivo plano,
favor de corregir
• 1348 - La extensión del archivo es diferente a “.zip”, por favor corregir
• 1346 - El tamaño del archivo comprimido en formato “.zip” debe ser menor o
igual a 6GB.
• 1350 - El tamaño del archivo mayor a 0 Kb.
47
• 1351 - Se ha producido un error al realizar el envío del archivo, por favor
volver a intentar el envío
• 1048 - Solo se permite dato numérico de 2 dígitos para el codTipoCorrelativo
• 1049 - El campo “codTipoCorrelativo” no enviado o es vacio
• 1050 - Código tipo de Correlativo no permitido o no valido
• 1140 - El campo “codLibro” no enviado o es vacío
Tecnología Uso de la librería TUS.io para cliente.
5.6 Servicio Web Api importar datos complementarios de los CP de la
propuesta
Nombre Web
Services
Servicio Web Api importar complemento de la propuesta
Descripción Servicio web api que permite al generador complementar o completar datos de
comprobantes propuestos por la administración.
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/receptorpropuesta/web/propuest
a/upload
Parámetros[body] No aplica
Parámetros[header] Valores:
Content-type: application/x-www-form-urlencoded
Metadata Cliente TUS
Param-formato-tipo Descripción
filename-alfanumérico-string Nombre de archivo (Obligatorio)
filetype-alfanumérico-string Tipo de archivo (Obligatorio)
numRuc-alfanumérico-string Número de RUC del contribuyente
(Obligatorio)
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
codOrigenEnvio-alfanumérico-string Código de origen de envío: 2 Servicio web
(Obligatorio)
codProceso-alfanumérico-String Código del indicador de carga masiva: 54.
Complementar la Propuesta (Ver Anexo I:
Indicador de carga masiva) (Obligatorio)
codTipoCorrelativo-alfanumérico-string Tipo de correlativo: 01: Tipo envíos masivos
(Ver Anexo II: Tipo de correlativo) (Obligatorio)
nomArchivoImportacion-alfanuméricoString
Nombre del archivo utilizado para la
importación o nombre de archivo generado
(Obligatorio)
codLibro-alfanumérico-String Código de libro: 080000 RCE (Obligatorio)
Parámetros[salida] Parámetros
de Salida Descripción Formato Tipo dato
numTicket
Número de ticket de envío [AAAA99999999]
AAAA: Año
99: Tipo de correlativo
99999999: Número correlativo de envío
alfanumerico String
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/receptorpropuesta/web/propuest
a/upload
Headers (metadata)
filename
TEUyMDEwMDE3NjQ1MDIwMjMwMjAwMTQwNDAwMDMxMTEwMi56aXA=,filetype
YXBwbGljYXRpb24vemlw,numRuc MjAxMDAxNzY0NTA=,perTributario
MjAyMzAy,codOrigenEnvio MQ==,codProceso ODc=,codTipoCorrelativo
MQ==,nomArchivoImportacion
TEUyMDEwMDE3NjQ1MDIwMjMwMjAwMTQwNDAwMDMxMTEwMi56aXA=,codLibro
MTQwMDAw
Body
(No aplica)
48
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presentó una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
● 1001 - El campo “numRuc” no enviado o es vacío
● 1002 - Solo se permite dato numérico de 11 dígitos para el número de RUC.
● 1003 - El RUC ingresado no existe o no es válido
● 1005 - El campo “perTributario” no enviado o es vacío
● 1006 - Formato de perTributario no cumple con el formato “yyyymm”
● 1007 - El perTributario de búsqueda no debe ser mayor a la fecha actual
● 1014 - Solo se permite dato numérico de 6 dígitos para el perTributario.
● 1064 - El periodo no debe ser mayor al periodo de la fecha actual
● 1093 - Formato de período no cumple con el formato “yyyymm”
● 1028 - El campo “codOrigenEnvio” no enviado o es vacío
● 1029 - Código tipo de Origen de Envio no permitido o no valido
● 1030 - Solo se permite dato numérico de 1 dígito para el codOrigenEnvio
● 1025 - El campo “codProceso” no enviado o es vacío
● 1026 - Código Proceso no permitido o no valido
● 1027 - Solo se permite dato numérico para el codProceso
● 1138 - El campo "codProceso" es nulo o vacío
● 1139 - Código de Proceso no permitido o no valido
● 1048 - Solo se permite dato numérico de 1 dígito para el codTipoOrigen
● 1022 - nombre del archivo no enviado o es vacio.
● 1024 - El archivo <nombre del archivo txt> fue previamente enviado.
● 1044 - Error en la <<Posición - Descripción>> del nombre del archivo plano, favor de
corregir
● 1348 - La extensión del archivo es diferente a “.zip”, por favor corregir
● 1346 - El tamaño del archivo comprimido en formato “.zip” debe ser menor o igual
a 6GB.
● 1350 - El tamaño del archivo mayor a 0 Kb.
● 1351 - Se ha producido un error al realizar el envío del archivo, por favor volver a
intentar el envío
● 1048 - Solo se permite dato numérico de 2 dígitos para el codTipoCorrelativo
● 1049 - El campo “codTipoCorrelativo” no enviado o es vacio
● 1050 - Código tipo de Correlativo no permitido o no valido
● 1140 - El campo “codLibro” no enviado o es vacío
Tecnología Uso de la librería TUS.io para cliente.
5.7 Servicio Web Api importar nuevos comprobantes preliminar
Nombre Web
Services
Servicio Web Api importar nuevos comprobantes en el preliminar
Descripción Permite importar nuevos comprobantes en el preliminar de RCE.
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/receptorpreliminar/web/prelimin
ar/upload
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Content-type: application/x-www-form-urlencoded
Metadata Cliente TUS
Param-formato-tipo Descripción
49
filename-alfanumérico-string Nombre de archivo (Obligatorio)
filetype-alfanumérico-string Tipo de archivo (Obligatorio)
numRuc-alfanumérico-string Número de RUC del contribuyente (Obligatorio)
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
codOrigenEnvio-alfanuméricostring
Código de origen de envío: 2 Servicio web
(Obligatorio)
codProceso-alfanumérico-String Código del indicador de carga masiva: 4. Importa
CP - Preliminar (Ver Anexo I: Indicador de carga
masiva) (Obligatorio)
codTipoCorrelativo-alfanuméricostring
Tipo de correlativo: 01: Tipo envíos masivos (Ver
Anexo II: Tipo de correlativo) (Obligatorio)
nomArchivoImportacionalfanumérico-String
Nombre del archivo utilizado para la importación o
nombre de archivo generado (Obligatorio)
codLibro-alfanumérico-String Código de libro: 080000 RCE (Obligatorio)
Parámetros[salida] Parámetros
de Salida Descripción Formato Tipo dato
numTicket
Número de ticket de envío [AAAA99999999]
AAAA: Año
99: Tipo de correlativo
99999999: Número correlativo de envío
alfanumerico String
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/receptorpreliminar/web/prelimin
ar/upload
Headers (metadata)
filename MjAxMDAxNzY0NTAtQ1BGLTIwMjMwMi0wMS56aXA=,filetype
YXBwbGljYXRpb24vemlw,numRuc MjAxMDAxNzY0NTA=,perTributario
MjAyMzAy,codOrigenEnvio MQ==,codProceso MQ==,codTipoCorrelativo
MQ==,nomArchivoImportacion
MjAxMDAxNzY0NTAtQ1BGLTIwMjMwMi0wMS56aXA=,codLibro MTQwMDAw
Body
(No aplica)
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores:
• 1001 - El campo “numRuc” no enviado o es vacío
• 1002 - Solo se permite dato numérico de 11 dígitos para el número de RUC.
• 1003 - El RUC ingresado no existe o no es válido
• 1005 - El campo “perTributario” no enviado o es vacío
• 1006 - Formato de perTributario no cumple con el formato “yyyymm”
• 1007 - El perTributario de búsqueda no debe ser mayor a la fecha actual
• 1014 - Solo se permite dato numérico de 6 dígitos para el perTributario.
• 1064 - El periodo no debe ser mayor al periodo de la fecha actual
• 1093 - Formato de período no cumple con el formato “yyyymm”
• 1028 - El campo “codOrigenEnvio” no enviado o es vacío
• 1029 - Código tipo de Origen de Envio no permitido o no valido
• 1030 - Solo se permite dato numérico de 1 dígito para el codOrigenEnvio
• 1025 - El campo “codProceso” no enviado o es vacío
• 1026 - Código Proceso no permitido o no valido
• 1027 - Solo se permite dato numérico para el codProceso
50
• 1138 - El campo "codProceso" es nulo o vacío
• 1139 - Código de Proceso no permitido o no valido
• 1048 - Solo se permite dato numérico de 1 dígito para el codTipoOrigen
• 1022 - nombre del archivo no enviado o es vacio.
• 1024 - El archivo <nombre del archivo txt> fue previamente enviado.
• 1044 - Error en la <<Posición - Descripción>> del nombre del archivo plano,
favor de corregir
• 1348 - La extensión del archivo es diferente a “.zip”, por favor corregir
• 1346 - El tamaño del archivo comprimido en formato “.zip” debe ser menor o
igual a 6GB.
 1350 - El tamaño del archivo mayor a 0 Kb.
 1351 - Se ha producido un error al realizar el envío del archivo, por favor volver a
intentar el envío
 1048 - Solo se permite dato numérico de 2 dígitos para el codTipoCorrelativo
 1049 - El campo “codTipoCorrelativo” no enviado o es vacio
 1050 - Código tipo de Correlativo no permitido o no valido
 1140 - El campo “codLibro” no enviado o es vacío
Tecnología Uso de la librería TUS.io para cliente.
5.8 Servicio Web Api incluir-excluir comprobantes de la propuesta
Nombre Web
Services
Servicio Web Api incluir-excluir comprobantes de la propuesta
Descripción Servicio web api que permite al generador incluir o excluir comprobantes que han sido
propuestos por la administración.
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/receptorpropuesta/web/propuest
a/upload
Parámetros[body] No aplica
Parámetros[header] Valores:
Content-type: application/x-www-form-urlencoded
Metadata Cliente TUS
Param-formato-tipo Descripción
filename-alfanumérico-string Nombre de archivo (Obligatorio)
filetype-alfanumérico-string Tipo de archivo (Obligatorio)
numRuc-alfanumérico-string Número de RUC del contribuyente
(Obligatorio)
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
codOrigenEnvio-alfanumérico-string Código de origen de envío: 2 Servicio web
(Obligatorio)
codProceso-alfanumérico-String Código del indicador de carga masiva: 55.
Carga Incluir Excluir (Ver Anexo I: Indicador de
carga masiva) (Obligatorio)
codTipoCorrelativo-alfanumérico-string Tipo de correlativo: 01: Tipo envíos masivos
(Ver Anexo II: Tipo de correlativo) (Obligatorio)
nomArchivoImportacion-alfanuméricoString
Nombre del archivo utilizado para la
importación o nombre de archivo generado
(Obligatorio)
codLibro-alfanumérico-String Código de libro: 080000 RCE (Obligatorio)
Parámetros[salida] Parámetros
de Salida Descripción Formato Tipo dato
numTicket
Número de ticket de envío [AAAA99999999]
AAAA: Año
99: Tipo de correlativo
99999999: Número correlativo de envío
alfanumerico String
Evidencias URL
51
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/receptorpropuesta/web/propuest
a/upload
Headers (metadata)
filename
TEUyMDEwMDE3NjQ1MDIwMjMwMjAwMTQwNDAwMDMxMTEwMi56aXA=,filetype
YXBwbGljYXRpb24vemlw,numRuc MjAxMDAxNzY0NTA=,perTributario
MjAyMzAy,codOrigenEnvio MQ==,codProceso ODc=,codTipoCorrelativo
MQ==,nomArchivoImportacion
TEUyMDEwMDE3NjQ1MDIwMjMwMjAwMTQwNDAwMDMxMTEwMi56aXA=,codLibro
MTQwMDAw
Body
(No aplica)
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
● 1001 - El campo “numRuc” no enviado o es vacío
● 1002 - Solo se permite dato numérico de 11 dígitos para el número de RUC.
● 1003 - El RUC ingresado no existe o no es válido
● 1005 - El campo “perTributario” no enviado o es vacío
● 1006 - Formato de perTributario no cumple con el formato “yyyymm”
● 1007 - El perTributario de búsqueda no debe ser mayor a la fecha actual
● 1014 - Solo se permite dato numérico de 6 dígitos para el perTributario.
● 1064 - El periodo no debe ser mayor al periodo de la fecha actual
● 1093 - Formato de período no cumple con el formato “yyyymm”
● 1028 - El campo “codOrigenEnvio” no enviado o es vacío
● 1029 - Código tipo de Origen de Envio no permitido o no valido
● 1030 - Solo se permite dato numérico de 1 dígito para el codOrigenEnvio
● 1025 - El campo “codProceso” no enviado o es vacío
● 1026 - Código Proceso no permitido o no valido
● 1027 - Solo se permite dato numérico para el codProceso
● 1138 - El campo "codProceso" es nulo o vacío
● 1139 - Código de Proceso no permitido o no valido
● 1048 - Solo se permite dato numérico de 1 dígito para el codTipoOrigen
● 1022 - nombre del archivo no enviado o es vacio.
● 1024 - El archivo <nombre del archivo txt> fue previamente enviado.
● 1044 - Error en la <<Posición - Descripción>> del nombre del archivo plano, favor de
corregir
● 1348 - La extensión del archivo es diferente a “.zip”, por favor corregir
● 1346 - El tamaño del archivo comprimido en formato “.zip” debe ser menor o igual
a 6GB.
● 1350 - El tamaño del archivo mayor a 0 Kb.
● 1351 - Se ha producido un error al realizar el envío del archivo, por favor volver a
intentar el envío
● 1048 - Solo se permite dato numérico de 2 dígitos para el codTipoCorrelativo
● 1049 - El campo “codTipoCorrelativo” no enviado o es vacio
● 1050 - Código tipo de Correlativo no permitido o no valido
● 1140 - El campo “codLibro” no enviado o es vacío
Tecnología Uso de la librería TUS.io para cliente.
5.9 Servicio Web Api importar nuevos comprobantes de pago
52
Nombre Web
Services
Servicio Web Api importar nuevos comprobantes en propuesta
Descripción Servicio web api que permite al generador, agregar nuevos comprobantes que no han sido
propuestos por la administración.
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/receptorpropuesta/web/propuest
a/upload
Parámetros[body] No aplica
Parámetros[header] Valores:
Content-type: application/x-www-form-urlencoded
Metadata Cliente TUS
Param-formato-tipo Descripción
filename-alfanumérico-string Nombre de archivo (Obligatorio)
filetype-alfanumérico-string Tipo de archivo (Obligatorio)
numRuc-alfanumérico-string Número de RUC del contribuyente
(Obligatorio)
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
codOrigenEnvio-alfanumérico-string Código de origen de envío: 2 Servicio web
(Obligatorio)
codProceso-alfanumérico-String Código del indicador de carga masiva: 1.
Importar CP - Propuesta (Ver Anexo I:
Indicador de carga masiva) (Obligatorio)
codTipoCorrelativo-alfanumérico-string Tipo de correlativo: 01: Tipo envíos masivos
(Ver Anexo II: Tipo de correlativo) (Obligatorio)
nomArchivoImportacion-alfanuméricoString
Nombre del archivo utilizado para la
importación o nombre de archivo generado
(Obligatorio)
codLibro-alfanumérico-String Código de libro: 080000 RCE (Obligatorio)
Parámetros[salida] Parámetros
de Salida Descripción Formato Tipo dato
numTicket
Número de ticket de envío [AAAA99999999]
AAAA: Año
99: Tipo de correlativo
99999999: Número correlativo de envío
alfanumerico String
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/receptorpropuesta/web/propuest
a/upload
Headers (metadata)
filename
TEUyMDEwMDE3NjQ1MDIwMjMwMjAwMTQwNDAwMDMxMTEwMi56aXA=,filetype
YXBwbGljYXRpb24vemlw,numRuc MjAxMDAxNzY0NTA=,perTributario
MjAyMzAy,codOrigenEnvio MQ==,codProceso ODc=,codTipoCorrelativo
MQ==,nomArchivoImportacion
TEUyMDEwMDE3NjQ1MDIwMjMwMjAwMTQwNDAwMDMxMTEwMi56aXA=,codLibro
MTQwMDAw
Body
(No aplica)
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
● 1001 - El campo “numRuc” no enviado o es vacío
53
● 1002 - Solo se permite dato numérico de 11 dígitos para el número de RUC.
● 1003 - El RUC ingresado no existe o no es válido
● 1005 - El campo “perTributario” no enviado o es vacío
● 1006 - Formato de perTributario no cumple con el formato “yyyymm”
● 1007 - El perTributario de búsqueda no debe ser mayor a la fecha actual
● 1014 - Solo se permite dato numérico de 6 dígitos para el perTributario.
● 1064 - El periodo no debe ser mayor al periodo de la fecha actual
● 1093 - Formato de período no cumple con el formato “yyyymm”
● 1028 - El campo “codOrigenEnvio” no enviado o es vacío
● 1029 - Código tipo de Origen de Envio no permitido o no valido
● 1030 - Solo se permite dato numérico de 1 dígito para el codOrigenEnvio
● 1025 - El campo “codProceso” no enviado o es vacío
● 1026 - Código Proceso no permitido o no valido
● 1027 - Solo se permite dato numérico para el codProceso
● 1138 - El campo "codProceso" es nulo o vacío
● 1139 - Código de Proceso no permitido o no valido
● 1048 - Solo se permite dato numérico de 1 dígito para el codTipoOrigen
● 1022 - nombre del archivo no enviado o es vacio.
● 1024 - El archivo <nombre del archivo txt> fue previamente enviado.
● 1044 - Error en la <<Posición - Descripción>> del nombre del archivo plano, favor de
corregir
● 1348 - La extensión del archivo es diferente a “.zip”, por favor corregir
● 1346 - El tamaño del archivo comprimido en formato “.zip” debe ser menor o igual
a 6GB.
● 1350 - El tamaño del archivo mayor a 0 Kb.
● 1351 - Se ha producido un error al realizar el envío del archivo, por favor volver a
intentar el envío
● 1048 - Solo se permite dato numérico de 2 dígitos para el codTipoCorrelativo
● 1049 - El campo “codTipoCorrelativo” no enviado o es vacio
● 1050 - Código tipo de Correlativo no permitido o no valido
● 1140 - El campo “codLibro” no enviado o es vacío
Tecnología Uso de la librería TUS.io para cliente.
5.10 Servicio Web Api importar tipo de cambio masivo
Nombre Web
Services
Servicio Web API importar tipo de cambio masivo
Descripción Permite actualizar masivamente todos los tipos de cambio de comprobantes que la
administración no encontró tipo de cambio propuesto, de la misma manera los montos
propuestos serán actualizados utilizando el o los tipos de cambio ingresados.
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/propuesta/web/{perTributario}/{codL
ibro}/resumenfechatipocambio
Parámetros[url] Param-formato-tipo Descripción
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
codLibro-alfanumérico-String Código de libro: 080000 RCE (Obligatorio)
Parámetros[body] No aplica.
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Parámetros valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: GET
Parámetros[salida] Parámetros de Salida Descripción
numRuc-alfanumérico-String Número de RUC del contribuyente
perTributario-alfanumérico-String Periodo tributario
54
numTicket-alfanumérico-String Número de ticket de envío [AAAA99999999]
AAAA: Año
99: Tipo de correlativo
99999999: Número correlativo de envío
nomArchivoImportacion-alfanuméricoString
Nombre del archivo utilizado para la
importación o nombre de archivo generado
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/propuesta/web/202201/080000/resu
menfechatipocambio
Headers
Body
(No aplica)
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
• 1005 - El campo “perTributario” no enviado o es vacío
• 1006 - Formato de perTributario no cumple con el formato “yyyymm”
• 1007 - El perTributario de búsqueda no debe ser mayor a la fecha actual
• 1014 - Solo se permite dato numérico de 6 dígitos para el perTributario.
• 1064 - El periodo no debe ser mayor al periodo de la fecha actual
• 1093 - Formato de período no cumple con el formato “yyyymm”
• 1141 - Código tipo de moneda no permitido o no valido
• 1142 - No se permite el tipo de dato para codMoneda
• 1143 - El campo "codMoneda" es nulo o vacío
• 1144 - El campo "mtoTipoCambio" es nulo o vacío
• 1145 - Solo se permite dato numérico y decimal para el mtoTipoCambio
• 1140 - El campo “codLibro” no enviado o es vacío
5.11 Servicio Web Api actualizar reintegro del crédito fiscal
Nombre Web
Services
Servicio Web Api registrar reintegro del crédito fiscal
Descripción Permite registrar el dato del reintegro del crédito fiscal asociado a los datos del FV0621
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/propuesta/web/{perTributario}/grab
acreditofiscal
Parámetros[URL] Param-formato-tipo Descripción
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
Parámetros[body] Param-formato-tipo Descripción
Registros-Object-Object Registros Inicio
valorRCF-numérico-decimal128 Reintegro de Crédito fiscal (Obligatorio)
55
Registros-Object-Object Registros Fin
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Parámetros Valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: PUT
Parámetros[salida] Parámetros Valor
HTTP status 200
Content-Type application/json
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/propuesta/web/202301/grabacredito
fiscal
Headers
Body
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
• 1005 – El campo “perTributario” no enviado o es vacío
• 1006 – Formato de perTributario no cumple con el formato “yyyymm”
• 1007 – El perTributario de búsqueda no debe ser mayor a la fecha actual
• 1070 – No se ha encontrado información de comprobantes de pago en Periodo
Seleccionado
• 1188 - El campo "valorRCF" no enviado o es vacío
5.12 Servicio Web Api actualizar crédito fiscal especial
Nombre Web
Services
Servicio Web Api actualizar crédito fiscal especial
Descripción Permite registrar el dato del crédito fiscal especial asociado a los datos del FV0621
56
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/propuesta/web/{perTributario}/grab
acreditofiscalespecial
Parámetros[URL] Param-formato-tipo Descripción
perTributario -alfanumérico-String Periodo tributario (Obligatorio)
Parámetros[body] Param-formato-tipo Descripción
Registros-Object-Object Registros Inicio
valorCFE-numérico-decimal128 Reintegro de Crédito fiscal especial
(Obligatorio)
Registros-Object-Object Registros Fin
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Parámetros valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: PUT
Parámetros[salida] Parámetros Valor
HTTP status 200
Content-Type application/json
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/propuesta/web/202301/grabacredito
fiscalespecial
Headers
Body
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
• 1005 – El campo “perTributario” no enviado o es vacío
• 1006 – Formato de perTributario no cumple con el formato “yyyymm”
• 1007 – El perTributario de búsqueda no debe ser mayor a la fecha actual
• 1189 - El campo "valorCFE" no enviado o es vacío
57
5.13 Servicio Web Api actualizar coeficiente de prorrata
Nombre Web
Services
Servicio Web Api actualizar coeficiente de la prorrata
Descripción Permite actualizar el coeficiente de la prorrata asociado a los datos del FV0621
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/propuesta/web/{perTributario}/grab
acreditofiscal
Parámetros[URL] Param-formato-tipo Descripción
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
Parámetros[body] Param-formato-tipo Descripción
Registros-Object-Object Registros Inicio
factProrrata-numérico-decimal128 Coefiente de Prorrata FV621
(Obligatorio)
Registros-Object-Object Registros Fin
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Parámetros valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: PUT
Parámetros[salida] Parámetros Valor
HTTP status 200
Content-Type application/json
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/propuesta/web/202301/grabacredito
fiscal
Headers
Body
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
• 1005 – El campo “perTributario” no enviado o es vacío
58
• 1006 – Formato de perTributario no cumple con el formato “yyyymm”
• 1007 – El perTributario de búsqueda no debe ser mayor a la fecha actual
• 1187 - El campo "factprorrata" no enviado o es vacío
5.14 Servicio Web Api consultar FV0621
Nombre Web
Services
Servicio Web Api consultar FV0621
Descripción Permite consultar los datos asociados al FV0621
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/propuesta/web?periodoSeleccionado
={periodoSeleccionado}
Parámetros[URL] Param-formato-tipo Descripción
periodoSeleccionado -alfanumérico-String Periodo tributario (Obligatorio)
Parámetros[body] No aplica.
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Parámetros valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: PUT
Parámetros[salida] Parámetros de Salida Descripción
registros-array-array Array de la Propuesta FV621 - inicio
factprorrata-numérico-decimal128 Coeficiente de Prorrata
valorRCF-numérico-decimal128 Reintegro del crédito fiscal
valorCFE-numérico-decimal128 Crédito fiscal especial
registros-array-array Array de la Propuesta FV621 - fin
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/propuesta/web?periodoSeleccionado
=202301&tipoInfo=FV0621
Headers
Body
(No aplica)
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
• 1005 - El campo “perTributario” no enviado o es vacío
59
• 1006 – Formato de perTributario no cumple con el formato “yyyymm”
• 1007 – El perTributario de búsqueda no debe ser mayor a la fecha actual
5.15 Servicio Web Api eliminar comprobante de la propuesta
Nombre Web
Services
Servicio Web Api eliminar comprobante de la propuesta
Descripción Permite eliminar un comprobante de la propuesta que ha sido agregado por el contribuyente
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/propuesta/web/propuestarce/{perTri
butario}
Parámetros[URL] Param-formato-tipo Descripción
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
Parámetros[body] Param-formato-tipo Descripción
Array Array - inicio
numSerieCDP-alfanumérico-string Número de serie del comprobante de pago o
documento (Obligatorio)
numCDP-alfanumérico-string Número del comprobante de pago o
documento (Obligatorio)
codCar-alfanumérico-string Código de Anotación de Registro (CAR SUNAT)
(Obligatorio)
codTipoCDP-alfanumérico-string Tipo de Comprobante de Pago o documento.
Solo permite los comprobantes de pago 00, 01,
03, 05, 06, 07, 08, 11, 12, 13, 14, 15, 16, 18, 21,
24, 25, 27, 28, 30, 32, 34, 35, 36, 37, 42, 43, 44,
45, 48, 49, 55 y 56 (Obligatorio)
Array Array - fin
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Parámetros valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: DELETE
Parámetros[salida] Parámetros Valor
HTTP status 200
Content-Type application/json
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/propuesta/web/propuestarce/20230
1
Headers
Body
60
Result OK
Result
Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
• 1005 - El campo “perTributario” no enviado o es vacío
• 1006 - Formato de perTributario no cumple con el formato “yyyymm”
• 1007 - El perTributario de búsqueda no debe ser mayor a la fecha actual
• 1070 - No se ha encontrado información de comprobantes de pago en Periodo
Seleccionado
• 1135 - El campo “codCar” no enviado o es vacío
• 1136 - Solo se permite dato numérico de 27 dígitos para el Codigo CAR.
• 1323- El campo "numSerieCDP" es nulo o vacío
• 1011 - El campo “codTipoCDP” no enviado o es vacío
• 1012 - El codTipoCDP ingresado no existe o no es válido
5.16 Servicio Web Api eliminar comprobante del preliminar
Nombre Web
Services
Servicio Web Api eliminar comprobante del preliminar RCE
Descripción Permite eliminar un comprobante del preliminar RCE o un comprobante no domiciliado del
RCE
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/preliminar/web/comprobanteslibrosc
ompras/{perTributario}/eliminacomprobante
Parámetros[URL] Param-formato-tipo Descripción
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
Parámetros[body] Param-formato-tipo Descripción
detalleAjustes-array-array Array detalle ajustes - inicio
codTipoCDP-alfanumérico-string Tipo de Comprobante de Pago o Documento.
Solo permite los comprobantes de pago 00, 01,
03, 05, 06, 07, 08, 11, 12, 13, 14, 15, 16, 18, 21,
24, 25, 27, 28, 30, 32, 34, 35, 36, 37, 42, 43, 44,
45, 48, 49, 55 y 56 (Obligatorio)
numSerieCDP-alfanumérico-string Número de serie del comprobante de pago o
documento (Obligatorio)
numCDP-alfanumérico-string Número del comprobante de pago o
documento (Obligatorio)
codCar-alfanumérico-string Código de Anotación de Registro (CAR SUNAT)
(Obligatorio)
detalleAjustes-array-array Array detalle ajustes - fin
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
61
Valores:
Parámetros valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: POST
Parámetros[salida] Parámetros Valor
HTTP status 200
Content-Type application/json
Evidencias Evidencia 1: Cuando el comprobante existe
URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/preliminar/web/comprobanteslibrosc
ompras/202203/eliminacomprobante
Headers
Body
Result OK
Evidencia 2: Cuando el comprobante no existe
URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/preliminar/web/comprobanteslibrosc
ompras/202203/eliminacomprobante
Headers
(No aplica)
Body
Result OK
Result Fail
62
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
• 1005 - El campo “perTributario” no enviado o es vacío
• 1006 - Formato de perTributario no cumple con el formato “yyyymm”
• 1007 - El perTributario de búsqueda no debe ser mayor a la fecha actual
• 1135 - El campo “codCar” no enviado o es vacío
• 1136 - Solo se permite dato numérico de 27 dígitos para el Codigo CAR.
• 1323- El campo "numSerieCDP" es nulo o vacío
• 1011 - El campo “codTipoCDP” no enviado o es vacío
• 1012 - El codTipoCDP ingresado no existe o no es válido
• 1070 - No se ha encontrado información de comprobantes de pago en Periodo
Seleccionado
5.17 Servicio Web Api eliminar preliminar
Nombre Web
Services
Servicio Web Api eliminar preliminar
Descripción Permite eliminar todos los preliminares o solo el preliminar de no domiciliados.
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/preliminar/web/registroslibros/{perT
ributario}/{indEliminar}/eliminapreliminar
Parámetros[URL] Param-formato-tipo Descripción
perTributario -alfanumérico-String Periodo tributario (Obligatorio)
indEliminar-numérico-int Indicador de Eliminación:
1 = Eliminar todo el preliminar
2 = Eliminar solo "No Domiciliados"
(Obligatorio)
Parámetros[body] No aplica
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Parámetros valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: PUT
Parámetros[salida] Parámetros Valor
HTTP status 200
Content-Type application/json
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/preliminar/web/registroslibros/2022
03/1/eliminapreliminar
63
Headers
Body
(No aplica)
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
• 1005 – El campo “perTributario” no enviado o es vacío
• 1006 – Formato de perTributario no cumple con el formato “yyyymm”
• 1007 – El perTributario de búsqueda no debe ser mayor a la fecha actual
• 2266 - El campo 'indEliminar' no enviado o es vacío
• 1140 - El campo “codLibro” no enviado o vacío
• 1014 - Solo se permite dato numérico de 6 dígitos para el perTributario
• 1009 - El libro electrónico con los siguientes datos: " + " numero de RUC: " +
numRuc + " periodoTributario: " + strPeriodoTributario + " y codigo de Libro: "
+ codLibro + " no existe.
• 2301 - No es posible eliminar su preliminar, debido a que aun no genera su
preliminar para el periodo ingresado.
• 2302 - No es posible eliminar su preliminar, debido a que ya registro su
preliminar para el periodo ingresado.
• 2297 - No es posible eliminar su preliminar, debido a que su registro se
encuentra generado para el periodo ingresado
• 2009 - El campo 'indEliminar' enviado no es válido.
5.18 Servicio Web Api cargar ajustes posteriores
Nombre Web
Services
Servicio Web Api cargar comprobantes en ajustes posteriores
Descripción Servicio web api que permite al generador, importar un archivo conteniendo los ajustes
posteriores
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/receptorajustesposteriores/web/
ajustesposteriores/upload
Parámetros[body] No aplica
Parámetros[header] Valores:
Content-type: application/x-www-form-urlencoded
Metadata Cliente TUS
Param-formato-tipo Descripción
filename-alfanumérico-string Nombre de archivo (Obligatorio)
filetype-alfanumérico-string Tipo de archivo (Obligatorio)
numRuc-alfanumérico-string Número de RUC del contribuyente (Obligatorio)
64
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
codOrigenEnvio-alfanuméricostring
Código de origen de envío: 2 Servicio web
(Obligatorio)
codProceso-alfanumérico-String Código del indicador de carga masiva: 6. Cargar
Ajuste posteriores del SIRE (Ver Anexo I: Indicador
de carga masiva) (Obligatorio)
codTipoCorrelativo-alfanuméricostring
Tipo de correlativo: 01: Tipo envíos masivos (Ver
Anexo II: Tipo de correlativo) (Obligatorio)
nomArchivoImportacionalfanumérico-String
Nombre del archivo utilizado para la importación o
nombre de archivo generado (Obligatorio)
codLibro-alfanumérico-String Código de libro: 080000 RCE (Obligatorio)
Parámetros[salida] Parámetros Valor
HTTP status 200
Content-Type application/json
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/receptorajustesposteriores/web/
ajustesposteriores/upload
Headers (metadata)
filename
TEUyMDEwMDE3NjQ1MDIwMjMwMjAwMTQwNDAwMDMxMTEwMi56aXA=,filetype
YXBwbGljYXRpb24vemlw,numRuc MjAxMDAxNzY0NTA=,perTributario
MjAyMzAy,codOrigenEnvio MQ==,codProceso ODc=,codTipoCorrelativo
MQ==,nomArchivoImportacion
TEUyMDEwMDE3NjQ1MDIwMjMwMjAwMTQwNDAwMDMxMTEwMi56aXA=,codLibro
MTQwMDAw
Body
(No aplica)
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
● 1001 - El campo “numRuc” no enviado o es vacío
● 1002 - Solo se permite dato numérico de 11 dígitos para el número de RUC.
● 1003 - El RUC ingresado no existe o no es válido
● 1005 - El campo “perTributario” no enviado o es vacío
● 1006 - Formato de perTributario no cumple con el formato “yyyymm”
● 1007 - El perTributario de búsqueda no debe ser mayor a la fecha actual
● 1014 - Solo se permite dato numérico de 6 dígitos para el perTributario.
● 1064 - El periodo no debe ser mayor al periodo de la fecha actual
● 1093 - Formato de período no cumple con el formato “yyyymm”
● 1028 - El campo “codOrigenEnvio” no enviado o es vacío
● 1029 - Código tipo de Origen de Envio no permitido o no valido
● 1030 - Solo se permite dato numérico de 1 dígito para el codOrigenEnvio
● 1025 - El campo “codProceso” no enviado o es vacío
● 1026 - Código Proceso no permitido o no valido
● 1027 - Solo se permite dato numérico para el codProceso
● 1138 - El campo "codProceso" es nulo o vacío
● 1139 - Código de Proceso no permitido o no valido
● 1048 - Solo se permite dato numérico de 1 dígito para el codTipoOrigen
● 1022 - nombre del archivo no enviado o es vacio.
● 1024 - El archivo <nombre del archivo txt> fue previamente enviado.
● 1044 - Error en la <<Posición - Descripción>> del nombre del archivo plano, favor de
corregir
65
● 1348 - La extensión del archivo es diferente a “.zip”, por favor corregir
● 1346 - El tamaño del archivo comprimido en formato “.zip” debe ser menor o igual
a 6GB.
● 1350 - El tamaño del archivo mayor a 0 Kb.
● 1351 - Se ha producido un error al realizar el envío del archivo, por favor volver a
intentar el envío
● 1048 - Solo se permite dato numérico de 2 dígitos para el codTipoCorrelativo
● 1049 - El campo “codTipoCorrelativo” no enviado o es vacio
● 1050 - Código tipo de Correlativo no permitido o no valido
● 1140 - El campo “codLibro” no enviado o es vacío
Tecnología Uso de la librería TUS.io para cliente.
5.19 Servicio Web Api enviar ajustes posteriores
Nombre Web
Services
Servicio Web Api enviar ajustes posteriores (registrar preliminar de ajustes posteriores)
Descripción Permite registrar los preliminares de ajustes posteriores
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/ajustesposteriores/web/comprobant
esajuspost/{perTributario}/{codOrigenEnvio}/registrarajustesposterioresrc
Parámetros[URL] Param-formato-tipo Descripción
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
codOrigenEnvio – alfanumérico - String Código de origen de envío: 1 (Obligatorio)
Parámetros[body] No aplica
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Content-type: application/x-www-form-urlencoded
Parámetros valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: POST
Parámetros[salida] Parámetros Valor
HTTP status 200
Content-Type application/json
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/ajustesposteriores/web/comprobant
esajuspost/{perTributario}/{codOrigenEnvio}/registrarajustesposterioresrc
Headers
Body
Result OK
66
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
• 1005 – El campo “perTributario” no enviado o es vacío
• 1006 – Formato de perTributario no cumple con el formato “yyyymm”
• 1007 – El perTributario de búsqueda no debe ser mayor a la fecha actual
• 1140 - El campo “codLibro” no enviado o es vacío
5.20 Servicio Web Api eliminar comprobante de ajustes posteriores
Nombre Web
Services
Servicio Web Api eliminar comprobantes de ajustes posteriores
Descripción Permite eliminar comprobantes en ajustes posteriores del SIRE
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/ajustesposteriores/web/comprobant
esajuspost/{perTributario}/{indTipoAjustePosterior}/eliminarcomprobanteaprc
Parámetros[URL] Param-formato-tipo Descripción
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
indTipoAjustePosterior-numérico-int Tipo de ajuste posterior: 1 Ajuste Posterior
(Ver Anexo II: Tipo de ajuste posterior)
(Obligatorio)
Parámetros[body] Param-formato-tipo Descripción
codAjustePosterior-alfanumérico-string Identificador de la colección (Obligatorio)
detalleAjustes-array-array Array detalle ajustes - inicio
codTipoCDP-alfanumérico-string Tipo de Comprobante de Pago o Documento.
Solo permite los comprobantes de pago 00, 01,
03, 05, 06, 07, 08, 11, 12, 13, 14, 15, 16, 18, 21,
24, 25, 27, 28, 30, 32, 34, 35, 36, 37, 42, 43, 44,
45, 48, 49, 55 y 56 (Obligatorio)
numSerieCDP-alfanumérico-string Número de serie del comprobante de pago o
documento (Obligatorio)
numCDP-alfanumérico-string Número del comprobante de pago o
documento (Obligatorio)
codCar-alfanumérico-string Código de Anotación de Registro (CAR SUNAT)
(Obligatorio)
Id-alfanumérico-string Identificador del comprobante en la colleción
(Obligatorio)
detalleAjustes-array-array Array detalle ajustes - fin
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Content-type: application/x-www-form-urlencoded
Parámetros valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: DELETE
Parámetros[salida] Parámetros Valor
67
HTTP status 200
Content-Type application/json
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/ajustesposteriores/web/comprobant
esajuspost/202301/1/eliminarcomprobanteaprc
Headers
Body
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
• 1005 – El campo “perTributario” no enviado o es vacío
• 1006 – Formato de perTributario no cumple con el formato “yyyymm”
• 1007 – El perTributario de búsqueda no debe ser mayor a la fecha actual
• 1011 - El campo “codTipoCDP” no enviado o es vacío
• 1012 - El codTipoCDP ingresado no existe o no es válido
• 1104 - El código de tipo de comprobante de pago enviado no es válido
• 1135 - El campo codCar no enviado o es vacío.
• 1136 - Solo se permite dato numérico de 27 dígitos para el código CAR.
• 1065 - El periodo debe ser mayor o igual al <<año-mes>> de vigencia del
módulo
• 1066 - No hay información para el periodo seleccionado debido a que ha
superado el plazo de los 6 años, para poder visualizar dicha información
deberá solicitarla a Administración Tributaria.
• 1323 - El campo "numSerieCDP" es nulo o vacío
• 2000 - El campo indTipoAjustePosterior no tiene asignado un valor válido
5.21 Servicio Web Api cargar ajustes posteriores no domiciliados
Nombre Web
Services
Servicio Web Api cargar comprobantes no domiciliados en ajustes posteriores
68
Descripción Servicio Web Api que permite al generador, importar un archivo conteniendo los ajustes
posteriores de operaciones con sujetos no domiciliados
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/receptorajustesposteriores/web/
ajustesposteriores/upload
Parámetros[body] No aplica
Parámetros[header] Valores:
Content-type: application/x-www-form-urlencoded
Metadata Cliente TUS
Param-formato-tipo Descripción
filename-alfanumérico-string Nombre de archivo (Obligatorio)
filetype-alfanumérico-string Tipo de archivo (Obligatorio)
numRuc-alfanumérico-string Número de RUC del contribuyente
(Obligatorio)
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
codOrigenEnvio-alfanumérico-string Código de origen de envío: 2 Servicio web
(Obligatorio)
codProceso-alfanumérico-String Código del indicador de carga masiva: 60.
Importar CP no domiciliados en Ajustes
Posteriores (Ver Anexo I: Indicador de carga
masiva) (Obligatorio)
codTipoCorrelativo-alfanumérico-string Tipo de correlativo: 01: Tipo envíos masivos
(Ver Anexo II: Tipo de correlativo) (Obligatorio)
nomArchivoImportacion-alfanuméricoString
Nombre del archivo utilizado para la
importación o nombre de archivo generado
(Obligatorio)
codLibro-alfanumérico-String Código de libro: 080000 RCE (Obligatorio)
Parámetros[salida] Parámetros
de Salida Descripción Formato Tipo dato
numTicket
Número de ticket de envío [AAAA99999999]
AAAA: Año
99: Tipo de correlativo
99999999: Número correlativo de envío
alfanumerico String
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/receptorajustesposteriores/web/
ajustesposteriores/upload
Headers (metadata)
filename
TEUyMDEwMDE3NjQ1MDIwMjMwMjAwMTQwNDAwMDMxMTEwMi56aXA=,filetype
YXBwbGljYXRpb24vemlw,numRuc MjAxMDAxNzY0NTA=,perTributario
MjAyMzAy,codOrigenEnvio MQ==,codProceso ODc=,codTipoCorrelativo
MQ==,nomArchivoImportacion
TEUyMDEwMDE3NjQ1MDIwMjMwMjAwMTQwNDAwMDMxMTEwMi56aXA=,codLibro
MTQwMDAw
Body
(No aplica)
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
● 1001 - El campo “numRuc” no enviado o es vacío
● 1002 - Solo se permite dato numérico de 11 dígitos para el número de RUC.
69
● 1003 - El RUC ingresado no existe o no es válido
● 1005 - El campo “perTributario” no enviado o es vacío
● 1006 - Formato de perTributario no cumple con el formato “yyyymm”
● 1007 - El perTributario de búsqueda no debe ser mayor a la fecha actual
● 1014 - Solo se permite dato numérico de 6 dígitos para el perTributario.
● 1064 - El periodo no debe ser mayor al periodo de la fecha actual
● 1093 - Formato de período no cumple con el formato “yyyymm”
● 1028 - El campo “codOrigenEnvio” no enviado o es vacío
● 1029 - Código tipo de Origen de Envio no permitido o no valido
● 1030 - Solo se permite dato numérico de 1 dígito para el codOrigenEnvio
● 1025 - El campo “codProceso” no enviado o es vacío
● 1026 - Código Proceso no permitido o no valido
● 1027 - Solo se permite dato numérico para el codProceso
● 1138 - El campo "codProceso" es nulo o vacío
● 1139 - Código de Proceso no permitido o no valido
● 1048 - Solo se permite dato numérico de 1 dígito para el codTipoOrigen
● 1022 - nombre del archivo no enviado o es vacio.
● 1024 - El archivo <nombre del archivo txt> fue previamente enviado.
● 1044 - Error en la <<Posición - Descripción>> del nombre del archivo plano, favor de
corregir
● 1348 - La extensión del archivo es diferente a “.zip”, por favor corregir
● 1346 - El tamaño del archivo comprimido en formato “.zip” debe ser menor o igual
a 6GB.
● 1350 - El tamaño del archivo mayor a 0 Kb.
● 1351 - Se ha producido un error al realizar el envío del archivo, por favor volver a
intentar el envío
● 1048 - Solo se permite dato numérico de 2 dígitos para el codTipoCorrelativo
● 1049 - El campo “codTipoCorrelativo” no enviado o es vacio
● 1050 - Código tipo de Correlativo no permitido o no valido
● 1140 - El campo “codLibro” no enviado o es vacío
Tecnología Uso de la librería TUS.io para cliente.
5.22 Servicio Web Api enviar ajustes posteriores no domiciliados
Nombre Web
Services
Servicio Web Api enviar ajustes posteriores de operaciones con sujetos no domiciliados
Descripción Permite registrar los preliminares de ajustes posteriores
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/ajustesposteriores/web/comprobant
esajuspost/{perTributario}/{numAjustePosterior}/{codLibro}/{numTicket}/registrarajustespos
terioresrcnd
Parámetro[URL] Param-formato-tipo Descripción
perTributario -alfanumérico-String Periodo tributario (Obligatorio)
numAjustePosterior-alfanumérico-String Correlativo o numero de ajuste posterior
(Obligatorio)
codLibro-alfanumérico-String Código de libro: 080000 RCE (Obligatorio)
numTicket-alfanumérico-string Número de ticket de envío [AAAA99999999]
AAAA: Año
99: Tipo de correlativo
99999999: Número correlativo de envío
(Obligatorio)
Parámetros[body] Param-formato-tipo Descripción
controlProcesos-Object - Object controlProcesos Inicio
lisFases -arrray- array lisFases Inicio
codFase -alfanumérico-String Codigo de Fase:
14: Ventas (RVIE)
8: Compras (RCE)
lisFases -arrray- array lisFases Fin
controlProcesos-Object - Object controlProcesos Fin
registrosLibros-Object - Object registrosLibros Inicio
indEnviadoAjuste – numerico - String Indicador de ajuste enviado: 1
70
registrosLibros-Object - Object registrosLibros Fin
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Content-type: application/x-www-form-urlencoded
Parámetros valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: POST
Parámetros[salida] Parámetros Valor
HTTP status 200
Content-Type application/json
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/ajustesposteriores/web/comprobant
esajuspost/202301/2/080000/20210300000001/registrarajustesposterioresrcnd
Headers
Body
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
• 1006 – Formato de perTributario no cumple con el formato “yyyymm”
• 1007 – El perTributario de búsqueda no debe ser mayor a la fecha actual
• 1051 - El campo 'numTicket' no enviado o es vacío.
• 1052 - Formato no permitido o no valido para el número de Ticket
• 2002 - Solo se permite valor númerico para el campo "codFase"
• 2003 - El valor enviado para el campo "codFase" no es el correcto.
• 2004 - Solo se permite valor númerico para el campo "indEnviadoAjuste"
• 2005 - El valor enviado para el campo "indEnviadoAjuste" no es el correcto.
• 1140 - El campo “codLibro” no enviado o es vacío
71
5.23 Servicio Web Api eliminar comprobante de ajustes posteriores no
domiciliados
Nombre Web
Services
Servicio Web Api eliminar comprobantes no domiciliados ajustes posteriores (registrar
preliminar de ajustes posteriores)
Descripción Permite eliminar comprobantes no domiciliados en ajustes posteriores del SIRE
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/ajustesposteriores/web/comprobant
esajuspost/{perTributario}/{indTipoAjustePosterior}/eliminarcomprobanteaprcnd
Parámetros[URL] Param-formato-tipo Descripción
perTributario -alfanumérico-String Periodo tributario (Obligatorio)
indTipoAjustePosterior-numéricoint
Tipo de ajuste posterior: 2 Ajuste Posterior con No
Domiciliados (Ver Anexo II: Tipo de ajuste
posterior) (Obligatorio)
Parámetros[body] Param-formato-tipo Descripción
codAjustePosterior-alfanumérico-string Identificador de la colección (Obligatorio)
detalleAjustes-array-array Array de detalle de ajustes - inicio
codTipoCDP-alfanumérico-string Tipo de Comprobante de Pago o Documento.
Solo permite los comprobantes de pago 00, 01,
03, 05, 06, 07, 08, 11, 12, 13, 14, 15, 16, 18, 21,
24, 25, 27, 28, 30, 32, 34, 35, 36, 37, 42, 43, 44,
45, 48, 49, 55 y 56 (Obligatorio)
numSerieCDP-alfanumérico-string Número de serie del comprobante de pago o
documento (Obligatorio)
numCDP-alfanumérico-string Número del comprobante de pago o
documento (Obligatorio)
codCar-alfanumérico-string CAR SUNAT (Obligatorio)
id-alfanumérico-string Identificador del comprobante (Obligatorio)
detalleAjustes-array-array Array de detalle de ajustes - fin
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Content-type: application/x-www-form-urlencoded
Parámetros valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: DELETE
Parámetros[salida] Parámetros Valor
HTTP status 200
Content-Type application/json
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/ajustesposteriores/web/comprobant
esajuspost/202301/5/eliminarcomprobanteaprcnd
Headers
Body
72
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
• 1005 – El campo “perTributario” no enviado o es vacío
• 1006 – Formato de perTributario no cumple con el formato “yyyymm”
• 1007 – El perTributario de búsqueda no debe ser mayor a la fecha actual
• 2000 - El campo indTipoAjustePosterior no tiene asigando un valor válido
• 1104 - El código de tipo de comprobante de pago enviado no es válido
• 1323 - El campo "numSerieCDP" es nulo o vacío
• 1011 - El campo “codTipoCDP” no enviado o es vacío
• 1012 - El codTipoCDP ingresado no existe o no es válido
5.24 Servicio Web Api cargar ajustes posteriores de periodos anteriores
Nombre Web
Services
Servicio Web Api cargar comprobantes en ajustes posteriores de periodos anteriores al SIRE
Descripción Servicio web api que permite al generador, importar un archivo conteniendo los ajustes
posteriores del RC de periodos anteriores al SIRE
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/receptorajustesposteriores/web/
ajustesposteriores/upload
Parámetros[body] No aplica
Parámetros[header] Valores:
Content-type: application/x-www-form-urlencoded
Metadata Cliente TUS
Param-formato-tipo Descripción
filename-alfanumérico-string Nombre de archivo (Obligatorio)
filetype-alfanumérico-string Tipo de archivo (Obligatorio)
numRuc-alfanumérico-string Número de RUC del contribuyente
(Obligatorio)
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
codOrigenEnvio-alfanumérico-string Código de origen de envío: 2 Servicio web
(Obligatorio)
codProceso-alfanumérico-String Código del indicador de carga masiva: 6.Cargar
Ajuste posteriores del SIRE (Ver Anexo I:
Indicador de carga masiva) (Obligatorio)
codTipoCorrelativo-alfanumérico-string Tipo de correlativo: 01: Tipo envíos masivos
73
(Ver Anexo II: Tipo de correlativo) (Obligatorio)
nomArchivoImportacion-alfanuméricoString
Nombre del archivo utilizado para la
importación o nombre de archivo generado
(Obligatorio)
codLibro-alfanumérico-String Código de libro: 080000 RCE (Obligatorio)
Parámetros[salida] Parámetros
de Salida Descripción Formato Tipo dato
numTicket
Número de ticket de envío [AAAA99999999]
AAAA: Año
99: Tipo de correlativo
99999999: Número correlativo de envío
alfanumerico String
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/receptorajustesposteriores/web/
ajustesposteriores/upload
Headers (metadata)
filename
TEUyMDEwMDE3NjQ1MDIwMjMwMjAwMTQwNDAwMDMxMTEwMi56aXA=,filetype
YXBwbGljYXRpb24vemlw,numRuc MjAxMDAxNzY0NTA=,perTributario
MjAyMzAy,codOrigenEnvio MQ==,codProceso ODc=,codTipoCorrelativo
MQ==,nomArchivoImportacion
TEUyMDEwMDE3NjQ1MDIwMjMwMjAwMTQwNDAwMDMxMTEwMi56aXA=,codLibro
MTQwMDAw
Body
(No aplica)
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
● 1001 - El campo “numRuc” no enviado o es vacío
● 1002 - Solo se permite dato numérico de 11 dígitos para el número de RUC.
● 1003 - El RUC ingresado no existe o no es válido
● 1005 - El campo “perTributario” no enviado o es vacío
● 1006 - Formato de perTributario no cumple con el formato “yyyymm”
● 1007 - El perTributario de búsqueda no debe ser mayor a la fecha actual
● 1014 - Solo se permite dato numérico de 6 dígitos para el perTributario.
● 1064 - El periodo no debe ser mayor al periodo de la fecha actual
● 1093 - Formato de período no cumple con el formato “yyyymm”
● 1028 - El campo “codOrigenEnvio” no enviado o es vacío
● 1029 - Código tipo de Origen de Envio no permitido o no valido
● 1030 - Solo se permite dato numérico de 1 dígito para el codOrigenEnvio
● 1025 - El campo “codProceso” no enviado o es vacío
● 1026 - Código Proceso no permitido o no valido
● 1027 - Solo se permite dato numérico para el codProceso
● 1138 - El campo "codProceso" es nulo o vacío
● 1139 - Código de Proceso no permitido o no valido
● 1048 - Solo se permite dato numérico de 1 dígito para el codTipoOrigen
● 1022 - nombre del archivo no enviado o es vacio.
● 1024 - El archivo <nombre del archivo txt> fue previamente enviado.
● 1044 - Error en la <<Posición - Descripción>> del nombre del archivo plano, favor de
corregir
● 1348 - La extensión del archivo es diferente a “.zip”, por favor corregir
● 1346 - El tamaño del archivo comprimido en formato “.zip” debe ser menor o igual
a 6GB.
74
● 1350 - El tamaño del archivo mayor a 0 Kb.
● 1351 - Se ha producido un error al realizar el envío del archivo, por favor volver a
intentar el envío
● 1048 - Solo se permite dato numérico de 2 dígitos para el codTipoCorrelativo
● 1049 - El campo “codTipoCorrelativo” no enviado o es vacio
● 1050 - Código tipo de Correlativo no permitido o no valido
● 1140 - El campo “codLibro” no enviado o es vacío
Tecnología Uso de la librería TUS.io para cliente.
5.25 Servicio Web Api enviar ajustes posteriores de periodos anteriores
Nombre Web
Services
Servicio Web Api enviar ajustes posteriores RC de periodos anteriores al SIRE
Descripción Permite registrar los preliminares de ajustes posteriores de RC de periodos anteriores al SIRE
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/ajustesposteriores/web/comprobant
esajuspost/{perTributario}/{numAjustePosterior}/{codLibro}/{numTicket}/registrarajustespos
terioresparc
Parámetros[URL] Param-formato-tipo Descripción
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
numAjustePosterior-alfanuméricoString
Correlativo o numero de ajuste posterior
(Obligatorio)
codLibro-alfanumérico-String Código de libro: 080000 RCE (Obligatorio)
numTicket-alfanumérico-string Número de ticket de envío [AAAA99999999]
AAAA: Año
99: Tipo de correlativo
99999999: Número correlativo de envío
(Obligatorio)
indTipoAjustePosterior-alfanuméricoString
Indice de ajuste posterior: 3
Parámetros[body] Param-formato-tipo Descripción
controlProcesos-Object - Object controlProcesos Inicio
lisFases -arrray- array lisFases Inicio
codFase -alfanumérico-String Codigo de Fase:
14: Ventas (RVIE)
8: Compras (RCE)
lisFases -arrray- array lisFases Fin
controlProcesos-Object - Object controlProcesos Fin
registrosLibros-Object - Object registrosLibros Inicio
indEnviadoAjuste – numerico - String Indicador de ajuste enviado: 1
registrosLibros-Object - Object registrosLibros Fin
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Content-type: application/x-www-form-urlencoded
Parámetros valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: POST
Parámetros[salida] Parámetros Valor
HTTP status 200
Content-Type application/json
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/ajustesposteriores/web/comprobant
esajuspost/{perTributario}/{numAjustePosterior}/{codLibro}/{numTicket}/registrarajustespos
terioresparc
Headers
75
Body
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
• 1005 - El campo “perTributario” no enviado o es vacío
• 1006 - Formato de "perTributario" no cumple con el formato “yyyymm”
• 1007 – El perTributario de búsqueda no debe ser mayor a la fecha actual
• 1051 - El campo 'numTicket' no enviado o es vacío.
• 1052 - Formato no permitido o no valido para el número de Ticket
• 2002 - Solo se permite valor númerico para el campo "codFase"
• 2003 - El valor enviado para el campo "codFase" no es el correcto.
• 2004 - Solo se permite valor númerico para el campo "indEnviadoAjuste"
• 2005 - El valor enviado para el campo "indEnviadoAjuste" no es el correcto.
• 1140 - El campo “codLibro” no enviado o es vacío
5.26 Servicio Web Api eliminar comprobante de ajustes posteriores de
periodos anteriores
Nombre Web
Services
Servicio Web Api eliminar comprobantes de ajustes posteriores RC de periodos anteriores
Descripción Permite eliminar comprobantes en ajustes posteriores RC de periodos anteriores al SIRE
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/ajustesposteriores/web/ajustesposte
riores/{indTipoAjustePosterior}/{perTributario}/eliminarcomprobanteapparc
Parámetros[URL] Param-formato-tipo Descripción
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
indTipoAjustePosterior-numérico-int Tipo de ajuste posterior: 3 Ajuste Posteriores de
periodos anteriores general (Ver Anexo II: Tipo
de ajuste posterior) (Obligatorio)
Parámetros[body] Param-formato-tipo Descripción
76
codAjustePosterior-alfanumérico-string Identificador de la colección (Obligatorio)
detalleAjustes-array-array Array de detalles de ajustes - inicio
codTipoCDP-alfanumérico-string Tipo de Comprobante de Pago o Documento.
Solo permite los comprobantes de pago 00, 01,
03, 05, 06, 07, 08, 11, 12, 13, 14, 15, 16, 18, 21,
24, 25, 27, 28, 30, 32, 34, 35, 36, 37, 42, 43, 44,
45, 48, 49, 55 y 56 (Obligatorio)
numSerieCDP-alfanumérico-string Número de serie del comprobante de pago o
documento (Obligatorio)
numCDP-alfanumérico-string Número del comprobante de pago o
documento (Obligatorio)
detalleAjustes-array-array Array de detalles de ajustes - fin
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Content-type: application/x-www-form-urlencoded
Parámetros Valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: DELETE (En Revisión) - POST
Parámetros[salida] Parámetros Valor
HTTP status 200
Content-Type application/json
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/ajustesposteriores/web/ajustesposte
riores/{indTipoAjustePosterior}/{perTributario}/eliminarcomprobanteapparc
Headers
Body
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
77
• 1005 – El campo “perTributario” no enviado o es vacío
• 1006 – Formato de perTributario no cumple con el formato “yyyymm”
• 1007 – El perTributario de búsqueda no debe ser mayor a la fecha actual
• 2000 - El campo indTipoAjustePosterior no tiene asigando un valor válido
• 1104 - El código de tipo de comprobante de pago enviado no es válido
• 1323 - El campo "numSerieCDP" es nulo o vacío
• 1011 - El campo “codTipoCDP” no enviado o es vacío
• 1012 - El codTipoCDP ingresado no existe o no es válido
5.27 Servicio Web Api cargar ajustes posteriores de periodos anteriores
no domiciliados
Nombre Web
Services
Servicio Web Api cargar comprobantes ND en ajustes posteriores de periodos anteriores al
SIRE
Descripción Servicio Web Api que permite al generador, importar un archivo conteniendo los ajustes
posteriores de operaciones con sujetos no domiciliados en períodos anteriores al SIRE
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/receptorajustesposteriores/web/
ajustesposteriores/upload
Parámetros[body] No aplica
Parámetros[header] Valores:
Content-type: application/x-www-form-urlencoded
Metadata Cliente TUS
Param-formato-tipo Descripción
filename-alfanumérico-string Nombre de archivo (Obligatorio)
filetype-alfanumérico-string Tipo de archivo (Obligatorio)
numRuc-alfanumérico-string Número de RUC del contribuyente (Obligatorio)
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
codOrigenEnvio-alfanumérico-string Código de origen de envío: 2 Servicio web
(Obligatorio)
codProceso-alfanumérico-String Código del indicador de carga masiva: 60.
Importar CP no domiciliados en Ajustes
Posteriores (Ver Anexo I: Indicador de carga
masiva) (Obligatorio)
codTipoCorrelativo-alfanuméricostring
Tipo de correlativo: 01: Tipo envíos masivos (Ver
Anexo II: Tipo de correlativo) (Obligatorio)
nomArchivoImportacionalfanumérico-String
Nombre del archivo utilizado para la importación
o nombre de archivo generado (Obligatorio)
codLibro-alfanumérico-String Código de libro: 080000 RCE (Obligatorio)
Parámetros[salida] Parámetros
de Salida Descripción Formato Tipo dato
numTicket
Número de ticket de envío [AAAA99999999]
AAAA: Año
99: Tipo de correlativo
99999999: Número correlativo de envío
alfanumerico String
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/receptorajustesposteriores/web/
ajustesposteriores/upload
Headers (metadata)
filename
TEUyMDEwMDE3NjQ1MDIwMjMwMjAwMTQwNDAwMDMxMTEwMi56aXA=,filetype
YXBwbGljYXRpb24vemlw,numRuc MjAxMDAxNzY0NTA=,perTributario
MjAyMzAy,codOrigenEnvio MQ==,codProceso ODc=,codTipoCorrelativo
MQ==,nomArchivoImportacion
TEUyMDEwMDE3NjQ1MDIwMjMwMjAwMTQwNDAwMDMxMTEwMi56aXA=,codLibro
MTQwMDAw
Body
(No aplica)
78
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
● 1001 - El campo “numRuc” no enviado o es vacío
● 1002 - Solo se permite dato numérico de 11 dígitos para el número de RUC.
● 1003 - El RUC ingresado no existe o no es válido
● 1005 - El campo “perTributario” no enviado o es vacío
● 1006 - Formato de perTributario no cumple con el formato “yyyymm”
● 1007 - El perTributario de búsqueda no debe ser mayor a la fecha actual
● 1014 - Solo se permite dato numérico de 6 dígitos para el perTributario.
● 1064 - El periodo no debe ser mayor al periodo de la fecha actual
● 1093 - Formato de período no cumple con el formato “yyyymm”
● 1028 - El campo “codOrigenEnvio” no enviado o es vacío
● 1029 - Código tipo de Origen de Envio no permitido o no valido
● 1030 - Solo se permite dato numérico de 1 dígito para el codOrigenEnvio
● 1025 - El campo “codProceso” no enviado o es vacío
● 1026 - Código Proceso no permitido o no valido
● 1027 - Solo se permite dato numérico para el codProceso
● 1138 - El campo "codProceso" es nulo o vacío
● 1139 - Código de Proceso no permitido o no valido
● 1048 - Solo se permite dato numérico de 1 dígito para el codTipoOrigen
● 1022 - nombre del archivo no enviado o es vacio.
● 1024 - El archivo <nombre del archivo txt> fue previamente enviado.
● 1044 - Error en la <<Posición - Descripción>> del nombre del archivo plano, favor de
corregir
● 1348 - La extensión del archivo es diferente a “.zip”, por favor corregir
● 1346 - El tamaño del archivo comprimido en formato “.zip” debe ser menor o igual
a 6GB.
● 1350 - El tamaño del archivo mayor a 0 Kb.
● 1351 - Se ha producido un error al realizar el envío del archivo, por favor volver a
intentar el envío
● 1048 - Solo se permite dato numérico de 2 dígitos para el codTipoCorrelativo
● 1049 - El campo “codTipoCorrelativo” no enviado o es vacio
● 1050 - Código tipo de Correlativo no permitido o no valido
● 1140 - El campo “codLibro” no enviado o es vacío
Tecnología Uso de la librería TUS.io para cliente.
5.28 Servicio Web Api enviar ajustes posteriores de periodos anteriores
no domiciliados
Nombre Web
Services
Servicio Web Api enviar ajustes posteriores de operaciones con sujetos no domiciliados de
periodos anteriores al SIRE
Descripción Permite registrar los preliminares de ajustes posteriores no domiciliados de periodos
anteriores al SIRE
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/ajustesposteriores/web/comprobant
esajuspost/{perTributario}/{numAjustePosterior}/{codLibro}/{numTicket}/registrarajustespos
terioresparcnd
Parámetros[URL] Param-formato-tipo Descripción
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
numAjustePosterior-alfanumérico-String Correlativo o numero de ajuste posterior
79
(Obligatorio)
codLibro-alfanumérico-String Código de libro: 080000 RCE (Obligatorio)
numTicket-alfanumérico-string Número de ticket de envío [AAAA99999999]
AAAA: Año
99: Tipo de correlativo
99999999: Número correlativo de
envío(Obligatorio)
Parámetros[body] Param-formato-tipo Descripción
controlProcesos-Object - Object controlProcesos Inicio
lisFases -arrray- array lisFases Inicio
codFase -alfanumérico-String Codigo de Fase:
14: Ventas (RVIE)
8: Compras (RCE)
lisFases -arrray- array lisFases Fin
controlProcesos-Object - Object controlProcesos Fin
registrosLibros-Object - Object registrosLibros Inicio
indEnviadoAjuste – numerico - String Indicador de ajuste enviado: 1
registrosLibros-Object - Object registrosLibros Fin
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Content-type: application/x-www-form-urlencoded
Parámetros valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: POST
Parámetros[salida] Parámetros Valor
HTTP status 200
Content-Type application/json
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/ajustesposteriores/web/comprobant
esajuspost/{perTributario}/{numAjustePosterior}/{codLibro}/{numTicket}/registrarajustespos
terioresparcnd
Headers
Body
Result OK
80
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
• 1005 – El campo “perTributario” no enviado o es vacío
• 1006 – Formato de perTributario no cumple con el formato “yyyymm”
• 1007 – El perTributario de búsqueda no debe ser mayor a la fecha actual
• 1051 - El campo 'numTicket' no enviado o es vacío.
• 1052 - Formato no permitido o no valido para el número de Ticket
• 2002 - Solo se permite valor númerico para el campo "codFase"
• 2003 - El valor enviado para el campo "codFase" no es el correcto.
• 2004 - Solo se permite valor númerico para el campo "indEnviadoAjuste"
• 2005 - El valor enviado para el campo "indEnviadoAjuste" no es el correcto.
• 1140 - El campo “codLibro” no enviado o es vacío
5.29 Servicio Web Api eliminar comprobante de ajustes posteriores de
periodos anteriores no domiciliados
Nombre Web
Services
Servicio Web Api eliminar comprobantes no domiciliados ajustes posteriores de periodos
anteriores al SIRE (registrar preliminar de ajustes posteriores)
Descripción Permite eliminar comprobantes no domiciliados en ajustes posteriores de periodos
anteriores al SIRE
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/ajustesposteriores/web/{numAjusteP
osterior}/{perTributario}/eliminarcomprobanteapparcnd
Parámetros[URL] Param-formato-tipo Descripción
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
numAjustePosterior-alfanumérico-String Correlativo o numero de ajuste posterior
(Obligatorio)
Parámetros[body] Param-formato-tipo Descripción
codAjustePosterior-alfanumérico-string Identificador de la colección (Obligatorio)
detalleAjustes-array-array Array de detalle de ajustes - inicio
codTipoCDP-alfanumérico-string Tipo de Comprobante de Pago o Documento.
Solo permite los comprobantes de pago 00, 01,
03, 05, 06, 07, 08, 11, 12, 13, 14, 15, 16, 18, 21,
24, 25, 27, 28, 30, 32, 34, 35, 36, 37, 42, 43, 44,
45, 48, 49, 55 y 56 (Obligatorio)
numSerieCDP-alfanumérico-string Número de serie del comprobante de pago o
documento (Obligatorio)
numCDP-alfanumérico-string Número del comprobante de pago o
documento (Obligatorio)
numTicket-alfanumérico-string Número de ticket de envío (Obligatorio)
detalleAjustes-array-array Array de detalle de ajustes - fin
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Content-type: application/x-www-form-urlencoded
Parámetros valor
81
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: DELETE (En Revisión) - POST
Parámetros[salida] Parámetros Valor
HTTP status 200
Content-Type application/json
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/ajustesposteriores/web/1/202301/eli
minarcomprobanteapparcnd
Headers
Body
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
• 1005 – El campo “perTributario” no enviado o es vacío
• 1006 – Formato de perTributario no cumple con el formato “yyyymm”
• 1007 – El perTributario de búsqueda no debe ser mayor a la fecha actual
• 2000 - El campo indTipoAjustePosterior no tiene asigando un valor válido
• 1104 - El código de tipo de comprobante de pago enviado no es válido
• 1323 - El campo "numSerieCDP" es nulo o vacío
• 1011 - El campo “codTipoCDP” no enviado o es vacío
• 1012 - El codTipoCDP ingresado no existe o no es válido
5.31 Servicio Web Api consultar estado de envío de ticket
82
Nombre Web
Services
Servicio Web Api consultar estado de envío de ticket.
Descripción Permite consultar el estado de envío del ticket.
Para que funcione el servicio, se necesita haber generado un ticket con reemplazar
propuesta, generar propuesta, descargar propuesta, entre otros.
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/gestionprocesosmasivos/web/ma
sivo/consultaestadotickets?perIni={perIni}&perFin={perFin}&page={page}&perPage={perPage
}&numTicket={numTicket}
Parámetros[URL] Param-formato-tipo Descripción
perIni-alfanumérico-string Periodo de consulta de documentos de
comprobantes del RCE preliminar Inicio.
(Obligatorio)
perFin-alfanumérico-string Periodo de consulta de documentos de
comprobantes del RCE preliminar Final.
(Obligatorio)
page-numerico-int Número de página.
Ejemplo: 1 (Obligatorio)
perPage-numerico-int Cantidad de tickets por página
Ejemplo: 20 (Obligatorio)
numTicket-alfanumérico-String Número de ticket de envío [AAAA99999999]
AAAA: Año
99: Tipo de correlativo
99999999: Número correlativo de envío
(Opcional: Solo si se desea ver los datos de un
ticket en específico)
codLibro-alfanumérico-String Código de libro: 080000 RCE (Obligatorio)
codOrigenEnvio-alfanuméricoString
Código de origen de envío: 2 Servicio web
(Obligatorio)
Parámetros[body] No aplica
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Parámetros valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: GET
Parámetros[salida] Parámetros de Salida Descripcion
paginacion-Object Object de paginación - inicio
page- numérico-Int Ejemplo: 1 (Obligatorio)
perPage- numérico-Int Ejemplo: 20 (Obligatorio)
totalRegistros- numérico-Int Total de registros (Obligatorio)
paginacion-Object Object de paginación - fin
registros-array-array Array de registros - inicio
showReportesDescarganumérico-Integer
Valores 0 y 1
0 - no muestra icono de archivo de texto
1 - muestra ícono de archivo de texto
perTributario-alfanumerico-String Periodo tributario
numTicket-alfanumerico-String Número de ticket de envío
fecCargaImportaciondd/mm/yyyy,'T','hh:ii:ss'-Date
Fecha de la carga del archivo de importación, o
fecha de solicitud de generacion de archivo
fecInicioProceso-yyyy-mm-ddString
Fecha de inicio de proceso
codProceso-alfanumerico-String Código del indicador de carga masiva.
(Ver Anexo I: Indicador de carga masiva)
desProceso-alfanumerico-String Descripcion del indicador de Carga Masiva.
(Ver Anexo I: Indicador de carga masiva)
codEstadoProceso-alfanumericoString
Código de estado de envio (Ver Anexo III: Código
de estado de envío)
83
desEstadoProceso-alfanumericoString
Descripción de estado de envio (Ver Anexo III:
Código de estado de envío)
nomArchivoImportacionalfanumérico-String
Nombre del archivo de importación
detalleTicket-Object Object detalle de ticket - inicio
numTicket-alfanumerico-String Número de ticket de envío [AAAA99999999]
AAAA: Año
99: Tipo de correlativo
99999999: Número correlativo de envío
fecCargaImportaciondd/mm/yyyy-Date
Fecha de la carga del archivo de importación, o
fecha de solicitud de generacion de archivo
horaCargaImportacionhh:mm:ss'-Date
(DetalleTicket.fecCargaImportacion).- Hora de la
carga del archivo de importación, o fecha de
solicutud de generacion de archivo
codEstadoEnvio-alfanuméricoString
Código del estado de envío
desEstadoEnvio-alfanuméricoString
Descripción del estado de envío
nomArchivoReportealfanumérico-String
Nombre del archivo reporte
cntFilasvalidada-numéricoInteger
Cantidad de filas validadas o total de registros
cntCPError-numérico-Integer Cantidad de comprobantes con error
cntCPInformados-numéricoInteger
Cantidad de CP informados
detalleTicket-Object Object detalle de ticket - fin
archivoReporte-Array Array archivo reporte - inicio
codTipoAchivoReportealfanumerico-String
Código del tipo de archivo de reporte
nomArchivoReportealfanumerico-String
Nombre del archivo de reporte
nomArchivoContenidoalfanumerico-String
Nombre del archivo contenido
archivoReporte- Array Array archivo reporte - fin
registros-array-array Array de registros - fin
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/gestionprocesosmasivos/web/ma
sivo/consultaestadotickets?perIni=202301&perFin=202301&page=1&perPage=20&numTicke
t=
Headers
Body
(No aplica)
Result OK
84
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
• 1067 – El campo “perIni” no enviado o es vacío
• 1068 – Formato de perIni no cumple con el formato “yyyymm”
• 1069 – El perIni de búsqueda no debe ser mayor a la fecha actual
• 1071 – El campo “perFin” no enviado o es vacío
• 1072 – Formato de perFin no cumple con el formato “yyyymm”
• 1073 – El perFin de búsqueda no debe ser mayor a la fecha actual
• 1076 - El campo 'page' no enviado o es vacío
• 1077 - El campo “page” debe ser numérico mayor a cero
• 1079 - El campo 'perPage' no enviado o es vacío
• 1078 - El campo “per_page” debe ser numérico mayor a cero
• 1052 - Formato no permitido o no valido para el número de Ticket
• 1138 - El numTicket enviado en la URI debe ser igual al numTicket enviado en
el Body.
5.32 Servicio Web Api descargar archivo
Nombre Web
Services
Servicio Web Api descargar archivo
Descripción Permite descargar los archivos generados zipeados y particionados guardados en el
fileserver.
Solo si el resultado del campo “registros[0].codProcesos” del servicio 5.31 Servicio Web Api
consultar estado ticket es 3 o 4, se podrá hacer uso de este servicio. De otro modo, no aparecerá
el estado de envío del ticket. Además, del servicio 5.31 se utilizaran los siguientes campos:
registros[0].codProceso
registros[0].detalleTicket
registros[0].perTributario
registros[0].numTicket
registros[0].nomArchivoImportacion
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/gestionprocesosmasivos/web/ma
sivo/archivoreporte?nomArchivoReporte={nomArchivoReporte}&codTipoArchivoReporte={c
odTipoArchivoReporte}&perTributario={perTributario}&codProceso={codProceso}&numTicket={n
umTicket}&codLibro={codLibro}
85
Parámetros[URL] Param-formato-tipo Descripción
nomArchivoReporte-alfanumérico-String Nombre o ruta del archivo generado
(Parámetro de salida del servicio 5.31
Servicio Web Api consultar estado ticket:
archivoReporte.nomArchivoReporte)
(Obligatorio)
codTipoArchivoReporte-numérico-String Codigo del tipo de archivo (Parámetro de
salida del servicio 5.31 Servicio Web Api
consultar estado ticket:
archivoReporte.codTipoArchivoReporte)
Nota: Si el campo codTipoAchivoReporte
que devuelve el API 5.16 es null, colocar el
mismo valor(null)
(Obligatorio)
Nota: Si el campo codTipoAchivoReporte
que devuelve el API 5.31 es null, colocar
el mismo valor(null)
codLibro-numérico-String Codigo de libro: RCE 080000 (Obligatorio)
perTributario-alfanumérico-String Periodo tributario (Parámetro de salida del
servicio 5.31 Servicio Web Api consultar
estado ticket: perTributario) (Obligatorio)
codProceso-alfanumérico-String Código del indicador de carga masiva.
(Parámetro de salida del servicio 5.31
Servicio Web Api consultar estado ticket:
codProceso) (Obligatorio)
numTicket-alfanumérico-String Número de ticket de envío (Parámetro de
salida del servicio 5.31 Servicio Web Api
consultar estado ticket:
detalleTicket.numTicket) (Obligatorio)
Parámetros[body] No aplica
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Content-type: application/x-www-form-urlencoded
Parámetros valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: GET
Parámetros[salida] Parámetros de Salida Descripcion
Buffer-binary-binary buffer: Arreglo de bits
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/gestionprocesosmasivos/web/ma
sivo/archivoreporte?nomArchivoReporte=20100176450-CPF-202302-
01.zip&codTipoArchivoReporte=01&perTributario=202302&codProceso=1&numTicket=2024
0100000131
Headers
Body
No aplica
86
Result OK
5.33 Servicio Web Api consultar año y mes
Nombre Web
Services
Servicio Web Api que consulta años y meses de RCE.
Descripción Permite consultar los periodos (años y meses) habilitados para el contribuyente.
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/padron/web/omisos/{codLibro}/p
eriodos
Parámetros[URL] Param-formato-tipo Descripción
codLibro-alfanumérico-string Código de libro: 080000 RCE (Obligatorio)
Parámetros[body] No aplica
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Parámetros valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: GET
Parámetros[salida] Parámetros de Salida Descripción
Object- Object- Object Object inicio
numEjercicio-alfanumérico-String Año o ejericicio
desEstado-alfanumérico-String Descripcion del ejercicio
lisPeriodos-array-array Array lista de periodos - inicio
perTributario-alfanumérico-String Periodo tributario
codEstado-alfanumérico-String Código del estado del periodo tributario
desEstado-alfanumérico-String Descripcion del estado del periodo tributario
lisPeriodos-array-array Array lista de periodos - fin
Object- Object- Object Object fin
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/padron/web/omisos/080000/peri
odos
Headers
Body
(No aplica)
Result OK
87
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
• 1140 – El campo “codLibro” no enviado o es vacío
• 1161 - Código de Libro no permitido o no válido
5.34 Servicio Web Api descargar propuesta
Nombre Web
Services
Servicio Web Api descargar propuesta
Descripción Permite descargar la propuesta de RCE.
Este servicio generará un ticket para poder utilizar el servicio “5.32 Servicio Web Api
descargar archivo” y descargar la propuesta.
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/propuesta/web/propuesta/{perTribut
ario}/exportacioncomprobantepropuesta?codTipoArchivo={codTipoArchivo}&codOrigenEnvi
o={codOrigenEnvio}&fecEmisionIni={fecEmisionIni}&fecEmisionFin={fecEmisionFin}&codTipo
CDP={codTipoCDP}&numSerieCDP={numSerieCDP}&numCDP={numCDP}&codInconsistencia=
{codInconsistencia}&codCar={codCar}&numDocAdquiriente={numDocAdquiriente}&mtoDesd
e={mtoDesde}&mtoHasta={mtoHasta}
Parámetros[URL] Param-formato-tipo Descripción
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
codTipoArchivo-numérico-Integer Código del tipo de archivo
0: txt,
1: csv
(Obligatorio)
mtoDesde-Numerico-decimal128 Importe total del comprobante de pago.
Monto del rango inicial (monto total)
(Opcional: Solo si se desea filtrar los
comprobantes de pago por un rango de
montos)
mtoHasta-Numerico-decimal128 Importe total del comprobante de pago.
Monto final del rango (monto total)
(Opcional: Solo si se desea filtrar los
comprobantes de pago por un rango de
montos.)
codTipoCDP-alfanumérico-String Tipo de Comprobante de Pago o Documento.
Se puede descargar todos los comprobantes
de pado indicados en la tabla 03 del anexo 1
de la Resolución de Superintendencia 112-
88
2021/SUNAT y modificatorias (Opcional: Para
descargar comprobantes de un tipo específico)
numSerieCDP-alfanumérico-string Número de serie del comprobante de pago o
documento (Obligatorio)
numCDP-alfanumérico-string Número del comprobante de pago o
documento (Obligatorio)
codInconsistencia-numérico-String Código de tipo de inconsistencia
(Opcional: Para filtrar por comprobantes con
inconsistencias)
codCar-alfanumerico-String Numero de identificación del comprobante
(Opcional: Para hallar un comprobante en
específico)
fecEmisionIni-dd/mm/aaaa-String Fecha de emision inicio (Opcional: Para filtrar
por fecha de inicio de emisión)
fecEmisionFin-dd/mm/aaaa-String Fecha de emisión final (Opcional: Para filtrar
por fecha de fin de emisión)
numDocAdquiriente-numerico-String Numero de documento del adquiriente
(Opcional: Para buscar comprobantes
relacionados a un adquirente específico)
codOrigenEnvio-alfanumérico-string Código de origen de envío: 2 Servicio API
(Obligatorio)
Parámetros[body] No aplica.
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Content-type: application/x-www-form-urlencoded
Parámetros valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: GET
Parámetros[salida] Parámetros
de Salida
Descripcion Formato Tipo
dato
numTicket Número de ticket de envío [AAAA99999999]
AAAA: Año
99: Tipo de correlativo
99999999: Número correlativo de envío
alfanumerico String
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/propuesta/web/propuesta/202301/e
xportacioncomprobantepropuesta?codTipoArchivo=0&codOrigenEnvio=2&fecEmisionIni=202
3-06-01&fecEmisionFin=2023-06-07&codTipoCDP=01
Headers
Body
(No aplica)
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
89
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
• 1005 - El campo “perTributario” no enviado o es vacío
• 1006 - Formato de "perTributario" no cumple con el formato “yyyymm”
• 1007 - El perTributario de búsqueda no debe ser mayor a la fecha actual
• 1518 - No existen documentos para exportar
• 1059 - Código tipo de Archivo no permitido o no valido
• 1060 - Solo se permite dato numérico de 1 dígito para el codTipoArchivo
• 1061 - El campo "codTipoArchivo" es nulo o vacío
• 1007 - El perTributario de búsqueda no debe ser mayor a la fecha actual
• 1112 - El Monto Total Desde debe ser mayor o igual al Monto Total Hasta
• 1113 - Si se realiza busqueda por monto Total, se debe ingresar los campos
mtoTotalDesde y mtoTotalHasta
• 1114 - Fecha Documento Desde debe estar dentro del Periodo seleccionado
• 1116 - Fecha de documento Hasta debe ser mayor o igual al Fecha de documento
Desde
• 1011 - El campo 'codTipoCDP' no enviado o es vacío
• 1099 – El campo 'fecEmisionIni' no enviado o es vacío
• 1101 - El campo 'fecEmisionFin' no enviado o es vacío
• 1118 - Fecha Documento Desde debe estar dentro del Periodo seleccionado
• 1104 - El código de tipo de comprobante de pago enviado no es válido
• 1119 - El código de tipo de inconsistencia enviado no es válido
• 2267 - El formato del campo 'mtoDesde' no es valido
• 2268 - El formato del campo 'mtoHasta' no es valido
• 2270 - El campo 'fecEmisionIni' debe cumplir con el siguiente formato 'yyyy-mm-dd'
• 2272 - El campo 'mtoDesde' no enviado o es vacío
• 2273 - El campo 'mtoHasta' no enviado o es vacío
• 2271 - El campo 'fecEmisionFin' debe cumplir con el siguiente formato 'yyyy-mm-dd'
• 2274 - El campo 'numSerieCDP' no enviado o es vacío
• 2275 - El campo 'numCDP' no enviado o es vacío
• 2276 - El campo 'codInconsistencia' no enviado o es vacío
• 2277 - El campo 'numDocAdquiriente' no enviado o es vacío
• 1070 - No se ha encontrado información de comprobantes de pago en Periodo
Seleccionado
5.35 Servicio Web Api descargar resumen
Nombre Web
Services
Servicio Web Api descargar resumen
Descripción Permite descargar todos los tipos de resumen, propuesta, incluidos o excluidos, preliminar,
RCE generado, ajustes posteriores.
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/resumen/web/resumencomproba
ntes/{perTributario}/{codTipoResumen}/{codTipoArchivo}/exporta?codLibro={codLibro}
Parámetros[URL] Param-formato-tipo Descripción
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
codTipoResumen -alfanumérico-String Código del tipo de resumen:
-1 Resumen de propuesta
-2 Resumen de preliminar
-3 Resumen no Incluidos (V) o Excluidos(C)
-4 Resumen de registro
-5 Resumen de preliminar registrado
-6 Resumen ajustes posteriores
-7 Resumen no domiciliados
(Obligatorio)
codTipoArchivo -numérico-int Extensión del archivo a exportar
- 0: txt
- 1: csv
90
(Obligatorio)
codLibro-alfanumérico-String Código de libro: 080000 RCE (Obligatorio)
Parámetros[body] No aplica.
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Content-type: application/x-www-form-urlencoded
Parámetros Valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: GET
Parámetros[salida] Parámetros de Salida Descripcion
buffer-binary-binary buffer: Arreglo de bits
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/resumen/web/resumencomproba
ntes/202301/1/0/exporta?codLibro=080000
Headers
Body
(No aplica)
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
• 1005 - El campo “perTributario” no enviado o es vacío
• 1006 - Formato de "perTributario" no cumple con el formato “yyyymm”
• 1070 - No se ha encontrado información de comprobantes de pago en Periodo
Seleccionado
• 1140 - El campo “codLibro” no enviado o es vacío
• 1518 - No existen documentos para exportar
• 1059 - Código tipo de Archivo no permitido o no valido
• 1060 - Solo se permite dato numérico de 1 dígito para el codTipoArchivo
• 1061 - El campo "codTipoArchivo" es nulo o vacío
• 1056 - Solo se permite dato numérico de 1 dígito para el codTipoResumen
• 1057 - El campo "codTipoResumen" es nulo o vacío
91
5.36 Servicio Web Api descargar resumen inconsistencias RCE
Nombre Web
Services
Servicio Web Api descargar resumen de inconsistencias RCE
Descripción Retorna una lista, con el resumen de inconsistencias de los comprobantes de pago de
acuerdo al periodo y tipo de resumen asociado al código enviado, en formato json.
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/resumen/web/resumeninconsiste
ncias/{perTributario}?codTipoResumen={codTipoResumen}&codLibro={codLibro}
Parámetros[URL] Param-formato-tipo Descripción
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
codLibro-alfanumérico-String Código de libro: 080000 RCE (Obligatorio)
codTipoResumen-alfanumérico-String Código del tipo de resumen:
-1 Resumen de propuesta
-2 Resumen de preliminar
-3 Resumen Incluidos o Excluidos
-4 Resumen de registro
-5 Resumen de preliminar registrado
-6 Resumen ajustes posteriores
(Obligatorio)
Parámetros[body] No aplica.
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Content-type: application/x-www-form-urlencoded
Parámetros Valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: POST
Parámetros[salida] Parámetros de Salida Descripcion
Object Object - inicio
numRuc-alfanumérico-String Número de ruc
perTributario-alfanumérico-String Periodo tributario
codTipoResumen-NuméricoInteger
Código de tipo resumen
cantidad-Object Object cantidad - inicio
porcentajeRelFiscal-Numericodecimal128
Porcentaje de cantidad de comprobantes con
inconsistencias Relacionadas al Crédito Fiscal
porcentajeNoRelFiscal-Numericodecimal128
Porcentaje de cantidad de comprobantes con
inconsistencias No Relacionadas al Crédito Fiscal
porcentajeSinValidacionesNumerico-decimal128
Porcentaje de cantidad de comprobantes sin
inconsistencias
total-Numerico-decimal128 Cantidad total de comprobantes en un
determinado periodo
cantidad-Object Object cantidad - fin
monto-Object Object monto - inicio
porcentajeRelFiscal-Numericodecimal128
Porcentaje de montos de comprobantes con
inconsistencias Relacionadas al Crédito
porcentajeNoRelFiscal-Numericodecimal128
Porcentaje de montos de comprobantes con
inconsistencias No Relacionadas al Crédito Fiscal
en un determinado periodo
porcentajeSinValidacionesNumerico-decimal128
Porcentaje de montos de comprobantes sin
inconsistencias en un determinado periodo
total-Numerico-decimal128 Monto total de comprobantes en un determinado
periodo
monto-Object Object monto - fin
Object Object - fin
Evidencias URL
92
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/resumen/web/resumeninconsiste
ncias/202301?codTipoResumen=1&codLibro=080000
Headers
Body
(No aplica)
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
• 1005 - El campo “perTributario” no enviado o es vacío
• 1006 - Formato de "perTributario" no cumple con el formato “yyyymm”
• 1140 - El campo “codLibro” no enviado o es vacío
• 1518 - No existen documentos para exportar
• 1056 - Solo se permite dato numérico de 1 dígito para el codTipoResumen
• 1057 - El campo "codTipoResumen" es nulo o vacío
5.37 Servicio Web Api descargar excluidos
Nombre Web
Services
Servicio Web Api descargar excluidos
Descripción Permite descargar los comprobantes excluidos. Solo aplicable para CP Excluidos del periodo
vigente.
Este servicio generará un ticket para poder utilizar el servicio “5.32 Servicio Web Api
descargar archivo” y descargar la propuesta.
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/propuesta/web/excluidos/{perTribut
ario}/exportaexcluidos?montoDesde={montoDesde}&montoHasta={montoHasta}&fecEmisio
nIni={fecEmisionIni}&fecEmisionFin={fecEmisionFin}&numRucCliente={numRucCliente}&codC
ar={codCar}&tipoDocumento={tipoDocumento}&codInconsistencia={codInconsistencia}&nu
mSerieCDP={numSerieCDP}&numCDP={numCDP}&codTipoArchivo={codTipoArchivo}&codOri
genEnvio={codOrigenEnvio}
Parámetros[URL] Param-formato-tipo Descripción
93
perTributario -alfanumérico-String Periodo tributario (Obligatorio)
montoDesde-decimal-Decimal Monto desde (Opcional: Para filtrar los
comprobantes excluidos dentro de un rango
de montos)
montoHasta-decimal-Decimal Monto hasta (Opcional: Para filtrar los
comprobantes excluidos dentro de un rango
de montos)
fecEmisionIni-dd/mm/aaaa-String Fecha de emisión del Comprobante de Pago o
documento - Inicio (Opcional: Para filtrar por
fechas)
fecEmisionFin-dd/mm/aaaa-String Fecha de emisión del Comprobante de Pago o
documento - FIN (Opcional: Para filtrar por
fechas)
numRucCliente-alfanumérico-String Número de RUC Cliente (Opcional: Para filtrar
por cliente)
codCar-alfanumérico-String CAR SUNAT (Opcional: Para hallar el
comprobante por su CAR)
codTipoCDP-alfanumérico-String Tipo de Comprobante de Pago o Documento.
Sólo permite los comprobantes de pago 00, 01,
03, 04, 05, 06, 07, 08, 11, 12, 13, 14, 15, 16, 18,
21, 24, 25, 27, 28, 30, 32, 34, 35, 36, 37, 42, 43,
44, 45, 48, 49, 55, 56, 87, 88 (Obligatorio)
codInconsistencia-alfanumerico-String Código de inconsistencia funcional o calculada,
ejemplo:
301 - Fecha de emisión del comprobante de
pago o fecha de pago del impuesto se anota
luego de los doce meses siguientes a la fecha
de emisión del comprobante o del pago del
impuesto, según corresponda (Opcional: Para
filtrar por inconsistencias específicas)
numSerieCDP-Alfanumérico-String Número de serie del comprobante de pago o
documento (Opcional: Para un comprobante
en específico)
numCDP-Alfanumérico-String Número del comprobante de pago o
documento (Opcional: Para un comprobante
en específico)
codTipoArchivo-numerico-integer Extension del archivo a descargar (Ver Anexo
III: Extension del archivo a descargar)
(Obligatorio)
codOrigenEnvio-alfanumérico-string Código de origen de envío: 2 Servicio web
(Obligatorio)
Parámetros[body] No aplica.
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Content-type: application/x-www-form-urlencoded
Parámetros Valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: GET
Parámetros[salida] Parámetros
de Salida Descripcion Formato Tipo
dato
numTicket
Número de ticket de envío [AAAA99999999]
AAAA: Año
99: Tipo de correlativo
99999999: Número correlativo de envío
alfanumerico String
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/propuesta/web/excluidos/202301/ex
portaexcluidos?codTipoArchivo=0&codOrigenEnvio=2&fecEmisionIni=2023-01-
01&fecEmisionFin=2023-06-08&codTipoCDP=01&
94
Headers
(No aplica)
Body
(No aplica)
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
• 1005 – El campo “perTributario” no enviado o es vacío
• 1006 – Formato de perTributario no cumple con el formato “yyyymm”
• 1007 – El perTributario de búsqueda no debe ser mayor a la fecha actual
• 1112 - El Monto Total Desde debe ser mayor o igual al Monto Total Hasta
• 1117 - Si se realiza busqueda por monto Total, se debe ingresar los campos
mtoTotalDesde y mtoTotalHasta
• 1112 - El Monto Total Desde debe ser mayor o igual al Monto Total Hasta
• 1059 - Código tipo de Archivo no permitido o no valido
• 1060 - Solo se permite dato numérico de 1 dígito para el codTipoArchivo
• 1061 - El campo "codTipoArchivo" es nulo o vacío
• 1114 - Fecha Documento Desde debe estar dentro del Periodo seleccionado
• 1115 - Debe cumplir con el siguiente formato “dd/mm/yyyy”.
• 1116 - Fecha de documento Hasta debe ser mayor o igual al Fecha de
documento Desde
• 1117 - Si se realiza busqueda por Fecha Documento, se debe ingresar los
campos Fecha Documento Desde, Fecha Documento Hasta
• 1118 - Fecha Documento Desde debe estar dentro del Periodo seleccionado
• 1104 - El código de tipo de comprobante de pago enviado no es válido
• 1115 - Debe cumplir con el siguiente formato “yyyy-mm-dd”.
• 1116 - Fecha de documento Hasta debe ser mayor o igual al Fecha de
documento Desde
• 1002 – Solo se permite dato numérico de 11 dígitos para el número de RUC.
• 1003 - El RUC ingresado no existe o no es válido
• 1104 - El código de tipo de comprobante de pago enviado no es válido
5.38 Servicio Web Api eliminar comprobante no domiciliado
Nombre Web
Services
Servicio Web Api eliminar comprobante no domiciliado
Descripción Permite eliminar un comprobante del preliminar RC operaciones con no domiciliados.
Este servicio generará un ticket para poder utilizar el servicio “5.32 Servicio Web Api
descargar archivo” y descargar la propuesta.
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/libronodomiciliado/web/nodomicilia
dos/{perTributario}/eliminarcomprobantepreliminarnd
Parámetros[URL] Param-formato-tipo Descripción
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
Parámetros[body] Param-formato-tipo Descripción
noDomiciliados-array-array Array no domiciliados - inicio
codCar-alfanumérico-string Código de Anotación de Registro (CAR SUNAT)
95
(Obligatorio)
codTipoCDP-alfanumérico-string Tipo de Comprobante de Pago o Documento.
Solo permite los comprobantes de pago 00, 01, 03,
05, 06, 07, 08, 11, 12, 13, 14, 15, 16, 18, 21, 24, 25,
27, 28, 30, 32, 34, 35, 36, 37, 42, 43, 44, 45, 48, 49,
55 y 56 (Obligatorio)
numSerieCDP-alfanumérico-string Número de serie del comprobante de pago o
documento (Obligatorio)
numCDP-alfanumérico-string Número del comprobante de pago o documento
(Obligatorio)
noDomiciliados-array-array Array no domiciliados - fin
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Parámetros Valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: PUT
Parámetros[salida] Parámetros Valor
HTTP status 200
Content-Type application/json
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/libronodomiciliado/web/nodomicilia
dos/202301/eliminarcomprobantepreliminarnd
Headers
Body
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
• 1005 – El campo “perTributario” no enviado o es vacío
96
• 1006 – Formato de perTributario no cumple con el formato “yyyymm”
• 1007 – El perTributario de búsqueda no debe ser mayor a la fecha actual
• 1104 - El código de tipo de comprobante de pago enviado no es válido
• 1323 - El campo "numSerieCDP" es nulo o vacío
• 1011 - El campo “codTipoCDP” no enviado o es vacío
• 1012 - El codTipoCDP ingresado no existe o no es válido
5.39 Servicio Web Api exportar preliminar de registro de compras no
domiciliados
Nombre Web
Services
Servicio Web Api exportar preliminar del registro de compras no domiciliados
Descripción Permite descargar el preliminar del registro de compras no domiciliados.
Este servicio generará un ticket para poder utilizar el servicio “5.32 Servicio Web Api
descargar archivo” y descargar la propuesta.
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/preliminar/web/nodomiciliados/{per
Tributario}/exportapreliminarnd?codTipoArchivo={codTipoArchivo}&codOrigenEnvio={codOri
genEnvio}&mtoTotalDesde={mtoTotalDesde}&mtoTotalHasta={mtoTotalHasta}&fecEmisionIn
i={fecEmisionIni}&fecEmisionFin={fecEmisionFin}&numDocIdentidadClienteProveedor={num
DocIdentidadClienteProveedor}&numSerieCDP={numSerieCDP}&numCDP={numCDP}&codTip
oCDP={codTipoCDP}&numDocAdquiriente={numDocAdquiriente}
Parámetros[URL] Param-formato-tipo Descripción
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
codTipoArchivo-numérico-Integer Código del tipo de archivo (Ver Anexo IV:
Extension del archivo a descargar)
(Obligatorio)
mtoTotalDesde-Numerico-decimal128 Importe total del comprobante de pago.
Monto del rango inicial (monto total)
(Opcional: Para filtrar por importe mínimo)
mtoTotalHasta-Numerico-decimal128 Importe total del comprobante de pago.
Monto final del rango (monto total) (Opcional:
Para filtrar por importe máximo)
codTipoCDP-alfanumérico-String Tipo de Comprobante de Pago o Documento.
Se puede descargar todos los comprobantes
de pado indicados en la tabla 03 del anexo 1
de la Resolución de Superintendencia 112-
2021/SUNAT y modificatorias (Opcional: Para
un solo tipo de comprobante)
numSerieCDP-alfanumérico-string Número de serie del comprobante de pago o
documento (Opcional: Para filtrar
comprobantes con un numero de serie
específico)
numCDP-alfanumérico-string Número del comprobante de pago o
documento (Opcional: Para obtener un
comprobante)
fecEmisionIni-dd/mm/aaaa-String Fecha de emision inicio (Opcional: Para filtrar
por fecha)
fecEmisionFin-dd/mm/aaaa-String Fecha de emisión final (Opcional: Para filtrar
por fecha)
numDocAdquiriente-alfanuméricoString
Numero de documento del adquiriente
(Opcional: Para filtrar por un adquiriente
específico)
numDocIdentidadClienteProveedoralfanumérico-String
Número de documento de identidad del
cliente / proveedor (Opcional: Para filtrar por
cliente o proveedor)
codOrigenEnvio-alfanumérico-string Código de origen de envío: 2 Servicio web
(Obligatorio)
Parámetros[body] No aplica
97
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Content-type: application/x-www-form-urlencoded
Parámetros Valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: GET
Parámetros[salida] Parámetros
de Salida Descripcion Formato Tipo
dato
numTicket
Número de ticket de envío [AAAA99999999]
AAAA: Año
99: Tipo de correlativo
99999999: Número correlativo de envío
alfanumerico String
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/preliminar/web/nodomiciliados/2022
06/exportapreliminarnd?codTipoArchivo=0&codOrigenEnvio=2&mtoTotalDesde=1000&mtoT
otalHasta=6000&fecEmisionIni=2022-06-02&fecEmisionFin=2022-06-
18&numDocIdentidadClienteProveedor=1234567891235&numSerieCDP=E001&numCDP=21
0&codTipoCDP=00&numDocAdquiriente=1234567891235
Headers
Body
(No aplica)
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
• 1005 – El campo “perTributario” no enviado o es vacío
• 1006 – Formato de perTributario no cumple con el formato “yyyymm”
• 1007 – El perTributario de búsqueda no debe ser mayor a la fecha actual
• 1112 - El Monto Total Desde debe ser mayor o igual al Monto Total Hasta
• 1113 - Si se realiza busqueda por monto Total, se debe ingresar los campos
mtoTotalDesde y mtoTotalHasta
• 1112 - El Monto Total Desde debe ser mayor o igual al Monto Total Hasta
• 1113 - Si se realiza busqueda por monto Total, se debe ingresar los campos
mtoTotalDesde y mtoTotalHasta
• 1059 - Código tipo de Archivo no permitido o no valido
• 1060 - Solo se permite dato numérico de 1 dígito para el codTipoArchivo
• 1061 - El campo "codTipoArchivo" es nulo o vacío
• 1114 - Fecha Documento Desde debe estar dentro del Periodo seleccionado
• 1115 - Debe cumplir con el siguiente formato “dd/mm/yyyy”.
98
• 1116 - Fecha de documento Hasta debe ser mayor o igual al Fecha de
documento Desde
• 1117 - Si se realiza busqueda por Fecha Documento, se debe ingresar los
campos Fecha Documento Desde, Fecha Documento Hasta
• 1118 - Fecha Documento Desde debe estar dentro del Periodo seleccionado
• 1104 - El código de tipo de comprobante de pago enviado no es válido
• 1119 - El código de tipo de inconsistencia enviado no es válido
• 1115 - Debe cumplir con el siguiente formato “yyyy-mm-dd”.
• 1116 - Fecha de documento Hasta debe ser mayor o igual al Fecha de
documento Desde
• 1002 – Solo se permite dato numérico de 11 dígitos para el número de RUC.
• 1003 - El RUC ingresado no existe o no es válido
• 1104 - El código de tipo de comprobante de pago enviado no es válido
5.40 Servicio Web Api exportar preliminar de registro de compras
Nombre Web
Services
Servicio Web Api exportar preliminar del registro de compras electrónico
Descripción Permite descargar el preliminar del registro de compras eletrónico.
Este servicio generará un ticket para poder utilizar el servicio “5.32 Servicio Web Api
descargar archivo” y descargar la propuesta.
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/preliminar/web/registroslibros/{perT
ributario}/exportareportepreliminar?codTipoArchivo={codTipoArchivo}&codOrigenEnvio={co
dOrigenEnvio}&mtoTotalDesde={mtoTotalDesde}&mtoTotalHasta={mtoTotalHasta}&fecEmisi
onIni={fecEmisionIni}&fecEmisionFin={fecEmisionFin}&numDocIdentidadClienteProveedor={
numDocIdentidadClienteProveedor}&numSerieCDP={numSerieCDP}&numCDP={numCDP}&co
dTipoCDP={codTipoCDP}&numDocAdquiriente={numDocAdquiriente}
Parámetros[URL] Param-formato-tipo Descripción
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
codTipoArchivo-numérico-Integer Código del tipo de archivo (Ver Anexo IV:
Extension del archivo a descargar)
(Obligatorio)
mtoTotalDesde-Numerico-decimal128 Importe total del comprobante de pago.
Monto del rango inicial (monto total)
(Opcional: Para filtrar por importe mínimo)
mtoTotalHasta-Numerico-decimal128 Importe total del comprobante de pago.
Monto final del rango (monto total) (Opcional:
Para filtrar por importe máximo)
codTipoCDP-alfanumérico-String Tipo de Comprobante de Pago o Documento.
Se puede descargar todos los comprobantes
de pado indicados en la tabla 03 del anexo 1
de la Resolución de Superintendencia 112-
2021/SUNAT y modificatorias (Opcional: Para
un solo tipo de comprobante)
numSerieCDP-alfanumérico-string Número de serie del comprobante de pago o
documento (Opcional: Para filtrar
comprobantes con un numero de serie
específico)
numCDP-alfanumérico-string Número del comprobante de pago o
documento (Opcional: Para obtener un
comprobante)
fecEmisionIni-dd/mm/aaaa-String Fecha de emision inicio (Opcional: Para filtrar
por fecha)
fecEmisionFin-dd/mm/aaaa-String Fecha de emisión final (Opcional: Para filtrar
por fecha)
numDocAdquiriente-alfanuméricoString
Numero de documento del adquiriente
(Opcional: Para filtrar por un adquiriente
específico)
99
numDocIdentidadClienteProveedoralfanumérico-String
Número de documento de identidad del
cliente / proveedor (Opcional: Para filtrar por
cliente o proveedor)
codOrigenEnvio-alfanumérico-string Código de origen de envío: 2 Servicio web
(Obligatorio)
Parámetros[body] No aplica
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Content-type: application/x-www-form-urlencoded
Parámetros Valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: GET
Parámetros[salida] Parámetros
de Salida Descripcion Formato Tipo
dato
numTicket
Número de ticket de envío [AAAA99999999]
AAAA: Año
99: Tipo de correlativo
99999999: Número correlativo de envío
alfanumerico String
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/preliminar/web/registroslibros/2022
06/exportareportepreliminar?codTipoArchivo=0&codOrigenEnvio=2&
Headers
Body
(No aplica)
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
• 1005 – El campo “perTributario” no enviado o es vacío
• 1006 – Formato de perTributario no cumple con el formato “yyyymm”
• 1007 – El perTributario de búsqueda no debe ser mayor a la fecha actual
• 1112 - El Monto Total Desde debe ser mayor o igual al Monto Total Hasta
• 1113 - Si se realiza busqueda por monto Total, se debe ingresar los campos
mtoTotalDesde y mtoTotalHasta
• 1112 - El Monto Total Desde debe ser mayor o igual al Monto Total Hasta
• 1113 - Si se realiza busqueda por monto Total, se debe ingresar los campos
mtoTotalDesde y mtoTotalHasta
• 1059 - Código tipo de Archivo no permitido o no valido
• 1060 - Solo se permite dato numérico de 1 dígito para el codTipoArchivo
100
• 1061 - El campo "codTipoArchivo" es nulo o vacío
• 1114 - Fecha Documento Desde debe estar dentro del Periodo seleccionado
• 1115 - Debe cumplir con el siguiente formato “dd/mm/yyyy”.
• 1116 - Fecha de documento Hasta debe ser mayor o igual al Fecha de
documento Desde
• 1117 - Si se realiza busqueda por Fecha Documento, se debe ingresar los
campos Fecha Documento Desde, Fecha Documento Hasta
• 1118 - Fecha Documento Desde debe estar dentro del Periodo seleccionado
• 1104 - El código de tipo de comprobante de pago enviado no es válido
• 1119 - El código de tipo de inconsistencia enviado no es válido
• 1002 – Solo se permite dato numérico de 11 dígitos para el número de RUC.
• 1003 - El RUC ingresado no existe o no es válido
• 1104 - El código de tipo de comprobante de pago enviado no es válido
5.41 Servicio Web Api descargar reporte de casillas
Nombre Web
Services
Servicio Web Api reporte de casillas
Descripción Permite descargar todos los tipos de resumen, propuesta, incluidos o excluidos, preliminar,
rce generado, ajustes posteriores.
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/casillas/e/casillaspropuestas/{per
Tributario}/reporte/{tipoReporte}/{tipoDescarga}
Parámetros[URL] Param-formato-tipo Descripción
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
tipoReporte-alfanumérico-String Tipo de reporte:
1. Preliminar
2. Comparada
(Obligatorio)
tipoDescarga-alfanumérico-String Código de tipo de descarga (Ver Anexo III:
Extension del archivo a descargar)
(Obligatorio)
Parámetros[body] No aplica.
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Content-type: application/x-www-form-urlencoded
Parámetros Valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: GET
Parámetros[salida] No aplica
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/casillas/e/casillaspropuestas/202
201/reporte/1/txt
Headers
101
Body
(No aplica)
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
• 1005 – El campo “perTributario” no enviado o es vacío
• 1006 – Formato de perTributario no cumple con el formato “yyyymm”
• 1007 – El perTributario de búsqueda no debe ser mayor a la fecha actual
• 1070 – No se ha encontrado información de comprobantes de pago en Periodo
Seleccionado
5.42 Servicio Web Api descargar inconsistencias en registros preliminar
registrado
Nombre Web
Services
Servicio Web Api descargar inconsistencias en registros preliminar registrado
Descripción Permite descargar las inconsistencias de los registros de preliminar registrado
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/casillas/inconsistenciaslibros/{per
Tributario}/reporteinconsistencia/{codTipoArchivo}?cntlimite={cntlimite}
Parámetros[URL] Param-formato-tipo Descripción
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
codTipoArchivo-numerico-integer Extension del archivo a descargar (Ver
Anexo III: Extension del archivo a
descargar) (Obligatorio)
cntlimite-numérico-int Cantidad de registros para validar el top
(Obligatorio)
Parámetros[body] No aplica.
Parámetros[header] Descripción:
102
Content-type: tipo de contenido a enviar
Valores:
Content-type: application/x-www-form-urlencoded
Parámetros Valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: GET
Parámetros[salida] Parámetros de Salida Descripcion
Buffer- binary-binary buffer: Arreglo de bits
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/casillas/inconsistenciaslibros/202
205/reporteinconsistencia/xls?cntlimite=20
Headers
Body
(No aplica)
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
• 1005 – El campo “perTributario” no enviado o es vacío
• 1006 – Formato de perTributario no cumple con el formato “yyyymm”
• 1007 – El perTributario de búsqueda no debe ser mayor a la fecha actual
• 1059 - Código tipo de Archivo no permitido o no valido
• 1060 - Solo se permite dato numérico de 1 dígito para el codTipoArchivo
• 1061 - El campo "codTipoArchivo" es nulo o vacío
• 1070 - No se ha encontrado información de comprobantes de pago en Periodo
Seleccionado
5.43 Servicio Web Api descargar inconsistencias por montos totales
103
Nombre Web
Services
Servicio Web Api descargar inconsistencias por montos totales
Descripción Permite exportar las inconsistencias por montos totales.
Este servicio generará un ticket para poder utilizar el servicio “5.32 Servicio Web Api
descargar archivo” y descargar la propuesta.
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/inconsistencias/web/periodoinconsis
tencias/{perTributario}/exportarinconsistenciasportotales?codTipoArchivo={codTipoArchivo}
&codLibro={codLibro}
Parámetros[URL] Param-formato-tipo Descripción
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
codTipoArchivo-numérico-int Código del tipo de archivo a descargar (Ver Anexo III:
Extension del archivo a descargar) (Obligatorio)
codLibro-alfanumérico-String Código de libro: 080000 RCE (Obligatorio)
Parámetros[body] No aplica.
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Content-type: application/x-www-form-urlencoded
Parámetros Valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: GET
Parámetros[salida] Parámetros
de Salida Descripcion Formato Tipo
dato
numTicket
Número de ticket de envío [AAAA99999999]
AAAA: Año
99: Tipo de correlativo
99999999: Número correlativo de envío
alfanumerico String
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/inconsistencias/web/periodoinconsis
tencias/202201/exportarinconsistenciasportotales?codOrigenEnvio=2&codTipoArchivo=0&co
dLibro=080000
Headers
Body
(No aplica)
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
• 1005 – El campo “perTributario” no enviado o es vacío
• 1006 – Formato de "perTributario" no cumple con el formato “yyyymm”
104
• 1059 - Código tipo de Archivo no permitido o no valido
• 1060 - Solo se permite dato numérico de 1 dígito para el codTipoArchivo
• 1061 - El campo "codTipoArchivo" es nulo o vacío
• 1140 - El campo “codLibro” no enviado o es vacío
5.44 Servicio Web Api descargar inconsistencias por comprobante pago
Nombre Web
Services
Servicio Web Api descargar inconsistencias por comprobantes de pago
Descripción Permite exportar las inconsistencias por comprobantes de pago.
Este servicio generará un ticket para poder utilizar el servicio “5.32 Servicio Web Api
descargar archivo” y descargar la propuesta.
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/inconsistencias/web/periodoinconsis
tencias/{perTributario}/{codLibro}/exportarinconsistenciasporcomprobantes?fecEmisionInici
o={fecEmisionInicio}&fecEmisionFin={fecEmisionFin}&codInconsistencia={codInconsistencia}
&numDocIdentidadClienteProveedor={numDocIdentidadClienteProveedor}&codTipoCDP={co
dTipoCDP}&numSerieCDP={numSerieCDP}&numCDP={numCDP}&codTipoArchivo={codTipoAr
chivo}&mtoTotalDesde={mtoTotalDesde}&mtoTotalHasta={mtoTotalHasta}&codEstado={cod
Estado}&codOrigenEnvio={codOrigenEnvio}
Parámetros[URL] Param-formato-tipo Descripción
perTributario-alfanumerico-String Periodo tributario (Obligatorio)
codLibro-alfanumerico-String Código de libro: 080000 RCE (Obligatorio)
fecEmisionIni-dd/mm/aaaa-String Fecha de emisión del Comprobante de Pago o
documento – Inicio (Opcional: Para filtrar por
fecha de incio)
fecEmisionFin-dd/mm/aaaa-String Fecha de emisión del Comprobante de Pago o
documento - FIN (Opcional: Para filtrar por
fecha de fin)
codInconsistencia-alfanumerico-String Código de inconsistencia funcional o calculada,
ejemplo:
301 - Fecha de emisión del comprobante de
pago o fecha de pago del impuesto se anota
luego de los doce meses siguientes a la fecha
de emisión del comprobante o del pago del
impuesto, según corresponda. (Opcional: Para
filtrar por inconsistencia específica)
numDocIdentidadClienteProveedorAlfanumérico-String
Número de RUC o Documento de Identidad del
cliente (Opcional: Para filtrar por cliente o
proveedor)
codTipoCDP-Alfanumérico-String Tipo de Comprobante de Pago o Documento.
Solo permite los comprobantes de pago 00, 01,
03, 05, 06, 07, 08, 11, 12, 13, 14, 15, 16, 18, 21,
24, 25, 27, 28, 30, 32, 34, 35, 36, 37, 42, 43, 44,
45, 48, 49, 55 y 56 (Opcional: Para filtrar por
comprobante)
numSerieCDP-Alfanumérico-String Número de serie del comprobante de pago o
documento (Opcional: Para filtrar por
comprobante)
numCDP-Alfanumérico-String Número del comprobante de pago o
documento (Opcional: Para filtrar por
comprobante)
codTipoArchivo-númerico-int Código del tipo de archivo a descargar
- 0: txt
- 1: excel
(Obligatorio)
mtoTotalDesde-Numerico-decimal128 Importe total del comprobante de pago
(Opcional: Para filtrar por importe mínimo)
mtoTotalHasta-Numerico-decimal128 Importe total del comprobante de pago
(Opcional: Para filtrar por importe máximo)
105
codEstado-alfanumerico-string Código de estado (Opcional: Para filtrar
comprobantes por su estado)
codOrigenEnvio-alfanumérico-string Código de origen de envío: 2 Servicio web
(Obligatorio)
Parámetros[body] No aplica.
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Content-type: application/x-www-form-urlencoded
Parámetros Valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: GET
Parámetros[salida] Parámetros
de Salida Descripcion Formato Tipo
dato
numTicket
Número de ticket de envío [AAAA99999999]
AAAA: Año
99: Tipo de correlativo
99999999: Número correlativo de envío
alfanumerico String
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/inconsistencias/web/periodoinconsis
tencias/202201/080000/exportarinconsistenciasporcomprobantes?codOrigenEnvio=2&codTi
poArchivo=0
Headers
Body
(No aplica)
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
• 1005 – El campo “perTributario” no enviado o es vacío
• 1006 – Formato de perTributario no cumple con el formato “yyyymm”
• 1007 – El perTributario de búsqueda no debe ser mayor a la fecha actual
• 1098 - Formato de fecha de emisión inicial no permitido o no válido para la
fecha
• 1100 - Formato de fecha de emisión final no permitido o no válido para la
fecha
• 1102 - La Fecha de Emisión Final debe ser mayor o igual a la Fecha de Emisión
Inicial
• 1422 - Se debe seleccionar una inconsistencia
• 1324- El campo "numDocIdentidadClienteProveedor" es nulo o vacío
106
• 1345- El campo "numDocIdentidadClienteProveedor", Solo números y letras
en mayusculas o minusculas de la A a la Z con un tamaño de 15 caracteres
• 1104 - El código de tipo de comprobante de pago enviado no es válido
• 1140 - El campo “codLibro” no enviado o es vacío
• 1161 - Código de libro no existe
• 1112 - El Monto Total Desde debe ser mayor o igual al Monto Total Hasta
• 1113 - Si se realiza busqueda por monto Total, se debe ingresar los campos
mtoTotalDesde y mtoTotalHasta
• 2303 - No se ha encontrado información de comprobantes de pago en Periodo
Seleccionado para los filtros ingresados.
5.45 Servicio Web Api descargar ajustes posteriores
Nombre Web
Services
Servicio Web Api descargar ajustes posteriores
Descripción Permite exportar los ajustes posteriores del RCE, en caso no se haya cargado ningún archivo
entonces descarga la propuesta informativa de ajustes posteriores de la SUNAT.
Este servicio generará un ticket para poder utilizar el servicio “5.32 Servicio Web Api
descargar archivo” y descargar la propuesta.
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/ajustesposteriores/web/comprobant
esajuspost/{perTributario}/exportaajustesposterioresrc?codTipoArchivo={codTipoArchivo}&
&codOrigenEnvio={codOrigenEnvio}
Parámetros[URL] Param-formato-tipo Descripción
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
codTipoArchivo-numérico-int Código del tipo de archivo a descargar
0: txt
1: csv
(Ver Anexo III: Extension del archivo a
descargar) (Obligatorio)
codOrigenEnvio-alfanumérico-string Código de origen de envío: 2 Servicio web
(Obligatorio)
Parámetros[body] No aplica.
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Content-type: application/x-www-form-urlencoded
Parámetros Valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: GET
Parámetros[salida] Parámetros de
Salida Descripcion Formato Tipo
dato
bytesArchivo Datos binarios del archivo alfanumerico String
nombreArchivo Nombre del archivo generado alfanumerico String
desMimeType Tipo de MIME del archivo alfanumerico String
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/ajustesposteriores/web/comprobant
esajuspost/202301/exportaajustesposterioresrc?codTipoArchivo=0&codOrigenEnvio=2
Headers
107
Body
(No aplica)
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
• 1005 – El campo “perTributario” no enviado o es vacío
• 1006 – Formato de perTributario no cumple con el formato “yyyymm”
• 1007 – El perTributario de búsqueda no debe ser mayor a la fecha actual
• 1028 - El campo 'codOrigenEnvio' no enviado o es vacio.
• 1059 - Código tipo de Archivo no permitido o no valido
• 1060 - Solo se permite dato numérico de 1 dígito para el codTipoArchivo
• 1061 - El campo "codTipoArchivo" es nulo o vacío
5.46 Servicio Web Api descargar ajustes posteriores no domiciliados
Nombre Web
Services
Servicio Web Api descargar ajustes posteriores de ND
Descripción Permite exportar los ajustes posteriores de operaciones con ND en caso se hayan cargado
ajustes por parte del generador.
Este servicio generará un ticket para poder utilizar el servicio “5.32 Servicio Web Api
descargar archivo” y descargar la propuesta.
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/ajustesposteriores/web/comprobant
esajuspost/{perTributario}/exportaajustesposterioresrcnd?codTipoArchivo={codTipoArchivo}
Parámetros[URL] Param-formato-tipo Descripción
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
codTipoArchivo-numérico-int Código del tipo de archivo a descargar
(Ver Anexo III: Extension del archivo a
descargar) (Obligatorio)
codOrigenEnvio-alfanumérico-string Código de origen de envío: 2 Servicio
web (Obligatorio)
Parámetros[body] No aplica.
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Content-type: application/x-www-form-urlencoded
Parámetros Valor
108
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: GET
Parámetros[salida] Parámetros de
Salida Descripcion Formato Tipo
dato
bytesArchivo Datos binarios del archivo alfanumerico String
nombreArchivo Nombre del archivo generado alfanumerico String
desMimeType Tipo de MIME del archivo alfanumerico String
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/ajustesposteriores/web/comprobant
esajuspost/202301/exportarajustesposterioresrcnd?codTipoArchivo=1
Headers
Body
(No aplica)
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
• 1005 – El campo “perTributario” no enviado o es vacío
• 1006 – Formato de perTributario no cumple con el formato “yyyymm”
• 1007 – El perTributario de búsqueda no debe ser mayor a la fecha actual
• 1059 - Código tipo de Archivo no permitido o no valido
• 1060 - Solo se permite dato numérico de 1 dígito para el codTipoArchivo
• 1061 - El campo "codTipoArchivo" es nulo o vacío
5.47 Servicio Web Api descargar ajustes posteriores de periodos
anteriores
Nombre Web
Services
Servicio Web Api descargar ajustes posteriores de periodos anteriores
Descripción Permite exportar los ajustes posteriores de periodos anteriores del RC en caso se hayan
cargado ajustes por parte del generador.
Este servicio generará un ticket para poder utilizar el servicio “5.32 Servicio Web Api
descargar archivo” y descargar la propuesta.
109
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/ajustesposteriores/web/comprobant
esajuspost/{perTributario}/exportaajustesposterioresparc?codTipoArchivo={codTipoArchivo}
&indAjustePosteriorPle={indAjustePosteriorPle}&codOrigenEnvio={codOrigenEnvio}
Parámetros[URL] Param-formato-tipo Descripción
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
codOrigenEnvio-alfanumérico-string Código de origen de envío: 2 Servicio web
(Obligatorio)
codTipoArchivo-numérico-int Código del tipo de archivo a descargar (Ver
Anexo III: Extension del archivo a
descargar) (Obligatorio)
indAjustePosteriorPle-alfanumérico-String Tipo de ajuste posteriores de periodos
anteriores al SIRE:
- G: General
- S: Simplificado
(Obligatorio)
Parámetros[body] No aplica.
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Content-type: application/x-www-form-urlencoded
Parámetros Valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: POST
Parámetros[salida] Parámetros de
Salida Descripcion Formato Tipo
dato
bytesArchivo Datos binarios del archivo alfanumerico String
nombreArchivo Nombre del archivo generado alfanumerico String
desMimeType Tipo de MIME del archivo alfanumerico String
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/ajustesposteriores/web/comprobant
esajuspost/202301/exportaajustesposterioresparc?codTipoArchivo=0&indAjustePosteriorPle
=G&codOrigenEnvio=2
Headers
Body
(No aplica)
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
110
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
• 1005 – El campo “perTributario” no enviado o es vacío
• 1006 – Formato de perTributario no cumple con el formato “yyyymm”
• 1007 – El perTributario de búsqueda no debe ser mayor a la fecha actual
• 1059 - Código tipo de Archivo no permitido o no valido
• 1060 - Solo se permite dato numérico de 1 dígito para el codTipoArchivo
• 1061 - El campo "codTipoArchivo" es nulo o vacío
• 1028 - El campo "codOrigenEnvio" no enviado o es vacio.
5.48 Servicio Web Api descargar ajustes posteriores de periodos
anteriores no domiciliados
Nombre Web
Services
Servicio Web Api descargar ajustes posteriores de periodos anteriores de ND
Descripción Permite exportar los ajustes posteriores de periodos anteriores de operaciones con sujetos
no domiciliados en caso se hayan cargado ajustes por parte del generador.
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/ajustesposteriores/web/comprobant
esajuspost/{perTributario}/exportaajustesposterioresparcnd?codTipoArchivo={codTipoArchiv
o}&codOrigenEnvio={codOrigenEnvio}
Parámetros[URL] Param-formato-tipo Descripción
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
codOrigenEnvio-alfanumérico-string Código de origen de envío: 2 Servicio web
(Obligatorio)
codTipoArchivo-numérico-int Código del tipo de archivo a descargar (Ver
Anexo III: Extension del archivo a descargar)
(Obligatorio)
Parámetros[body] No aplica.
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Content-type: application/x-www-form-urlencoded
Parámetros Valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: GET
Parámetros[salida] Parámetros de
Salida Descripcion Formato Tipo
dato
bytesArchivo Datos binarios del archivo alfanumerico String
nombreArchivo Nombre del archivo generado alfanumerico String
desMimeType Tipo de MIME del archivo alfanumerico String
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/ajustesposteriores/web/co
mprobantesajuspost/202301/exportaajustesposterioresparcnd?codTipoArchivo=1
&codOrigenEnvio=2
Headers
111
Body
(No aplica)
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
• 1005 – El campo “perTributario” no enviado o es vacío
• 1006 – Formato de perTributario no cumple con el formato “yyyymm”
• 1007 – El perTributario de búsqueda no debe ser mayor a la fecha actual
• 1059 - Código tipo de Archivo no permitido o no valido
• 1060 - Solo se permite dato numérico de 1 dígito para el codTipoArchivo
• 1061 - El campo "codTipoArchivo" es nulo o vacío
• 1028 - El campo "codOrigenEnvio" no enviado o es vacio.
• 1070 - No se ha encontrado información de comprobantes de pago en Periodo
Seleccionado
5.49 Servicio Web Api descargar constancia de recepción
Nombre Web
Services
Servicio Web Api descargar constancia de recepción
Descripción Permite descargar la constancia de recepción del RCE.
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/gestionlibro/web/registroslibros/
constancia/constanciarecepcion?nomConstanciaRecepcion={nomConstanciaRecepcion}
Parámetros[URL] Param-formato-tipo Descripción
nomConstanciaRecepcion-alfanumérico-string Nombre o ruta del archivo generado
(Obligatorio)
Parámetros[body] No aplica.
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Content-type: application/x-www-form-urlencoded
Parámetros Valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: GET
112
Parámetros[salida] Parámetros de Salida Descripcion
archivoPdf-Bytes Arreglo de Bytes
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/gestionlibro/web/registroslibros/
constancia/constanciarecepcion?nomConstanciaRecepcion=LE2019592375320221100080400
011022.pdf
Headers
Body
(No aplica)
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
• 1080 – El campo 'nomConstanciaRecepcion' no enviado o es vacío
5.50 Servicio Web Api descargar reporte consolidado registro por
periodo
Nombre Web
Services
Servicio Web Api descargar reporte consolidado de registros por período
Descripción Permite descargar el reporte consolidado de registro por periodo.
Este servicio generará un ticket para poder utilizar el servicio “5.32 Servicio Web Api
descargar archivo” y descargar la propuesta.
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/ajustesposteriores/web/ajustesposte
riores/{perTributario}/solicitardescarga?codTipoArchivo={codTipoArchivo}&codMoneda={cod
Moneda}&codProceso={codProceso}&codOrigen={codOrigenEnvio}&lisPeriodos={lisPeriodos}
Parámetros[URL] Param-formato-tipo Descripción
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
codTipoArchivo-numérico-int Código del tipo de archivo a descargar (Ver
Anexo III: Extension del archivo a descargar)
113
(Obligatorio)
codMoneda-alfanumérico-String Se considerará la moneda en que se emitió el
comprobante de pago
codProceso-alfanumérico-String Código de proceso
00 RCE No Domiciliados informado
01 RCE Cuando acepta la propuesta
02 RCE Cuando reemplaza la propuesta
(Obligatorio)
codOrigen-alfanumérico-string Código de origen de envío: 2 Servicio web
(Obligatorio)
lisPeriodos-alfanumérico-String Lista de periodos (Obligatorio)
Parámetros[body] No aplica.
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Content-type: application/x-www-form-urlencoded
Parámetros Valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: GET
Parámetros[salida] Parámetros
de Salida Descripcion Formato Tipo
dato
numTicket
Número de ticket de envío [AAAA99999999]
AAAA: Año
99: Tipo de correlativo
99999999: Número correlativo de envío
alfanumerico String
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/ajustesposteriores/web/ajustesposte
riores/202212/solicitardescarga?codTipoArchivo=0&codMoneda=PEN&codProceso=69&cod
Origen=1&lisPeriodos=202211
Headers
Body
(No aplica)
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
• 1005 – El campo “perTributario” no enviado o es vacío
• 1006 – Formato de perTributario no cumple con el formato “yyyymm”
• 1007 – El perTributario de búsqueda no debe ser mayor a la fecha actual
• 1059 – Código tipo de Archivo no permitido o no valido
114
• 1060 - Solo se permite dato numérico de 1 dígito para el codTipoArchivo
• 1061 - El campo "codTipoArchivo" es nulo o vacío
• 1028 – El campo “codOrigenEnvio” no enviado o es vacío
• 1029 – Código tipo de Origen de Envio no permitido o no valido
• 1030 - Solo se permite dato numérico de 1 dígito para el codOrigenEnvio
• 1138 - El campo "codProceso" es nulo o vacío
• 1139 – Código de Proceso no permitido o no valido
5.51 Servicio Web Api descargar RCE por periodo
Nombre Web
Services
Servicio Web Api descargar RCE por periodo
Descripción Permite descargar el reporte consolidado de registro por periodo.
Este servicio generará un ticket para poder utilizar el servicio “5.32 Servicio Web Api
descargar archivo” y descargar la propuesta.
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/ajustesposteriores/web/ajustesposte
riores/{perTributario}/solicitardescarga?codTipoArchivo={codTipoArchivo}&codMoneda={cod
Moneda}&codProceso={codProceso}&codOrigen={codOrigen}&lisPeriodos={lisPeriodos}
Parámetros[URL] Param-formato-tipo Descripción
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
codTipoArchivo-numérico-int Código del tipo de archivo a descargar
- 0: txt
- 1: csv
(Obligatorio)
codMoneda-alfanumérico-String Se considerará la moneda en que se emitió el
comprobante de pago
codProceso-alfanumérico-String Código de proceso
00 RCE No Domiciliados informado
01 RCE Cuando acepta la propuesta
02 RCE Cuando reemplaza la propuesta
(Obligatorio)
codOrigen-alfanumérico-String Código de origen de envío: 2 Servicio web
(Obligatorio)
lisPeriodos-alfanumérico-String Lista de periodos (Obligatorio)
Parámetros[body] No aplica.
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Content-type: application/x-www-form-urlencoded
Parámetros Valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: GET
Parámetros[salida] Parámetros
de Salida Descripcion Formato Tipo
dato
numTicket
Número de ticket de envío [AAAA99999999]
AAAA: Año
99: Tipo de correlativo
99999999: Número correlativo de envío
alfanumerico String
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/ajustesposteriores/web/ajustesposte
riores/202305/solicitardescarga?codTipoArchivo=0&codMoneda=PEN&codProceso=70&cod
Origen=1&lisPeriodos=202212
Headers
115
Body
(No aplica)
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
• 1005 – El campo “perTributario” no enviado o es vacío
• 1006 – Formato de perTributario no cumple con el formato “yyyymm”
• 1007 – El perTributario de búsqueda no debe ser mayor a la fecha actual
• 1059 – Código tipo de Archivo no permitido o no valido
• 1060 - Solo se permite dato numérico de 1 dígito para el codTipoArchivo
• 1061 - El campo "codTipoArchivo" es nulo o vacío
• 1028 – El campo “codOrigen” no enviado o es vacío
• 1029 – Código tipo de Origen de Envio no permitido o no valido
• 1030 - Solo se permite dato numérico de 1 dígito para el codOrigenEnvio
• 1138 - El campo "codProceso" es nulo o vacío
• 1139 – Código de Proceso no permitido o no valido
5.52 Servicio Web Api descargar reporte inconsistencias por periodo
Nombre Web
Services
Servicio Web Api descargar inconsistencias por periodo
Descripción Permite descargar las inconsistencias por periodo.
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/gestionconsultas/web/registrolibr
o/archivoreporte?nomArchivo={nomArchivo}&codTipoArchivoReporte={codTipoArchivoRepo
rte}&codOrigen={codOrigen}
Parámetros[URL] Param-formato-tipo Descripción
nomArchivo Nombre del archivo utilizado para la descarga
o nombre de archivo generado (Obligatorio)
codTipoArchivoReporte-numérico-int Extension del archivo a descargar (Ver Anexo
III: Extension del archivo a descargar)
(Obligatorio)
codOrigen-alfanumérico-string Código de origen de envío: 2 Servicio web
(Obligatorio)
Parámetros[body] No aplica.
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Content-type: application/x-www-form-urlencoded
Parámetros Valor
Content-Type application/json
116
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: GET
Parámetros[salida] Parámetros de Salida Descripcion
buffer-binary-binary buffer: Arreglo de bits
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/gestionconsultas/web/registrolibr
o/archivoreporte?nomArchivo=LE201001764502022120008040002PCW2.zip&codTipoArchiv
oReporte=00&codOrigen=1
Headers
Body
(No aplica)
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
• 1006 – Formato de perTributario no cumple con el formato “yyyymm”
• 1007 – El perTributario de búsqueda no debe ser mayor a la fecha actual
• 1059 - Código tipo de Archivo no permitido o no valido
• 1060 - Solo se permite dato numérico de 1 dígito para el codTipoArchivo
• 1061 - El campo "codTipoArchivo" es nulo o vacío
• 1028 - El campo “codOrigen” no enviado o es vacío
• 1029 - Código tipo de Origen de Envio no permitido o no valido
• 1030 - Solo se permite dato numérico de 1 dígito para el codOrigenEnvio
• 2278 - El campo 'codTipoArchivoReporte' no enviado o es vacío
5.53 Servicio Web Api descargar reporte CAR
Nombre Web
Services
Servicio Web Api descargar reporte de CAR
Descripción Permite descargar la lista de CAR dependiendo de la fase en que se encuentre.
Este servicio generará un ticket para poder utilizar el servicio “5.32 Servicio Web Api
descargar archivo” y descargar la propuesta.
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/gestionlibro/web/comprobantesli
bros/{perTributario}/reportecar?codOrigenEnvio={codOrigenEnvio}&codLibro={codLibro}&co
dFase={codFase}
Parámetros[URL] Param-formato-tipo Descripción
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
codLibro-alfanumérico-String Código de libro: 080000 RCE (Obligatorio)
117
codFase-alfanumérico-String Código de fase (Obligatorio)
codOrigen-alfanumérico-string Código de origen de envío: 2 Servicio web
(Obligatorio)
Parámetros[body] No aplica.
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Content-type: application/x-www-form-urlencoded
Parámetros Valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: GET
Parámetros[salida] Parámetros
de Salida Descripcion Formato Tipo
dato
numTicket
Número de ticket de envío [AAAA99999999]
AAAA: Año
99: Tipo de correlativo
99999999: Número correlativo de envío
alfanumerico String
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/gestionlibro/web/comprobantesli
bros/202302/reportecar?codOrigenEnvio=2&codLibro=080000&codFase=1
Headers
Body
(No aplica)
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
• 1005 – El campo “perTributario” no enviado o es vacío
• 1006 – Formato de perTributario no cumple con el formato “yyyymm”
• 1007 – El perTributario de búsqueda no debe ser mayor a la fecha actual
• 2002 - Solo se permite valor númerico para el campo "codFase"
• 2003 - El valor enviado para el campo "codFase" no es el correcto.
• 1140 - El campo “codLibro” no enviado o es vacío
• 1028 - El campo “codOrigen” no enviado o es vacío
• 1029 - Código tipo de Origen de Envio no permitido o no valido
• 1030 - Solo se permite dato numérico de 1 dígito para el codOrigenEnvio
118
5.54 Servicio Web Api descargar reporte estadístico compras por
proveedor por periodo
Nombre Web
Services
Servicio Web Api descargar reporte estadístico compras por proveedor por periodo
Descripción Permite exportar resumen estadístico de compras por proveedor por periodo (Razón social,
Monto, Porcentaje)
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/estadistica/web/resumenestadisti
co/exporta?numRuc={numRuc}&numRuc={perTributario}&fechaini={fechaini}&?fechafin={fec
hafin}&numRucproveedor={numRucproveedor}&odTipoCDP={codTipoCDP}&codTipoArchivo=
{codTipoArchivo}&codTipoReporte={codTipoReporte}&codLibro={codLibro}
Parámetros[URL] Param-formato-tipo Descripción
numRuc-alfanumérico-String Número de RUC del generador (Obligatorio)
perTributario-numérico-int Periodo tributario (Obligatorio)
fechaIni-dd/mm/yyyy-date Fecha emision desde del comprobante de pago
(Opcional: Para filtrar por fecha de inicio)
fechaFin-dd/mm/yyyy-date Fecha emision hasta del comprobante de pago
(Opcional: Para filtrar por fecha de fin)
numRucProveedor-alfanumericoalfanumerico
Numero del RUC o Documento de identidad
del proveedor (Opcional: Filtrar por proveedor)
codTipoCDP-alfanumerico-alfanumerico Tipo de comprobante (Opcional: Para filtrar
por comprobante)
codTipoArchivo-numérico-Integer Extension del archivo a descargar
- 0: txt
- 1: csv
(Obligatorio)
codTipoReporte-numérico-Integer Código de tipo de reporte: 1 Reporte
montos/proveedor (Obligatorio)
codLibro-alfanumérico-String Código de libro: 080000 RCE (Obligatorio)
Parámetros[body] No aplica.
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Content-type: application/x-www-form-urlencoded
Parámetros Valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: GET
Parámetros[salida] Parámetros Valor
HTTP status 200
Content-Type application/json
ContentDisposition
El sistema descarga el archivo con el siguiente formato de nombre:
1-REPORTE MONTOS/ PROVEEDOR
(estadisticaPorProveedor.<extensión>)
Razón Social|Monto|Porcentaje
Los constructores SAC|127 000|16%
El ingeniero perez|86 999|9%
El consorcio unido|75 000|7%
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/estadistica/web/resumenestadisti
co/exporta?numRuc=20195923753&perTributario=202203&codTipoArchivo=0&codTipoRepo
rte=1&codLibro=080000
Headers
119
Body
(No aplica)
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
• 1005 – El campo “perTributario” no enviado o es vacío
• 1006 – Formato de perTributario no cumple con el formato “yyyymm”
• 1007 – El perTributario de búsqueda no debe ser mayor a la fecha actual
• 1059 – Código tipo de Archivo no permitido o no valido
• 1060 - Solo se permite dato numérico de 1 dígito para el codTipoArchivo
• 1061 - El campo "codTipoArchivo" es nulo o vacío
• 1333 - El campo "codTipoReporte" es nulo o vacío
• 1334 - El campo "codTipoReporte" solo admite valores: 1, 2, 3 ó 4
• 1325 - Fecha de inicio debe estar dentro del Periodo seleccionado
• 1115 - Debe cumplir con el siguiente formato “dd/mm/yyyy”.
• 1327 - Fecha Fin debe ser mayor o igual a la Fecha Inicio
• 1328 - Si se realiza busqueda por Fecha de emision de cp, se debe ingresar los
campos: Fecha Inicio, Fecha Fin
• 1329 - Fecha Fin debe estar dentro del Periodo seleccionado
• 1331 - Fecha Fin debe ser mayor o igual al Fecha Inicio
• 1332 - Si se realiza busqueda por Fecha de emision de cp, se debe ingresar los
campos: Fecha Fin, Fecha Inicio
• 1011 – El campo “codTipoCDP” no enviado o es vacío
5.55 Servicio Web Api descargar reporte estadístico NC-ND por
proveedor y periodo
Nombre Web
Services
Servicio Web Api descargar reporte estadístico NC-ND por proveedor y periodo
Descripción Permite exportar resumen estadístico de NC-ND por proveedor y periodo
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/estadistica/web/resumenestadisti
co/exporta?numRuc={numRuc}&perTributario={perTributario}&fechaini={fechaini}&?fechafin
={fechafin}&numRucproveedor={numRucproveedor}&odTipoCDP={codTipoCDP}&codTipoArc
hivo={codTipoArchivo}&codTipoReporte={codTipoReporte}&codLibro={codLibro}
Parámetros[URL] Param-formato-tipo Descripción
numRuc-alfanumérico-String Número de RUC del generador (Obligatorio)
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
fechaIni-dd/mm/yyyy-date Fecha emision desde del comprobante de
120
pago (Opcional: Para filtrar por fecha de
inicio)
fechaFin-dd/mm/yyyy-date Fecha emision hasta del comprobante de
pago (Opcional: Para filtrar por fecha de fin)
numRucProveedor-alfanumericoalfanumerico
Numero del RUC o Documento de identidad
del proveedor (Opcional: Para filtrar por
proveedor)
codTipoCDP-alfanumerico-alfanumerico Tipo de comprobante (Opcional: Para filtrar
por tipo de comprobante)
codTipoArchivo-numérico-Integer Extension del archivo a descargar
- 0: txt
- 1: excel
(Obligatorio)
codTipoReporte-numérico-Integer Código de tipo de reporte: 2 Reporte
montos/Notas credito y notas de debito
(Obligatorio)
codLibro-alfanumérico-String Código de libro: 080000 RCE (Obligatorio)
Parámetros[body] No aplica.
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Content-type: application/x-www-form-urlencoded
Parámetros Valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: GET
Parámetros[salida] Parámetros Valor
HTTP status 200
Content-Type application/json
ContentDisposition
El sistema descarga el archivo con el siguiente formato de nombre:
2-REPORTE MONTOS/NOTAS CREDITO Y NOTAS DE DEBITO
(estadisticaPorProveedorNotaCreDeb.<extensión> )
Razón Social|Monto|Porcentaje
Los constructores SAC|12 000|16%
El ingeniero perez|8 999|9%
El consorcio unido|7 000|7%
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/estadistica/web/resumenestadisti
co/exporta?numRuc=20195923753&perTributario=202201&codTipoArchivo=0&codTipoRepo
rte=2&codLibro=080000
Headers
Body
(No aplica)
Result OK
Result Fail
121
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
• 1001 – El campo “numRuc” no enviado o es vacío
• 1002 – Solo se permite dato numérico de 11 dígitos para el número de RUC.
• 1003 - El RUC ingresado no existe o no es válido
• 1005 – El campo “perTributario” no enviado o es vacío
• 1006 – Formato de perTributario no cumple con el formato “yyyymm”
• 1007 – El perTributario de búsqueda no debe ser mayor a la fecha actual
• 1059 – Código tipo de Archivo no permitido o no valido
• 1060 - Solo se permite dato numérico de 1 dígito para el codTipoArchivo
• 1061 - El campo "codTipoArchivo" es nulo o vacío
• 1333 - El campo "codTipoReporte" es nulo o vacío
• 1334 - El campo "codTipoReporte" solo admite valores: 1, 2, 3 ó 4
• 1325 -Fecha de inicio debe estar dentro del Periodo seleccionado
• 1326 - Debe cumplir con el siguiente formato “dd/mm/yyyy”.
• 1327 - Fecha Fin debe ser mayor o igual a la Fecha Inicio
• 1328 - Si se realiza busqueda por Fecha de emision de cp, se debe ingresar los
campos: Fecha Inicio, Fecha Fin
• 1329 - Fecha Fin debe estar dentro del Periodo seleccionado
• 1330 - Debe cumplir con el siguiente formato “dd/mm/yyyy”.
• 1331 - Fecha Fin debe ser mayor o igual al Fecha Inicio
• 1332 - Si se realiza busqueda por Fecha de emision de cp, se debe ingresar los
campos: Fecha Fin, Fecha Inicio
• 1011 – El campo “codTipoCDP” no enviado o es vacío
5.56 Servicio Web Api descargar reporte estadístico Compras por día y
periodo
Nombre Web
Services
Servicio Web Api descargar reporte estadístico Compras por día y periodo
Descripción Permite exportar resumen estadístico de compras por día y periodo.
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/estadistica/web/resumenestadisti
co/exporta?numRuc={numRuc}&perTributario={perTributario}&fechaIni={fechaIni}&fechaFin
={fechaFin}&numRucproveedor={numRucproveedor}&codTipoCDP={codTipoCDP}&codTipoAr
chivo={codTipoArchivo}&codTipoReporte={codTipoReporte}&codLibro={codLibro}
Parámetros[URL] Param-formato-tipo Descripción
numRuc-alfanumérico-String Número de RUC del generador (Obligatorio)
perTributario-numérico-int Periodo tributario (Obligatorio)
fechaIni-dd/mm/yyyy-date Fecha emision desde del comprobante de pago
(Opcional: Para filtrar por fecha de incio)
fechaFin-dd/mm/yyyy-date Fecha emision hasta del comprobante de pago
(Opcional: Para filtrar por fecha de fin)
numRucProveedor-alfanumericoalfanumerico
Numero del RUC o Documento de identidad
del proveedor / sino se envía listar todos
(Opcional: Para filtrar por proveedor)
codTipoCDP-alfanumerico-alfanumerico Tipo de comprobante (Opcional: Para filtrar
por tipo de comprobante)
codTipoArchivo-numérico-Integer Extension del archivo a descargar (Ver Anexo
III: Extension del archivo a descargar)
(Obligatorio)
codTipoReporte-numérico-Integer Código de tipo de reporte: 3 Reporte
montos/dia (Obligatorio)
122
codLibro-alfanumérico-String Código de libro: 080000 RCE (Obligatorio)
Parámetros[body] No aplica.
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Content-type: application/x-www-form-urlencoded
Parámetros Valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: GET
Parámetros[salida] Parámetros Valor
HTTP status 200
Content-Type application/json
ContentDisposition
El sistema descarga el archivo con el siguiente formato de nombre:
3-REPORTE MONTOS/DIA
(estadisticaPorDia.<extensión>)
Día|Monto|Porcentaje
15|12 000|16%
20|8 999|9%
27|7 000|7%
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/estadistica/web/resumenestadisti
co/exporta?numRuc=20195923753&perTributario=202203&codTipoArchivo=0&codTipoRepo
rte=3&codLibro=080000
Headers
Body
(No aplica)
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
• 1001 – El campo “numRuc” no enviado o es vacío
• 1002 – Solo se permite dato numérico de 11 dígitos para el número de RUC.
• 1003 - El RUC ingresado no existe o no es válido
• 1005 – El campo “perTributario” no enviado o es vacío
• 1006 – Formato de perTributario no cumple con el formato “yyyymm”
• 1007 – El perTributario de búsqueda no debe ser mayor a la fecha actual
• 1059 – Código tipo de Archivo no permitido o no valido
• 1060 - Solo se permite dato numérico de 1 dígito para el codTipoArchivo
• 1061 - El campo "codTipoArchivo" es nulo o vacío
• 1333 - El campo "codTipoReporte" es nulo o vacío
123
• 1334 - El campo "codTipoReporte" solo admite valores: 1, 2, 3 ó 4
• 1325 -Fecha de inicio debe estar dentro del Periodo seleccionado
• 1115 - Debe cumplir con el siguiente formato dd/mm/yyyy.
• 1327 - Fecha Fin debe ser mayor o igual a la Fecha Inicio
• 1328 - Si se realiza busqueda por Fecha de emision de cp, se debe ingresar los
campos: Fecha Inicio, Fecha Fin
• 1346 - Fecha Fin debe ser menor o igual al Periodo seleccionado.
• 1332 - Si se realiza busqueda por Fecha de emision de cp, se debe ingresar los
campos: Fecha Fin, Fecha Inicio
• 1011 – El campo “codTipoCDP” no enviado o es vacío
5.57 Servicio Web Api descargar reporte estadístico Compras por CIIU
Nombre Web
Services
Servicio Web Api descargar reporte estadístico Compras por CIIU
Descripción Permite exportar resumen estadístico de compras por CIIU
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/estadistica/web/resumenestadisti
co/exporta?numRuc={numRuc}&perTributario={perTributario}&fechaIni={fechaIni}&fechaFin
={fechaFin}&numRucproveedor={numRucproveedor}&odTipoCDP={codTipoCDP}&codTipoArc
hivo={codTipoArchivo}&codTipoReporte={codTipoReporte}&codLibro={codLibro}
Parámetros[URL] Param-formato-tipo Descripción
numRuc-alfanumérico-String Número de RUC del generador (Obligatorio)
perTributario-numérico-int Periodo tributario (Obligatorio)
fechaIni-dd/mm/yyyy-date Fecha emision desde del comprobante de pago
(Opcional: Para filtrar por fecha de inicio)
fechaFin-dd/mm/yyyy-date Fecha emision hasta del comprobante de pago
(Opcional: Para filtrar por fecha de fin)
numRucProveedor-alfanumericoalfanumerico
Numero del RUC o Documento de identidad
del proveedor / sino se envía listar todos
(Opcional: Para filtrar por proveedor)
codTipoCDP-alfanumerico-alfanumerico Tipo de comprobante (Opcional: Para filtrar
por tipo de comprobante)
codTipoArchivo-numérico-Integer Extension del archivo a descargar
- 0: txt
- 1: excel
(Obligatorio)
codTipoReporte-numérico-Integer Código de tipo de reporte: 4 Reporte
montos/CIIU (Obligatorio)
codLibro-alfanumérico-String Código de libro: 080000 RCE (Obligatorio)
Parámetros[body] No aplica.
Parámetros[header] Descripción:
Content-type: tipo de contenido a envia
Valores:
Content-type: application/x-www-form-urlencoded
Parámetros Valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: GET
Parámetros[salida] Parámetros Valor
HTTP status 200
Content-Type application/json
ContentDisposition
El sistema descarga el archivo con el siguiente formato de nombre:
4-REPORTE MONTOS/CIIU
(estadisticaPorCIIUProveedor.<extensión>)
CIIU|Monto|Porcentaje
4690 VENTA POR MAYOR|12 000|16%
124
4751 VENTA AL POR MENOR|8 999|9%
5510 ACTIVIDADES DE ALOJAMIENTO|7 000|7%
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/estadistica/web/resumenestadisti
co/exporta?numRuc=20195923753&perTributario=202203&codTipoArchivo=0&codTipoRepo
rte=4&codLibro=080000
Headers
Body
(No aplica)
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
• 1001 – El campo “numRuc” no enviado o es vacío
• 1002 – Solo se permite dato numérico de 11 dígitos para el número de RUC.
• 1003 - El RUC ingresado no existe o no es válido
• 1005 – El campo “perTributario” no enviado o es vacío
• 1006 – Formato de perTributario no cumple con el formato “yyyymm”
• 1007 – El perTributario de búsqueda no debe ser mayor a la fecha actual
• 1059 – Código tipo de Archivo no permitido o no valido
• 1060 - Solo se permite dato numérico de 1 dígito para el codTipoArchivo
• 1061 - El campo "codTipoArchivo" es nulo o vacío
• 1333 - El campo "codTipoReporte" es nulo o vacío
• 1334 - El campo "codTipoReporte" solo admite valores: 1, 2, 3 ó 4
• 1325 -Fecha de inicio debe estar dentro del Periodo seleccionado
• 1115 - Debe cumplir con el siguiente formato “dd/mm/yyyy”.
• 1327 - Fecha Fin debe ser mayor o igual a la Fecha Inicio
• 1328 - Si se realiza búsqueda por Fecha de emisión de cp, se debe ingresar los
campos: Fecha Inicio, Fecha Fin
• 1329 - Fecha Fin debe estar dentro del Periodo seleccionado
• 1332 - Si se realiza busqueda por Fecha de emision de cp, se debe ingresar los
campos: Fecha Fin, Fecha Inicio
• 1011 – El campo “codTipoCDP” no enviado o es vacío
5.58 Servicio Web Api descargar reporte de cumplimiento
Nombre Web
Services
Servicio Web Api descargar reporte de cumplimiento
Descripción Permite descargar el reporte de cumplimiento.
125
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/cumplimiento/web/omi
sos/{perTributario}/{codLibro}/consultaReporteCumplimiento/exportardocumento
Parámetros[URL] Param-formato-tipo Descripción
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
codLibro-alfanumérico-String Código de libro: 080000 RCE (Obligatorio)
Parámetros[body] No aplica
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Content-type: application/x-www-form-urlencoded
Parámetros Valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: GET
Parámetros[salida] Parámetros de Salida Descripción
archivoPdf-Base64-String Base64 representando el archivo
nombreArchivoPdf-afanumérico-String Nombre de archive de descarga
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/cumplimiento/web/omisos/2023
05/080000/consultaReporteCumplimiento/exportardocumento
Headers
Body
(No aplica)
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
• 1005 – El campo “perTributario” no enviado o es vacío
• 1006 – Formato de perTributario no cumple con el formato “yyyymm”
• 1007 – El perTributario de búsqueda no debe ser mayor a la fecha actual
• 1140 – El campo “codLibro” no enviado o es vacío
126
5.59 Servicio Web Api consultar ajustes posteriores RCE
Nombre Web
Services
Servicio Web Api consultar ajustes posteriores RCE
Descripción Permite consultar el código de ajuste posterior y comprobantes de ajustes posteriores RCE
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/ajustesposteriores/web/comprobant
esajuspost/{periodoSeleccionado}/listarcap?page={page}&perPage={perPage}
Parámetros[URL] Param-formato-tipo Descripción
periodoSeleccionado -alfanumérico-String Periodo tributario (Obligatorio)
page-numérico-entero Número de pagina (Obligatorio)
perPage-numérico-entero Número de registros a obtener
(Obligatorio)
Parámetros[body] No aplica.
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Parámetros valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: GET
Parámetros[salida] Parámetros de Salida Descripción
registros-array-array Array de la Propuesta FV621 - inicio
registros.factprorrata-numérico-decimal128 Coeficiente de Prorrata
registros.valorRCF-numérico-decimal128 reintegro del crédito fiscal
registros.valorCFE-numérico-decimal128 crédito fiscal especial
registros-array-array Array de la Propuesta FV621 - fin
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/propuesta/web?periodoSeleccionado
=202301&tipoInfo=FV0621
Headers
Body
(No aplica)
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
• 1005 - El campo “perTributario” no enviado o es vacío
• 1006 – Formato de perTributario no cumple con el formato “yyyymm”
• 1007 – El perTributario de búsqueda no debe ser mayor a la fecha actual
127
5.60 Servicio Web Api eliminar preliminar registrado
Nombre Web
Services
Servicio Web Api eliminar el preliminar registrado.
Descripción Permite eliminar el preliminar registrado. Se utilizan los campos” registros[0].id” y
“registros[0].codTipoRegistro” del servicio “5.61 Servicio Web Api consultar preliminares
registrados ” para hallar los parámetros necesarios y hacer uso de este servicio.
Url https://api-sire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/gestionlibro/web/regi
stroslibros/{perTributario}/eliminapreliminar?codLibro={codLibro}
Parámetros[URL] Param-formato-tipo Descripción
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
codLibro-alfanumérico-String Código de libro: 080000 RCE (Obligatorio)
Parámetros[body] Param-formato-tipo Descripción
id-alfanumérico-String Id de registro (Obligatorio)
codTipoRegistro-alfanumérico-String Código de tipo registro: 8 (Obligatorio)
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Content-type: application/x-www-form-urlencoded
Parámetros valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: PUT
Parámetros[salida] Parámetros Valor
HTTP status 200
Content-Type application/json
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/gestionlibro/web/registroslibros/
202304/eliminapreliminar?codLibro=140000
Headers
Body
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
128
 1005 - El campo ‘perTributario’ no enviado o es vacio
 1006 - Formato de perTributario no cumple con el formato ‘yyyymm’
 1007 - El perTributario de búsqueda no debe ser mayor a la fecha actual
 El campo “codRegistroLibro” no enviado o es vacío
 1010 - El libro electronico con los siguientes datos: numero de RUC: XXXXXXXX
periodo Tributario: AAAAMM y codigo de Libro:140000 no existe.
 2296 - No es posible eliminar su preliminar, debido a que aun no registra su
preliminar para el periodo/registro ingresado.
 2297 - No es posible eliminar su preliminar, debido a que su registro se encuentra
generado para el periodo ingresado.
5.61 Servicio Web Api consultar preliminares registrados
Nombre Web
Services
Servicio Web Api consultar preliminares registrados
Descripción Permite consultar todos los preliminares registrados.
Url https://api-sire.sunat.gob.pe /v1/contribuyente/migeigv/libros/rvierce/gestionlibro/web/regi
stroslibros/consultapreliminaresregistro?page={page}&perPage={perPage}&perIni={perIni}&p
erFin={perFin}
Parámetros[URL] Param-formato-tipo Descripción
page-alfanumérico-String Número de página (Obligatorio)
perPage-alfanumérico-String Cantidad por pagina (Obligatorio)
perIni-alfanumérico-String Periodo de consulta de documentos de
comprobantes del RVIE preliminar Inicio.
(Obligatorio)
perFin-alfanumérico-String Periodo de consulta de documentos de
comprobantes del RVIE preliminar Final.
(Obligatorio)
Parámetros[body] No aplica.
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Content-type: application/x-www-form-urlencoded
Parámetros valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: GET
Parámetros[salida] Parámetros Valor
HTTP status 200
Content-Type application/json
Evidencias URL
https://api-sire.sunat.gob.pe
/v1/contribuyente/migeigv/libros/rvierce/gestionlibro/web/registroslibros/consultaprelimina
resregistro?page=1&perPage=100&perIni=202001&perFin=202505
Headers
Result OK
129
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
 1005 - El campo ‘perTributario’ no enviado o es vacio
 1006 - Formato de perTributario no cumple con el formato ‘yyyymm’
 1007 - El perTributario de búsqueda no debe ser mayor a la fecha actual
 El campo “codRegistroLibro” no enviado o es vacío
 1010 - El libro electronico con los siguientes datos: numero de RUC: XXXXXXXX
periodo Tributario: AAAAMM y codigo de Libro:140000 no existe.
 2296 - No es posible eliminar su preliminar, debido a que aun no registra su
preliminar para el periodo/registro ingresado.
 2297 - No es posible eliminar su preliminar, debido a que su registro se encuentra
generado para el periodo ingresado.
6. Documentación TUS.IO
Tus.io es un protocolo abierto para carga reanudable basado en HTTP el cual te
permite poder implementarlo con cualquier lenguaje de programación, ya sea
angular, java, Python, Android, etc. Pero, lo único que necesita es de la
configuración de un servicio como servidor y otro como cliente.
Este manual api lo que proporciona es el endpoint servidor en donde los usuarios
pueden generar sus peticiones para la importación/carga de archivos
reanudables de manera rápida y segura.
Por lo tanto, el usuario que quiera cargar archivos a los servicios api mencionados
en el apartado “5. Documentación Servicios Web API”, deberá configurar su
cliente de acuerdo a su necesidad, por lo que podrá ubicar más detalle de ello en
la documentación que es propia del protocolo tus.io en la página web
https://tus.io/implementations
130
Servicios Web Api que funcionan como servidor para la importación de archivos:
5.3 Servicio Web Api importar reemplazo de la propuesta
5.4 Servicio Web Api importar nuevos comprobantes propuesta
5.5 Servicio Web Api importar nuevos comprobantes preliminar
5.6 Servicio Web Api importar ajustes posteriores
5.7 Servicio Web Api importar ajustes posteriores de periodos anteriores
7. Anexos
7.1 Anexo I: Indicador de carga masiva
Código Descripción
1 Importar CP - Propuesta
2 Aceptar propuesta
3 Reemplazo de la Propuesta
4 Importa CP - Preliminar
5 Generar libro RVIE
6 Cargar Ajuste posteriores al periodo actual
6 Cargar Ajuste posteriores de periodos del sire
7 Cargar Ajuste posteriores anteriores a la vigencia
8 Generar registro Ajustes Posterior RVIE
9 Generar registro Ajustes Posterior Anterior RVIE
10 Generar archivo exportar propuesta
11 Generar archivo exportar no incluidos
12 Generar archivo exportar preliminar
13 Generar archivo exportar inconsistencias
14 Generar archivo exportar propuesta ajustes posteriores
15 Generar archivo exportar CAR
16 Generar reporte de observaciones de comparación
131
17 Generar archivo exportar Libro Venta
18 Generar reporte de ajustes posteriores individual
19 Generar reporte de ajustes posteriores consolidado
20 Generar reporte de ajustes posteriores de periodos anteriores individual
21 Generar reporte de ajustes posteriores de periodos anteriores consolidado
22 Generar reporte consolidado del libro y ajustes
23 Generar reporte Libro RVIE
24 Generar Archivo personalizado Libros RVIE
25 Generar Archivo personalizado Propuesta RVIE
26 Generar Archivo personalizado Ajustes Posteriores RVIE
27 Carga archivo de comparación - validación
28 Generar archivo exportar preliminar registrado
29 Generar archivo exportar preliminar ajustes posteriores registrado
30 Generar reporte de inconsistencias generación del RVIE
31 Generar reporte de inconsistencias ajustes posteriores del RVIE
32 Generar libro RVIE - Archivo exportar Libro Venta
33 Generar libro RVIE - Archivo reporte inconsistencias
34 Generar libro RVIE - Achivo Reporte Exportadores
35 Generar libro RVIE - Archivo Propuesta Casillas
36 Generar Ajustes Posteriroes RVIE - Archivo exportar Ajuste
37 Generar Ajustes Posteriroes RVIE - Archivo reporte inconsistencias
38 Generar Ajustes Posteriores de periodos anteriores RVIE - Archivo exportar Ajuste
39 Aceptar propuesta sin Movimiento
40 Carga Tipo de Cambio
41 Generar reportes Estadisticos
42 Generar Reporte de comparación
43 Descargar Registros Electronicos RVIE
44 Descargar Registros Electronicos RCE
45 Descargar Constancia de Recepción RVIE
46 Descargar Constancia de Recepción RCE
47 Descargar Reporte de Inconcistencias RVIE
48 Descargar Reporte de Inconcistencias RCE
49 Descargar Reporte de Ajustes Posteriores RVIE
50 Descargar Reporte de Ajustes Posteriores RCE
51 Descargar Reporte de Casillas Vista Comparada
52 Descargar Reporte de Inconsistencias de Casillas
53 Generar Reporte de comparación RCE
54 Carga Complementar
55 Carga Incluir Excluir
56 Carga No Domiciliados
57 Carga Comparacion RCE
58 Carga Comparacion RVIE
59 importar CP en Ajustes Posteriores RCE
60 importar CP no domiciliados en Ajustes Posteriores
61 Reemplazo de la Propuesta
62 Generacion de Inconsistencia por Casilla
63 Generación de ventas por Casilla (100. 101)
64 Generacion Inconsistencias en Registros para Casillas
65 Validar Propuesta
66 Validar Preliminar
67 Validar No Domiciliados
68 Reporte de Ajustes posteriores de periodos anteriores del RCE
69 Descarga Consolidada de registros del RCE
70 Descarga RCE
71 Reporte de ajustes posteriores del RVIE
72 Reporte de Ajustes posteriores de periodos anteriores del RVIE
73 Descarga Consolidada de registros del RVIE
74 Descarga RVIE
75 Generación de ventas por Casilla (100. 101)
132
76 Generacion Inconsistencias en Registros para Casillas
77 Validar Propuesta
78 Validar Preliminar
79 Validar No Domiciliados
80 Generación de archivo personalizado Propuesta RCE
81 Generación de archivo personalizado Preliminar RCE
82 Generación de archivo personalizado Preliminar Registrado RCE
83 Generación de archivo personalizado Registro Compras
84 Generación de archivo personalizado Ajuste Posterior RCE
85 Generacion de archivo del libro de Ajustes Posteriores RVIE
86 Generacion de archivo de inconsistencias de libro de Ajustes Posteriores RVIE
87 Importar CP en Ajustes Posteriores RVIE
88 Importar CP en Ajustes Posteriores de periodos anteriores RVIE general
89 Importar CP en Ajustes Posteriores de periodos anteriores RVIE simplificado
90 Generación de documentos para Intranet
91 Exportar detalle propuesta casilla - Registro
92 Exportar inconsistencias en registro
93 Importar CP en Ajustes Posteriores RCE de Periodos Anteriores Simplificado
94 Importar CP en Ajustes Posteriores RCE de Periodos Anteriores General
95 Importar CP no domiciliados en Ajustes Posteriores RCE de Periodos Anteriores
96 Generar archivo exportar preliminar - RCE No Domiciliados
97 Exportar comprobantes excluidos
7.2 Anexo II: Tipo de ajuste posterior
Código Descripción
1 Ajuste Posterior
2 Ajuste Posterior con No Domiciliados
3 Ajuste Posteriores de periodos anteriores general
4 Ajuste Posteriores de periodos anteriores simplificado
5 Ajuste Posteriores de periodos anteriores con No Domiciliados
7.3 Anexo III: Extension del archivo a descargar
Código Descripción
0 txt
1 csv
2 excel
7.4 Anexo IV: Ejemplo cliente TUS JAVA
Para poder hacer uso de las API-REST de carga de archivos SIRE es necesario tener configurado en su
proyecto la librería “tus-java-client” en la versión “0-5-0”, la cual se puede encontrar en el repositorio Maven
https://repo1.maven.org/maven2/io/tus/java/client/tus-java-client/0.5.0/tus-java-client-0.5.0.jar
Esta librería tiene algunas deficiencias para la gestión de los mensajes de retorno y error.
Por lo cual se tienen que hacer algunas adecuaciones para que se muestren de forma correcta los errores
proporcionados por el servicio SIRE.
1. Crear el paquete: io.tus.java.client y dentro crear las clases:
• TusResponseBody.java: transforma los errores a texto que se puede imprimir en la bitácora.
• Http401And403CodeException.java: Muestra los errores de autenticación o de autorización
• Http422CodeException.java: Muestra los errores de validación de negocio
• HttpErrorCodeException.java: Clase de ayuda para la gestión de errores
• TusClientCustom.java: Cliente tus personalizado que permite ver la gestión de errores.
• TusUploaderCustom.java: Uploader tus personalizado que permite ver la gestión de errores.
133
2. Crear la clase: Demo.java (puede usar el paquete que desee): se usará para realizar la operación de
carga de archivos del SIRE.
Clase:: TusResponseBody.java
/**
*
* Copyright 2011-2024 the original author or authors.
* *
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* *
* https://www.apache.org/licenses/LICENSE-2.0
* *
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*
*/
package io.tus.java.client;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.Serializable;
import java.net.HttpURLConnection;
public class TusResponseBody implements Serializable {
private int responseCode;
private String responseMessage;
private String responseBody;
public TusResponseBody(HttpURLConnection connection)
throws IOException {
if (connection != null) {
responseCode = connection.getResponseCode();
responseBody = readResponseBody(connection);
responseMessage = connection.getResponseMessage();
}
}
public int getResponseCode() {
return responseCode;
}
134
public String getResponseBody() {
return responseBody;
}
public String getResponseMessage() {
return responseMessage;
}
private String readResponseBody (
HttpURLConnection connection
) throws IOException {
ByteArrayOutputStream result = new ByteArrayOutputStream();
byte[] buffer = new byte[1024];
int length;
InputStream inputStream;
if (connection.getErrorStream() != null) {
inputStream = connection.getErrorStream();
} else {
try {
inputStream = connection.getInputStream();
} catch (IOException e) {
return e.getMessage();
}
}
if (inputStream == null) {
return "";
}
try {
while ((length = inputStream.read(buffer)) != -1) {
result.write(buffer, 0, length);
}
connection.disconnect();
} catch (IOException e) {
return e.getMessage();
}
return result.toString("UTF-8");
}
@Override
public String toString() {
return responseBody.isEmpty()? responseMessage: responseBody;
}
}
135
Clase:: Http401And403CodeException.java
/**
*
* Copyright 2011-2024 the original author or authors.
* *
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* *
* https://www.apache.org/licenses/LICENSE-2.0
* *
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*
*/
package io.tus.java.client;
import java.net.HttpURLConnection;
public class Http401And403CodeException extends HttpErrorCodeException {
public Http401And403CodeException(
TusResponseBody response,
HttpURLConnection connection
) {
super(response, connection);
}
}
136
Clase:: Http422CodeException.java
/**
*
* Copyright 2011-2024 the original author or authors.
* *
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* *
* https://www.apache.org/licenses/LICENSE-2.0
* *
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*
*/
package io.tus.java.client;
import java.io.IOException;
import java.net.HttpURLConnection;
public class Http422CodeException extends HttpErrorCodeException {
public Http422CodeException(
TusResponseBody response,
HttpURLConnection connection
) throws IOException {
super(response, connection);
}
}
137
Clase:: HttpErrorCodeException.java
/**
*
* Copyright 2011-2024 the original author or authors.
* *
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* *
* https://www.apache.org/licenses/LICENSE-2.0
* *
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*
*/
package io.tus.java.client;
import java.net.HttpURLConnection;
public class HttpErrorCodeException extends ProtocolException {
private static final long serialVersionUID = 0l;
private final TusResponseBody response;
public HttpErrorCodeException(
TusResponseBody response,
HttpURLConnection connection
) {
super(response.getResponseMessage(), connection);
this.response = response;
}
public TusResponseBody getResponseBody() {
return response;
}
}
138
Clase:: TusClientCustom.java
/**
*
* Copyright 2011-2024 the original author or authors.
* *
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* *
* https://www.apache.org/licenses/LICENSE-2.0
* *
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*
*/
package io.tus.java.client;
import java.net.Proxy;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;
import java.io.IOException;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Map;
/**
* This class is used for creating or resuming uploads.
*/
public class TusClientCustom {
/**
* Version of the tus protocol used by the client. The remote server
needs to support this
* version, too.
*/
public static final String TUS_VERSION = "1.0.0";
private URL uploadCreationURL;
private Proxy proxy;
private boolean resumingEnabled;
private boolean removeFingerprintOnSuccessEnabled;
private TusURLStore urlStore;
private Map<String, String> headers;
private int connectTimeout = 5000;
/**
139
* Create a new tus client.
*/
public TusClientCustom() {
}
/**
* Set the URL used for creating new uploads. This is required if you
want to initiate new
* uploads using {@link #createUpload} or {@link #resumeOrCreateUpload}
but is not used if you
* only resume existing uploads.
*
* @param uploadCreationURL Absolute upload creation URL
*/
public void setUploadCreationURL(URL uploadCreationURL) {
this.uploadCreationURL = uploadCreationURL;
}
/**
* Get the current upload creation URL.
*
* @return Current upload creation URL
*/
public URL getUploadCreationURL() {
return uploadCreationURL;
}
/**
* Set the proxy that will be used for all requests.
*
* @param proxy Proxy to use
*/
public void setProxy(Proxy proxy) {
this.proxy = proxy;
}
/**
* Get the current proxy used for all requests.
*
* @return Current proxy
*/
public Proxy getProxy() {
return proxy;
}
/**
* Enable resuming already started uploads. This step is required if you
want to use
140
* {@link #resumeUpload(TusUpload)}.
*
* @param urlStore Storage used to save and retrieve upload URLs by its
fingerprint.
*/
public void enableResuming(@NotNull TusURLStore urlStore) {
resumingEnabled = true;
this.urlStore = urlStore;
}
/**
* Disable resuming started uploads.
*
* @see #enableResuming(TusURLStore)
*/
public void disableResuming() {
resumingEnabled = false;
this.urlStore = null;
}
/**
* Get the current status if resuming.
*
* @see #enableResuming(TusURLStore)
* @see #disableResuming()
*
* @return True if resuming has been enabled using {@link
#enableResuming(TusURLStore)}
*/
public boolean resumingEnabled() {
return resumingEnabled;
}
/**
* Enable removing fingerprints after a successful upload.
*
* @see #disableRemoveFingerprintOnSuccess()
*/
public void enableRemoveFingerprintOnSuccess() {
removeFingerprintOnSuccessEnabled = true;
}
/**
* Disable removing fingerprints after a successful upload.
*
* @see #enableRemoveFingerprintOnSuccess()
*/
public void disableRemoveFingerprintOnSuccess() {
removeFingerprintOnSuccessEnabled = false;
141
}
/**
* Get the current status if removing fingerprints after a successful
upload.
*
* @see #enableRemoveFingerprintOnSuccess()
* @see #disableRemoveFingerprintOnSuccess()
*
* @return True if resuming has been enabled using {@link
#enableResuming(TusURLStore)}
*/
public boolean removeFingerprintOnSuccessEnabled() {
return removeFingerprintOnSuccessEnabled;
}
/**
* Set headers which will be added to every HTTP requestes made by this
TusClient instance.
* These may to overwrite tus-specific headers, which can be identified
by their Tus-*
* prefix, and can cause unexpected behavior.
*
* @see #getHeaders()
* @see #prepareConnection(HttpURLConnection)
*
* @param headers The map of HTTP headers
*/
public void setHeaders(@Nullable Map<String, String> headers) {
this.headers = headers;
}
/**
* Get the HTTP headers which should be contained in every request and
were configured using
* {@link #setHeaders(Map)}.
*
* @see #setHeaders(Map)
* @see #prepareConnection(HttpURLConnection)
*
* @return The map of configured HTTP headers
*/
@Nullable
public Map<String, String> getHeaders() {
return headers;
}
/**
142
* Sets the timeout for a Connection.
* @param timeout in milliseconds
*/
public void setConnectTimeout(int timeout) {
connectTimeout = timeout;
}
/**
* Returns the Connection Timeout.
* @return Timeout in milliseconds.
*/
public int getConnectTimeout() {
return connectTimeout;
}
/**
* Create a new upload using the Creation extension. Before calling this
function, an "upload
* creation URL" must be defined using {@link #setUploadCreationURL(URL)}
or else this
* function will fail.
* In order to create the upload a POST request will be issued. The
file's chunks must be
* uploaded manually using the returned {@link TusUploader} object.
*
* @param upload The file for which a new upload will be created
* @return Use {@link TusUploader} to upload the file's chunks.
* @throws ProtocolException Thrown if the remote server sent an
unexpected response, e.g.
* wrong status codes or missing/invalid headers.
* @throws IOException Thrown if an exception occurs while issuing the
HTTP request.
*/
public TusUploaderCustom createUpload(@NotNull TusUpload upload) throws
ProtocolException, IOException {
HttpURLConnection connection = openConnection(uploadCreationURL);
connection.setRequestMethod("POST");
prepareConnection(connection);
String encodedMetadata = upload.getEncodedMetadata();
if (encodedMetadata.length() > 0) {
connection.setRequestProperty("Upload-Metadata",
encodedMetadata);
}
connection.addRequestProperty("Upload-Length",
Long.toString(upload.getSize()));
connection.connect();
143
int responseCode = connection.getResponseCode();
if (responseCode == 401 || responseCode == 403) {
throw new Http401And403CodeException(new
TusResponseBody(connection), connection);
}
if(responseCode == 422) {
throw new Http422CodeException(new TusResponseBody(connection),
connection);
}
if(!(responseCode >= 200 && responseCode < 300)) {
throw new ProtocolException("unexpected status code (" +
responseCode + ") while creating upload", connection);
}
String urlStr = connection.getHeaderField("Location");
if (urlStr == null || urlStr.length() == 0) {
throw new ProtocolException("missing upload URL in response for
creating upload", connection);
}
// The upload URL must be relative to the URL of the request by which
is was returned,
// not the upload creation URL. In most cases, there is no difference
between those two
// but there may be cases in which the POST request is redirected.
URL uploadURL = new URL(connection.getURL(), urlStr);
if (resumingEnabled) {
urlStore.set(upload.getFingerprint(), uploadURL);
}
return createUploader(upload, uploadURL, 0L);
}
@NotNull
private HttpURLConnection openConnection(@NotNull URL uploadURL) throws
IOException {
if (proxy != null) {
return (HttpURLConnection) uploadURL.openConnection(proxy);
}
return (HttpURLConnection) uploadURL.openConnection();
}
@NotNull
private TusUploaderCustom createUploader(@NotNull TusUpload upload,
@NotNull URL uploadURL, long offset)
throws IOException {
144
TusUploaderCustom uploader = new TusUploaderCustom(this, upload,
uploadURL, upload.getTusInputStream(), offset);
uploader.setProxy(proxy);
return uploader;
}
/**
* Try to resume an already started upload. Before call this function,
resuming must be
* enabled using {@link #enableResuming(TusURLStore)}. This method will
look up the URL for this
* upload in the {@link TusURLStore} using the upload's fingerprint (see
* {@link TusUpload#getFingerprint()}). After a successful lookup a HEAD
request will be issued
* to find the current offset without uploading the file, yet.
*
* @param upload The file for which an upload will be resumed
* @return Use {@link TusUploader} to upload the remaining file's chunks.
* @throws FingerprintNotFoundException Thrown if no matching fingerprint
has been found in
* {@link TusURLStore}. Use {@link #createUpload(TusUpload)} to create a
new upload.
* @throws ResumingNotEnabledException Throw if resuming has not been
enabled using {@link
* #enableResuming(TusURLStore)}.
* @throws ProtocolException Thrown if the remote server sent an
unexpected response, e.g.
* wrong status codes or missing/invalid headers.
* @throws IOException Thrown if an exception occurs while issuing the
HTTP request.
*/
public TusUploaderCustom resumeUpload(@NotNull TusUpload upload) throws
FingerprintNotFoundException, ResumingNotEnabledException,
ProtocolException, IOException {
if (!resumingEnabled) {
throw new ResumingNotEnabledException();
}
URL uploadURL = urlStore.get(upload.getFingerprint());
if (uploadURL == null) {
throw new FingerprintNotFoundException(upload.getFingerprint());
}
return beginOrResumeUploadFromURL(upload, uploadURL);
}
/**
* Begin an upload or alternatively resume it if the upload has already
been started before. In contrast to
145
* {@link #createUpload(TusUpload)} and {@link
#resumeOrCreateUpload(TusUpload)} this method will not create a new
* upload. The user must obtain the upload location URL on their own as
this method will not send the POST request
* which is normally used to create a new upload.
* Therefore, this method is only useful if you are uploading to a
service which takes care of creating the tus
* upload for yourself. One example of such a service is the Vimeo API.
* When called a HEAD request will be issued to find the current offset
without uploading the file, yet.
* The uploading can be started by using the returned {@link TusUploader}
object.
*
* @param upload The file for which an upload will be resumed
* @param uploadURL The upload location URL at which has already been
created and this file should be uploaded to.
* @return Use {@link TusUploader} to upload the remaining file's chunks.
* @throws ProtocolException Thrown if the remote server sent an
unexpected response, e.g.
* wrong status codes or missing/invalid headers.
* @throws IOException Thrown if an exception occurs while issuing the
HTTP request.
*/
public TusUploaderCustom beginOrResumeUploadFromURL(@NotNull TusUpload
upload, @NotNull URL uploadURL) throws
ProtocolException, IOException {
HttpURLConnection connection = openConnection(uploadURL);
connection.setRequestMethod("HEAD");
prepareConnection(connection);
connection.connect();
int responseCode = connection.getResponseCode();
if (responseCode == 401 || responseCode == 403) {
throw new Http401And403CodeException(new
TusResponseBody(connection), connection);
}
if(responseCode == 422) {
throw new Http422CodeException(new TusResponseBody(connection),
connection);
}
if(!(responseCode >= 200 && responseCode < 300)) {
throw new HttpErrorCodeException(new TusResponseBody(connection),
connection);
}
146
String offsetStr = connection.getHeaderField("Upload-Offset");
if (offsetStr == null || offsetStr.length() == 0) {
throw new ProtocolException("missing upload offset in response
for resuming upload", connection);
}
long offset = Long.parseLong(offsetStr);
return createUploader(upload, uploadURL, offset);
}
/**
* Try to resume an upload using {@link #resumeUpload(TusUpload)}. If the
method call throws
* an {@link ResumingNotEnabledException} or {@link
FingerprintNotFoundException}, a new upload
* will be created using {@link #createUpload(TusUpload)}.
*
* @param upload The file for which an upload will be resumed
* @throws ProtocolException Thrown if the remote server sent an
unexpected response, e.g.
* wrong status codes or missing/invalid headers.
* @throws IOException Thrown if an exception occurs while issuing the
HTTP request.
* @return {@link TusUploader} instance.
*/
public TusUploaderCustom resumeOrCreateUpload(@NotNull TusUpload upload)
throws ProtocolException, IOException {
try {
return resumeUpload(upload);
} catch (FingerprintNotFoundException e) {
return createUpload(upload);
} catch (ResumingNotEnabledException e) {
return createUpload(upload);
} catch (ProtocolException e) {
// If the attempt to resume returned a 404 Not Found, we
immediately try to create a new
// one since TusExectuor would not retry this operation.
HttpURLConnection connection = e.getCausingConnection();
if (connection != null && connection.getResponseCode() == 404) {
return createUpload(upload);
}
throw e;
}
}
/**
* Set headers used for every HTTP request. Currently, this will add the
Tus-Resumable header
147
* and any custom header which can be configured using {@link
#setHeaders(Map)},
*
* @param connection The connection whose headers will be modified.
*/
public void prepareConnection(@NotNull HttpURLConnection connection) {
// Only follow redirects, if the POST methods is preserved. If
http.strictPostRedirect is
// disabled, a POST request will be transformed into a GET request
which is not wanted by us.
// CHECKSTYLE:OFF
// LineLength - Necessary because of length of the link
// See:https://github.com/openjdk/jdk/blob/jdk7-
b43/jdk/src/share/classes/sun/net/www/protocol/http/HttpURLConnection.java#L2
020-L2035
// CHECKSTYLE:ON
connection.setInstanceFollowRedirects(Boolean.getBoolean("http.strict
PostRedirect"));
connection.setConnectTimeout(connectTimeout);
connection.addRequestProperty("Tus-Resumable", TUS_VERSION);
if (headers != null) {
for (Map.Entry<String, String> entry : headers.entrySet()) {
connection.addRequestProperty(entry.getKey(),
entry.getValue());
}
}
}
/**
* Actions to be performed after a successful upload completion.
* Manages URL removal from the URL store if remove fingerprint on
success is enabled
*
* @param upload that has been finished
*/
protected void uploadFinished(@NotNull TusUpload upload) {
if (resumingEnabled && removeFingerprintOnSuccessEnabled) {
urlStore.remove(upload.getFingerprint());
}
}
}
148
Clase: TusUploaderCustom.java
/**
*
* Copyright 2011-2024 the original author or authors.
* *
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
* *
* https://www.apache.org/licenses/LICENSE-2.0
* *
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*
*/
package io.tus.java.client;
import java.io.IOException;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.Proxy;
import java.net.URL;
import java.net.URLConnection;
import java.util.Optional;
/**
* This class is used for doing the actual upload of the files. Instances are
returned by
* {@link TusClientCustom#createUpload(TusUpload)}, {@link
TusClientCustom#createUpload(TusUpload)} and
* {@link TusClientCustom#resumeOrCreateUpload(TusUpload)}.
* <br>
* After obtaining an instance you can upload a file by following these
steps:
* <ol>
* <li>Upload a chunk using {@link #uploadChunk()}</li>
* <li>Optionally get the new offset ({@link #getOffset()} to calculate the
progress</li>
* <li>Repeat step 1 until the {@link #uploadChunk()} returns -1</li>
* <li>Close HTTP connection and InputStream using {@link #finish()} to free
resources</li>
* </ol>
*/
public class TusUploaderCustom {
private URL uploadURL;
149
private Proxy proxy;
private TusInputStream input;
private long offset;
private TusClientCustom client;
private TusUpload upload;
private byte[] buffer;
private int requestPayloadSize = 10 * 1024 * 1024;
private int bytesRemainingForRequest;
private HttpURLConnection connection;
private OutputStream output;
/**
* Begin a new upload request by opening a PATCH request to specified
upload URL. After this
* method returns a connection will be ready and you can upload chunks of
the file.
*
* @param client Used for preparing a request ({@link
TusClient#prepareConnection(HttpURLConnection)}
* @param upload {@link TusUpload} to be uploaded.
* @param uploadURL URL to send the request to
* @param input Stream to read (and seek) from and upload to the remote
server
* @param offset Offset to read from
* @throws IOException Thrown if an exception occurs while issuing the
HTTP request.
*/
public TusUploaderCustom(TusClientCustom client, TusUpload upload, URL
uploadURL, TusInputStream input, long offset)
throws IOException {
this.uploadURL = uploadURL;
this.input = input;
this.offset = offset;
this.client = client;
this.upload = upload;
input.seekTo(offset);
setChunkSize(2 * 1024 * 1024);
}
private void openConnection() throws IOException, ProtocolException {
// Only open a connection, if we have none open.
if (connection != null) {
return;
}
bytesRemainingForRequest = requestPayloadSize;
150
input.mark(requestPayloadSize);
if (proxy != null) {
connection = (HttpURLConnection) uploadURL.openConnection(proxy);
} else {
connection = (HttpURLConnection) uploadURL.openConnection();
}
client.prepareConnection(connection);
connection.setRequestProperty("Upload-Offset",
Long.toString(offset));
connection.setRequestProperty("Content-Type",
"application/offset+octet-stream");
connection.setRequestProperty("Expect", "100-continue");
try {
connection.setRequestMethod("PATCH");
// Check whether we are running on a buggy JRE
} catch (java.net.ProtocolException pe) {
connection.setRequestMethod("POST");
connection.setRequestProperty("X-HTTP-Method-Override", "PATCH");
}
connection.setDoOutput(true);
connection.setChunkedStreamingMode(0);
try {
output = connection.getOutputStream();
} catch (java.net.ProtocolException pe) {
// If we already have a response code available, our expectation
using the "Expect: 100-
// continue" header failed and we should handle this response.
if (connection.getResponseCode() != -1) {
finish();
}
throw pe;
}
}
/**
* Sets the used chunk size. This number is used by {@link
#uploadChunk()} to indicate how
* much data is uploaded in a single take. When choosing a value for this
parameter you need to
* consider that uploadChunk() will only return once the specified number
of bytes has been
* sent. For slow internet connections this may take a long time. In
addition, a buffer with
* the chunk size is allocated and kept in memory.
*
151
* @param size The new chunk size
*/
public void setChunkSize(int size) {
buffer = new byte[size];
}
/**
* Returns the current chunk size set using {@link #setChunkSize(int)}.
*
* @return Current chunk size
*/
public int getChunkSize() {
return buffer.length;
}
/**
* Set the maximum payload size for a single request counted in bytes.
This is useful for splitting
* bigger uploads into multiple requests. For example, if you have a
resource of 2MB and
* the payload size set to 1MB, the upload will be transferred by two
requests of 1MB each.
*
* The default value for this setting is 10 * 1024 * 1024 bytes (10 MiB).
*
* Be aware that setting a low maximum payload size (in the low megabytes
or even less range) will result in
* decreased performance since more requests need to be used for an
upload. Each request will come with its overhead
* in terms of longer upload times.
*
* Be aware that setting a high maximum payload size may result in a high
memory usage since
* tus-java-client usually allocates a buffer with the maximum payload
size (this buffer is used
* to allow retransmission of lost data if necessary). If the client is
running on a memory-
* constrained device (e.g. mobile app) and the maximum payload size is
too high, it might
* result in an {@link OutOfMemoryError}.
*
* This method must not be called when the uploader has currently an open
connection to the
* remote server. In general, try to set the payload size before invoking
{@link #uploadChunk()}
* the first time.
*
* @see #getRequestPayloadSize()
*
152
* @param size Number of bytes for a single payload
* @throws IllegalStateException Thrown if the uploader currently has a
connection open
*/
public void setRequestPayloadSize(int size) throws IllegalStateException
{
if (connection != null) {
throw new IllegalStateException("payload size for a single
request must not be "
+ "modified as long as a request is in progress");
}
requestPayloadSize = size;
}
/**
* Get the current maximum payload size for a single request.
*
* @see #setChunkSize(int)
*
* @return Number of bytes for a single payload
*/
public int getRequestPayloadSize() {
return requestPayloadSize;
}
/**
* Upload a part of the file by reading a chunk from the InputStream and
writing
* it to the HTTP request's body. If the number of available bytes is
lower than the chunk's
* size, all available bytes will be uploaded and nothing more.
* No new connection will be established when calling this method,
instead the connection opened
* in the previous calls will be used.
* The size of the read chunk can be obtained using {@link
#getChunkSize()} and changed
* using {@link #setChunkSize(int)}.
* In order to obtain the new offset, use {@link #getOffset()} after this
method returns.
*
* @return Number of bytes read and written.
* @throws IOException Thrown if an exception occurs while reading from
the source or writing
* to the HTTP request.
*/
public int uploadChunk() throws IOException, ProtocolException {
openConnection();
153
int bytesToRead = Math.min(getChunkSize(), bytesRemainingForRequest);
int bytesRead = input.read(buffer, bytesToRead);
if (bytesRead == -1) {
// No bytes were read since the input stream is empty
return -1;
}
// Do not write the entire buffer to the stream since the array will
// be filled up with 0x00s if the number of read bytes is lower then
// the chunk's size.
output.write(buffer, 0, bytesRead);
output.flush();
offset += bytesRead;
bytesRemainingForRequest -= bytesRead;
if (bytesRemainingForRequest <= 0) {
finishConnection();
}
return bytesRead;
}
/**
* Upload a part of the file by read a chunks specified size from the
InputStream and writing
* it to the HTTP request's body. If the number of available bytes is
lower than the chunk's
* size, all available bytes will be uploaded and nothing more.
* No new connection will be established when calling this method,
instead the connection opened
* in the previous calls will be used.
* In order to obtain the new offset, use {@link #getOffset()} after this
method returns.
*
* This method ignored the payload size per request, which may be set
using
* {@link #setRequestPayloadSize(int)}. Please, use {@link
#uploadChunk()} instead.
*
* @deprecated This method is inefficient and has been replaced by {@link
#setChunkSize(int)}
* and {@link #uploadChunk()} and should not be used anymore.
The reason is, that
* this method allocates a new buffer with the supplied chunk
size for each time
* it's called without reusing it. This results in a high
number of memory
154
* allocations and should be avoided. The new methods do not
have this issue.
*
* @param chunkSize Maximum number of bytes which will be uploaded. When
choosing a value
* for this parameter you need to consider that the
method call will only
* return once the specified number of bytes have been
sent. For slow
* internet connections this may take a long time.
* @return Number of bytes read and written.
* @throws IOException Thrown if an exception occurs while reading from
the source or writing
* to the HTTP request.
*/
@Deprecated public int uploadChunk(int chunkSize) throws IOException,
ProtocolException {
openConnection();
byte[] buf = new byte[chunkSize];
int bytesRead = input.read(buf, chunkSize);
if (bytesRead == -1) {
// No bytes were read since the input stream is empty
return -1;
}
// Do not write the entire buffer to the stream since the array will
// be filled up with 0x00s if the number of read bytes is lower then
// the chunk's size.
output.write(buf, 0, bytesRead);
output.flush();
offset += bytesRead;
return bytesRead;
}
/**
* Get the current offset for the upload. This is the number of all bytes
uploaded in total and
* in all requests (not only this one). You can use it in conjunction
with
* {@link TusUpload#getSize()} to calculate the progress.
*
* @return The upload's current offset.
*/
public long getOffset() {
return offset;
}
155
/**
* This methods returns the destination {@link URL} of the upload.
* @return The {@link URL} of the upload.
*/
public URL getUploadURL() {
return uploadURL;
}
/**
* Set the proxy that will be used when uploading.
*
* @param proxy Proxy to use
*/
public void setProxy(Proxy proxy) {
this.proxy = proxy;
}
/**
* This methods returns the proxy used when uploading.
*
* @return The {@link Proxy} used for the upload or null when not set.
*/
public Proxy getProxy() {
return proxy;
}
/**
* Finish the request by closing the HTTP connection and the InputStream.
* You can call this method even before the entire file has been
uploaded. Use this behavior to
* enable pausing uploads.
* This method is equivalent to calling {@code finish(false)}.
*
* @throws ProtocolException Thrown if the server sends an unexpected
status
* code
* @throws IOException Thrown if an exception occurs while cleaning up.
*/
public Optional<TusResponseBody> finish() throws ProtocolException,
IOException {
return finish(true);
}
/**
* Finish the request by closing the HTTP connection. You can choose
whether to close the InputStream or not.
* You can call this method even before the entire file has been
uploaded. Use this behavior to
156
* enable pausing uploads.
* Be aware that it doesn't automatically release local resources if
{@code closeStream == false} and you do
* not close the InputStream on your own. To be safe use {@link
TusUploader#finish()}.
* @param closeInputStream Determines whether the InputStream is closed
with the HTTP connection. Not closing the
* Input Stream may be useful for future upload a
future continuation of the upload.
* @throws ProtocolException Thrown if the server sends an unexpected
status code
* @throws IOException Thrown if an exception occurs while cleaning up.
*/
public Optional<TusResponseBody> finish(boolean closeInputStream) throws
ProtocolException, IOException {
Optional<TusResponseBody> response = finishConnection();
if (upload.getSize() == offset) {
client.uploadFinished(upload);
}
// Close the TusInputStream after checking the response and closing
the connection to ensure
// that we will not need to read from it again in the future.
if (closeInputStream) {
input.close();
}
return response;
}
private Optional<TusResponseBody> finishConnection() throws
ProtocolException, IOException {
if (output != null) {
output.close();
}
if (connection == null) {
return Optional.empty();
}
int responseCode = connection.getResponseCode();
TusResponseBody response = new TusResponseBody(connection);
connection.disconnect();
if (responseCode == 401 || responseCode == 403) {
throw new Http401And403CodeException(response, connection);
}
if(responseCode == 422) {
throw new Http422CodeException(response, connection);
157
}
if (!(responseCode >= 200 && responseCode < 300)) {
throw new ProtocolException("unexpected status code (" +
responseCode + ") while uploading chunk",
connection);
}
// TODO detect changes and seek accordingly
long serverOffset = getHeaderFieldLong(connection, "Upload-Offset");
if (serverOffset == -1) {
throw new ProtocolException("response to PATCH request contains
no or invalid Upload-Offset header",
connection);
}
if (offset != serverOffset) {
throw new ProtocolException(
String.format("response contains different Upload-Offset
value (%d) than expected (%d)",
serverOffset,
offset),
connection);
}
connection = null;
return Optional.of(response);
}
private long getHeaderFieldLong(URLConnection connection, String field) {
String value = connection.getHeaderField(field);
if (value == null) {
return -1;
}
try {
return Long.parseLong(value);
} catch (NumberFormatException e) {
return -1;
}
}
}
158
Clase:: Demo.java
package pe.gob.sunat.tecnologia.client.tus.main;
import java.io.File;
import java.io.IOException;
import java.net.URL;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import io.tus.java.client.HttpErrorCodeException;
import io.tus.java.client.ProtocolException;
import io.tus.java.client.TusClientCustom;
import io.tus.java.client.TusExecutor;
import io.tus.java.client.TusResponseBody;
import io.tus.java.client.TusURLMemoryStore;
import io.tus.java.client.TusUpload;
import io.tus.java.client.TusUploaderCustom;
public class Demo {
private static final String TOKEN = "";
private static final String HOST_PUBLICA = "https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/";
private static final String END_POINT_PROPUESTA =
"libros/rvierce/receptorpropuesta/web/propuesta/upload";
private static final Logger log = LoggerFactory.getLogger(Demo.class);
public static void main(String[] args) {
try {
// Create a new TusClient instance
final TusClientCustom client = new TusClientCustom();
client.setUploadCreationURL(new URL(HOST_PUBLICA +
END_POINT_PROPUESTA));
client.enableResuming(new TusURLMemoryStore());
Map<String, String> headers = new HashMap<>();
headers.put("authorization", "Bearer " + TOKEN);
client.setHeaders(headers);
File archivo = new File(
159
"D:\\migeigv\\archivos\\ajuste_posterior\\LE2010001749120231100140400
03111201.zip"
);
final TusUpload upload = new TusUpload(archivo);
String[] extension = archivo.getName().split("\\.");
Map<String, String> metaData = new HashMap<>();
metaData.put("filename", archivo.getName());
metaData.put("filetype", extension[1]);
metaData.put("numRuc", "20108745216");
metaData.put("perTributario", "202304");
metaData.put("codOrigenEnvio", "3");
metaData.put("codLibro", "140000");
metaData.put("codProceso", "1");
metaData.put("codTipoCorrelativo", "1");
metaData.put("nomArchivoImportacion", archivo.getName());
upload.setMetadata(metaData);
log.info("Starting upload...");
TusExecutor executor = new TusExecutor() {
@Override
protected void makeAttempt() throws ProtocolException, IOException {
TusUploaderCustom uploader = client.resumeOrCreateUpload(upload);
uploader.setChunkSize(1024);
do {
long totalBytes = upload.getSize();
long bytesUploaded = uploader.getOffset();
double progress = (double) bytesUploaded / totalBytes * 100;
String porcentaje = String.format("%06.2f%%", progress);
log.info("Upload at {}.", porcentaje);
} while (uploader.uploadChunk() > -1);
Optional<TusResponseBody> response = uploader.finish();
response.ifPresent(resp -> {
log.info(
"************** ==============> code: {} message: {}
<=============================== *****************",
resp.getResponseCode(),
resp.getResponseMessage()
);
log.info(
"************** ==============> Result {} {}
<=============================== *****************",
"20108745216",
resp.getResponseBody()
);
});
}
};
160
executor.makeAttempts();
} catch (HttpErrorCodeException e) {
log.info(
"************** ==============> code: {} message: {}
<=============================== *****************",
e.getResponseBody().getResponseCode(),
e.getResponseBody().getResponseMessage()
);
log.error("Error en la peticion: {}", e.getResponseBody(), e);
} catch (ProtocolException e) {
log.error("/////// //// ==> Error inesperado en la petición: ", e);
} catch (IOException e) {
e.printStackTrace();
} catch (Exception ex) {
log.error("ex.getCause(): {}", ex.getMessage(), ex);
}
}
}