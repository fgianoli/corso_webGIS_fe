# Cartella `data/`

Dataset usati nel corso. Questa cartella è **montata read-only** dentro il
container GeoServer al path `/data` (vedi `docker-compose.yml`).

## File presenti

| File | Cosa contiene | Usato in |
|---|---|---|
| `poi-padova.geojson` | 12 punti di interesse di Padova | sorgente per il `.gpkg` (V4) |
| `padova-corso.gpkg` | GeoPackage con 3 layer: `poi`, `piste_ciclabili`, `quartieri` | V4, V5 (pubblicazione GeoServer) |
| `build_padova_gpkg.py` | Script Python che ri-genera il `.gpkg` da OSM | manutenzione |

> **Nota:** lo stesso `poi-padova.geojson` è duplicato in
> `frontend/src/data/poi-padova.geojson` perché serve anche al codice frontend
> (V3, V6, V7) che lo carica via `import poiData from "./data/poi-padova.geojson?url"`.
> Se aggiorni il file, **aggiorna entrambe le copie** (oppure tieni solo la sorgente
> qui in `data/` e usa un alias Vite — vedi sotto).

## I 3 layer dentro `padova-corso.gpkg`

| Layer | Tipo | Feature | Sorgente |
|---|---|---|---|
| `poi` | Point | 12 | `poi-padova.geojson` (curato a mano) |
| `piste_ciclabili` | LineString | ~2150 | OpenStreetMap via Overpass API (highway=cycleway, bicycle=designated, cycleway=lane/track) |
| `quartieri` | Polygon | 6 | **Fallback bbox** (vedi nota sotto) |

### Nota sui quartieri

Il layer `quartieri` nel `.gpkg` distribuito col corso contiene **6 poligoni rettangolari** generati come bbox approssimativi delle 6 ripartizioni del Comune di Padova. Sono OK per la didattica (basta che ci sia un layer di poligoni da pubblicare in GeoServer), ma **non sono i confini reali**.

I veri quartieri di Padova non sono mappati in OpenStreetMap come `boundary=administrative`/`admin_level=10`. Per averli reali:
1. Andare sul Geoportale del Comune di Padova (`https://geoportalegis.comune.padova.it/`)
2. Scaricare lo shapefile delle "Unità urbane" o "Quartieri amministrativi"
3. Sostituire il layer `quartieri` nel `.gpkg`:
   ```bash
   ogr2ogr -update -overwrite -nln quartieri \
       data/padova-corso.gpkg quartieri-reali.shp
   ```

## Schema dei POI

Ogni feature in `poi-padova.geojson` (e nel layer `poi` del `.gpkg`) ha:

| Property | Tipo | Esempio |
|---|---|---|
| `id` | int | `1` |
| `name` | string | `"Prato della Valle"` |
| `category` | string | `piazza` / `monumento` / `parco` / `istituzione` / `trasporti` |
| `description` | string | testo breve |

Le categorie sono usate nei video V3 (cluster), V5 (filtri CQL), V6 (espressioni `match`/`step`).

## Rigenerare `padova-corso.gpkg` da zero

```bash
# Dipendenze (dentro il container o nel sistema)
pip install geopandas pyogrio

# Esegui dalla root del repo
cd data
python3 build_padova_gpkg.py
```

Lo script:
- Legge i POI dal GeoJSON locale
- Scarica le piste ciclabili da Overpass (richiede ~1 min per la query)
- Genera quartieri di fallback (o, se trova relazioni admin in OSM, le usa)
- Combina tutto in `padova-corso.gpkg`

## (Opzionale) Eliminare la duplicazione del `poi-padova.geojson`

Se preferisci tenere il file solo qui in `data/` e referenziarlo dal frontend
senza duplicare, configura un alias in `frontend/vite.config.js`:

```js
import { defineConfig } from "vite";
import path from "path";

export default defineConfig({
  resolve: {
    alias: {
      "@data": path.resolve(__dirname, "../data"),
    },
  },
  // ...
});
```

E nel codice usa:

```js
import poiData from "@data/poi-padova.geojson?url";
```

Ma per il corso lasciamo la duplicazione — è didatticamente più semplice.

## Sostituire Padova con un'altra città

1. Sostituisci `poi-padova.geojson` con i tuoi POI (formato GeoJSON FeatureCollection)
2. Cambia il `BBOX` in `build_padova_gpkg.py` con quello della città target
3. Esegui lo script
4. Aggiorna le coordinate centro nel `frontend/src/main.js`
5. Sincronizza la copia in `frontend/src/data/poi-XXX.geojson`
