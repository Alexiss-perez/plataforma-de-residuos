const variants = {
  primary:
    "bg-eco-600 text-white hover:bg-eco-700 focus-visible:ring-eco-300 disabled:bg-eco-300",
  secondary:
    "border border-eco-200 bg-eco-50 text-eco-700 hover:bg-eco-100 focus-visible:ring-eco-200 disabled:opacity-50",
  outline:
    "border border-gray-200 bg-white text-gray-700 hover:bg-gray-50 focus-visible:ring-gray-200 disabled:opacity-50",
  ghost:
    "text-gray-600 hover:bg-gray-100 focus-visible:ring-gray-200 disabled:opacity-50",
  danger:
    "bg-red-600 text-white hover:bg-red-700 focus-visible:ring-red-300 disabled:bg-red-300",
};

const sizes = {
  sm: "px-3 py-1.5 text-xs gap-1.5",
  md: "px-4 py-2.5 text-sm gap-2",
  lg: "px-5 py-3 text-base gap-2",
  icon: "p-2",
};

export default function Button({
  variant = "primary",
  size = "md",
  loading = false,
  children,
  className = "",
  ...props
}) {
  return (
    <button
      className={`inline-flex items-center justify-center rounded-lg font-semibold transition-colors focus-visible:ring-2 focus-visible:outline-none disabled:cursor-not-allowed ${variants[variant]} ${sizes[size]} ${className}`}
      disabled={loading || props.disabled}
      {...props}
    >
      {loading && (
        <span className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
      )}
      {children}
    </button>
  );
}
