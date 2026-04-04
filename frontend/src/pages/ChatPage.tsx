import { useEffect, useState, useRef } from "react";
import { useParams, Link } from "react-router-dom";
import ReactMarkdown from "react-markdown";
import { api, ChatMessage } from "../api/client";

export default function ChatPage() {
  const { id } = useParams<{ id: string }>();
  const materialId = parseInt(id || "0");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [loading, setLoading] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    api
      .getChatHistory(materialId)
      .then(setMessages)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [materialId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    const text = input.trim();
    if (!text || sending) return;

    // Optimistically add user message
    const tempUserMsg: ChatMessage = {
      id: Date.now(),
      material_id: materialId,
      role: "user",
      content: text,
    };
    setMessages((prev) => [...prev, tempUserMsg]);
    setInput("");
    setSending(true);

    try {
      const assistantMsg = await api.sendChatMessage(materialId, text);
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      console.error(err);
      const errorMsg: ChatMessage = {
        id: Date.now() + 1,
        material_id: materialId,
        role: "assistant",
        content: "Sorry, something went wrong. Please try again.",
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setSending(false);
    }
  };

  const handleClear = async () => {
    if (!confirm("Clear all chat history?")) return;
    await api.clearChat(materialId);
    setMessages([]);
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner" />
        <p>Loading chat...</p>
      </div>
    );
  }

  return (
    <div className="chat-container">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
        <Link to={`/materials/${materialId}`} className="back-link">
          &larr; Back to material
        </Link>
        {messages.length > 0 && (
          <button className="btn btn-secondary" onClick={handleClear} style={{ padding: "4px 12px", fontSize: 12 }}>
            Clear chat
          </button>
        )}
      </div>

      <h2 style={{ marginBottom: 8 }}>Ask about this material</h2>

      <div className="chat-messages">
        {messages.length === 0 && !sending && (
          <div className="empty-state" style={{ padding: 40 }}>
            <p>Ask any question about your study material.</p>
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id} className={`chat-bubble ${msg.role}`}>
            {msg.role === "assistant" ? (
              <ReactMarkdown>{msg.content}</ReactMarkdown>
            ) : (
              msg.content
            )}
          </div>
        ))}

        {sending && <div className="chat-typing">AI is thinking...</div>}
        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input-area" onSubmit={handleSend}>
        <input
          type="text"
          placeholder="Ask a question..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={sending}
        />
        <button type="submit" className="btn btn-primary" disabled={sending || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}
