import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Button from "../components/ui/Button";
import Input from "../components/ui/Input";
import Logo from "../components/Logo";
import { useAuth } from "../lib/auth";
import { useToast } from "../components/ui/Toast";
import { validateEmail, validateRequired } from "../lib/validation";
import { Mail, Lock } from "../components/icons";
import api from "../lib/api";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    const errs = {
      email: validateEmail(email),
      password: validateRequired(password, "Contraseña"),
    };
    setErrors(errs);
    if (errs.email || errs.password) return;

    setLoading(true);
    try {
      const { data } = await api.post("/auth/login", { email, password });
      login(data.user, data.access_token);
      toast("Sesión iniciada", "success");
      navigate(data.user.role === "ADMIN" ? "/admin" : "/dashboard");
    } catch (err) {
      const msg = err.response?.data?.error?.message || "Credenciales inválidas";
      toast(msg, "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative flex min-h-screen flex-col items-center justify-center overflow-hidden bg-gradient-to-br from-eco-50 via-white to-earth-50 px-4">
      {/* Decoración SVG sutil */}
      <svg className="pointer-events-none absolute top-0 left-0 h-full w-full opacity-[0.03]" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <pattern id="leafs" x="0" y="0" width="120" height="120" patternUnits="userSpaceOnUse">
            <path d="M60 20C50 35 50 55 60 70C70 55 70 35 60 20Z" fill="currentColor" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#leafs)" className="text-eco-600" />
      </svg>

      <div className="relative w-full max-w-md">
        <div className="mb-8 flex flex-col items-center gap-3">
          <Link to="/">
            <Logo size="xl" />
          </Link>
          <p className="text-sm text-gray-400">
            Economía circular potenciada por IA
          </p>
        </div>

        <div className="rounded-2xl border-2 border-eco-100 bg-white p-8 shadow-lg">
          <h1 className="mb-1 text-2xl font-bold text-gray-800">Bienvenido</h1>
          <p className="mb-6 text-sm text-gray-500">
            Conecta tus residuos con quienes los necesitan.
          </p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Email"
              type="email"
              icon={<Mail className="h-4 w-4" />}
              value={email}
              onChange={(e) => {
                setEmail(e.target.value);
                setErrors((p) => ({ ...p, email: null }));
              }}
              error={errors.email}
              placeholder="usuario@ejemplo.com"
              autoComplete="email"
            />
            <Input
              label="Contraseña"
              type="password"
              icon={<Lock className="h-4 w-4" />}
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                setErrors((p) => ({ ...p, password: null }));
              }}
              error={errors.password}
              placeholder="••••••••"
              autoComplete="current-password"
            />

            <div className="flex justify-end">
              <Link
                to="/forgot-password"
                className="text-xs text-gray-400 hover:text-eco-600"
              >
                ¿Olvidaste tu contraseña?
              </Link>
            </div>

            <Button type="submit" loading={loading} className="w-full" size="lg">
              {loading ? "Ingresando..." : "Ingresar"}
            </Button>
          </form>

          <p className="mt-6 text-center text-sm text-gray-500">
            ¿No tienes cuenta?{" "}
            <Link
              to="/register"
              className="font-medium text-eco-600 hover:underline"
            >
              Regístrate
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
