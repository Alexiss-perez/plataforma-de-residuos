import { useState } from "react";
import { Link } from "react-router-dom";
import Button from "../components/ui/Button";
import Input from "../components/ui/Input";
import Logo from "../components/Logo";
import { useToast } from "../components/ui/Toast";
import { validateEmail } from "../lib/validation";
import { Mail, ArrowLeft, Check } from "../components/icons";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const toast = useToast();

  const handleSubmit = async (e) => {
    e.preventDefault();
    const err = validateEmail(email);
    if (err) {
      setError(err);
      return;
    }
    setLoading(true);
    try {
      // TODO: api.post("/auth/forgot", { email })
      await new Promise((r) => setTimeout(r, 1000));
      setSent(true);
      toast("Email de recuperación enviado", "success");
    } catch {
      toast("Error al enviar email", "error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-eco-50 to-earth-50 px-4">
      <div className="w-full max-w-md">
        <div className="mb-6 flex justify-center">
          <Logo />
        </div>

        <div className="rounded-2xl border border-eco-100 bg-white p-8 shadow-sm">
          {sent ? (
            <div className="text-center">
              <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-eco-100">
                <Check className="h-6 w-6 text-eco-600" />
              </div>
              <h1 className="text-xl font-bold text-gray-800">
                Revisa tu email
              </h1>
              <p className="mt-2 text-sm text-gray-500">
                Enviamos instrucciones de recuperación a{" "}
                <span className="font-medium text-gray-700">{email}</span>
              </p>
              <Link to="/login" className="mt-6 inline-block">
                <Button variant="outline" size="sm">
                  <ArrowLeft className="h-4 w-4" />
                  Volver a login
                </Button>
              </Link>
            </div>
          ) : (
            <>
              <h1 className="text-xl font-bold text-gray-800">
                Recuperar contraseña
              </h1>
              <p className="mb-6 mt-1 text-sm text-gray-500">
                Te enviaremos un email con instrucciones.
              </p>
              <form onSubmit={handleSubmit} className="space-y-4">
                <Input
                  label="Email"
                  type="email"
                  icon={<Mail className="h-4 w-4" />}
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value);
                    setError(null);
                  }}
                  error={error}
                  placeholder="empresa@ejemplo.com"
                  autoComplete="email"
                />
                <Button type="submit" loading={loading} className="w-full">
                  Enviar instrucciones
                </Button>
              </form>
              <Link
                to="/login"
                className="mt-4 flex items-center justify-center gap-1.5 text-sm text-gray-500 hover:text-eco-600"
              >
                <ArrowLeft className="h-4 w-4" />
                Volver a login
              </Link>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
