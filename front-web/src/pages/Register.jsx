import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Button from "../components/ui/Button";
import Input from "../components/ui/Input";
import Logo from "../components/Logo";
import { useAuth } from "../lib/auth";
import { useToast } from "../components/ui/Toast";
import {
  validateEmail,
  validatePassword,
  validateRequired,
  validatePhone,
} from "../lib/validation";
import {
  Mail,
  Lock,
  Building,
  MapPin,
  Phone,
  ArrowLeft,
  ArrowRight,
  Recycle,
  User,
  Handshake,
  Truck,
  Shield,
} from "../components/icons";
import { USER_ROLES, ROLE_LABELS, ROLE_DESCRIPTIONS } from "../lib/constants";
import api from "../lib/api";

const ROLE_TO_BACKEND = {
  donador: "NATURAL",
  ong: "ORGANIZATION",
  transportista: "COLLECTOR",
  admin: "ADMIN",
};

const steps = ["Cuenta", "Perfil", "Confirmar"];

const roleOptions = [
  { value: USER_ROLES.DONADOR, label: ROLE_LABELS[USER_ROLES.DONADOR], Icon: User, desc: ROLE_DESCRIPTIONS[USER_ROLES.DONADOR] },
  { value: USER_ROLES.ONG, label: ROLE_LABELS[USER_ROLES.ONG], Icon: Handshake, desc: ROLE_DESCRIPTIONS[USER_ROLES.ONG] },
  { value: USER_ROLES.TRANSPORTISTA, label: ROLE_LABELS[USER_ROLES.TRANSPORTISTA], Icon: Truck, desc: ROLE_DESCRIPTIONS[USER_ROLES.TRANSPORTISTA] },
  { value: USER_ROLES.ADMIN, label: ROLE_LABELS[USER_ROLES.ADMIN], Icon: Shield, desc: ROLE_DESCRIPTIONS[USER_ROLES.ADMIN] },
];

