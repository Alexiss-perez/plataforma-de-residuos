import { Link } from "react-router-dom";
import Button from "../components/ui/Button";
import Logo from "../components/Logo";
import {
  Recycle,
  Sparkles,
  MapPin,
  Truck,
  Leaf,
  TrendingUp,
  Globe,
  Heart,
  ArrowRight,
  Github,
  User,
  Handshake,
  Shield,
} from "../components/icons";

const features = [
  { icon: Sparkles, title: "Agente IA GLM 5.2", desc: "Un asistente que entiende tus residuos, repregunta si falta info y busca matches automáticamente." },
  { icon: MapPin, title: "Logística inteligente", desc: "Calcula distancias y rutas entre generador y receptor para minimizar costos de transporte." },
  { icon: TrendingUp, title: "Métricas de impacto", desc: "Visualiza kg desviados de vertederos, CO₂ ahorrado y tu contribución a la economía circular." },
  { icon: Leaf, title: "Cero alucinaciones", desc: "El agente solo opera con datos reales del backend. Nunca inventa empresas, direcciones ni leyes." },
  { icon: Truck, title: "Coordinación de retiros", desc: "Agenda retiros, asigna transportistas y confirma transacciones dentro de la plataforma." },
  { icon: Globe, title: "Para todos los actores", desc: "Donadores, ONGs, transportistas y admin en una sola red circular." },
];

const stats = [
  { value: "38%", label: "de residuos reutilizados" },
  { value: "10km", label: "radio de matching por defecto" },
  { value: "24/7", label: "agente disponible siempre" },
  { value: "0", label: "alucinaciones permitidas" },
];

const steps = [
  { n: "01", title: "Publica tu residuo", desc: "Describe qué tienes, cuánto y dónde. El agente IA te guía si falta algo." },
  { n: "02", title: "Recibe matches", desc: "La plataforma busca receptores cercanos que necesiten tu material." },
  { n: "03", title: "Coordina el retiro", desc: "Agenda el transporte, confirma la transacción y mide tu impacto." },
];

const userTypes = [
  { icon: User, title: "Donador", desc: "Persona natural que dona residuos" },
  { icon: Handshake, title: "ONG / Fundación", desc: "Recibe residuos para sus programas" },
  { icon: Truck, title: "Transportista", desc: "Recolector que mueve residuos" },
  { icon: Shield, title: "Admin", desc: "Gestiona la plataforma completa" },
];

