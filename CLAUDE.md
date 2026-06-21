# ViajeVerano2026 — Rutina diaria de búsqueda de alojamiento

Esta sesión es una **rutina programada** que se ejecuta todos los días a las **09:00 hora Madrid (Europe/Madrid)**.

## Objetivo
Buscar alojamiento en Valencia/Gandía para 5 personas en julio 2026, dentro de un presupuesto total de ≤650€ por estancia de 2 noches, en 3 zonas × 3 fechas = 9 combinaciones.

## Zonas de búsqueda
- Platja de Gandia, Spain
- La Malvarrosa, Valencia, Spain
- El Cabanyal-Canyamelar, Valencia, Spain

## Fechas objetivo
- 10-12 julio 2026
- 17-19 julio 2026
- 24-26 julio 2026

## Parámetros fijos
- Adultos: 5
- Presupuesto total: ≤650€ por estancia (2 noches)
- API Booking price.maximum: 325€/noche (= 650€ total / 2 noches)
- user_country_code: "es" | user_locale: "es"

## Comportamiento de la rutina (ejecutar en orden)

### Paso 1: Booking.com — 9 búsquedas paralelas
Usar `mcp__Booking-com__accommodations_search` para las 9 combinaciones zona×fecha.
- **Retry**: Si una zona devuelve `not_found` o `destination_not_found`, reintentar con coordenadas (radio 2km) y sin filtro de precio (filtrar en post-procesado).
- Coordenadas de fallback:
  - Platja de Gandia: lat 38.9957, lng -0.1534
  - La Malvarrosa: lat 39.4729, lng -0.3269
  - El Cabanyal-Canyamelar: lat 39.4673, lng -0.3283

### Paso 2: Airbnb — 9 búsquedas web paralelas
Usar `WebSearch` con queries tipo: "Airbnb [zona] [fechas] 5 personas alquiler"

### Paso 3: Filtrado
- Grupo A: resultados ≤650€ total → "Oportunidades"
- Grupo B: si ninguno cumple en una plataforma → identificar el más barato como fallback

### Paso 4: Email via Gmail
- Herramienta: `mcp__Gmail__create_draft` (el conector solo crea borradores — revisar y enviar manualmente)
- Destinatario: danielglagoa@gmail.com
- Asunto: `Booking + Airbnb Valencia/Gandía [YYYY/MM/DD] — X oportunidades`
- Si X=0 en total: `0 oportunidades dentro de presupuesto — alternativas más cercanas`
- Incluir siempre LUGAR y FECHAS en cada alojamiento listado

### Paso 5: Log
- Guardar `logs/YYYY-MM-DD.json` con estadísticas (fecha, nº resultados por plataforma, nº dentro de presupuesto)
- Hacer git commit y push a la rama `claude/adoring-maxwell-ov1scr`

## Cron schedule
```
Expresión:  0 9 * * *
Timezone:   Europe/Madrid
```
- Equivalente UTC verano (CEST = UTC+2): `0 7 * * *`
- Equivalente UTC invierno (CET = UTC+1): `0 8 * * *`

## Notas importantes
- La API de Booking usa precio **por noche**; el presupuesto del usuario es **por estancia total** (2 noches). Filtrar siempre el resultado final por ≤650€ total.
- Las zonas La Malvarrosa y El Cabanyal están muy próximas (≈1km). Con radio 2km las búsquedas por coordenadas se solapan — es esperado y correcto.
- Guardar todos los resultados encontrados en el log, no solo los que cumplen el presupuesto.
