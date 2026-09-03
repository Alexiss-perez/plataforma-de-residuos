from __future__ import annotations

import enum


class RoleEnum(str, enum.Enum):
    NATURAL = "NATURAL"
    COLLECTOR = "COLLECTOR"
    ORGANIZATION = "ORGANIZATION"
    ADMIN = "ADMIN"


class OrganizationTypeEnum(str, enum.Enum):
    FOUNDATION = "FOUNDATION"
    NGO = "NGO"
    WORKSHOP = "WORKSHOP"
    COMMUNITY = "COMMUNITY"
    OTHER = "OTHER"


class PostTypeEnum(str, enum.Enum):
    OFFER = "OFFER"
    NEED = "NEED"
    IMPACT = "IMPACT"
    PROJECT = "PROJECT"


class PostStatusEnum(str, enum.Enum):
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    ARCHIVED = "ARCHIVED"


class MaterialCategoryEnum(str, enum.Enum):
    WOOD = "WOOD"
    METAL = "METAL"
    FURNITURE = "FURNITURE"
    BRICKS = "BRICKS"
    DOORS_WINDOWS = "DOORS_WINDOWS"
    CARDBOARD = "CARDBOARD"
    TEXTILE = "TEXTILE"
    TOOLS = "TOOLS"
    CONSTRUCTION = "CONSTRUCTION"
    PLASTIC = "PLASTIC"
    OTHER = "OTHER"


class MaterialConditionEnum(str, enum.Enum):
    NEW = "NEW"
    GOOD = "GOOD"
    REUSABLE = "REUSABLE"
    REPAIRABLE = "REPAIRABLE"
    RECYCLE_ONLY = "RECYCLE_ONLY"
    UNKNOWN = "UNKNOWN"


class RiskLevelEnum(str, enum.Enum):
    SAFE = "SAFE"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"
    SPECIAL_HANDLING = "SPECIAL_HANDLING"


class MaterialStatusEnum(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    MATCHED = "MATCHED"
    RESERVED = "RESERVED"
    PICKED_UP = "PICKED_UP"
    DELIVERED = "DELIVERED"
    REUSED = "REUSED"
    CANCELLED = "CANCELLED"


class ProjectStatusEnum(str, enum.Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class NeedStatusEnum(str, enum.Enum):
    OPEN = "OPEN"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FULFILLED = "FULFILLED"
    CLOSED = "CLOSED"


class NeedPriorityEnum(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class MatchStatusEnum(str, enum.Enum):
    PROPOSED = "PROPOSED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    COMPLETED = "COMPLETED"


class PickupStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    ASSIGNED = "ASSIGNED"
    ACCEPTED = "ACCEPTED"
    ON_ROUTE = "ON_ROUTE"
    PICKED_UP = "PICKED_UP"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class NotificationTypeEnum(str, enum.Enum):
    MATCH_FOUND = "MATCH_FOUND"
    MATCH_ACCEPTED = "MATCH_ACCEPTED"
    MATCH_REJECTED = "MATCH_REJECTED"
    COLLECTOR_ASSIGNED = "COLLECTOR_ASSIGNED"
    COLLECTOR_CANCELLED = "COLLECTOR_CANCELLED"
    MATERIAL_PICKED_UP = "MATERIAL_PICKED_UP"
    MATERIAL_DELIVERED = "MATERIAL_DELIVERED"
    IMPACT_REGISTERED = "IMPACT_REGISTERED"
    INFO = "INFO"
