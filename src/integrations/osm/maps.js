import api from "../../lib/api";

export const mapsApi = {
  geocodificar: async (direccion) => {
    const { data } = await api.post("/maps/geocode", { direccion });
    return data;
  },

  reverseGeocodificar: async (lat, lon) => {
    const { data } = await api.post("/maps/reverse-geocode", { lat, lon });
    return data;
  },

  calcularRuta: async (origen, destino, conGeometry = false) => {
    const { data } = await api.post("/maps/ruta", {
      origen_lat: origen.lat,
      origen_lon: origen.lon,
      destino_lat: destino.lat,
      destino_lon: destino.lon,
      con_geometry: conGeometry,
    });
    return data;
  },
};

export default mapsApi;
