import {
  createContext,
  useCallback,
  useContext,
  useState,
} from "react";
import { AlertCircle, Check, X } from "../icons";

const ToastContext = createContext(null);

const tones = {
  success: { icon: Check, ring: "border-eco-200", bg: "bg-eco-50", text: "text-eco-700" },
  error: { icon: AlertCircle, ring: "border-red-200", bg: "bg-red-50", text: "text-red-700" },
  info: { icon: AlertCircle, ring: "border-blue-200", bg: "bg-blue-50", text: "text-blue-700" },
};

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const remove = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const toast = useCallback(
    (message, tone = "success") => {
      const id = Date.now() + Math.random();
      setToasts((prev) => [...prev, { id, message, tone }]);
      setTimeout(() => remove(id), 4000);
    },
    [remove],
  );

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}
      <div className="fixed bottom-4 right-4 z-[100] flex flex-col gap-2">
        {toasts.map((t) => {
          const cfg = tones[t.tone];
          const Icon = cfg.icon;
          return (
            <div
              key={t.id}
              className={`flex items-center gap-3 rounded-lg border ${cfg.ring} ${cfg.bg} px-4 py-3 shadow-lg animate-[slideIn_0.2s_ease-out]`}
              role="alert"
            >
              <Icon className={`h-4 w-4 ${cfg.text}`} />
              <span className={`text-sm font-medium ${cfg.text}`}>
                {t.message}
              </span>
              <button
                onClick={() => remove(t.id)}
                className="ml-2 text-gray-400 hover:text-gray-600"
                aria-label="Cerrar"
              >
                <X className="h-3.5 w-3.5" />
              </button>
            </div>
          );
        })}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast must be used within ToastProvider");
  return ctx.toast;
}
