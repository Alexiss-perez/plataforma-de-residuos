import Badge from "./ui/Badge";

const statusConfig = {
  borrador: { tone: "gray", label: "Borrador" },
  publicado: { tone: "blue", label: "Publicado" },
  matcheado: { tone: "earth", label: "Match" },
  agendado: { tone: "amber", label: "Agendado" },
  completado: { tone: "eco", label: "Completado" },
  cancelado: { tone: "red", label: "Cancelado" },
};

export default function StatusBadge({ status }) {
  const cfg = statusConfig[status] || statusConfig.borrador;
  return <Badge tone={cfg.tone}>{cfg.label}</Badge>;
}
