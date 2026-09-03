from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.models import CollectorProfile, User
from app.repositories.repos import CollectorProfileRepository
from app.schemas.schemas import CollectorProfileCreate, CollectorProfilePublic, CollectorProfileUpdate, CollectorWithUserPublic
from app.utils.distance import haversine_km


class CollectorService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = CollectorProfileRepository(db)

    def _require_user(self, user_id: int) -> User:
        user = self.db.get(User, user_id)
        if not user:
            raise NotFoundError("User not found")
        return user

    def create_profile(self, user_id: int, data: CollectorProfileCreate) -> CollectorProfile:
        if self.repo.get_by_user(user_id):
            raise ConflictError("Collector profile already exists")
        user = self._require_user(user_id)
        if not user.can_collect and user.role.value != "COLLECTOR":
            user.can_collect = True
        profile = self.repo.create(
            user_id=user_id,
            vehicle_type=data.vehicle_type,
            max_weight_kg=data.max_weight_kg,
            radius_km=data.radius_km,
            available=data.available,
            materials_accepted=",".join(data.materials_accepted) if data.materials_accepted else None,
            description=data.description,
        )
        return profile

    def get_my_profile(self, user_id: int) -> CollectorProfile:
        profile = self.repo.get_by_user(user_id)
        if not profile:
            raise NotFoundError("Collector profile not found")
        return profile

    def update_profile(self, user_id: int, data: CollectorProfileUpdate) -> CollectorProfile:
        profile = self.get_my_profile(user_id)
        fields = data.model_dump(exclude_unset=True)
        if "materials_accepted" in fields and fields["materials_accepted"] is not None:
            fields["materials_accepted"] = ",".join(fields["materials_accepted"]) if fields["materials_accepted"] else None
        return self.repo.update(profile, fields)

    def list_available(
        self,
        material_category: str | None = None,
        max_distance_km: float | None = None,
        origin_lat: float | None = None,
        origin_lon: float | None = None,
        min_capacity_kg: float | None = None,
    ) -> list[CollectorWithUserPublic]:
        profiles = self.repo.list_available()
        results: list[CollectorWithUserPublic] = []
        for p in profiles:
            user = self.db.get(User, p.user_id)
            if not user or not user.is_active:
                continue
            if min_capacity_kg and (p.max_weight_kg is None or p.max_weight_kg < min_capacity_kg):
                continue
            if material_category and p.materials_accepted_list:
                if material_category not in p.materials_accepted_list:
                    continue
            distance = None
            if origin_lat is not None and origin_lon is not None and user.latitude and user.longitude:
                distance = haversine_km(origin_lat, origin_lon, user.latitude, user.longitude)
                if max_distance_km and distance > max_distance_km:
                    continue
                if p.radius_km and distance > p.radius_km:
                    continue
            results.append(
                CollectorWithUserPublic(
                    user_id=p.user_id,
                    user_name=user.name,
                    vehicle_type=p.vehicle_type,
                    max_weight_kg=p.max_weight_kg,
                    radius_km=p.radius_km,
                    available=p.available,
                    materials_accepted=p.materials_accepted_list,
                    commune=user.commune,
                    latitude=user.latitude,
                    longitude=user.longitude,
                    distance_km=round(distance, 2) if distance is not None else None,
                )
            )
        return results

    @staticmethod
    def to_public(profile: CollectorProfile) -> CollectorProfilePublic:
        return CollectorProfilePublic.from_model(profile)
