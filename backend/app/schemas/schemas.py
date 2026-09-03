from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.enums import (
    MaterialCategoryEnum,
    MaterialConditionEnum,
    NeedPriorityEnum,
    OrganizationTypeEnum,
    PostStatusEnum,
    PostTypeEnum,
    RiskLevelEnum,
    RoleEnum,
)


class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ---------- Auth ----------
class UserRegister(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    role: RoleEnum = RoleEnum.NATURAL
    can_collect: bool = False
    commune: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserPublic"


class UserPublic(ORMBase):
    id: int
    name: str
    email: str
    role: RoleEnum
    can_collect: bool
    commune: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    is_active: bool
    created_at: datetime


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    commune: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    can_collect: bool | None = None


# ---------- Collector ----------
class CollectorProfileCreate(BaseModel):
    vehicle_type: str | None = None
    max_weight_kg: float | None = None
    radius_km: float | None = None
    available: bool = True
    materials_accepted: list[str] = Field(default_factory=list)
    description: str | None = None


class CollectorProfileUpdate(BaseModel):
    vehicle_type: str | None = None
    max_weight_kg: float | None = None
    radius_km: float | None = None
    available: bool | None = None
    materials_accepted: list[str] | None = None
    description: str | None = None


class CollectorProfilePublic(ORMBase):
    id: int
    user_id: int
    vehicle_type: str | None = None
    max_weight_kg: float | None = None
    radius_km: float | None = None
    available: bool
    materials_accepted: list[str] = Field(default_factory=list)
    description: str | None = None
    created_at: datetime

    @classmethod
    def from_model(cls, obj) -> "CollectorProfilePublic":
        return cls(
            id=obj.id,
            user_id=obj.user_id,
            vehicle_type=obj.vehicle_type,
            max_weight_kg=obj.max_weight_kg,
            radius_km=obj.radius_km,
            available=obj.available,
            materials_accepted=obj.materials_accepted_list,
            description=obj.description,
            created_at=obj.created_at,
        )


class CollectorWithUserPublic(ORMBase):
    user_id: int
    user_name: str
    vehicle_type: str | None = None
    max_weight_kg: float | None = None
    radius_km: float | None = None
    available: bool
    materials_accepted: list[str] = Field(default_factory=list)
    commune: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    distance_km: float | None = None


# ---------- Organization ----------
class OrganizationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    type: OrganizationTypeEnum = OrganizationTypeEnum.NGO
    description: str | None = None
    commune: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class OrganizationUpdate(BaseModel):
    name: str | None = None
    type: OrganizationTypeEnum | None = None
    description: str | None = None
    commune: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    verified: bool | None = None


class OrganizationPublic(ORMBase):
    id: int
    owner_id: int
    name: str
    type: str
    description: str | None = None
    commune: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    verified: bool
    created_at: datetime


# ---------- Post ----------
class PostCreate(BaseModel):
    type: PostTypeEnum = PostTypeEnum.OFFER
    title: str = Field(min_length=1, max_length=500)
    description: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    commune: str | None = None
    status: PostStatusEnum = PostStatusEnum.ACTIVE


class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=500)
    description: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    commune: str | None = None
    status: PostStatusEnum | None = None


class PostPublic(ORMBase):
    id: int
    author_id: int
    type: str
    title: str
    description: str | None = None
    commune: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime
    latitude: float | None = None
    longitude: float | None = None


# ---------- Material ----------
class MaterialCreate(BaseModel):
    post_id: int | None = None
    name: str = Field(min_length=1, max_length=255)
    category: MaterialCategoryEnum
    description: str | None = None
    quantity: float = Field(default=1, gt=0)
    unit: str = "unit"
    condition: MaterialConditionEnum = MaterialConditionEnum.UNKNOWN
    estimated_weight_kg: float | None = None
    risk_level: RiskLevelEnum = RiskLevelEnum.SAFE
    requires_pickup: bool = True


class MaterialUpdate(BaseModel):
    name: str | None = None
    category: MaterialCategoryEnum | None = None
    description: str | None = None
    quantity: float | None = Field(default=None, gt=0)
    unit: str | None = None
    condition: MaterialConditionEnum | None = None
    estimated_weight_kg: float | None = None
    risk_level: RiskLevelEnum | None = None
    requires_pickup: bool | None = None
    status: str | None = None


class MaterialPublic(ORMBase):
    id: int
    post_id: int | None = None
    owner_id: int
    name: str
    category: str
    description: str | None = None
    quantity: float
    unit: str
    condition: str
    estimated_weight_kg: float | None = None
    risk_level: str
    requires_pickup: bool
    status: str
    created_at: datetime
    updated_at: datetime


