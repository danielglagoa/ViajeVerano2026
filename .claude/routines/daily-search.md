# Rutina diaria — Búsqueda alojamiento Valencia / Gandía 2026

Esta rutina debe ejecutarse ENTERA y en orden. No omitas ningún paso.

---

## VARIABLES DEL DÍA

- TODAY: fecha actual en formato YYYY-MM-DD
- ENVIRONMENT: "CI" si la variable de entorno CI=true; "web" en caso contrario

---

## PASO 1 — BOOKING.COM (9 búsquedas)

Usa la herramienta `mcp__Booking-com__accommodations_search` (o el nombre exacto
disponible para Booking.com en este entorno).

### Zonas
| ID | Destino (destination) |
|----|----------------------|
| Z1 | Platja de Gandia, Spain |
| Z2 | La Malvarrosa, Valencia, Spain |
| Z3 | El Cabanyal-Canyamelar, Valencia, Spain |

### Fechas
| ID | checkin_date | checkout_date |
|----|-------------|---------------|
| F1 | 2026-07-10  | 2026-07-12    |
| F2 | 2026-07-17  | 2026-07-19    |
| F3 | 2026-07-24  | 2026-07-26    |

### Parámetros fijos para CADA búsqueda
```
number_of_adults : 5
price.maximum    : 325        ← 650 € total / 2 noches = 325 €/noche (la API filtra por noche)
user_country_code: "es"
user_locale      : "es"
```

Realiza las 9 combinaciones (Z1×F1, Z1×F2, Z1×F3, Z2×F1, …, Z3×F3).

### Reintento con coordenadas
Si una zona devuelve error `not_found` o 0 resultados, reintenta UNA VEZ usando
coordenadas en lugar del nombre (radio 2 km):

| Zona | latitude  | longitude |
|------|-----------|-----------|
| Z1   | 38.9953   | -0.1540   |
| Z2   | 39.4790   | -0.3200   |
| Z3   | 39.4699   | -0.3264   |

### Datos a extraer por cada resultado
- nombre del alojamiento
- zona (nombre del destino que se buscó)
- fechas (checkin–checkout)
- precio por noche según la API
- **precio total** = precio_noche × 2 (duración de todas las estancias es 2 noches)
- precio por persona = precio_total / 5
- valoración (rating/puntuación)
- URL / link del alojamiento

---

## PASO 2 — AIRBNB (9 búsquedas web)

Usa WebSearch para cada una de las 9 combinaciones con estas queries:

```
"Airbnb Platja de Gandia 10 al 12 julio 2026 5 personas precio total"
"Airbnb Platja de Gandia 17 al 19 julio 2026 5 personas precio total"
"Airbnb Platja de Gandia 24 al 26 julio 2026 5 personas precio total"
"Airbnb La Malvarrosa Valencia 10 al 12 julio 2026 5 personas precio"
"Airbnb La Malvarrosa Valencia 17 al 19 julio 2026 5 personas precio"
"Airbnb La Malvarrosa Valencia 24 al 26 julio 2026 5 personas precio"
"Airbnb El Cabanyal Valencia 10 al 12 julio 2026 5 personas alquiler precio"
"Airbnb El Cabanyal Valencia 17 al 19 julio 2026 5 personas alquiler precio"
"Airbnb El Cabanyal Valencia 24 al 26 julio 2026 5 personas alquiler precio"
```

Por cada resultado extraído anota:
- nombre o descripción breve del alojamiento
- zona exacta (la misma que se buscó)
- fechas (checkin–checkout)
- precio total estimado para la estancia completa; si no está claro escribe
  "precio no confirmado, revisar en el enlace"
- URL del anuncio (Airbnb o agregador)

---

## PASO 3 — FILTRADO Y CLASIFICACIÓN

Separa TODOS los resultados (Booking + Airbnb) en dos grupos:

