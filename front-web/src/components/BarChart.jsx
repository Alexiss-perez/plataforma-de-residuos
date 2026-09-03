export default function BarChart({ data, className = "" }) {
  const max = Math.max(...data.map((d) => d.value));

  return (
    <div className={`flex items-end justify-between gap-2 ${className}`}>
      {data.map((d) => (
        <div key={d.month} className="flex flex-1 flex-col items-center gap-2">
          <div className="flex w-full flex-1 items-end">
            <div
              className="w-full rounded-t-md bg-gradient-to-t from-eco-400 to-eco-600 transition-all hover:from-eco-500 hover:to-eco-700"
              style={{ height: `${(d.value / max) * 100}%`, minHeight: "4px" }}
              title={`${d.value} kg`}
            />
          </div>
          <span className="text-[10px] text-gray-400">{d.month}</span>
        </div>
      ))}
    </div>
  );
}
