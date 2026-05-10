// vite.config.js — configurazione del dev server Vite
//
// Note importanti per il corso:
//
// 1. server.host: "0.0.0.0" — necessario perché il dev server giri DENTRO
//    il container Docker e sia raggiungibile dal browser sul Windows host.
//    Senza questo, Vite ascolta solo su 127.0.0.1 dentro il container e
//    da fuori non vedi nulla.
//
// 2. server.proxy — riscrive le richieste a /geoserver verso http://geoserver:8080
//    in modo trasparente. Così dal codice frontend chiami `/geoserver/...`
//    e il browser non si lamenta di CORS (V5 lo spiega bene).

import { defineConfig } from "vite";

export default defineConfig({
  server: {
    host: "0.0.0.0",
    port: 5173,
    strictPort: true,
    proxy: {
      // Tutto ciò che inizia con /geoserver viene proxato al container GeoServer
      "/geoserver": {
        target: "http://geoserver:8080",
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: "dist",
    sourcemap: true,
  },
});