export default function Register() {
  const [step, setStep] = useState(0);
  const [form, setForm] = useState({
    email: "",
    password: "",
    fullName: "",
    role: "",
    address: "",
    phone: "",
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();

  const set = (key) => (e) => {
    setForm((p) => ({ ...p, [key]: e.target.value }));
    setErrors((p) => ({ ...p, [key]: null }));
  };

  const validateStep0 = () => {
    const errs = {
      email: validateEmail(form.email),
      password: validatePassword(form.password),
    };
    setErrors(errs);
    return !errs.email && !errs.password;
  };

  const validateStep1 = () => {
    const errs = {
      fullName: validateRequired(form.fullName, "Nombre"),
      role: validateRequired(form.role, "Rol"),
      address: validateRequired(form.address, "Dirección"),
      phone: validatePhone(form.phone),
    };
    setErrors(errs);
    return !errs.fullName && !errs.role && !errs.address && !errs.phone;
  };

  const next = () => {
    if (step === 0 && !validateStep0()) return;
    if (step === 1 && !validateStep1()) return;
    setStep((s) => Math.min(s + 1, 2));
  };

  const back = () => setStep((s) => Math.max(s - 1, 0));

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const { data } = await api.post("/auth/register", {
        name: form.fullName,
        email: form.email,
        password: form.password,
        role: ROLE_TO_BACKEND[form.role] || "NATURAL",
        commune: form.address,
      });
      login(data.user, data.access_token);
      toast("Cuenta creada exitosamente", "success");
      navigate(form.role === "admin" ? "/admin" : "/dashboard");
    } catch (err) {
      const msg = err.response?.data?.error?.message || "Error al crear cuenta";
      toast(msg, "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden bg-gradient-to-br from-eco-50 via-white to-earth-50 px-4 py-8">
      <svg className="pointer-events-none absolute top-0 left-0 h-full w-full opacity-[0.03]" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <pattern id="leafs2" x="0" y="0" width="120" height="120" patternUnits="userSpaceOnUse">
            <path d="M60 20C50 35 50 55 60 70C70 55 70 35 60 20Z" fill="currentColor" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#leafs2)" className="text-eco-600" />
      </svg>

      <div className="relative w-full max-w-lg">
        <div className="mb-6 flex justify-center">
          <Logo size="lg" />
        </div>

        <div className="rounded-2xl border-2 border-eco-100 bg-white p-8 shadow-lg">
          <div className="mb-8 flex items-center justify-between">
            {steps.map((label, i) => (
              <div key={label} className="flex flex-1 items-center">
                <div
                  className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-sm font-bold ${
                    i <= step ? "bg-eco-600 text-white" : "bg-gray-100 text-gray-400"
                  }`}
                >
                  {i + 1}
                </div>
                {i < steps.length - 1 && (
                  <div className={`mx-2 h-1 flex-1 rounded ${i < step ? "bg-eco-600" : "bg-gray-100"}`} />
                )}
              </div>
            ))}
          </div>

          <h2 className="mb-1 text-xl font-bold text-gray-800">{steps[step]}</h2>
          <p className="mb-6 text-sm text-gray-500">
            {step === 0 && "Crea tu cuenta para empezar."}
            {step === 1 && "Cuéntanos sobre ti."}
            {step === 2 && "Revisa y confirma tus datos."}
          </p>

          {step === 0 && (
            <div className="space-y-4">
              <Input label="Email" type="email" icon={<Mail className="h-4 w-4" />} value={form.email} onChange={set("email")} error={errors.email} placeholder="usuario@ejemplo.com" autoComplete="email" />
              <Input label="Contraseña" type="password" icon={<Lock className="h-4 w-4" />} value={form.password} onChange={set("password")} error={errors.password} hint="Mín. 8 caracteres, 1 mayúscula, 1 número" placeholder="••••••••" autoComplete="new-password" />
            </div>
          )}

          {step === 1 && (
            <div className="space-y-4">
              <Input label="Nombre completo o de empresa" icon={<Building className="h-4 w-4" />} value={form.fullName} onChange={set("fullName")} error={errors.fullName} placeholder="Ej: María González / EcoConstrucción S.A." />

              <div>
                <label className="mb-2 block text-sm font-medium text-gray-700">¿Qué tipo de usuario eres?</label>
                <div className="grid grid-cols-2 gap-3">
                  {roleOptions.map((opt) => (
                    <button key={opt.value} type="button" onClick={() => setForm((p) => ({ ...p, role: opt.value }))} className={`flex flex-col items-center gap-2 rounded-xl border-2 p-4 text-center transition-all ${form.role === opt.value ? "border-eco-500 bg-eco-50 shadow-sm" : "border-gray-200 hover:border-eco-200 hover:bg-gray-50"}`}>
                      <opt.Icon className={`h-7 w-7 ${form.role === opt.value ? "text-eco-600" : "text-gray-400"}`} />
                      <span className="text-sm font-semibold text-gray-700">{opt.label}</span>
                      <span className="text-[11px] text-gray-400">{opt.desc}</span>
                    </button>
                  ))}
                </div>
                {errors.role && <p className="mt-1 text-xs text-red-500">{errors.role}</p>}
              </div>

              <Input label="Dirección" icon={<MapPin className="h-4 w-4" />} value={form.address} onChange={set("address")} error={errors.address} placeholder="Av. Principal 123, Ciudad" />
              <Input label="Teléfono (opcional)" icon={<Phone className="h-4 w-4" />} value={form.phone} onChange={set("phone")} error={errors.phone} placeholder="+56 9 1234 5678" />
            </div>
          )}

          {step === 2 && (
            <div className="space-y-4">
              <div className="rounded-lg border-2 border-eco-200 bg-eco-50 p-4">
                <div className="flex items-center gap-2 text-eco-700">
                  <Recycle className="h-5 w-5" />
                  <span className="text-sm font-semibold">Todo listo para crear tu cuenta</span>
                </div>
              </div>
              <dl className="space-y-2 text-sm">
                {[
                  ["Email", form.email],
                  ["Nombre", form.fullName],
                  ["Rol", roleOptions.find((r) => r.value === form.role)?.label],
                  ["Dirección", form.address],
                  ["Teléfono", form.phone || "—"],
                ].map(([k, v]) => (
                  <div key={k} className="flex justify-between border-b border-gray-50 py-1.5">
                    <dt className="text-gray-500">{k}</dt>
                    <dd className="font-medium text-gray-700">{v || "—"}</dd>
                  </div>
                ))}
              </dl>
            </div>
          )}

          <div className="mt-8 flex gap-3">
            {step > 0 && (
              <Button variant="outline" onClick={back} className="flex-1">
                <ArrowLeft className="h-4 w-4" />
                Atrás
              </Button>
            )}
            {step < 2 ? (
              <Button onClick={next} className="flex-1">
                Siguiente
                <ArrowRight className="h-4 w-4" />
              </Button>
            ) : (
              <Button onClick={handleSubmit} loading={loading} className="flex-1">Crear cuenta</Button>
            )}
          </div>
        </div>

        <p className="mt-6 text-center text-sm text-gray-500">
          ¿Ya tienes cuenta?{" "}
          <Link to="/login" className="font-medium text-eco-600 hover:underline">Inicia sesión</Link>
        </p>
      </div>
    </div>
  );
}
