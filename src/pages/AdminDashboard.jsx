import { useMemo, useState } from "react";
import Navbar from "../components/Navbar";
import Button from "../components/ui/Button";
import Badge from "../components/ui/Badge";
import Modal from "../components/ui/Modal";
import RoleIcon from "../components/RoleIcon";
import { useToast } from "../components/ui/Toast";
import { MOCK_USERS, MOCK_ADMIN_STATS } from "../lib/mockAdmin";
import { ROLE_LABELS } from "../lib/constants";
import {
  Search,
  Check,
  X,
  Building,
  Mail,
  Phone,
  MapPin,
  Recycle,
  Link2,
  Package,
  AlertCircle,
  Shield,
  Users,
  Handshake,
  Truck,
} from "../components/icons";

const statusConfig = {
  activo: { tone: "eco", label: "Activo" },
  pendiente: { tone: "amber", label: "Pendiente" },
  suspendido: { tone: "red", label: "Suspendido" },
};

const statCards = [
  { key: "totalUsers", label: "Usuarios totales", icon: Users, color: "text-eco-600", bg: "bg-eco-50" },
  { key: "donadores", label: "Donadores", icon: Package, color: "text-blue-600", bg: "bg-blue-50" },
  { key: "ongs", label: "ONGs", icon: Handshake, color: "text-earth-600", bg: "bg-earth-50" },
  { key: "transportistas", label: "Transportistas", icon: Truck, color: "text-amber-600", bg: "bg-amber-50" },
];

