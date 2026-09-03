import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import Button from "../components/ui/Button";
import Badge from "../components/ui/Badge";
import Modal from "../components/ui/Modal";
import StatusBadge from "../components/StatusBadge";
import BarChart from "../components/BarChart";
import { useAuth } from "../lib/auth";
import { useToast } from "../components/ui/Toast";
import { MOCK_WASTES, MOCK_STATS, MOCK_MONTHLY_DATA } from "../lib/mockData";
import { MATERIAL_CATEGORIES } from "../lib/constants";
import {
  Package,
  Link2,
  Check,
  Recycle,
  TrendingUp,
  Filter,
  Search,
  Sparkles,
  MapPin,
  Clock,
  Inbox,
} from "../components/icons";

const statCards = [
  { key: "published", label: "Publicados", icon: Package, color: "text-blue-600", bg: "bg-blue-50" },
  { key: "matched", label: "Matches", icon: Link2, color: "text-earth-600", bg: "bg-earth-50" },
  { key: "scheduled", label: "Agendados", icon: Clock, color: "text-amber-600", bg: "bg-amber-50" },
  { key: "completed", label: "Completados", icon: Check, color: "text-eco-600", bg: "bg-eco-50" },
];

export default function Dashboard() {
  const { user } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();
  const [search, setSearch] = useState("");
  const [materialFilter, setMaterialFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [selected, setSelected] = useState(null);

  const filtered = useMemo(() => {
    return MOCK_WASTES.filter((w) => {
      if (search && !w.description.toLowerCase().includes(search.toLowerCase()))
        return false;
      if (materialFilter && w.material !== materialFilter) return false;
      if (statusFilter && w.status !== statusFilter) return false;
      return true;
    });
  }, [search, materialFilter, statusFilter]);

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <main className="mx-auto max-w-6xl px-4 py-8">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-800">
              Hola, {user?.companyName || user?.email}
            </h1>
            <p className="mt-1 text-sm text-gray-500">
              Gestiona tus residuos y conecta con la red circular.
            </p>
          </div>
          <Button onClick={() => navigate("/chat")}>
            <Sparkles className="h-4 w-4" />
            Publicar con IA
          </Button>
        </div>

        {/* Stats */}
        <div className="mb-6 grid grid-cols-2 gap-4 lg:grid-cols-4">
          {statCards.map((s) => (
            <div
              key={s.key}
              className="rounded-xl border border-gray-100 bg-white p-5 shadow-sm"
            >
              <div className={`mb-3 inline-flex h-10 w-10 items-center justify-center rounded-lg ${s.bg}`}>
                <s.icon className={`h-5 w-5 ${s.color}`} />
              </div>
              <p className="text-2xl font-bold text-gray-800">
                {MOCK_STATS[s.key]}
              </p>
              <p className="text-xs text-gray-500">{s.label}</p>
            </div>
          ))}
        </div>

        {/* Impact + Chart */}
        <div className="mb-6 grid gap-4 lg:grid-cols-3">
          <div className="rounded-xl border border-gray-100 bg-white p-6 shadow-sm lg:col-span-2">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-800">
                Residuos desviados (kg)
              </h2>
              <Badge tone="eco">
                <TrendingUp className="mr-1 h-3 w-3" />
                +15% este mes
              </Badge>
            </div>
            <BarChart data={MOCK_MONTHLY_DATA} className="h-40" />
          </div>

          <div className="rounded-xl border border-eco-100 bg-gradient-to-br from-eco-50 to-white p-6 shadow-sm">
            <Recycle className="mb-3 h-8 w-8 text-eco-600" />
            <p className="text-3xl font-bold text-eco-700">
              {MOCK_STATS.co2Saved} kg
            </p>
            <p className="text-sm text-gray-500">CO₂ ahorrado</p>
            <div className="mt-4 border-t border-eco-100 pt-4">
              <p className="text-lg font-semibold text-gray-700">
                {MOCK_STATS.activeMatches}
              </p>
              <p className="text-xs text-gray-500">matches activos en la red</p>
            </div>
          </div>
        </div>

        {/* Waste table */}
        <div className="rounded-xl border border-gray-100 bg-white shadow-sm">
          <div className="border-b border-gray-100 p-4">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <h2 className="text-lg font-semibold text-gray-800">
                Mis residuos
              </h2>
              <div className="flex flex-wrap gap-2">
                <div className="relative">
                  <Search className="pointer-events-none absolute top-1/2 left-2.5 h-4 w-4 -translate-y-1/2 text-gray-400" />
                  <input
                    type="text"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    placeholder="Buscar..."
                    className="w-40 rounded-lg border border-gray-200 py-1.5 pr-3 pl-8 text-sm focus:border-eco-500 focus:ring-2 focus:ring-eco-200 focus:outline-none"
                  />
                </div>
                <select
                  value={materialFilter}
                  onChange={(e) => setMaterialFilter(e.target.value)}
                  className="rounded-lg border border-gray-200 px-3 py-1.5 text-sm focus:border-eco-500 focus:outline-none"
                >
                  <option value="">Todos los materiales</option>
                  {MATERIAL_CATEGORIES.map((m) => (
                    <option key={m} value={m}>{m}</option>
                  ))}
                </select>
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="rounded-lg border border-gray-200 px-3 py-1.5 text-sm focus:border-eco-500 focus:outline-none"
                >
                  <option value="">Todos los estados</option>
                  <option value="publicado">Publicado</option>
                  <option value="matcheado">Matcheado</option>
                  <option value="agendado">Agendado</option>
                  <option value="completado">Completado</option>
                </select>
              </div>
            </div>
          </div>

          {filtered.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <Inbox className="mb-3 h-10 w-10 text-gray-300" />
              <p className="text-sm text-gray-400">
                No se encontraron residuos con estos filtros.
              </p>
              <Button
                variant="ghost"
                size="sm"
                className="mt-3"
                onClick={() => {
                  setSearch("");
                  setMaterialFilter("");
                  setStatusFilter("");
                }}
              >
                Limpiar filtros
              </Button>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-50 text-left text-xs text-gray-400">
                    <th className="px-4 py-3 font-medium">Material</th>
                    <th className="px-4 py-3 font-medium">Descripción</th>
                    <th className="px-4 py-3 font-medium">Cantidad</th>
                    <th className="px-4 py-3 font-medium">Estado</th>
                    <th className="px-4 py-3 font-medium">Matches</th>
                    <th className="px-4 py-3 font-medium">Fecha</th>
                    <th className="px-4 py-3" />
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((w) => (
                    <tr
                      key={w.id}
                      className="border-b border-gray-50 transition-colors hover:bg-eco-50/50"
                    >
                      <td className="px-4 py-3">
                        <Badge tone="gray">{w.material}</Badge>
                      </td>
                      <td className="max-w-48 truncate px-4 py-3 text-gray-700">
                        {w.description}
                      </td>
                      <td className="px-4 py-3 font-medium text-gray-700">
                        {w.quantity} {w.unit}
                      </td>
                      <td className="px-4 py-3">
                        <StatusBadge status={w.status} />
                      </td>
                      <td className="px-4 py-3 text-gray-600">
                        {w.matches > 0 ? (
                          <span className="flex items-center gap-1">
                            <Link2 className="h-3.5 w-3.5 text-eco-500" />
                            {w.matches}
                          </span>
                        ) : (
                          "—"
                        )}
                      </td>
                      <td className="px-4 py-3 text-gray-400">
                        {w.createdAt}
                      </td>
                      <td className="px-4 py-3 text-right">
                        <button
                          onClick={() => setSelected(w)}
                          className="text-xs font-medium text-eco-600 hover:underline"
                        >
                          Ver
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Quick actions */}
        <div className="mt-6 grid gap-4 lg:grid-cols-3">
          <button
            onClick={() => navigate("/chat")}
            className="rounded-xl border border-eco-200 bg-eco-50 p-5 text-left transition-colors hover:bg-eco-100"
          >
            <Sparkles className="mb-2 h-6 w-6 text-eco-600" />
            <p className="font-semibold text-eco-700">Publicar residuo con IA</p>
            <p className="text-xs text-eco-600">Chat asistido por GLM 5.2</p>
          </button>
          <button
            onClick={() => toast("Próximamente", "info")}
            className="rounded-xl border border-gray-200 bg-white p-5 text-left transition-colors hover:bg-gray-50"
          >
            <MapPin className="mb-2 h-6 w-6 text-earth-600" />
            <p className="font-semibold text-gray-700">Ver mapa de matches</p>
            <p className="text-xs text-gray-400">Receptores cercanos</p>
          </button>
          <button
            onClick={() => toast("Próximamente", "info")}
            className="rounded-xl border border-gray-200 bg-white p-5 text-left transition-colors hover:bg-gray-50"
          >
            <Filter className="mb-2 h-6 w-6 text-gray-600" />
            <p className="font-semibold text-gray-700">Historial</p>
            <p className="text-xs text-gray-400">Transacciones pasadas</p>
          </button>
        </div>
      </main>

      {/* Detail modal */}
      <Modal
        open={!!selected}
        onClose={() => setSelected(null)}
        title="Detalle del residuo"
        size="lg"
      >
        {selected && (
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <Badge tone="gray">{selected.material}</Badge>
              <StatusBadge status={selected.status} />
            </div>
            <p className="text-gray-700">{selected.description}</p>
            <dl className="grid grid-cols-2 gap-4 text-sm">
              {[
                ["Cantidad", `${selected.quantity} ${selected.unit}`],
                ["Dirección", selected.address],
                ["Matches", selected.matches],
                ["Publicado", selected.createdAt],
              ].map(([k, v]) => (
                <div key={k} className="rounded-lg bg-gray-50 p-3">
                  <dt className="text-xs text-gray-400">{k}</dt>
                  <dd className="mt-1 font-medium text-gray-700">{v}</dd>
                </div>
              ))}
            </dl>
            <div className="flex gap-2 pt-2">
              <Button className="flex-1">
                <Link2 className="h-4 w-4" />
                Ver matches
              </Button>
              <Button
                variant="outline"
                className="flex-1"
                onClick={() => {
                  toast("Retiro agendado (demo)", "success");
                  setSelected(null);
                }}
              >
                Agendar retiro
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
