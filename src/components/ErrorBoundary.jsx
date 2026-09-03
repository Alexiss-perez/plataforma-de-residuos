import { Component } from "react";
import { AlertCircle } from "./icons";

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, info) {
    console.error("ErrorBoundary caught:", error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-screen flex-col items-center justify-center bg-gray-50 px-4 text-center">
          <AlertCircle className="mb-4 h-12 w-12 text-red-400" />
          <h1 className="text-xl font-bold text-gray-800">
            Algo salió mal
          </h1>
          <p className="mt-2 max-w-md text-sm text-gray-500">
            Ocurrió un error inesperado. Puedes recargar la página o volver al
            panel principal.
          </p>
          <div className="mt-6 flex gap-3">
            <button
              onClick={() => window.location.reload()}
              className="rounded-lg bg-eco-600 px-4 py-2 text-sm font-semibold text-white hover:bg-eco-700"
            >
              Recargar
            </button>
            <button
              onClick={() => {
                this.setState({ hasError: false });
                window.location.href = "/dashboard";
              }}
              className="rounded-lg border border-gray-200 px-4 py-2 text-sm font-semibold text-gray-600 hover:bg-gray-50"
            >
              Ir al panel
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
