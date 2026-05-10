// frontend/src/main.js — Stato V2 — prima mappa Leaflet di Padova.
//
// Branch v2-prima-mappa.
// Cosa cambia rispetto al main: importiamo Leaflet, inizializziamo una mappa
// centrata su Piazza dei Signori e aggiungiamo il tile layer di OpenStreetMap.
//
// Promemoria coordinate:
//   Leaflet usa [lat, lon]  (latitudine prima)
//   GeoJSON / MapLibre usano [lon, lat]
// Sbagliarli e' la fonte numero uno di errori del corso.

import L from "leaflet";
import "leaflet/dist/leaflet.css";

// Coordinate del centro di Padova (Piazza dei Signori)
const PADOVA = [45.4076, 11.8748];

const map = L.map("map").setView(PADOVA, 14);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution:
    '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
}).addTo(map);
