import { useEffect, useRef, useState } from "react";
import Navbar from "../components/Navbar";
import Button from "../components/ui/Button";
import Markdown from "../components/Markdown";
import MatchCard from "../components/MatchCard";
import { useToast } from "../components/ui/Toast";
import { Download, Send, Sparkles, Recycle } from "../components/icons";

const SUGGESTIONS = [
  "Tengo escombros de una demolición",
  "Dispongo de 50 kg de plástico PET",
  "Busco quien reciba palets de madera",
];

const MOCK_MATCHES = [
  {
    companyName: "Reciclajes del Sur",
    material: "escombros",
    distanceKm: 3.2,
    address: "Polígono Industrial 12, Maipú",
  },
  {
    companyName: "ConstruyeReutiliza",
    material: "escombros",
    distanceKm: 7.8,
    address: "Av. Pedro Aguirre Cerda 88",
  },
  {
    companyName: "ONG Recupera",
    material: "escombros",
    distanceKm: 12,
    address: "Calle Comercio 200, San Miguel",
  },
];

function MessageBubble({ role, content, matches, onAcceptMatch }) {
  const isUser = role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} animate-fadeIn`}>
      <div className={`max-w-[85%] ${isUser ? "" : "w-full"}`}>
        <div
          className={`rounded-2xl px-4 py-3 ${
            isUser
              ? "bg-eco-600 text-white"
              : "border border-gray-100 bg-white text-gray-700"
          }`}
        >
          {!isUser && (
            <div className="mb-1.5 flex items-center gap-1.5">
              <Recycle className="h-4 w-4 text-eco-600" />
              <span className="text-xs font-semibold text-eco-600">EcoMatch</span>
            </div>
          )}
          {isUser ? (
            <p className="whitespace-pre-wrap text-sm">{content}</p>
          ) : (
            <Markdown content={content} />
          )}
        </div>

        {!isUser && matches && matches.length > 0 && (
          <div className="mt-3 space-y-2">
            <p className="px-1 text-xs font-medium text-gray-500">
              {matches.length} receptores encontrados:
            </p>
            {matches.map((m, i) => (
              <MatchCard key={i} match={m} onAccept={onAcceptMatch} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function TypingIndicator() {
  return (
    <div className="flex justify-start animate-fadeIn">
      <div className="flex items-center gap-1.5 rounded-2xl border border-gray-100 bg-white px-4 py-3">
        <Recycle className="h-4 w-4 text-eco-600" />
        <span className="text-xs text-gray-400">EcoMatch está escribiendo</span>
        <div className="flex gap-1">
          <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-eco-400 [animation-delay:-0.3s]" />
          <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-eco-400 [animation-delay:-0.15s]" />
          <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-eco-400" />
        </div>
      </div>
    </div>
  );
}

export default function Chat() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "¡Hola! Soy **EcoMatch**, tu asistente para la economía circular. ♻️\n\nPuedo ayudarte a:\n- Publicar residuos\n- Buscar receptores cercanos\n- Coordinar retiros\n\n¿Qué residuos tienes disponibles?",
    },
  ]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const scrollRef = useRef(null);
  const toast = useToast();

  useEffect(() => {
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages, isTyping]);

  const sendMessage = async (text) => {
    if (!text.trim() || isTyping) return;

    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setInput("");
    setIsTyping(true);

    try {
      // TODO: api.post("/agent/chat", { messages })
      await new Promise((r) => setTimeout(r, 1200));

      let reply;
      let matches = null;

      if (text.toLowerCase().includes("escombro")) {
        reply =
          "Perfecto. Encontré **3 receptores** de escombros en un radio de 10 km de tu zona:\n\nRevisa las opciones debajo. ¿Te interesa alguno?";
        matches = MOCK_MATCHES;
      } else if (text.toLowerCase().includes("madera") || text.toLowerCase().includes("palet")) {
        reply =
          "Buena noticia — la madera tiene alta demanda. 🌲\n\nPara filtrar mejor:\n1. ¿Es madera **tratada** o **virgen**?\n2. ¿Cuántos **kilos** aproximadamente?\n3. ¿En qué **dirección** está?";
      } else if (text.toLowerCase().includes("pet") || text.toLowerCase().includes("plastico")) {
        reply =
          "Plástico PET — excelente para reciclaje. ♻️\n\n¿Está **limpio y separado** de otros plásticos? Eso afecta qué receptores pueden aceptarlo.";
      } else {
        reply =
          "Gracias por la información. Para encontrar el mejor receptor necesito algunos detalles más:\n\n1. ¿Qué **tipo específico** de material es?\n2. ¿Cuál es el **volumen o peso** aproximado?\n3. ¿En qué **dirección** se encuentra?\n\nCon estos datos podré buscar matches en tu zona.";
      }

      setMessages((prev) => [...prev, { role: "assistant", content: reply, matches }]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "⚠️ Ocurrió un error de conexión. Por favor, intenta nuevamente.",
        },
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleAcceptMatch = (match) => {
    setMessages((prev) => [
      ...prev,
      {
        role: "assistant",
        content: `¡Genial! Has seleccionado **${match.companyName}** (${match.distanceKm} km).\n\nPara coordinar el retiro necesito:\n- Fecha preferida\n- Horario de disponibilidad\n\n¿Cuándo te viene bien?`,
      },
    ]);
    toast(`Match aceptado: ${match.companyName}`, "success");
  };

  const exportConversation = () => {
    const text = messages
      .map((m) => `[${m.role === "user" ? "Yo" : "EcoMatch"}]\n${m.content}`)
      .join("\n\n---\n\n");
    const blob = new Blob([text], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `ecomatch-chat-${new Date().toISOString().slice(0, 10)}.md`;
    a.click();
    URL.revokeObjectURL(url);
    toast("Conversación exportada", "success");
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(input);
  };

  return (
    <div className="flex h-screen flex-col bg-gray-50">
      <Navbar />

      {/* Chat header bar */}
      <div className="border-b border-gray-100 bg-white px-4 py-2">
        <div className="mx-auto flex max-w-3xl items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-eco-50">
              <Sparkles className="h-4 w-4 text-eco-600" />
            </div>
            <div>
              <p className="text-sm font-semibold text-gray-800">Asistente EcoMatch</p>
              <p className="text-xs text-eco-500">● En línea — GLM 5.2</p>
            </div>
          </div>
          <div className="flex gap-2">
            <Button variant="ghost" size="sm" onClick={exportConversation}>
              <Download className="h-4 w-4" />
              <span className="hidden sm:inline">Exportar</span>
            </Button>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto" role="log" aria-live="polite">
        <div className="mx-auto max-w-3xl space-y-4 px-4 py-6">
          {messages.map((msg, i) => (
            <MessageBubble
              key={i}
              role={msg.role}
              content={msg.content}
              matches={msg.matches}
              onAcceptMatch={handleAcceptMatch}
            />
          ))}
          {isTyping && <TypingIndicator />}
        </div>
      </div>

      {/* Suggestions */}
      {messages.length <= 1 && (
        <div className="mx-auto w-full max-w-3xl px-4 pb-2">
          <p className="mb-2 px-1 text-xs text-gray-400">Sugerencias:</p>
          <div className="flex flex-wrap gap-2">
            {SUGGESTIONS.map((s) => (
              <button
                key={s}
                onClick={() => sendMessage(s)}
                disabled={isTyping}
                className="rounded-full border border-eco-200 bg-eco-50 px-3 py-1.5 text-xs font-medium text-eco-700 transition-colors hover:bg-eco-100 disabled:opacity-50"
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <form onSubmit={handleSubmit} className="border-t border-gray-100 bg-white px-4 py-3">
        <div className="mx-auto flex max-w-3xl items-end gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
            rows={1}
            disabled={isTyping}
            placeholder="Describe los residuos que tienes..."
            className="max-h-32 flex-1 resize-none rounded-xl border border-gray-200 px-4 py-2.5 text-sm focus:border-eco-500 focus:ring-2 focus:ring-eco-200 focus:outline-none disabled:opacity-50"
          />
          <Button type="submit" disabled={!input.trim() || isTyping} size="icon">
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </form>
    </div>
  );
}
