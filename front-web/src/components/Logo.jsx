export default function Logo({ size = "md", className = "" }) {
  const sizes = {
    sm: { svg: "h-6 w-6", text: "text-lg" },
    md: { svg: "h-8 w-8", text: "text-2xl" },
    lg: { svg: "h-12 w-12", text: "text-3xl" },
    xl: { svg: "h-14 w-14", text: "text-4xl" },
  };
  const s = sizes[size] || sizes.md;

  return (
    <div className={`flex items-center gap-2.5 ${className}`}>
      <svg className={`${s.svg} text-eco-600`} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M7 19l-3-3 3-3" /><path d="M4 16h13" />
        <path d="M17 5l3 3-3 3" /><path d="M20 8H7" />
        <path d="M12 19l-2 2 2 2" /><path d="M10 21h6" />
      </svg>
      <span className={`${s.text} font-extrabold tracking-tight`}>
        <span className="text-eco-700">Eco</span>
        <span className="text-earth-600">Innova</span>
      </span>
    </div>
  );
}
