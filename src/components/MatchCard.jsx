import Badge from "./ui/Badge";
import Button from "./ui/Button";
import { MapPin, Building, Check, ArrowRight } from "./icons";

export default function MatchCard({ match, onAccept }) {
  return (
    <div className="rounded-xl border border-eco-200 bg-eco-50/50 p-4">
      <div className="mb-3 flex items-start justify-between">
        <div className="flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-white">
            <Building className="h-5 w-5 text-eco-600" />
          </div>
          <div>
            <p className="font-semibold text-gray-800">{match.companyName}</p>
            <p className="text-xs text-gray-500">{match.material}</p>
          </div>
        </div>
        <Badge tone={match.distanceKm <= 5 ? "eco" : "earth"}>
          {match.distanceKm} km
        </Badge>
      </div>

      <div className="mb-3 flex items-center gap-1.5 text-xs text-gray-500">
        <MapPin className="h-3.5 w-3.5" />
        {match.address}
      </div>

      <div className="flex items-center gap-2">
        <Button size="sm" onClick={() => onAccept(match)} className="flex-1">
          <Check className="h-3.5 w-3.5" />
          Aceptar
        </Button>
        <Button size="sm" variant="outline" className="flex-1">
          Ver detalle
          <ArrowRight className="h-3.5 w-3.5" />
        </Button>
      </div>
    </div>
  );
}