# ---------- Project ----------
class ProjectCreate(BaseModel):
    title: str = Field(min_length=1, max_length=500)
    description: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    commune: str | None = None


class ProjectUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    commune: str | None = None
    status: str | None = None


class ProjectPublic(ORMBase):
    id: int
    organization_id: int
    title: str
    description: str | None = None
    status: str
    latitude: float | None = None
    longitude: float | None = None
    commune: str | None = None
    created_at: datetime
    updated_at: datetime
    progress: float = 0.0


# ---------- Need ----------
class NeedCreate(BaseModel):
    project_id: int | None = None
    material_category: MaterialCategoryEnum
    material_name: str | None = None
    description: str | None = None
    quantity_required: float = Field(default=1, gt=0)
    unit: str = "unit"
    priority: NeedPriorityEnum = NeedPriorityEnum.MEDIUM


class NeedUpdate(BaseModel):
    material_name: str | None = None
    description: str | None = None
    quantity_required: float | None = Field(default=None, gt=0)
    priority: NeedPriorityEnum | None = None
    status: str | None = None


class NeedPublic(ORMBase):
    id: int
    organization_id: int
    project_id: int | None = None
    material_category: str
    material_name: str | None = None
    description: str | None = None
    quantity_required: float
    quantity_received: float
    unit: str
    priority: str
    status: str
    created_at: datetime
    updated_at: datetime


# ---------- Match ----------
class MatchPublic(ORMBase):
    id: int
    material_id: int
    need_id: int
    score: float
    material_score: float
    quantity_score: float
    distance_score: float
    priority_score: float
    condition_score: float
    status: str
    reason: str | None = None
    created_at: datetime


class MatchGenerateResponse(BaseModel):
    material_id: int
    matches: list[MatchPublic]


# ---------- Pickup ----------
class PickupCreate(BaseModel):
    match_id: int
    collector_id: int
    scheduled_at: datetime | None = None
    pickup_address: str | None = None
    delivery_address: str | None = None
    notes: str | None = None


class PickupPublic(ORMBase):
    id: int
    match_id: int
    collector_id: int
    donor_id: int
    organization_id: int
    scheduled_at: datetime | None = None
    pickup_address: str | None = None
    delivery_address: str | None = None
    status: str
    notes: str | None = None
    created_at: datetime
    updated_at: datetime


class ReplacementCandidate(BaseModel):
    collector_id: int
    user_name: str
    vehicle_type: str | None = None
    max_weight_kg: float | None = None
    radius_km: float | None = None
    distance_km: float | None = None
    materials_accepted: list[str] = Field(default_factory=list)


# ---------- Impact ----------
class ImpactCreate(BaseModel):
    match_id: int
    description: str | None = None
    final_use: str | None = None
    weight_reused_kg: float = Field(default=0, ge=0)
    people_benefited: int | None = Field(default=None, ge=0)
    image_url: str | None = None


class ImpactPublic(ORMBase):
    id: int
    match_id: int
    organization_id: int
    description: str | None = None
    final_use: str | None = None
    weight_reused_kg: float
    people_benefited: int | None = None
    image_url: str | None = None
    created_at: datetime


class ImpactStats(BaseModel):
    total_weight_reused_kg: float
    total_deliveries: int
    total_materials: int
    organizations_helped: int
    donors_count: int
    collectors_count: int


# ---------- Notification ----------
class NotificationPublic(ORMBase):
    id: int
    user_id: int
    type: str
    title: str
    message: str
    read: bool
    created_at: datetime


# ---------- AI ----------
class AIMaterialAnalysis(BaseModel):
    materials: list["AnalyzedMaterial"]


class AnalyzedMaterial(BaseModel):
    type: str
    category: str
    condition: str
    estimated_reuse: str | None = None
    risk_level: str
    confidence: float = Field(ge=0, le=1)


class AINeedInterpretation(BaseModel):
    material_category: str
    material_name: str | None = None
    quantity: float | None = None
    unit: str | None = None
    confidence: float = Field(ge=0, le=1)
    missing_info: list[str] = Field(default_factory=list)


class AIMatchExplanation(BaseModel):
    score: float
    reasons: list[str]
    confidence: float = Field(ge=0, le=1)


class AIChatRequest(BaseModel):
    message: str
    context: dict | None = None


class AIChatResponse(BaseModel):
    response: str
    action: str | None = None
    data: dict | None = None


TokenResponse.model_rebuild()
AIMaterialAnalysis.model_rebuild()
