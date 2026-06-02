export default function ErrorBubble({ message }) {
  return (
    <div className="flex items-start gap-3 mb-4">
      <div className="w-8 h-8 rounded-full bg-red-500 flex items-center justify-center text-white text-sm font-bold shrink-0">
        !
      </div>
      <div className="bg-red-50 border border-red-200 rounded-2xl rounded-tl-sm px-4 py-3 max-w-2xl">
        <p className="text-red-800 text-sm font-medium mb-1">Something went wrong</p>
        <p className="text-red-700 text-sm">{message || "I couldn't retrieve that data. Try rephrasing your question."}</p>
      </div>
    </div>
  );
}
