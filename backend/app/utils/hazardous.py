from __future__ import annotations

from app.models.enums import MaterialCategoryEnum, RiskLevelEnum

HAZARDOUS_CATEGORIES: set[str] = {
    "ASBESTOS",
    "CHEMICAL",
    "MEDICAL_WASTE",
    "FUEL",
    "CONTAMINATED_OIL",
    "UNKNOWN_HAZARDOUS",
}

HAZARDOUS_KEYWORDS: list[str] = [
    "asbesto",
    "amianto",
    "quimico",
    "químico",
    "chemical",
    "medic",
    "combustible",
    "fuel",
    "gasolina",
    "petroleo",
    "petróleo",
    "aceite contaminado",
    "contaminado",
    "toxico",
    "tóxico",
    "veneno",
    "radioactivo",
    "radiactivo",
]


def is_hazardous(category: str, name: str | None = None, description: str | None = None) -> bool:
    cat_upper = (category or "").upper().strip()
    if cat_upper in HAZARDOUS_CATEGORIES:
        return True
    text = " ".join(filter(None, [name or "", description or ""])).lower()
    return any(kw in text for kw in HAZARDOUS_KEYWORDS)


def determine_risk_level(category: str, name: str | None = None, description: str | None = None) -> str:
    if is_hazardous(category, name, description):
        return RiskLevelEnum.SPECIAL_HANDLING.value
    return RiskLevelEnum.SAFE.value
