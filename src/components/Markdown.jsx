function renderInline(text) {
  const parts = [];
  const regex = /(\*\*([^*]+)\*\*|\*([^*]+)\*|`([^`]+)`)/g;
  let last = 0;
  let m;

  while ((m = regex.exec(text)) !== null) {
    if (m.index > last) parts.push(text.slice(last, m.index));
    if (m[2]) parts.push(<strong key={m.index} className="font-semibold">{m[2]}</strong>);
    else if (m[3]) parts.push(<em key={m.index} className="italic">{m[3]}</em>);
    else if (m[4]) parts.push(<code key={m.index} className="rounded bg-gray-100 px-1 py-0.5 text-xs">{m[4]}</code>);
    last = regex.lastIndex;
  }
  if (last < text.length) parts.push(text.slice(last));
  return parts;
}

export default function Markdown({ content }) {
  const lines = content.split("\n");
  const elements = [];
  let listItems = [];

  const flushList = () => {
    if (listItems.length > 0) {
      elements.push(
        <ul key={`ul-${elements.length}`} className="ml-4 list-disc space-y-1">
          {listItems}
        </ul>,
      );
      listItems = [];
    }
  };

  lines.forEach((line, i) => {
    if (line.startsWith("### ")) {
      flushList();
      elements.push(
        <h3 key={i} className="mt-2 text-sm font-bold">{renderInline(line.slice(4))}</h3>,
      );
    } else if (line.startsWith("## ")) {
      flushList();
      elements.push(
        <h2 key={i} className="mt-2 text-base font-bold">{renderInline(line.slice(3))}</h2>,
      );
    } else if (line.startsWith("# ")) {
      flushList();
      elements.push(
        <h1 key={i} className="mt-2 text-lg font-bold">{renderInline(line.slice(2))}</h1>,
      );
    } else if (line.startsWith("- ") || line.startsWith("* ")) {
      listItems.push(
        <li key={i} className="text-sm">{renderInline(line.slice(2))}</li>,
      );
    } else if (line.match(/^\d+\.\s/)) {
      listItems.push(
        <li key={i} className="text-sm">{renderInline(line.replace(/^\d+\.\s/, ""))}</li>,
      );
    } else if (line.trim() === "") {
      flushList();
      elements.push(<div key={i} className="h-2" />);
    } else {
      flushList();
      elements.push(
        <p key={i} className="text-sm leading-relaxed">{renderInline(line)}</p>,
      );
    }
  });
  flushList();

  return <div className="space-y-1">{elements}</div>;
}