export default function AdminDashboard() {
  const toast = useToast();
  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [selectedUser, setSelectedUser] = useState(null);

  const filtered = useMemo(() => {
    return MOCK_USERS.filter((u) => {
      if (
        search &&
        !u.fullName.toLowerCase().includes(search.toLowerCase()) &&
        !u.email.toLowerCase().includes(search.toLowerCase())
      )
        return false;
      if (roleFilter && u.role !== roleFilter) return false;
      if (statusFilter && u.status !== statusFilter) return false;
      return true;
    });
  }, [search, roleFilter, statusFilter]);

  const handleApprove = (user) => {
    toast(`${user.fullName} aprobado`, "success");
    setSelectedUser(null);
  };

  const handleSuspend = (user) => {
    toast(`${user.fullName} suspendido`, "error");
    setSelectedUser(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <main className="mx-auto max-w-7xl px-6 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-800">
            Panel de Administración
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Gestiona usuarios, residuos y la plataforma completa.
          </p>
        </div>

        {/* Stats */}
        <div className="mb-6 grid grid-cols-2 gap-4 lg:grid-cols-4">
          {statCards.map((s) => {
            const Icon = s.icon;
            return (
              <div
                key={s.key}
                className="rounded-xl border border-gray-100 bg-white p-5 shadow-sm"
              >
                <div
                  className={`mb-3 inline-flex h-10 w-10 items-center justify-center rounded-lg ${s.bg}`}
                >
                  <Icon className={`h-5 w-5 ${s.color}`} />
                </div>
                <p className="text-2xl font-bold text-gray-800">
                  {MOCK_ADMIN_STATS[s.key]}
                </p>
                <p className="text-xs text-gray-500">{s.label}</p>
              </div>
            );
          })}
        </div>

        {/* Secondary stats */}
        <div className="mb-6 grid gap-4 lg:grid-cols-4">
          {[
            { label: "Residuos publicados", value: MOCK_ADMIN_STATS.totalWastes, Icon: Package },
            { label: "Kg gestionados", value: MOCK_ADMIN_STATS.totalKg, Icon: Recycle },
            { label: "Matches activos", value: MOCK_ADMIN_STATS.activeMatches, Icon: Link2 },
            { label: "Transferencias completadas", value: MOCK_ADMIN_STATS.completedTransfers, Icon: Check },
          ].map((s) => (
            <div
              key={s.label}
              className="flex items-center gap-3 rounded-xl border border-gray-100 bg-white p-4 shadow-sm"
            >
              <s.Icon className="h-6 w-6 text-eco-600" />
              <div>
                <p className="text-lg font-bold text-gray-800">{s.value}</p>
                <p className="text-xs text-gray-500">{s.label}</p>
              </div>
            </div>
          ))}
        </div>

        {/* Pending approval alert */}
        {MOCK_ADMIN_STATS.pendingApprovals > 0 && (
          <div className="mb-6 flex items-center gap-3 rounded-xl border border-amber-200 bg-amber-50 p-4">
            <AlertCircle className="h-5 w-5 text-amber-600" />
            <p className="text-sm font-medium text-amber-700">
              {MOCK_ADMIN_STATS.pendingApprovals} usuario(s) pendiente(s) de
              aprobación
            </p>
            <Button
              size="sm"
              variant="outline"
              className="ml-auto border-amber-300 text-amber-700 hover:bg-amber-100"
              onClick={() => setStatusFilter("pendiente")}
            >
              Revisar
            </Button>
          </div>
        )}

        {/* Users table */}
        <div className="rounded-xl border border-gray-100 bg-white shadow-sm">
          <div className="border-b border-gray-100 p-4">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <h2 className="text-lg font-semibold text-gray-800">
                Usuarios registrados
              </h2>
              <div className="flex flex-wrap gap-2">
                <div className="relative">
                  <Search className="pointer-events-none absolute top-1/2 left-2.5 h-4 w-4 -translate-y-1/2 text-gray-400" />
                  <input
                    type="text"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    placeholder="Buscar usuario..."
                    className="w-48 rounded-lg border border-gray-200 py-1.5 pr-3 pl-8 text-sm focus:border-eco-500 focus:ring-2 focus:ring-eco-200 focus:outline-none"
                  />
                </div>
                <select
                  value={roleFilter}
                  onChange={(e) => setRoleFilter(e.target.value)}
                  className="rounded-lg border border-gray-200 px-3 py-1.5 text-sm focus:border-eco-500 focus:outline-none"
                >
                  <option value="">Todos los roles</option>
                  <option value="donador">Donador</option>
                  <option value="ong">ONG</option>
                  <option value="transportista">Transportista</option>
                  <option value="admin">Admin</option>
                </select>
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="rounded-lg border border-gray-200 px-3 py-1.5 text-sm focus:border-eco-500 focus:outline-none"
                >
                  <option value="">Todos los estados</option>
                  <option value="activo">Activo</option>
                  <option value="pendiente">Pendiente</option>
                  <option value="suspendido">Suspendido</option>
                </select>
              </div>
            </div>
          </div>

          {filtered.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <span className="mb-2 text-3xl">🔍</span>
              <p className="text-sm text-gray-400">
                No se encontraron usuarios.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-50 text-left text-xs text-gray-400">
                    <th className="px-4 py-3 font-medium">Usuario</th>
                    <th className="px-4 py-3 font-medium">Rol</th>
                    <th className="px-4 py-3 font-medium">Estado</th>
                    <th className="px-4 py-3 font-medium">Residuos</th>
                    <th className="px-4 py-3 font-medium">Kg</th>
                    <th className="px-4 py-3 font-medium">Registro</th>
                    <th className="px-4 py-3" />
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((u) => {
                    const sc = statusConfig[u.status];
                    return (
                      <tr
                        key={u.id}
                        className="border-b border-gray-50 transition-colors hover:bg-eco-50/50"
                      >
                        <td className="px-4 py-3">
                          <div className="flex items-center gap-2">
                            <RoleIcon
                              name={u.role ? u.role.charAt(0).toUpperCase() + u.role.slice(1) : "User"}
                              className="h-5 w-5 text-gray-400"
                            />
                            <div>
                              <p className="font-medium text-gray-700">
                                {u.fullName}
                              </p>
                              <p className="text-xs text-gray-400">
                                {u.email}
                              </p>
                            </div>
                          </div>
                        </td>
                        <td className="px-4 py-3">
                          <Badge tone="gray">
                            {ROLE_LABELS[u.role] || u.role}
                          </Badge>
                        </td>
                        <td className="px-4 py-3">
                          <Badge tone={sc.tone}>{sc.label}</Badge>
                        </td>
                        <td className="px-4 py-3 text-gray-600">
                          {u.wastesPublished}
                        </td>
                        <td className="px-4 py-3 font-medium text-gray-700">
                          {u.totalKg > 0 ? `${u.totalKg} kg` : "—"}
                        </td>
                        <td className="px-4 py-3 text-gray-400">
                          {u.createdAt}
                        </td>
                        <td className="px-4 py-3 text-right">
                          <button
                            onClick={() => setSelectedUser(u)}
                            className="text-xs font-medium text-eco-600 hover:underline"
                          >
                            Gestionar
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>

      {/* User detail modal */}
      <Modal
        open={!!selectedUser}
        onClose={() => setSelectedUser(null)}
        title="Gestionar usuario"
        size="lg"
      >
        {selectedUser && (
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <RoleIcon
                name={selectedUser.role ? selectedUser.role.charAt(0).toUpperCase() + selectedUser.role.slice(1) : "User"}
                className="h-8 w-8 text-eco-600"
              />
              <div>
                <p className="text-lg font-bold text-gray-800">
                  {selectedUser.fullName}
                </p>
                <Badge tone="gray">
                  {ROLE_LABELS[selectedUser.role] || selectedUser.role}
                </Badge>
              </div>
            </div>

            <dl className="grid grid-cols-2 gap-3 text-sm">
              {[
                ["Email", selectedUser.email, Mail],
                ["Teléfono", selectedUser.phone || "—", Phone],
                ["Dirección", selectedUser.address, MapPin],
                ["Registro", selectedUser.createdAt, Building],
              ].map(([k, v, Icon]) => (
                <div key={k} className="rounded-lg bg-gray-50 p-3">
                  <dt className="flex items-center gap-1.5 text-xs text-gray-400">
                    {Icon && <Icon className="h-3.5 w-3.5" />}
                    {k}
                  </dt>
                  <dd className="mt-1 font-medium text-gray-700">{v}</dd>
                </div>
              ))}
            </dl>

            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-lg border border-eco-100 bg-eco-50 p-3 text-center">
                <p className="text-2xl font-bold text-eco-700">
                  {selectedUser.wastesPublished}
                </p>
                <p className="text-xs text-eco-600">residuos publicados</p>
              </div>
              <div className="rounded-lg border border-earth-100 bg-earth-50 p-3 text-center">
                <p className="text-2xl font-bold text-earth-700">
                  {selectedUser.totalKg}
                </p>
                <p className="text-xs text-earth-600">kg gestionados</p>
              </div>
            </div>

            <div className="flex gap-2 pt-2">
              {selectedUser.status === "pendiente" && (
                <Button
                  className="flex-1"
                  onClick={() => handleApprove(selectedUser)}
                >
                  <Check className="h-4 w-4" />
                  Aprobar
                </Button>
              )}
              {selectedUser.status !== "suspendido" && (
                <Button
                  variant="danger"
                  className="flex-1"
                  onClick={() => handleSuspend(selectedUser)}
                >
                  <X className="h-4 w-4" />
                  Suspender
                </Button>
              )}
              {selectedUser.status === "suspendido" && (
                <Button
                  className="flex-1"
                  onClick={() => handleApprove(selectedUser)}
                >
                  <Check className="h-4 w-4" />
                  Reactivar
                </Button>
              )}
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
