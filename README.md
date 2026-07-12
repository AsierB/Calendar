# Festivos de Bilbao y Basauri para iPhone

Este proyecto descarga el calendario laboral de Open Data Euskadi, conserva las entradas correspondientes a **Bilbao/Bilbo** y **Basauri**, elimina duplicados y publica un único archivo `.ics`.

## Publicación

1. Ejecuta manualmente la acción `Actualizar calendario` desde la pestaña Actions.
2. En `Settings → Pages`, elige:
   - Source: `Deploy from a branch`
   - Branch: `main`
   - Folder: `/docs`
3. La dirección de suscripción será:

   `https://asierb.github.io/Calendar/festivos-bilbao-basauri.ics`

## Añadirlo en iPhone/iPad

`Ajustes → Apps → Calendario → Cuentas de calendario → Añadir cuenta → Otra → Añadir calendario suscrito`

Pega la URL publicada por GitHub Pages.

## Actualización

GitHub Actions regenera el calendario el día 1 de cada mes y también puede ejecutarse manualmente. Incluye el año actual y, cuando esté disponible, el siguiente.
