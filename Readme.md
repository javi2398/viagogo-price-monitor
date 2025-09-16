# Viagogo Price Monitor

Script en Python para **monitorizar precios de entradas en Viagogo** y **enviar alertas a Discord** cuando aparecen listados por debajo de un umbral definido. Gestiona el antibot del sitio tomando cookies con SeleniumBase y realiza las consultas posteriores con `tls_client` para minimizar bloqueos.

---

## ✨ Características

- ✅ Monitorización concurrente de múltiples eventos (un hilo por fila en `data.csv`).
- 🔐 Bypass básico del anti-bot con SeleniumBase (modo undetected) y `tls_client`.
- ⚡ Consultas rápidas a la API interna de Viagogo.
- 🔔 Notificaciones a Discord Webhook con imagen, sección/fila/asiento, cantidad y enlace de checkout.
- 🛡️ Manejo de rate limit/baneos con backoff y reintentos.

---

## 🧩 ¿Cómo funciona?

1. **Warm-up de cookies**  
   `challenge_handler()` abre el evento con SeleniumBase (`uc=True`), extrae cookies válidas y las inyecta en la sesión de `tls_client`.

2. **Scraping de la página del evento**  
   `fetch_event_page()` obtiene el HTML del evento y extrae:
   - `pageVisitId`
   - `categoryId`
   - `title` del evento

3. **Consulta de precios**  
   `fetch_prices()` llama a `Browse/VenueMap/GetMapAvailabilityAndPrices` con filtros predefinidos y calcula el **precio mínimo** disponible.

4. **Alerta si cumple umbral**  
   Si `precio < precioMaximo`, extrae detalles del listing (id, sección, fila, asiento, qty), compone la **URL de checkout** y envía un **embed a Discord** mediante `notification_viagogo()`.

5. **Ejecución concurrente**  
   `leer_csv_y_ejecutar_threads('data.csv')` crea un hilo por evento, con un pequeño *stagger* para evitar picos simultáneos.

---

## 📦 Requisitos

- **Python** 3.10+ recomendado
- **Google Chrome** instalado
- Dependencias:
  - [`tls_client`](https://pypi.org/project/tls-client/)
  - [`seleniumbase`](https://pypi.org/project/seleniumbase/)
  - Módulos locales:
    - `printColor.py` (logs con color)
    - `WebhookOk.py` (función `notification_viagogo` para enviar mensajes a Discord)

---

## 🔧 Instalación

```bash
# Clonar el repo
git clone https://github.com/javi2398/viagogo-price-monitor
cd viagogo-price-monitor

# Crear entorno virtual (opcional)
python -m venv .venv
# Activar en Windows
.venv\Scripts\activate
# Activar en macOS/Linux
source .venv/bin/activate

# Instalar dependencias
pip install -U pip
pip install tls_client seleniumbase




## Explicación detallada de data.csv

El archivo **`data.csv`** define **qué eventos** se monitorizan, **con qué umbral de precio**, y **a qué webhook** se envían las alertas. Debe ser **CSV válido con cabecera**.

### 📌 Columnas obligatorias

| Columna         | Tipo   | Obligatoria | Descripción                                                                                          |
|-----------------|--------|-------------|------------------------------------------------------------------------------------------------------|
| `enlace`        | texto  | ✅          | URL **completa** del evento en Viagogo. **Debe incluir** `?quantity=<n>`.                           |
| `precioMax`     | entero | ✅          | Umbral **por entrada** en euros. Se notifica si `precio_encontrado < precioMax`.                     |
| `discordWebhook`| texto  | ✅          | URL del webhook de Discord donde recibirás el embed con la oferta.                                   |

Se recomienda extraer los enlaces de 'https://www.viagogo.com/' puesto que marcan el precio más ajustado a las fees respecto a sus otros dominios.
### ✅ Ejemplo mínimo correcto

```csv
enlace,precioMax,discordWebhook
https://www.viagogo.com/Concert-Tickets/Rap-and-Hip-Hop-Music/Bad-Bunny-Tickets/E-158171526?quantity=2,150,https://discord.com/api/webhooks/XXXXXXXX/AAAAAAAA
