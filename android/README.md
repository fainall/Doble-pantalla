# App Android - Doble Pantalla

Cliente Android nativo que recibe el stream del servidor y envia toques.

## Compilar el .apk

Opcion A - **Android Studio** (lo mas comodo):

1. Instala Android Studio (Hedgehog 2023.1.1 o posterior).
2. *File -> Open*, selecciona la carpeta `android/`.
3. Android Studio descarga el SDK y genera el Gradle wrapper.
4. *Build -> Build Bundle(s) / APK(s) -> Build APK(s)*.
5. El .apk queda en `app/build/outputs/apk/debug/app-debug.apk`.

Opcion B - **Linea de comandos** (necesitas JDK 17 + Android SDK):

```bash
cd android
# La primera vez genera el wrapper:
gradle wrapper --gradle-version 8.10.2
./gradlew assembleRelease
# o assembleDebug para version de prueba
```

El .apk de release sin firmar queda en `app/build/outputs/apk/release/`.

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
