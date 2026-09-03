export default function Spinner({ size = "md", className = "" }) {
  const dims = { sm: "h-4 w-4", md: "h-8 w-8", lg: "h-12 w-12" };
  return (
    <div
      className={`${dims[size]} animate-spin rounded-full border-2 border-eco-200 border-t-eco-600 ${className}`}
      role="status"
      aria-label="Cargando"
    />
  );
}

export function Skeleton({ className = "" }) {
  return (
    <div
      className={`animate-pulse rounded-lg bg-gray-100 ${className}`}
      aria-hidden="true"
    />
  );
}
