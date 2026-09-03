export const USER_ROLES = {
  ADMIN: "admin",
  DONADOR: "donador",
  TRANSPORTISTA: "transportista",
  ONG: "ong",
};

export const ROLE_LABELS = {
  [USER_ROLES.ADMIN]: "Administrador",
  [USER_ROLES.DONADOR]: "Donador",
  [USER_ROLES.TRANSPORTISTA]: "Transportista",
  [USER_ROLES.ONG]: "ONG / Fundación",
};

export const ROLE_ICONS = {
  [USER_ROLES.ADMIN]: "Shield",
  [USER_ROLES.DONADOR]: "User",
  [USER_ROLES.TRANSPORTISTA]: "Truck",
  [USER_ROLES.ONG]: "Handshake",
};

export const ROLE_DESCRIPTIONS = {
  [USER_ROLES.ADMIN]: "Gestiona la plataforma y usuarios",
  [USER_ROLES.DONADOR]: "Persona natural que dona residuos",
  [USER_ROLES.TRANSPORTISTA]: "Recolector que transporta residuos",
  [USER_ROLES.ONG]: "Fundación o taller que recibe residuos",
};

export const WASTE_STATUS = {
  DRAFT: "borrador",
  PUBLISHED: "publicado",
  MATCHED: "matcheado",
  SCHEDULED: "agendado",
  COMPLETED: "completado",
  CANCELLED: "cancelado",
};

export const MATERIAL_CATEGORIES = [
  "escombros",
  "madera",
  "metal",
  "plastico",
  "papel-carton",
  "vidrio",
  "organico",
  "electronicos",
  "textiles",
  "quimicos",
  "otros",
];
