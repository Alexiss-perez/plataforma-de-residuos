from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.models.models import Material, Need, Pickup, User
from app.services.collector_service import CollectorService
from app.services.matching_service import MatchingService
from app.services.need_service import NeedService
from app.services.pickup_service import PickupService
from app.utils.distance import haversine_km


class AgentTools:
    """Backend tools the agent can call. The LLM never touches the DB directly."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_material(self, material_id: int) -> dict[str, Any] | None:
        m = self.db.get(Material, material_id)
        if not m:
            return None
        return {
            "id": m.id,
            "name": m.name,
            "category": m.category,
            "quantity": m.quantity,
            "unit": m.unit,
            "condition": m.condition,
            "risk_level": m.risk_level,
            "status": m.status,
        }

    def search_needs(self, category: str | None = None, status: str = "OPEN") -> list[dict[str, Any]]:
        ns = NeedService(self.db).list_filtered(material_category=category, status=status)
        return [
            {
                "id": n.id,
                "material_category": n.material_category,
                "quantity_required": n.quantity_required,
                "quantity_received": n.quantity_received,
                "status": n.status,
            }
            for n in ns
        ]

    def search_collectors(
        self,
        material_category: str | None = None,
        origin_lat: float | None = None,
        origin_lon: float | None = None,
        max_distance_km: float | None = None,
    ) -> list[dict[str, Any]]:
        cs = CollectorService(self.db)
        results = cs.list_available(
            material_category=material_category,
            origin_lat=origin_lat,
            origin_lon=origin_lon,
            max_distance_km=max_distance_km,
        )
        return [r.model_dump() for r in results]

    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        return round(haversine_km(lat1, lon1, lat2, lon2), 2)

    def calculate_match(self, material_id: int, need_id: int) -> dict[str, Any] | None:
        material = self.db.get(Material, material_id)
        need = self.db.get(Need, need_id)
        if not material or not need:
            return None
        from app.services.matching_service import compute_match
        return compute_match(material, need)

    def create_match(self, material_id: int) -> list[dict[str, Any]]:
        matches = MatchingService(self.db).generate_for_material(material_id)
        self.db.commit()
        return [{"id": m.id, "score": m.score, "need_id": m.need_id} for m in matches]

    def find_replacement_collectors(self, pickup_id: int) -> list[dict[str, Any]]:
        candidates = PickupService(self.db).find_replacement_collectors(pickup_id)
        return [c.model_dump() for c in candidates]

    def get_pickup(self, pickup_id: int) -> dict[str, Any] | None:
        p = self.db.get(Pickup, pickup_id)
        if not p:
            return None
        return {
            "id": p.id,
            "status": p.status,
            "collector_id": p.collector_id,
            "donor_id": p.donor_id,
            "organization_id": p.organization_id,
        }

    def assign_collector(self, pickup_id: int, collector_id: int) -> dict[str, Any]:
        pickup = self.db.get(Pickup, pickup_id)
        if not pickup:
            return {"error": "Pickup not found"}
        pickup.collector_id = collector_id
        pickup.status = "ASSIGNED"
        self.db.flush()
        self.db.commit()
        return {"id": pickup.id, "status": pickup.status, "collector_id": pickup.collector_id}

    def get_project(self, project_id: int) -> dict[str, Any] | None:
        from app.services.project_service import ProjectService
        p = ProjectService(self.db).get(project_id)
        return {
            "id": p.id,
            "title": p.title,
            "status": p.status,
            "progress": ProjectService(self.db).compute_progress(p),
        }

    def register_impact(
        self,
        match_id: int,
        description: str | None = None,
        final_use: str | None = None,
        weight_reused_kg: float = 0,
        people_benefited: int | None = None,
    ) -> dict[str, Any]:
        from app.schemas.schemas import ImpactCreate
        from app.services.impact_service import ImpactService
        match = self.db.get(__import__("app.models.models", fromlist=["Match"]).Match, match_id)
        if not match or not match.need or not match.need.organization:
            return {"error": "Match/need/org not found"}
        user = self.db.get(User, match.need.organization.owner_id)
        if not user:
            return {"error": "Owner not found"}
        impact = ImpactService(self.db).register(
            user,
            ImpactCreate(
                match_id=match_id,
                description=description,
                final_use=final_use,
                weight_reused_kg=weight_reused_kg,
                people_benefited=people_benefited,
            ),
        )
        self.db.commit()
        return {"id": impact.id, "weight_reused_kg": impact.weight_reused_kg}
