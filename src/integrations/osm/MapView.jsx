import { useEffect, useState, useCallback } from "react";
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "./styles.css";
import { mapsApi } from "./maps";

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

const greenIcon = L.icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  className: "marker-green",
});

const blueIcon = L.icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  className: "marker-blue",
});

function RecentrarMapa({ centro }) {
  const map = useMap();
  useEffect(() => {
    if (centro) map.setView([centro.lat, centro.lon], 14);
  }, [centro, map]);
  return null;
}

export default function MapView({ direccionOrigen, receptores = [], onReceptorClick, onUbicacionChange }) {
  const [origen, setOrigen] = useState(null);
  const [rutaCoords, setRutaCoords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [gpsLoading, setGpsLoading] = useState(false);
  const [direccionManual, setDireccionManual] = useState(direccionOrigen || "");

  useEffect(() => {
    if (!direccionOrigen) {
      setLoading(false);
      return;
    }
    setLoading(true);
    setError(null);
    mapsApi
      .geocodificar(direccionOrigen)
      .then((r) => setOrigen({ lat: r.lat, lon: r.lon }))
      .catch(() => setError("No se pudo geocodificar la direccion"))
      .finally(() => setLoading(false));
  }, [direccionOrigen]);

  const usarMiUbicacion = useCallback(() => {
    if (!navigator.geolocation) {
      setError("Tu navegador no soporta geolocalizacion");
      return;
    }
    setGpsLoading(true);
    setError(null);
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const coords = { lat: pos.coords.latitude, lon: pos.coords.longitude };
        setOrigen(coords);
        try {
          const r = await mapsApi.reverseGeocodificar(coords.lat, coords.lon);
          setDireccionManual(r.display_name);
          if (onUbicacionChange) onUbicacionChange(r.display_name, coords);
        } catch {
          if (onUbicacionChange) onUbicacionChange("", coords);
        }
        setGpsLoading(false);
      },
      () => {
        setError("No se pudo obtener tu ubicacion. Permiso denegado o GPS no disponible.");
        setGpsLoading(false);
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  }, [onUbicacionChange]);

  const buscarDireccionManual = useCallback(async () => {
    if (!direccionManual.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const r = await mapsApi.geocodificar(direccionManual);
      setOrigen({ lat: r.lat, lon: r.lon });
      if (onUbicacionChange) onUbicacionChange(r.display_name, { lat: r.lat, lon: r.lon });
    } catch {
      setError("Direccion no encontrada");
    }
    setLoading(false);
  }, [direccionManual, onUbicacionChange]);

  const trazarRuta = useCallback(
    async (receptor) => {
      if (!origen) return;
      try {
        const r = await mapsApi.calcularRuta(
          origen,
          { lat: receptor.lat, lon: receptor.lon },
          true
        );
        if (r.geometry) {
          setRutaCoords(r.geometry.map(([lon, lat]) => [lat, lon]));
        }
        if (onReceptorClick) onReceptorClick(receptor, r);
      } catch {
        setError("No se pudo calcular la ruta");
      }
    },
    [origen, onReceptorClick]
  );

  if (loading)
    return (
      <div className="flex h-[500px] items-center justify-center text-gray-500">
        Cargando mapa...
      </div>
    );

  return (
    <div>
      <div className="mb-3 flex flex-wrap items-center gap-2">
        <input
          type="text"
          value={direccionManual}
          onChange={(e) => setDireccionManual(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && buscarDireccionManual()}
          placeholder="Escribe una direccion..."
          className="min-w-[200px] flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-eco-500 focus:outline-none"
        />
        <button
          onClick={buscarDireccionManual}
          className="rounded-lg bg-eco-600 px-4 py-2 text-sm font-medium text-white hover:bg-eco-700"
        >
          Buscar
        </button>
        <button
          onClick={usarMiUbicacion}
          disabled={gpsLoading}
          className="rounded-lg border border-eco-300 bg-eco-50 px-4 py-2 text-sm font-medium text-eco-700 hover:bg-eco-100 disabled:opacity-50"
        >
          {gpsLoading ? "Obteniendo..." : "Usar mi ubicacion"}
        </button>
      </div>

      {error && (
        <div className="mb-2 rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">
          {error}
        </div>
      )}

      <MapContainer
        center={origen ? [origen.lat, origen.lon] : [-33.45, -70.66]}
        zoom={12}
        style={{ height: "500px", width: "100%", borderRadius: "0.5rem" }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution="&copy; OpenStreetMap"
        />

        <RecentrarMapa centro={origen} />

        {origen && (
          <Marker position={[origen.lat, origen.lon]} icon={greenIcon}>
            <Popup>
              <strong>Origen (generador)</strong>
            </Popup>
          </Marker>
        )}

        {receptores.map((r, i) => (
          <Marker
            key={i}
            position={[r.lat, r.lon]}
            icon={blueIcon}
            eventHandlers={{ click: () => trazarRuta(r) }}
          >
            <Popup>
              <strong>{r.nombre}</strong>
              {r.distancia_km && <br />}
              {r.distancia_km && `${r.distancia_km} km — ${r.duracion_min} min`}
            </Popup>
          </Marker>
        ))}

        {rutaCoords.length > 0 && (
          <Polyline positions={rutaCoords} color="#16a34a" weight={3} opacity={0.7} />
        )}
      </MapContainer>
    </div>
  );
}
