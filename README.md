# App para el recuento de vehiculos
Gabriel Furnieles\
Diciembre 2023

## Guía de uso
Antes de ejecutar ninguna instrucción, instalar requisitos (recomendable crear entorno virtual) `pip install -r requirements.txt`\
Para iniciar la aplicación ejecutar comando `python .\app.py`

### Ventana de carga de  vídeo
Tras iniciar aplicación se abrirá una venana de carga de video. Hacer click en _Load Video_ y selecciona archivo **.mp4** de tu dispositivo.\
Una vez se haya cargado el vídeo, se mostrará el primer fotograma del mismo en la ventana.
>❗El algoritmo implementado en esta aplicación funciona para vídeos donde la cámara es estática y el fondo permanece invariante.

### Crear máscara  
A continuación se debe demarcar la zona de recuento de vehículos. Para ello hacer click en botón _Mask Video_.\
Se abrirán dos nuevas ventanas, una con las instrucciones del editor de máscara y otra con el propio Mask Editor (por favor, asegúrese de que se encuentra en la ventana Mask Editor y no en la de carga de video).\
Tras terminar de crear la máscara, seleccionar _Save Mask_ para guardarla.

> ⚡ Ten en cuenta que el algoritmo de conteo solo verá la zona segmentada por la máscara. Esto puede ayudar a reducir el número de elementos que se desean contar o determinar líneas de conteo.


### Iniciar algoritmo de conteo
Finalmente, después de guardar la máscara, la opción _Start Counting_ se mostrará activada. Al seleccionarla, dos ventanas nuevas se abrirán para mostrar el proceso de conteo y se inicirá el conteo de los objetos en movimiento del vídeo. 