export default function Landing() {
  return (
    <div className="min-h-screen bg-white">
      {/* Nav */}
      <header className="sticky top-0 z-50 border-b-2 border-eco-100 bg-white/95 backdrop-blur">
        <div className="mx-auto flex h-20 max-w-7xl items-center justify-between px-6">
          <Logo size="md" />
          <nav className="hidden items-center gap-6 md:flex">
            <a href="#features" className="text-sm text-gray-600 hover:text-eco-600">Características</a>
            <a href="#how" className="text-sm text-gray-600 hover:text-eco-600">Cómo funciona</a>
            <a href="#users" className="text-sm text-gray-600 hover:text-eco-600">Usuarios</a>
            <a href="#impact" className="text-sm text-gray-600 hover:text-eco-600">Impacto</a>
          </nav>
          <div className="flex items-center gap-2">
            <Link to="/login"><Button variant="ghost" size="sm">Ingresar</Button></Link>
            <Link to="/register"><Button size="sm">Registrarse</Button></Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-eco-50 via-white to-earth-50" />
        <svg className="pointer-events-none absolute inset-0 h-full w-full opacity-[0.04]" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <pattern id="heroLeafs" x="0" y="0" width="100" height="100" patternUnits="userSpaceOnUse">
              <path d="M50 15C40 30 40 50 50 65C60 50 60 30 50 15Z" fill="currentColor" />
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#heroLeafs)" className="text-eco-600" />
        </svg>

        <div className="relative mx-auto max-w-6xl px-4 py-24 text-center md:py-36">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border-2 border-eco-200 bg-eco-50 px-4 py-2 text-xs font-medium text-eco-700">
            <Recycle className="h-4 w-4" />
            Economía circular potenciada por IA
          </div>
          <h1 className="mx-auto max-w-3xl text-5xl font-bold tracking-tight text-gray-900 md:text-7xl">
            Conecta tus residuos con <span className="text-eco-600">quien los necesita</span>
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-gray-500">
            EcoMatch usa un agente de IA para encontrar el mejor destino para tus residuos — reduciendo vertederos, costos y impacto ambiental.
          </p>
          <div className="mt-10 flex flex-col items-center justify-center gap-3 sm:flex-row">
            <Link to="/register"><Button size="lg" className="w-full sm:w-auto">Empezar gratis<ArrowRight className="h-4 w-4" /></Button></Link>
            <Link to="/login"><Button variant="outline" size="lg" className="w-full sm:w-auto">Ya tengo cuenta</Button></Link>
          </div>

          <div className="mx-auto mt-20 grid max-w-3xl grid-cols-2 gap-6 md:grid-cols-4">
            {stats.map((s) => (
              <div key={s.label}>
                <p className="text-4xl font-bold text-eco-600">{s.value}</p>
                <p className="mt-1 text-xs text-gray-500">{s.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* User types */}
      <section id="users" className="mx-auto max-w-6xl px-4 py-20">
        <div className="mb-12 text-center">
          <h2 className="text-3xl font-bold text-gray-900">Una plataforma, todos los roles</h2>
          <p className="mt-3 text-gray-500">EcoMatch conecta a todos los actores de la economía circular.</p>
        </div>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {userTypes.map((u) => (
            <div key={u.title} className="rounded-2xl border-2 border-gray-100 bg-white p-6 text-center transition-all hover:border-eco-200 hover:shadow-md">
              <div className="mb-3 inline-flex h-14 w-14 items-center justify-center rounded-xl bg-eco-50">
                <u.icon className="h-7 w-7 text-eco-600" />
              </div>
              <h3 className="mb-1 text-lg font-semibold text-gray-800">{u.title}</h3>
              <p className="text-sm text-gray-500">{u.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section id="features" className="bg-gradient-to-b from-eco-50/50 to-white py-20">
        <div className="mx-auto max-w-6xl px-4">
          <div className="mb-12 text-center">
            <h2 className="text-3xl font-bold text-gray-900">Todo lo que necesitas para circular</h2>
            <p className="mt-3 text-gray-500">Una plataforma, todos los actores de la economía circular.</p>
          </div>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {features.map((f) => (
              <div key={f.title} className="rounded-2xl border border-gray-100 bg-white p-6 transition-shadow hover:shadow-md">
                <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-eco-50">
                  <f.icon className="h-6 w-6 text-eco-600" />
                </div>
                <h3 className="mb-2 text-lg font-semibold text-gray-800">{f.title}</h3>
                <p className="text-sm text-gray-500">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section id="how" className="bg-gradient-to-b from-eco-50 to-white py-20">
        <div className="mx-auto max-w-6xl px-4">
          <div className="mb-12 text-center">
            <h2 className="text-3xl font-bold text-gray-900">Cómo funciona</h2>
            <p className="mt-3 text-gray-500">Del residuo al retiro en tres pasos.</p>
          </div>
          <div className="grid gap-8 md:grid-cols-3">
            {steps.map((s) => (
              <div key={s.n} className="relative">
                <span className="text-6xl font-bold text-eco-200">{s.n}</span>
                <h3 className="mt-2 text-xl font-semibold text-gray-800">{s.title}</h3>
                <p className="mt-2 text-sm text-gray-500">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Impact / CTA */}
      <section id="impact" className="mx-auto max-w-6xl px-4 py-20">
        <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-eco-600 to-eco-800 px-8 py-16 text-center text-white">
          <Leaf className="mx-auto mb-6 h-12 w-12 text-eco-200" />
          <h2 className="text-3xl font-bold">Cada kilo cuenta. Cada match importa.</h2>
          <p className="mx-auto mt-4 max-w-xl text-eco-100">
            Únete a la red de empresas y personas que están transformando sus residuos en recursos.
          </p>
          <Link to="/register" className="inline-block">
            <Button variant="secondary" size="lg" className="mt-8 bg-white text-eco-700 hover:bg-eco-50">
              Crear cuenta gratuita<ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-100 py-12">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-4 px-4 md:flex-row">
          <Logo size="sm" />
          <p className="flex items-center gap-1.5 text-sm text-gray-400">
            Hecho con <Heart className="h-4 w-4 text-red-400" /> para el planeta
          </p>
          <a href="https://github.com" className="text-gray-400 hover:text-gray-600" aria-label="GitHub">
            <Github className="h-5 w-5" />
          </a>
        </div>
      </footer>
    </div>
  );
}
