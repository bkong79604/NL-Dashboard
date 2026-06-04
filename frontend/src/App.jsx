import { useState, useEffect, useRef } from "react";
import { classifyQuery, sendQuery, checkHealth } from "./services/api";
import ChatInput from "./components/ChatInput";
import ResultTable from "./components/ResultTable";
import ResultChart from "./components/ResultChart";
import ErrorBubble from "./components/ErrorBubble";

// Message types:
// "user"      — user's typed question
// "off_topic" — friendly AI reply for non-data questions
// "meta"      — table/capability description
// "result"    — data result (table or chart)
// "error"     — error message

let idCounter = 0;
const uid = () => ++idCounter;

export default function App() {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [health, setHealth] = useState(null);
  const bottomRef = useRef(null);

  useEffect(() => {
    checkHealth()
      .then((data) => setHealth(data.ollama === "connected" ? "ok" : "error"))
      .catch(() => setHealth("error"));
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const addMessage = (msg) =>
    setMessages((prev) => [...prev, { id: uid(), ...msg }]);

  const handleQuery = async (query) => {
    if (isLoading) return;

    addMessage({ type: "user", text: query });
    setIsLoading(true);

    try {
      // Step 1: Classify intent
      const { intent, message } = await classifyQuery(query);

      if (intent === "OFF_TOPIC") {
        addMessage({ type: "off_topic", text: message });
        return;
      }

      if (intent === "META_QUERY") {
        addMessage({ type: "meta", text: message });
        return;
      }

      // Step 2: DATA_QUERY — execute directly, no confirmation
      const data = await sendQuery(query);
      addMessage({ type: "result", data });

    } catch (err) {
      const detail = err?.response?.data?.detail || "Something went wrong. Please try again.";
      addMessage({ type: "error", message: detail });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between sticky top-0 z-10">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <div>
            <h1 className="text-base font-semibold text-gray-900">NL Dashboard</h1>
            <p className="text-xs text-gray-500">Ask questions about your data in plain English</p>
          </div>
        </div>
        <div className="flex items-center gap-2 text-xs">
          <span className={`w-2 h-2 rounded-full ${health === "ok" ? "bg-green-500" : health === "error" ? "bg-red-500" : "bg-yellow-400"}`} />
          <span className="text-gray-500">
            {health === "ok" ? "Ollama connected" : health === "error" ? "Ollama unavailable" : "Checking..."}
          </span>
        </div>
      </header>

      {/* Chat area */}
      <main className="flex-1 overflow-y-auto px-4 py-6 max-w-4xl w-full mx-auto">
        {messages.length === 0 && !isLoading && (
          <div className="text-center mt-20">
            <div className="w-16 h-16 bg-indigo-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
            </div>
            <h2 className="text-lg font-semibold text-gray-800 mb-2">Ask anything about your data</h2>
            <p className="text-sm text-gray-500 max-w-md mx-auto">
              Try: <span className="italic">"Show me the top 10 customers by total order value"</span> or{" "}
              <span className="italic">"Which sales territory had the highest revenue?"</span>
            </p>
          </div>
        )}

        {messages.map((msg) => {
          // User bubble
          if (msg.type === "user") {
            return (
              <div key={msg.id} className="flex justify-end mb-4">
                <div className="bg-indigo-600 text-white rounded-2xl rounded-tr-sm px-4 py-3 max-w-xl text-sm">
                  {msg.text}
                </div>
              </div>
            );
          }

          // Off-topic — friendly redirect
          if (msg.type === "off_topic") {
            return (
              <div key={msg.id} className="flex items-start gap-3 mb-4">
                <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-white text-sm font-bold shrink-0">AI</div>
                <div className="bg-white border border-gray-200 rounded-2xl rounded-tl-sm px-4 py-3 max-w-2xl">
                  <p className="text-gray-800 text-sm">{msg.text}</p>
                </div>
              </div>
            );
          }

          // Meta query — table/capability info
          if (msg.type === "meta") {
            const lines = msg.text.split("\n");
            return (
              <div key={msg.id} className="flex items-start gap-3 mb-4">
                <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-white text-sm font-bold shrink-0">AI</div>
                <div className="bg-white border border-gray-200 rounded-2xl rounded-tl-sm px-4 py-3 max-w-2xl">
                  {lines.map((line, i) => {
                    const isTableLine = ["📦","🧾","📋","👤","🗺️","🏷️","🔗","🏪"].some(e => line.startsWith(e));
                    if (isTableLine) {
                      const [bold, ...rest] = line.split(" — ");
                      return <p key={i} className="text-sm text-gray-800 mb-1"><span className="font-semibold">{bold}</span>{rest.length ? " — " + rest.join(" — ") : ""}</p>;
                    }
                    if (line.startsWith("- *")) {
                      return <p key={i} className="text-sm text-gray-500 ml-3">• {line.replace(/- \*|\*/g, "")}</p>;
                    }
                    if (line.trim() === "") return <br key={i} />;
                    return <p key={i} className="text-sm text-gray-800 mb-1">{line}</p>;
                  })}
                </div>
              </div>
            );
          }

          // Data result
          if (msg.type === "result") {
            const { chart_type, columns, rows, row_count } = msg.data;
            return (
              <div key={msg.id} className="mb-6 ml-11">
                {chart_type === "table" ? (
                  <ResultTable columns={columns} rows={rows} rowCount={row_count} />
                ) : (
                  <>
                    <ResultChart chartType={chart_type} columns={columns} rows={rows} rowCount={row_count} />
                    <details className="mt-3">
                      <summary className="text-xs text-gray-400 cursor-pointer hover:text-gray-600">View raw data</summary>
                      <ResultTable columns={columns} rows={rows} rowCount={row_count} />
                    </details>
                  </>
                )}
              </div>
            );
          }

          // Error
          if (msg.type === "error") {
            return <ErrorBubble key={msg.id} message={msg.message} />;
          }

          return null;
        })}

        {/* Loading indicator */}
        {isLoading && (
          <div className="flex items-start gap-3 mb-4">
            <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-white text-sm font-bold shrink-0">AI</div>
            <div className="bg-indigo-50 border border-indigo-200 rounded-2xl rounded-tl-sm px-4 py-3">
              <div className="flex gap-1 items-center h-4">
                <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
              </div>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </main>

      {/* Input */}
      <footer className="bg-white border-t border-gray-200 px-4 py-4 sticky bottom-0">
        <div className="max-w-4xl mx-auto">
          <ChatInput onSubmit={handleQuery} isLoading={isLoading} />
        </div>
      </footer>
    </div>
  );
}
