# App Android - Doble Pantalla

Cliente Android nativo que recibe el stream del servidor y envia toques.

## Compilar el .apk (sin Android Studio)

Tres caminos. Elige el que mas te guste:

### Opcion A - GitHub Actions (cero instalacion)

1. Haz push de esta rama (ya esta hecho).
2. Ve al repo en GitHub -> pestana **Actions** -> workflow **Build APK**.
3. Espera a que termine (~3-5 min la primera vez).
4. Descarga el artefacto **DoblePantalla-debug-apk** del run.

El workflow `.github/workflows/build-apk.yml` se dispara en cada push
que toque `android/` y tambien manualmente desde *Run workflow*.

### Opcion B - Terminal de Windows (`build_apk.bat`)

Desde la raiz del repo, doble-click o:

```bat
build_apk.bat
```

Requiere **JDK 17** en el PATH (Temurin: https://adoptium.net/).
La primera ejecucion descarga el SDK de Android y Gradle (~2 GB) en
`%USERPROFILE%\.doblepantalla-build`. Las siguientes son rapidas.

Al terminar deja el apk en:
`android\app\build\outputs\apk\debug\app-debug.apk`

### Opcion C - Android Studio

Si ya lo tienes, *File -> Open* sobre la carpeta `android/` y
*Build -> Build APK(s)*.

## Instalar en la tablet

1. Activa *Origenes desconocidos* o *Instalar apps desconocidas* en la
   tablet para tu navegador / gestor de archivos.
2. Copia el .apk a la tablet (USB o nube) y abrelo para instalar.
3. Tambien con `adb install app-debug.apk` si tienes la tablet en modo
   depuracion USB.

## Uso

1. Arranca el servidor en el PC (`run.bat` o `python server.py --monitor 2`).
2. Anota la IP que imprime el servidor, p.ej. `192.168.1.42:8080`.
3. Abre la app **Doble Pantalla** en la tablet.
4. Escribe `192.168.1.42:8080` y pulsa **Conectar**.
5. Ya tienes la pantalla extendida en la tablet. Toca para mover el raton.

## Notas

- La app admite cleartext (`ws://`) porque el servidor local no usa TLS.
- Orientacion bloqueada en horizontal.
- minSdk 26 (Android 8.0).
