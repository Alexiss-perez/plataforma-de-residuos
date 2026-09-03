import { useEffect, useState, useCallback } from "react";
import { MapContainer, TileLayer, Marker, Popup, Polyline } from "react-leaflet";
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

export default function MapView({ direccionOrigen, receptores = [], onReceptorClick }) {
  const [origen, setOrigen] = useState(null);
  const [rutaCoords, setRutaCoords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

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

  if (error)
    return (
      <div className="flex h-[500px] items-center justify-center text-red-500">
        {error}
      </div>
    );

  return (
    <MapContainer
      center={origen ? [origen.lat, origen.lon] : [-33.45, -70.66]}
      zoom={12}
      style={{ height: "500px", width: "100%", borderRadius: "0.5rem" }}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution="&copy; OpenStreetMap"
      />

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
  );
}
