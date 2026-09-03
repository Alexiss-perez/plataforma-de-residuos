export function validateEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!email) return "El email es obligatorio";
  if (!re.test(email)) return "Email inválido";
  return null;
}

export function validatePassword(password) {
  if (!password) return "La contraseña es obligatoria";
  if (password.length < 8) return "Mínimo 8 caracteres";
  if (!/[A-Z]/.test(password)) return "Debe incluir una mayúscula";
  if (!/[0-9]/.test(password)) return "Debe incluir un número";
  return null;
}

export function validateRequired(value, label = "Este campo") {
  if (!value || !value.trim()) return `${label} es obligatorio`;
  return null;
}

export function validatePhone(phone) {
  if (!phone) return null;
  const re = /^\+?[\d\s-]{8,}$/;
  if (!re.test(phone)) return "Teléfono inválido";
  return null;
}

export function validateRUT(rut) {
  if (!rut) return null;
  const clean = rut.replace(/[.\s-]/g, "");
  if (clean.length < 8) return "RUT inválido";
  return null;
}
