const tones = {
  eco: "bg-eco-100 text-eco-700",
  earth: "bg-earth-100 text-earth-700",
  gray: "bg-gray-100 text-gray-600",
  red: "bg-red-100 text-red-700",
  amber: "bg-amber-100 text-amber-700",
  blue: "bg-blue-100 text-blue-700",
};

export default function Badge({ tone = "gray", children, className = "" }) {
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${tones[tone]} ${className}`}
    >
      {children}
    </span>
  );
}