**Grupo A — Dentro de presupuesto**: precio total ≤ 650 €
**Grupo B — Fuera de presupuesto**: precio total > 650 € (o desconocido)

Define:
- `X` = número total de resultados del Grupo A (ambas plataformas combinadas)
- `fallback_booking` = el resultado más barato del Grupo B en Booking.com
  (solo si no hay ninguno en el Grupo A de Booking.com)
- `fallback_airbnb` = el resultado más barato del Grupo B en Airbnb
  (solo si no hay ninguno en el Grupo A de Airbnb)

---

## PASO 4 — GENERAR CONTENIDO DEL EMAIL

### Asunto
```
Si X > 0:
  "Booking + Airbnb Valencia/Gandía {TODAY} — {X} oportunidades"

Si X = 0:
  "Booking + Airbnb Valencia/Gandía {TODAY} — 0 oportunidades dentro de presupuesto — alternativas más cercanas"
```

### Cuerpo (respetar este formato exacto)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BÚSQUEDA DIARIA ALOJAMIENTO — {TODAY}
5 adultos · presupuesto máximo 650 € total
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OPORTUNIDADES EN BOOKING.COM
────────────────────────────
[Si hay resultados ≤650 € total, uno por línea:]
• {nombre} | {zona} | {checkin}–{checkout} | {precio_total}€ total ({precio_persona}€/persona) | ⭐{valoración} | {url}

[Si no hay ninguno:]
Sin oportunidades dentro de presupuesto en Booking.com.

OPORTUNIDADES EN AIRBNB
────────────────────────
[Si hay resultados ≤650 € total, uno por línea:]
• {nombre} | {zona} | {checkin}–{checkout} | {precio_total}€ total ({precio_persona}€/persona) | {url}

[Si no hay ninguno:]
Sin oportunidades dentro de presupuesto en Airbnb.

[INCLUIR ESTA SECCIÓN SOLO SI X = 0:]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ALTERNATIVAS MÁS CERCANAS A TUS NECESIDADES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Booking.com: {nombre} | {zona} | {checkin}–{checkout} | {precio_total}€ total | {url}
             (o "Sin resultados disponibles para estas fechas/zonas")

Airbnb:      {nombre} | {zona} | {checkin}–{checkout} | {precio_aprox}€ aprox. | {url}
             (o "Sin resultados disponibles")
```

**REGLA OBLIGATORIA**: cada alojamiento listado DEBE incluir zona + fechas.
Nunca listar un precio o nombre sin esos dos datos.

---

## PASO 5 — ENVÍO / GUARDADO DEL EMAIL

### Si ENVIRONMENT = "web" (Claude Code on the web)
Usa `mcp__Gmail__create_draft` con:
```
to      : ["danielglagoa@gmail.com"]
subject : {asunto generado en Paso 4}
body    : {cuerpo generado en Paso 4}
```

### Si ENVIRONMENT = "CI" (GitHub Actions)
Escribe el asunto en `logs/email-subject.txt` (solo una línea, sin salto al final).
Escribe el cuerpo en `logs/email-body.txt` (texto plano).
El workflow de GitHub Actions se encargará de enviarlo por SMTP.

---

## PASO 6 — LOG

Añade UNA LÍNEA (sin reemplazar las anteriores) al fichero `logs/search-log.jsonl`:

```json
{"date":"{TODAY}","booking_total":N,"booking_within_budget":N,"airbnb_total":N,"airbnb_within_budget":N,"email_sent":true,"notes":""}
```

- `booking_total`: resultados totales devueltos por Booking.com (Grupo A + B)
- `booking_within_budget`: resultados Booking dentro de presupuesto (Grupo A)
- `airbnb_total`: resultados totales encontrados en web para Airbnb
- `airbnb_within_budget`: resultados Airbnb dentro de presupuesto
- `email_sent`: true si se creó el borrador o se escribió el archivo para envío
- `notes`: cualquier incidencia destacable (zona sin resultados, reintentos, etc.)
