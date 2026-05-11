"""Genera padova-corso.gpkg con 3 layer: poi, piste_ciclabili, quartieri."""
import json
import urllib.request
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, LineString, Polygon, MultiPolygon, shape
from pathlib import Path

OUT = Path("data/padova-corso.gpkg")
SRC = Path("data/poi-padova.geojson")
BBOX = (45.37, 11.83, 45.45, 11.93)  # s, w, n, e

# === Layer 1: POI =========================================================
print("→ Layer 1: poi")
poi = gpd.read_file(SRC)
print(f"   {len(poi)} feature, geom={poi.geom_type.unique()}")
poi.to_file(OUT, layer="poi", driver="GPKG")
print(f"   ✓ scritto in {OUT.name}")

# === Layer 2: piste_ciclabili (Overpass) ==================================
print("→ Layer 2: piste_ciclabili (Overpass API)")
query = f'''[out:json][timeout:60];
(
  way["highway"="cycleway"]({BBOX[0]},{BBOX[1]},{BBOX[2]},{BBOX[3]});
  way["bicycle"="designated"]["highway"]({BBOX[0]},{BBOX[1]},{BBOX[2]},{BBOX[3]});
  way["cycleway"~"lane|track|opposite"]({BBOX[0]},{BBOX[1]},{BBOX[2]},{BBOX[3]});
);
out geom;'''
req = urllib.request.Request(
    "https://overpass-api.de/api/interpreter",
    data=query.encode("utf-8"),
    headers={"Content-Type": "text/plain", "User-Agent": "corso-webgis-padova/1.0"},
)
with urllib.request.urlopen(req, timeout=90) as r:
    osm = json.load(r)

ways = [el for el in osm.get("elements", []) if el.get("type") == "way" and el.get("geometry")]
print(f"   {len(ways)} ways recuperate")
features = []
for w in ways:
    coords = [(p["lon"], p["lat"]) for p in w["geometry"]]
    if len(coords) < 2:
        continue
    tags = w.get("tags", {})
    features.append({
        "geometry": LineString(coords),
        "osm_id": w["id"],
        "name": tags.get("name", ""),
        "highway": tags.get("highway", ""),
        "surface": tags.get("surface", ""),
        "bicycle": tags.get("bicycle", ""),
        "cycleway": tags.get("cycleway", ""),
    })
piste = gpd.GeoDataFrame(features, crs="EPSG:4326")
piste.to_file(OUT, layer="piste_ciclabili", driver="GPKG")
print(f"   ✓ {len(piste)} piste salvate")

# === Layer 3: quartieri (Overpass admin_level) ============================
print("→ Layer 3: quartieri")
# I "quartieri" di Padova sono boundary admin level=10 con designation=quartiere
# Provo prima Overpass; se non trova, fallback a 6 poligoni dummy.
query_q = f'''[out:json][timeout:60];
(
  relation["boundary"="administrative"]["admin_level"="10"]({BBOX[0]},{BBOX[1]},{BBOX[2]},{BBOX[3]});
  relation["boundary"="administrative"]["admin_level"="9"]({BBOX[0]},{BBOX[1]},{BBOX[2]},{BBOX[3]});
);
out geom;'''
req2 = urllib.request.Request(
    "https://overpass-api.de/api/interpreter",
    data=query_q.encode("utf-8"),
    headers={"Content-Type": "text/plain", "User-Agent": "corso-webgis-padova/1.0"},
)
with urllib.request.urlopen(req2, timeout=90) as r:
    osm_q = json.load(r)
relations = [el for el in osm_q.get("elements", []) if el.get("type") == "relation"]
print(f"   {len(relations)} relations admin trovate (admin_level 9-10)")

quartieri_features = []
if relations:
    for rel in relations:
        tags = rel.get("tags", {})
        name = tags.get("name", "Quartiere")
        # Membri = lista di way con geometry, da cucire in (multi)polygon
        outer_rings = []
        for m in rel.get("members", []):
            if m.get("role") == "outer" and m.get("geometry"):
                pts = [(p["lon"], p["lat"]) for p in m["geometry"]]
                if pts and pts[0] != pts[-1]:
                    pts.append(pts[0])
                if len(pts) >= 4:
                    outer_rings.append(Polygon(pts))
        if outer_rings:
            geom = outer_rings[0] if len(outer_rings) == 1 else MultiPolygon(outer_rings)
            quartieri_features.append({
                "geometry": geom,
                "name": name,
                "admin_level": tags.get("admin_level", ""),
                "ref": tags.get("ref", ""),
            })

if not quartieri_features:
    # Fallback: 6 quartieri dummy come bbox approssimativi
    print("   ⚠ Overpass non ha restituito quartieri — uso fallback 6 bbox")
    fallback = [
        ("Q1 Centro",      (11.86, 45.40, 11.89, 45.42)),
        ("Q2 Nord",        (11.85, 45.42, 11.92, 45.45)),
        ("Q3 Est",         (11.89, 45.40, 11.93, 45.43)),
        ("Q4 Sud-Est",     (11.86, 45.37, 11.91, 45.40)),
        ("Q5 Sud-Ovest",   (11.83, 45.37, 11.86, 45.40)),
        ("Q6 Ovest",       (11.83, 45.40, 11.86, 45.43)),
    ]
    for name, (w, s, e, n) in fallback:
        quartieri_features.append({
            "geometry": Polygon([(w,s),(e,s),(e,n),(w,n),(w,s)]),
            "name": name,
            "admin_level": "fallback",
            "ref": name.split()[0],
        })

quartieri = gpd.GeoDataFrame(quartieri_features, crs="EPSG:4326")
quartieri.to_file(OUT, layer="quartieri", driver="GPKG")
print(f"   ✓ {len(quartieri)} quartieri salvati")

# === Verifica ============================================================
print()
print(f"=== {OUT.name} pronto ===")
import sqlite3
con = sqlite3.connect(OUT)
for (name,) in con.execute("SELECT table_name FROM gpkg_contents"):
    n = con.execute(f"SELECT count(*) FROM '{name}'").fetchone()[0]
    print(f"  {name:25} {n:4} feature")
con.close()
print(f"Dimensione: {OUT.stat().st_size/1024:.1f} KB")
