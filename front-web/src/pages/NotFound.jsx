import { Link } from "react-router-dom";
import { Recycle } from "../components/icons";

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gray-50 px-4 text-center">
      <Recycle className="mb-4 h-12 w-12 text-eco-300" />
      <h1 className="text-4xl font-bold text-gray-800">404</h1>
      <p className="mt-2 text-sm text-gray-500">
        Esta página no existe en el ecosistema.
      </p>
      <Link
        to="/dashboard"
        className="mt-6 rounded-lg bg-eco-600 px-4 py-2 text-sm font-semibold text-white hover:bg-eco-700"
      >
        Volver al panel
      </Link>
    </div>
  );
}
