# ViajeVerano2026 — Rutina diaria de búsqueda de alojamiento

## Contexto del proyecto
Búsqueda automática diaria de alojamiento para 5 adultos en la zona de Valencia/Gandía
durante el verano de 2026. Presupuesto máximo: **650 € total por estancia** (estancias de 2 noches).

---

## INSTRUCCIONES PARA LA SESIÓN PROGRAMADA

Cuando esta sesión se ejecuta, sigue los pasos 1–5 exactamente en este orden.
No omitas ningún paso. No pidas confirmación entre pasos.

---

## PASO 1 — Búsquedas en Booking.com (9 combinaciones)

Ejecuta las siguientes 9 búsquedas usando `mcp__Booking-com__accommodations_search`.

### Zonas y coordenadas de fallback
| Zona (destination) | lat_fallback | lng_fallback |
|---|---|---|
| `Platja de Gandia, Spain` | 38.9936 | -0.1603 |
| `La Malvarrosa, Valencia, Spain` | 39.4850 | -0.3264 |
| `El Cabanyal-Canyamelar, Valencia, Spain` | 39.4727 | -0.3268 |

### Fechas (3 combinaciones por zona)
| checkin_date | checkout_date |
|---|---|
| 2026-07-10 | 2026-07-12 |
| 2026-07-17 | 2026-07-19 |
| 2026-07-24 | 2026-07-26 |

### Parámetros fijos por búsqueda
```
number_of_adults: 5
price.maximum: 325        ← NOTA: la API filtra POR NOCHE; 325€/noche × 2 noches = 650€ total
user_country_code: "es"
user_locale: "es"
currency: "EUR"
```
Pasa también `user_query` con algo como: "alojamiento para 5 adultos en [zona] [fechas] máximo 650€ total estancia".

Usa `max_results: 10` si el conector lo soporta; si no, acepta los resultados por defecto.

### Manejo de errores
- Si una búsqueda por `destination` devuelve 0 resultados o error `not_found`:
  reintenta **una sola vez** usando `coordinates` (lat/lng de la tabla + `radius: 2`).
- Si el reintento también falla, registra la combinación como "sin resultados" y continúa.

### Procesado de resultados de Booking.com
Para cada resultado devuelto:
1. Calcula `precio_total = precio_por_noche × 2` (2 noches).
2. Calcula `precio_por_persona = precio_total / 5`.
3. Considera el resultado **dentro de presupuesto** si `precio_total ≤ 650`.
4. Guarda: nombre, zona, fechas, precio_total, precio_por_persona, valoración (review score), link.

---

## PASO 2 — Búsquedas de Airbnb (9 combinaciones, vía WebSearch)

Para cada una de las 9 combinaciones zona × fechas, haz una búsqueda con `WebSearch`
usando el siguiente formato de query:

```
Airbnb [zona simplificada] [checkin] [checkout] 5 personas alquiler completo
```

Ejemplos:
- `Airbnb Platja de Gandia 10 julio 12 julio 2026 5 personas alquiler`
- `Airbnb Malvarrosa Valencia 17 julio 19 julio 2026 5 personas`
- `Airbnb Cabanyal Valencia 24 julio 26 julio 2026 5 adultos`

De los resultados web, extrae para cada alojamiento encontrado:
- Nombre / descripción breve
- Zona
- Fechas (checkin–checkout)
- Precio aproximado total para la estancia (si figura)
- Link (URL de Airbnb o del agregador que lo muestre)

Si el precio no aparece explícitamente: anota `"precio no confirmado, revisar en el enlace"`.
Considera dentro de presupuesto solo si el precio total aparece de forma explícita y es ≤ 650 €.

---

## PASO 3 — Filtrado y clasificación

### Grupo A: Resultados dentro de presupuesto
- Booking.com: todos los resultados con `precio_total ≤ 650 €`
- Airbnb: todos los resultados con precio total explícito ≤ 650 €

### Grupo B: Fallback (solo si el Grupo A de una plataforma está vacío)
- Si ningún resultado de **Booking.com** cumple presupuesto → identifica el más barato de toda
  la búsqueda de Booking como "resultado más cercano a las necesidades".
- Si ningún resultado de **Airbnb** cumple presupuesto → identifica el más barato/relevante
  encontrado en Airbnb como "resultado más cercano a las necesidades".

Calcula `X = total de resultados en Grupo A (ambas plataformas combinadas)`.

---

## PASO 4 — Correo electrónico (borrador Gmail)

Usa `mcp__Gmail__create_draft` con estos parámetros:

### Destinatario
`to: ["danielglagoa@gmail.com"]`

### Asunto
- Si X > 0: `"Booking + Airbnb Valencia/Gandía [FECHA_HOY] — X oportunidades"`
- Si X = 0: `"Booking + Airbnb Valencia/Gandía [FECHA_HOY] — 0 oportunidades dentro de presupuesto — alternativas más cercanas"`

Reemplaza `[FECHA_HOY]` con la fecha actual en formato DD/MM/YYYY.
Reemplaza `X` con el número real.

### Cuerpo del correo (htmlBody)

Usa el siguiente template HTML, rellenando con los datos reales:

