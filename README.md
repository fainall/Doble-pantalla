# Doble Pantalla

Usa una tablet Android como segundo monitor de un PC Windows por WiFi.

Arquitectura:

```
Windows (servidor Python)              Tablet Android (navegador)
+----------------------------+         +--------------------------+
| Monitor virtual (IDD)      |  WiFi   | Chrome / Firefox         |
|   capturado con DXGI/mss   | <-----> | <img> con frames JPEG    |
| WebSocket -> JPEG stream   |         | touch -> WebSocket -> PC |
+----------------------------+         +--------------------------+
```

## Requisitos

- PC con Windows 10/11.
- Python 3.10 o superior.
- Tablet Android con navegador moderno (Chrome).
- PC y tablet en la **misma red WiFi**.

## 1. Instalar un monitor virtual (para extender el escritorio)

Para que Windows trate la tablet como un monitor *real* y puedas mover ventanas
a ella, necesitas un *Indirect Display Driver* (IDD). Recomendado:

- **Virtual Display Driver** (open source):
  https://github.com/itsmikethetech/Virtual-Display-Driver

Tras instalarlo:

1. Abre **Configuracion -> Sistema -> Pantalla**.
2. Veras un monitor adicional. En *Varias pantallas* elige **Extender estas pantallas**.
3. Reorganiza la disposicion para que el monitor virtual quede a la derecha (o donde quieras).

> Si solo quieres **espejo** del monitor principal puedes saltarte este paso;
> arrancas el servidor con `--monitor 1` y veras la pantalla actual en la tablet.

## 2. Arrancar el servidor en el PC

Doble-click en `run.bat` (la primera vez crea el entorno virtual e instala
dependencias). O manualmente:

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python server.py --monitor 2
```

Listar los monitores disponibles:

```bat
python server.py --list
```

Opciones utiles:

| Flag | Descripcion | Default |
|---|---|---|
| `--monitor N` | Indice del monitor a enviar (1 = primario, 2 = virtual) | `1` |
| `--port P` | Puerto del servidor | `8080` |
| `--fps N` | Frames por segundo | `20` |
| `--quality Q` | Calidad JPEG (1-100) | `65` |
| `--max-width W` | Ancho maximo enviado a la tablet | `1280` |

Al arrancar, el servidor imprime la URL que tienes que abrir en la tablet,
por ejemplo:

```
Abre en la tablet: http://192.168.1.42:8080/
```

## 3. Conectar la tablet

Tienes dos clientes equivalentes:

- **App Android nativa** (recomendada): ver `android/README.md` para
  compilar e instalar el .apk. Abre la app y escribe `IP:8080`.
- **Navegador**: abre la URL impresa en consola en Chrome de la tablet.

Toca la pantalla para mover y pulsar el raton dentro del monitor capturado.

## 4. Generar .exe portable

Si no quieres tener Python en cada PC donde lo uses, ejecuta:

```bat
build_exe.bat
```

Crea `dist\DoblePantalla.exe`, un binario unico que arranca el servidor
con doble-click. Sin instalacion ni dependencias.

## Notas

- Si el firewall de Windows pregunta, **permite** el acceso a Python en
  redes privadas la primera vez que arrancas el servidor.
- La inyeccion de raton usa coordenadas de virtual desktop (`SendInput` con
  `MOUSEEVENTF_VIRTUALDESK`), por lo que funciona en el monitor extendido.
- MVP: streaming JPEG y un solo dedo como raton. Pendiente: WebRTC/H.264 para
  menos latencia, teclado, scroll, multi-touch.
