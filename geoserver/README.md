# Cartella `geoserver/`

Cartella di supporto per la configurazione di GeoServer.

I dati di GeoServer (workspace, store, layer, style) sono persistiti nel
**volume Docker** `geoserver_data` definito in `docker-compose.yml`. Quando
fai `docker compose down` i dati restano. Per cancellare tutto:

```bash
docker compose down -v
```

## Note di configurazione

- **URL GeoServer**: http://localhost:8080/geoserver
- **Utente admin**: `admin`
- **Password admin**: `corsowebgis` (vedi `docker-compose.yml`, env `GEOSERVER_ADMIN_PASSWORD`)
- **CORS**: abilitato per tutte le origini (corso in localhost — non per produzione!)
- **Plugin extra installati**: `vectortiles-plugin` (per il V8)

## Path interni utili

- Datasets host (read-only): `/data` dentro il container, `./data` sul tuo PC
- Data directory GeoServer: `/opt/geoserver/data_dir` dentro il container