```html
<html><body style="font-family:Arial,sans-serif;font-size:14px;color:#333">

<h2>🏖️ Búsqueda diaria — Valencia/Gandía [FECHA_HOY]</h2>
<p><strong>Parámetros:</strong> 5 adultos · máx. 650€ total por estancia (2 noches)</p>
<p><strong>Zonas:</strong> Platja de Gandia · La Malvarrosa · El Cabanyal-Canyamelar<br>
<strong>Fechas buscadas:</strong> 10–12 jul · 17–19 jul · 24–26 jul</p>

<hr>

<h3>📗 Oportunidades en Booking.com</h3>

<!-- SI hay resultados Grupo A de Booking: -->
<ul>
  <!-- Por cada resultado: -->
  <li>
    <strong>[Nombre del alojamiento]</strong><br>
    📍 Zona: [zona] · 📅 Fechas: [checkin] – [checkout]<br>
    💶 Precio total: [X]€ · Por persona: [X/5]€ · ⭐ Valoración: [score]/10<br>
    🔗 <a href="[link]">Ver en Booking.com</a>
  </li>
</ul>

<!-- SI NO hay resultados Grupo A de Booking: -->
<p><em>Sin oportunidades dentro de presupuesto en Booking.com para estas fechas y zonas.</em></p>

<hr>

<h3>🏡 Oportunidades en Airbnb</h3>

<!-- SI hay resultados Grupo A de Airbnb: -->
<ul>
  <!-- Por cada resultado: -->
  <li>
    <strong>[Nombre/descripción]</strong><br>
    📍 Zona: [zona] · 📅 Fechas: [checkin] – [checkout]<br>
    💶 Precio aprox.: [X]€ total<br>
    🔗 <a href="[link]">Ver en Airbnb</a>
  </li>
</ul>

<!-- SI NO hay resultados Grupo A de Airbnb: -->
<p><em>Sin oportunidades dentro de presupuesto en Airbnb para estas fechas y zonas.</em></p>

<!-- SOLO SI X=0 en total, añadir esta sección: -->
<hr>
<h3>⚠️ Alternativas más cercanas a tus necesidades</h3>
<p>Esta sección aparece solo cuando ningún resultado cumple el presupuesto de 650€.</p>
<ul>
  <li>
    <strong>Booking.com:</strong>
    [nombre] — 📍 [zona] · 📅 [checkin]–[checkout] · 💶 [precio_total]€ total
    · 🔗 <a href="[link]">Ver</a>
    <br><em>(o: "sin resultados disponibles para estas fechas/zona")</em>
  </li>
  <li>
    <strong>Airbnb:</strong>
    [nombre] — 📍 [zona] · 📅 [checkin]–[checkout] · 💶 [precio_aprox]€ aprox.
    · 🔗 <a href="[link]">Ver</a>
    <br><em>(o: "sin resultados disponibles")</em>
  </li>
</ul>

<hr>
<p style="font-size:12px;color:#888">
  Generado automáticamente el [FECHA_HOY] a las 09:00 (Madrid) por la rutina ViajeVerano2026.<br>
  ⚠️ Este mensaje es un borrador en Gmail. Revísalo y envíalo manualmente si lo deseas,
  o simplemente úsalo como referencia de los resultados del día.
</p>

</body></html>
```

**REGLA OBLIGATORIA**: Cada alojamiento listado, sin excepción, debe indicar explícitamente
la FECHA (checkin–checkout) y el LUGAR (zona). Nunca listar precio sin esos dos datos.

---

## PASO 5 — Log

Añade una línea al fichero `logs/busqueda_log.csv` con este formato:

```
YYYY-MM-DD,<booking_oportunidades>,<airbnb_oportunidades>,<total_X>,<notas>
```

- `booking_oportunidades`: número de resultados ≤650€ encontrados en Booking.com
- `airbnb_oportunidades`: número de resultados ≤650€ encontrados en Airbnb
- `total_X`: suma de los dos anteriores
- `notas`: puede ser vacío, o indicar algo relevante como "Zona Gandia sin resultados",
  "Airbnb sin precios explícitos", etc.

Después de añadir la línea, haz `git add logs/busqueda_log.csv && git commit -m "log: búsqueda [FECHA]" && git push -u origin claude/adoring-maxwell-kdisul`.

---

## PASO 6 — Notificación push (PushNotification)

Si la herramienta `PushNotification` está disponible en la sesión, envía una notificación
al finalizar la rutina con el resumen:

```
<routine_summary>
Rutina ViajeVerano2026 completada — [FECHA_HOY].
Oportunidades encontradas: X (Booking: N, Airbnb: M).
[Si X>0: "Hay resultados dentro de presupuesto. Revisa el borrador en Gmail."]
[Si X=0: "Sin resultados dentro de 650€. Se incluyeron alternativas más cercanas en el borrador."]
Borrador guardado en Gmail: danielglagoa@gmail.com
</routine_summary>
```

---

## CONFIGURACIÓN DE SCHEDULE

**Cron expression (UTC):** `0 7 * * *`
→ equivale a 09:00 hora Madrid en verano (CEST = UTC+2)
→ en invierno (CET = UTC+1) sería 08:00 Madrid — ajustar a `0 8 * * *` en octubre

**Zona horaria recomendada si la plataforma lo soporta:** `Europe/Madrid` con cron `0 9 * * *`

**Prompt para la sesión programada:**
```
Ejecuta la rutina diaria de búsqueda de alojamiento descrita en CLAUDE.md.
Sigue todos los pasos en orden (1-6) sin pedir confirmación.
```

---

## Notas técnicas

- **Booking.com price.maximum**: La API filtra por precio/noche. Se usa 325€/noche
  (= 650€ total / 2 noches). El filtro final de 650€ total se aplica manualmente
  sobre los resultados devueltos.
- **Gmail**: El MCP disponible solo permite crear borradores (`create_draft`), no enviar
  directamente. El borrador aparecerá en la carpeta Borradores de Gmail.
- **Airbnb**: No existe conector oficial; se usa WebSearch para extraer resultados
  disponibles públicamente.
- **Log**: El fichero `logs/busqueda_log.csv` mantiene el histórico. Cada ejecución
  añade una fila.
