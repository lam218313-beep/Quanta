Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
• 1005 – El campo “perTributario” no enviado o es vacío
• 1006 – Formato de perTributario no cumple con el formato “yyyymm”
• 1007 – El perTributario de búsqueda no debe ser mayor a la fecha actual
• 1187 - El campo "factprorrata" no enviado o es vacío
5.14 Servicio Web Api consultar FV0621
Nombre Web
Services
Servicio Web Api consultar FV0621
Descripción Permite consultar los datos asociados al FV0621
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/propuesta/web?periodoSeleccionado
={periodoSeleccionado}&tipoInfo={tipoInfo}
Parámetros[URL] Param-formato-tipo Descripción
periodoSeleccionado -alfanumérico-String Periodo tributario (Obligatorio)
tipoInfo-alfanumérico-String Tipo de información (Opcional)
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
57
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
• 1005 - El campo “perTributario” no enviado o es vacío
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
58
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
Array Array - inicio
codTipoCDP-alfanumérico-string Tipo de Comprobante de Pago o Documento.
Solo permite los comprobantes de pago 00, 01, 03,
05, 06, 07, 08, 11, 12, 13, 14, 15, 16, 18, 21, 24, 25,
27, 28, 30, 32, 34, 35, 36, 37, 42, 43, 44, 45, 48, 49,
55 y 56 (Obligatorio)
numSerieCDP-alfanumérico-string Número de serie del comprobante de pago o
documento (Obligatorio)
numCDP-alfanumérico-string Número del comprobante de pago o documento
(Obligatorio)
codCar-alfanumérico-string Código de Anotación de Registro (CAR SUNAT)
(Obligatorio)
Array Array - fin
59
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
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
60
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
1 = Eliminar todo el preliminar, 2 = Eliminar
solo "No Domiciliados" (Obligatorio)
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
61
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
62
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
● 1348 - La extensión del archivo es diferente a “.zip”, por favor corregir
● 1346 - El tamaño del archivo comprimido en formato “.zip” debe ser menor o igual
a 6GB.
● 1350 - El tamaño del archivo mayor a 0 Kb.
● 1351 - Se ha producido un error al realizar el envío del archivo, por favor volver a
intentar el envío
● 1048 - Solo se permite dato numérico de 2 dígitos para el codTipoCorrelativo
● 1049 - El campo “codTipoCorrelativo” no enviado o es vacio
63
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
numAjustePosterior-alfanumérico-String Correlativo o numero de ajuste posterior
(Obligatorio)
codLibro-alfanumérico-String Código de libro: 080000 RCE (Obligatorio)
numTicket-alfanumérico-string Número de ticket de envío [AAAA99999999]
AAAA: Año
99: Tipo de correlativo
99999999: Número correlativo de envío
(Obligatorio)
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
64
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
HTTP status 200
Content-Type application/json
Evidencias URL
65
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
Descripción Servicio Web Api que permite al generador, importar un archivo conteniendo los ajustes
posteriores de operaciones con sujetos no domiciliados
66
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
● 1003 - El RUC ingresado no existe o no es válido
● 1005 - El campo “perTributario” no enviado o es vacío
67
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
68
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
69
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
documento (Opcional)
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
Result OK
70
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
71
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
● 1350 - El tamaño del archivo mayor a 0 Kb.
● 1351 - Se ha producido un error al realizar el envío del archivo, por favor volver a
intentar el envío
● 1048 - Solo se permite dato numérico de 2 dígitos para el codTipoCorrelativo
● 1049 - El campo “codTipoCorrelativo” no enviado o es vacio
● 1050 - Código tipo de Correlativo no permitido o no valido
● 1140 - El campo “codLibro” no enviado o es vacío
Tecnología Uso de la librería TUS.io para cliente.
5.25 Servicio Web Api enviar ajustes posteriores de periodos anteriores
72
Nombre Web
Services
Servicio Web Api enviar ajustes posteriores RC de periodos anteriores al sire
Descripción Permite registrar los preliminares de ajustes posteriores
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
Body
73
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
Descripción Permite eliminar comprobantes en ajustes posteriores RC bde periodos anteriores al SIRE
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/ajustesposteriores/web/ajustesposte
riores/{indTipoAjustePosterior}/{perTributario}/eliminarcomprobanteapparc
Parámetros[URL] Param-formato-tipo Descripción
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
indTipoAjustePosterior-numérico-int Tipo de ajuste posterior: 3 Ajuste Posteriores de
periodos anteriores general (Ver Anexo II: Tipo
de ajuste posterior) (Obligatorio)
Parámetros[body] Param-formato-tipo Descripción
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
74
detalleAjustes-array-array Array de detalles de ajustes - fin
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Content-type: application/x-www-form-urlencoded
Parámetros Valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: DELETE
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
• 1005 – El campo “perTributario” no enviado o es vacío
• 1006 – Formato de perTributario no cumple con el formato “yyyymm”
• 1007 – El perTributario de búsqueda no debe ser mayor a la fecha actual
• 2000 - El campo indTipoAjustePosterior no tiene asigando un valor válido
• 1104 - El código de tipo de comprobante de pago enviado no es válido
• 1323 - El campo "numSerieCDP" es nulo o vacío
• 1011 - El campo “codTipoCDP” no enviado o es vacío
• 1012 - El codTipoCDP ingresado no existe o no es válido
75
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
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
76
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
Descripción Permite registrar los preliminares de ajustes posteriores
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/ajustesposteriores/web/comprobant
esajuspost/{perTributario}/{numAjustePosterior}/{codLibro}/{numTicket}/registrarajustespos
terioresparcnd
Parámetros[URL] Param-formato-tipo Descripción
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
numAjustePosterior-alfanumérico-String Correlativo o numero de ajuste posterior
(Obligatorio)
codLibro-alfanumérico-String Código de libro: 080000 RCE (Obligatorio)
numTicket-alfanumérico-string Número de ticket de envío [AAAA99999999]
AAAA: Año
99: Tipo de correlativo
99999999: Número correlativo de
envío(Obligatorio)
Parámetros[body] No aplica
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
77
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
78
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
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: DELETE
Parámetros[salida] Parámetros Valor
HTTP status 200
Content-Type application/json
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/ajustesposteriores/web/1/202301/eli
minarcomprobanteapparcnd
Headers
Body
79
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
5.31 Servicio Web Api consultar estado ticket
Nombre Web
Services
Servicio Web Api consultar estado de envío de ticket.
Descripción Permite consultar el estado de envío del ticket.
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
numTicket-alfanumérico-string Número de ticket de envío [AAAA99999999]
AAAA: Año
99: Tipo de correlativo
99999999: Número correlativo de envío (Opcional)
page-numerico-int Ejemplo: 1 (Obligatorio)
perPage-numerico-int Ejemplo: 20 (Obligatorio)
Parámetros[body] No aplica
80
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Parámetros valor
Content-Type application/json
Accept application/json
Authorization Bearer token obtenido de la autenticación
Método: GET
Parámetros[salida] Parámetros de Salida Descripcion
paginacion-array-array Array de paginación - inicio
paginacion.page- numérico-Int Ejemplo: 1 (Obligatorio)
paginacion.perPage- numérico-Int Ejemplo: 20 (Obligatorio)
paginacion.totalRegistrosnumérico-Int
Total de registros (Obligatorio)
paginacion-array-array Array de paginación - fin
registros-array-array Array de registros - inicio
showReportesDescargaalfanumerico-String
Valores 0 y 1
0 - no muestra icono de archivo de texto
1 - muestra ícono de archivo de texto
perTributario-alfanumerico-String Periodo tributario
numTicket-alfanumerico-String Número de ticket de envío [AAAA99999999]
AAAA: Año
99: Tipo de correlativo
99999999: Número correlativo de envío
fecCargaImportacion- yyyy-mmdd,'T','hh:ii:ss'-Date
Fecha de la carga del archivo de importación, o fecha
de solicutud de generacion de archivo
Obligatorio
fecInicioProceso - yyyy-mm-dd –
Date
Fecha de la Inicio del archivo de importación, o fecha
de solicutud de generacion de archivo
Obligatorio
codProceso-alfanumerico-String Código del indicador de carga masiva.
(Ver Anexo I: Indicador de carga masiva)
desProceso-alfanumerico-String Descripcion del indicador de Carga Masiva.
(Ver Anexo I: Indicador de carga masiva)
codEstadoProceso-alfanumericoString
Código de estado de envio
desEstadoProceso-alfanumericoString
Descripción de estado de envio
nomArchivoImportacion--
alfanumerico-String
Nombre del archivo de importacion
detalleTicket-array-array Array detalle de ticket - inicio
detalleTicket.numTicketalfanumerico-String
Número de ticket de envío [AAAA99999999]
AAAA: Año
99: Tipo de correlativo
99999999: Número correlativo de envío
detalleTicket.fecCargaImportacio
n- yyyy-mm-dd-Date
Fecha de la carga del archivo de importación, o fecha
de solicitud de generacion de archivo
detalleTicket.horaCargaImportaci
on- hh:mm:ss'-Date
(DetalleTicket.fecCargaImportacion).- Hora de la
carga del archivo de importación, o fecha de solicitud
de generacion de archivo
detalleTicket.codEstadoEnvioalfanumérico-String
Código del Estado de envío
detalleTicket.desEstadoEnvio -
alfanumérico-String
Descripción del estado de envío
detalleTicket.
nomArchivoReporte -
alfanumérico-String
Nombre del a
detalleTicket.cntFilasvalidadanumérico-Integer
Cantidad de filas validadas o total de registros
81
detalleTicket.cntCPErrornumérico-Integer
Cantidad de comprobantes con error
detalleTicket.cntCPInformadosnumérico-Integer
Cantidad de CP informados
detalleTicket-array-array Array detalle de ticket - fin
archivoReporte-array-array Array archive reporte - inicio
archivoReporte.nomArchivoRepo
rte-alfanumerico-String
Nombre del archivo de reporte
codTipoAchivoReportealfanumerico-String
Código del tipo de archivo de reporte
archivoReporte-array-array Array archive reporte - fin
registros-array-array Array de registros - fin
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/gestionprocesosmasivos/web/ma
sivo/consultaestadotickets?perIni=202301&perFin=202301&page=1&perPage=20&numTicke
t=
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
• 1067 – El campo “perIni” no enviado o es vacío
• 1068 – Formato de perIni no cumple con el formato “yyyymm”
• 1069 – El perIni de búsqueda no debe ser mayor a la fecha actual
• 1071 – El campo “perFin” no enviado o es vacío
• 1072 – Formato de perFin no cumple con el formato “yyyymm”
• 1073 – El perFin de búsqueda no debe ser mayor a la fecha actual
82
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
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/gestionprocesosmasivos/web/ma
sivo/archivoreporte?nomArchivoReporte={nomArchivoReporte}&codTipoArchivoReporte={c
odTipoArchivoReporte}
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
(Obligatorio)
Nota: Si el campo codTipoAchivoReporte
que devuelve el API 5.31 es null, colocar
el mismo valor(null)
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
Parámetros[salida] Parámetros Valor
HTTP status 200
Content-Type application/json
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/gestionprocesosmasivos/web/ma
sivo/archivoreporte?nomArchivoReporte=20100176450-CPF-202302-
01.zip&codTipoArchivoReporte=01
Headers
83
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
• 1134 – El campo “nomArchivoReporte” no enviado o es vacío
• 2278 - El campo 'codTipoArchivoReporte' no enviado o es vacío
5.33 Servicio Web Api consultar año y mes del RCE
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
numEjercicio-alfanumérico-String Año o ejericicio
desEstado-alfanumérico-String Descripcion del ejercicio
lisPeriodos-array-array Array de lista de periodos - inicio
perTributario-alfanumérico-String Periodo tributario
codEstado-alfanumérico-String Código del estado del periodo tributario
desEstado-alfanumérico-String Descripcion del estado del periodo tributario
84
lisPeriodos-array-array Array de lista de periodos - fin
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/padron/web/omisos/080000/peri
odos
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
• 1140 – El campo “codLibro” no enviado o es vacío
• 1161 - Código de Libro no permitido o no válido
5.34 Servicio Web Api descargar propuesta
Nombre Web
Services
Servicio Web Api descargar propuesta
Descripción Permite descargar la propuesta de RCE.
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/propuesta/web/propuesta/{perTribut
ario}/exportacioncomprobantepropuesta?codTipoArchivo={codTipoArchivo}&codOrigenEnvi
o={codOrigenEnvio}&fecEmisionIni={fecEmisionIni}&fecEmisionFin={fecEmisionFin}&codTipo
CDP={codTipoCDP}&numSerieCDP={numSerieCDP}&numCDP={numCDP}&codInconsistencia=
{codInconsistencia}&codCar={codCar}&numDocAdquiriente={numDocAdquiriente}&mtoDesd
e={mtoDesde}&mtoHasta={mtoHasta}
Parámetros[URL] Param-formato-tipo Descripción
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
codTipoArchivo-numérico-Integer Código del tipo de archivo (0: txt, 1: csv)
(Obligatorio)
mtoDesde-Numerico-decimal128 Importe total del comprobante de pago.
85
Monto del rango inicial (monto total)
(Opcional)
mtoHasta-Numerico-decimal128 Importe total del comprobante de pago.
Monto final del rango (monto total) (Opcional)
codTipoCDP-alfanumérico-String Tipo de Comprobante de Pago o Documento.
Se puede descargar todos los comprobantes
de pado indicados en la tabla 03 del anexo 1
de la Resolución de Superintendencia 112-
2021/SUNAT y modificatorias (Opcional)
numSerieCDP-alfanumérico-string Número de serie del comprobante de pago o
documento (Obligatorio)
numCDP-alfanumérico-string Número del comprobante de pago o
documento (Obligatorio)
codInconsistencia-numérico-String Código de tipo de inconsistencia (Opcional)
codCar-alfanumerico-String Numero de identificación del comprobante
(Opcional)
fecEmisionIni-dd/mm/aaaa-String Fecha de emision inicio (Opcional)
fecEmisionFin-dd/mm/aaaa-String Fecha de emisión final (Opcional)
numDocAdquiriente-numerico-String Numero de documento del adquiriente
(Opcional)
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
86
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
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
rce generado, ajustes posteriores
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/resumen/web/resumencomproba
ntes/{perTributario}/{codTipoResumen}/{codTipoArchivo}/exporta?codLibro={codLibro}
Parámetros[URL] Param-formato-tipo Descripción
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
tipoReporte-alfanumérico-String Código del tipo de resumen:
-1 Resumen de propuesta
-2 Resumen de preliminar
-3 Resumen no Incluidos (V) o Excluidos(C)
-4 Resumen de registro
-5 Resumen de preliminar registrado
-6 Resumen ajustes posteriores
-7 Resumen no domiciliados
(Obligatorio)
tipoDescarga-numérico-int Extensión del archivo a exportar (Ver Anexo III:
87
Extension del archivo a descargar)
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
88
5.36 Servicio Web Api descargar resumen inconsistencias RCE
Nombre Web
Services
Servicio Web Api descargar resumen de inconsistencias RCE
Descripción Permite descargar el resumen de inconsistencias
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/resumen/web/resumeninconsiste
ncias/{perPeriodoTributario}?codTipoResumen={codTipoResumen}&codLibro={codLibro}
Parámetros[URL] Param-formato-tipo Descripción
perPeriodoTributario-alfanumérico-String Periodo tributario (Obligatorio)
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
Parámetros[salida] Parámetros de Salida Descripción
numRuc-alfanumérico-String número de ruc
perTributario-alfanumérico-String código de periodo
codTipoResumen-alfanumérico-String Código del tipo de resumen
cantidad-array-array Array cantidad - inicio
cantidad.porcentajeRelFiscalnumérico-decimal128
Porcentaje de cantidad de comprobantes con
inconsistencias Relacionadas al Crédito Fiscal
cantidad.porcentajeNoRelFiscalnumérico-decimal128
Porcentaje de cantidad de comprobantes con
inconsistencias No Relacionadas al Crédito Fiscal
cantidad.porcentajeSinValidacionesnumérico-decimal128
Porcentaje de cantidad de comprobantes sin
inconsistencias
cantidad.total-numérico-int Cantidad total de comprobantes en un
determinado periodo
cantidad-array-array Array cantidad - fin
monto-array-array Array monto - inicio
monto.porcentajeRelFiscal-numéricodecimal128
Porcentaje de montos de comprobantes con
inconsistencias Relacionadas al Crédito Fiscal en
un determinado periodo
monto.porcentajeNoRelFiscalnumérico-decimal128
Porcentaje de montos de comprobantes con
inconsistencias No Relacionadas al Crédito Fiscal
en un determinado periodo
monto.porcentajeSinValidacionesnumérico-decimal128
Porcentaje de montos de comprobantes sin
inconsistencias en un determinado periodo
monto.total-numérico-decimal128 Monto total de comprobantes en un
determinado periodo
monto-array-array Array monto - fin
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/resumen/web/resumeninconsiste
ncias/202301?codTipoResumen=1&codLibro=080000
Headers
89
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
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/propuesta/web/excluidos/{perTribut
ario}/exportaexcluidos?montoDesde={montoDesde}&montoHasta={montoHasta}&fecEmisio
nIni={fecEmisionIni}&fecEmisionFin={fecEmisionFin}&numRucCliente={numRucCliente}&codC
ar={codCar}&tipoDocumento={tipoDocumento}&codInconsistencia={codInconsistencia}&nu
mSerieCDP={numSerieCDP}&numCDP={numCDP}&codTipoArchivo={codTipoArchivo}&codOri
genEnvio={codOrigenEnvio}
Parámetros[URL] Param-formato-tipo Descripción
perTributario -alfanumérico-String Periodo tributario (Obligatorio)
montoDesde-decimal-Decimal Monto desde (Opcional)
montoHasta-decimal-Decimal Monto hasta (Opcional)
fecEmisionIni-dd/mm/aaaa-String Fecha de emisión del Comprobante de Pago o
documento - Inicio (Opcional)
fecEmisionFin-dd/mm/aaaa-String Fecha de emisión del Comprobante de Pago o
90
documento - FIN (Opcional)
numRucCliente-alfanumérico-String Número de RUC Cliente (Opcional)
codCar-alfanumérico-String CAR SUNAT (Opcional)
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
impuesto, según corresponda (Opcional)
numSerieCDP-Alfanumérico-String Número de serie del comprobante de pago o
documento (Opcional)
numCDP-Alfanumérico-String Número del comprobante de pago o
documento (Opcional)
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
91
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
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/libronodomiciliado/web/nodomicilia
dos/{perTributario}/eliminarcomprobantepreliminarnd
Parámetros[URL] Param-formato-tipo Descripción
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
Parámetros[body] Param-formato-tipo Descripción
noDomiciliados-array-array Array no domiciliados - inicio
codCar-alfanumérico-string Código de Anotación de Registro (CAR SUNAT)
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
92
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
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/preliminar/web/nodomiciliados/{per
Tributario}/exportapreliminarnd?codTipoArchivo={codTipoArchivo}&codOrigenEnvio={codOri
genEnvio}&mtoTotalDesde={mtoTotalDesde}&mtoTotalHasta={mtoTotalHasta}&fecEmisionIn
93
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
(Opcional)
mtoTotalHasta-Numerico-decimal128 Importe total del comprobante de pago.
Monto final del rango (monto total) (Opcional)
codTipoCDP-alfanumérico-String Tipo de Comprobante de Pago o Documento.
Se puede descargar todos los comprobantes
de pado indicados en la tabla 03 del anexo 1
de la Resolución de Superintendencia 112-
2021/SUNAT y modificatorias (Opcional)
numSerieCDP-alfanumérico-string Número de serie del comprobante de pago o
documento (Obligatorio)
numCDP-alfanumérico-string Número del comprobante de pago o
documento (Obligatorio)
fecEmisionIni-dd/mm/aaaa-String Fecha de emision inicio (Opcional)
fecEmisionFin-dd/mm/aaaa-String Fecha de emisión final (Opcional)
numDocAdquiriente-alfanuméricoString
Numero de documento del adquiriente
(Opcional)
numDocIdentidadClienteProveedoralfanumérico-String
Número de documento de identidad del
cliente / proveedor (Opcional)
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
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/preliminar/web/nodomiciliados/2022
06/exportapreliminarnd?codTipoArchivo=0&codOrigenEnvio=2&mtoTotalDesde=1000&mtoT
otalHasta=6000&fecEmisionIni=2022-06-02&fecEmisionFin=2022-06-
18&numDocIdentidadClienteProveedor=1234567891235&numSerieCDP=E001&numCDP=21
0&codTipoCDP=00&numDocAdquiriente=1234567891235
Headers
94
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
95
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
(Opcional)
mtoTotalHasta-Numerico-decimal128 Importe total del comprobante de pago.
Monto final del rango (monto total) (Opcional)
codTipoCDP-alfanumérico-String Tipo de Comprobante de Pago o Documento.
Se puede descargar todos los comprobantes
de pado indicados en la tabla 03 del anexo 1
de la Resolución de Superintendencia 112-
2021/SUNAT y modificatorias (Opcional)
numSerieCDP-alfanumérico-string Número de serie del comprobante de pago o
documento (Obligatorio)
numCDP-alfanumérico-string Número del comprobante de pago o
documento (Obligatorio)
fecDocumentoDesde-dd/mm/aaaaString
Fecha de emision inicio (Opcional)
fecDocumentoHasta-dd/mm/aaaaString
Fecha de emisión final (Opcional)
numDocAdquiriente-alfanuméricoString
Numero de documento del adquiriente
(Opcional)
numDocIdentidadClienteProveedoralfanumérico-String
Número de documento de identidad del
cliente / proveedor (Opcional)
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
96
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
rce generado, ajustes posteriores
97
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
Parámetros[salida] Parámetros de Salida Descripcion
Buffer- binary-binary buffer: Arreglo de bits
Evidencias URL
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rvierce/casillas/e/casillaspropuestas/202
201/reporte/1/txt
Headers
Body
(No aplica)
Result OK
Result Fail
{ "cod":"500", "msg":"Internal Server Error - Se presento una condicion inesperada que
impidio completar el Request", "exc":"java.lang.NullPointerException at ..." }
98
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
Descripción Permite descargar inconsistencias
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
99
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
Nombre Web
Services
Servicio Web Api descargar inconsistencias por montos totales
Descripción Permite exportar las inconsistencias por montos totales.
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
numTicket Número de ticket de envío [AAAA99999999]
AAAA: Año alfanumerico String
100
99: Tipo de correlativo
99999999: Número correlativo de envío
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
• 1059 - Código tipo de Archivo no permitido o no valido
• 1060 - Solo se permite dato numérico de 1 dígito para el codTipoArchivo
• 1061 - El campo "codTipoArchivo" es nulo o vacío
• 1140 - El campo “codLibro” no enviado o es vacío
5.44 Servicio Web Api descargar inconsistencias por comprobante pago
Nombre Web
Services
Servicio Web Api descargar inconsistencias por comprobantes de pago
Descripción Permite exportar las inconsistencias por comprobantes de pago.
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
documento – Inicio (Opcional)
fecEmisionFin-dd/mm/aaaa-String Fecha de emisión del Comprobante de Pago o
documento - FIN (Opcional)
codInconsistencia-alfanumerico-String Código de inconsistencia funcional o calculada,
101
ejemplo:
301 - Fecha de emisión del comprobante de
pago o fecha de pago del impuesto se anota
luego de los doce meses siguientes a la fecha
de emisión del comprobante o del pago del
impuesto, según corresponda. (Opcional)
numDocIdentidadClienteProveedorAlfanumérico-String
Número de RUC o Documento de Identidad del
cliente (Opcional)
codTipoCDP-Alfanumérico-String Tipo de Comprobante de Pago o Documento.
Solo permite los comprobantes de pago 00, 01,
03, 05, 06, 07, 08, 11, 12, 13, 14, 15, 16, 18, 21,
24, 25, 27, 28, 30, 32, 34, 35, 36, 37, 42, 43, 44,
45, 48, 49, 55 y 56 (Opcional)
numSerieCDP-Alfanumérico-String Número de serie del comprobante de pago o
documento (Opcional)
numCDP-Alfanumérico-String Número del comprobante de pago o
documento (Opcional)
codTipoArchivo-númerico-int Código del tipo de archivo a descargar (Ver
Anexo III: Extension del archivo a descargar)
(Obligatorio)
mtoTotalDesde-Numerico-decimal128 Importe total del comprobante de pago
(Opcional)
mtoTotalHasta-Numerico-decimal128 Importe total del comprobante de pago
(Opcional)
codEstado-alfanumerico-string Código de estado (Opcional)
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
102
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
• 1345- El campo "numDocIdentidadClienteProveedor", Solo números y letras
en mayusculas o minusculas de la A a la Z con un tamaño de 15 caracteres
• 1104 - El código de tipo de comprobante de pago enviado no es válido
• 1140 - El campo “codLibro” no enviado o es vacío
• 1161 - Código de libro no existe
• 1112 - El Monto Total Desde debe ser mayor o igual al Monto Total Hasta
• 1113 - Si se realiza busqueda por monto Total, se debe ingresar los campos
mtoTotalDesde y mtoTotalHasta
5.45 Servicio Web Api descargar ajustes posteriores
Nombre Web
Services
Servicio Web Api descargar ajustes posteriores
Descripción Permite exportar los ajustes posteriores del RCE, en caso no se haya cargado ningún archivo
entonces descarga la propuesta informativa de ajustes posteriores de la SUNAT.
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/ajustesposteriores/web/comprobant
esajuspost/{perTributario}/exportaajustesposterioresrc?codTipoArchivo={codTipoArchivo}&
&codOrigenEnvio={codOrigenEnvio}
Parámetros[URL] Param-formato-tipo Descripción
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
codTipoArchivo-numérico-int Código del tipo de archivo a descargar (Ver
Anexo III: Extension del archivo a
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
103
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
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/ajustesposteriores/web/comprobant
esajuspost/202301/exportaajustesposterioresrc?codTipoArchivo=0&codOrigenEnvio=2
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
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/ajustesposteriores/web/comprobant
esajuspost/{perTributario}/exportarajustesposterioresrcnd?codTipoArchivo={codTipoArchivo
}
Parámetros[URL] Param-formato-tipo Descripción
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
codTipoArchivo-numérico-int Código del tipo de archivo a descargar
(Ver Anexo III: Extension del archivo a
descargar) (Obligatorio)
Parámetros[body] No aplica.
104
Parámetros[header] Descripción:
Content-type: tipo de contenido a enviar
Valores:
Content-type: application/x-www-form-urlencoded
Parámetros Valor
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
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/ajustesposteriores/web/comprobant
105
esajuspost/{perTributario}/exportaajustesposterioresparc?codTipoArchivo={codTipoArchivo}
&indAjustePosteriorPle={indAjustePosteriorPle}&codOrigenEnvio={codOrigenEnvio}
Parámetros[URL] Param-formato-tipo Descripción
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
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
Mensaje Error { "cod":"422", "msg":"Unprocessable Entity - Se presentaron errores de validacion que
impidieron completar el Request", "errors":[ { "cod":"1001", "msg":"El campo “numRuc” no
enviado o es vacío" }] }
Lista de errores 422:
• 1005 – El campo “perTributario” no enviado o es vacío
• 1006 – Formato de perTributario no cumple con el formato “yyyymm”
• 1007 – El perTributario de búsqueda no debe ser mayor a la fecha actual
• 1059 - Código tipo de Archivo no permitido o no valido
106
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
https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/ajustesposteriores/web/co
mprobantesajuspost/202301/exportaajustesposterioresparcnd?codTipoArchivo=1
&codOrigenEnvio=2
Headers
Body
(No aplica)
Result OK
Result Fail
107
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
Descripción Permite descargar la constancia de recepción.
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
108
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
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/ajustesposteriores/web/ajustesposte
riores/{perTributario}/solicitardescarga?codTipoArchivo={codTipoArchivo}&codMoneda={cod
Moneda}&codProceso={codProceso}&codOrigen={codOrigenEnvio}&lisPeriodos={lisPeriodos}
Parámetros[URL] Param-formato-tipo Descripción
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
codTipoArchivo-numérico-int Código del tipo de archivo a descargar (Ver
Anexo III: Extension del archivo a descargar)
(Obligatorio)
codMoneda-alfanumérico-String Se considerará la moneda en que se emitió el
comprobante de pago
codProceso-alfanumérico-String Código de proceso
00 RCE No Domiciliados informado
01 RCE Cuando acepta la propuesta
02 RCE Cuando reemplaza la propuesta
(Obligatorio)
codOrigenEnvio-alfanumérico-string Código de origen de envío: 2 Servicio web
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
109
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
Url https://apisire.sunat.gob.pe/v1/contribuyente/migeigv/libros/rce/ajustesposteriores/web/ajustesposte
riores/{perTributario}/solicitardescarga?codTipoArchivo={codTipoArchivo}&codMoneda={cod
Moneda}&codProceso={codProceso}&codOrigen={codOrigen}&lisPeriodos={lisPeriodos}
Parámetros[URL] Param-formato-tipo Descripción
perTributario-alfanumérico-String Periodo tributario (Obligatorio)
110
codTipoArchivo-numérico-int Código del tipo de archivo a descargar (Ver Anexo III:
Extension del archivo a descargar) (Obligatorio)
codMoneda-alfanumérico-String Se considerará la moneda en que se emitió el
comprobante de pago
codProceso-alfanumérico-String Código de proceso
00 RCE No Domiciliados informado
01 RCE Cuando acepta la propuesta
02 RCE Cuando reemplaza la propuesta
(Obligatorio)
codOrigen-alfanumérico-String Código de origen de envío: 1 Portal web Obligatorio)
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