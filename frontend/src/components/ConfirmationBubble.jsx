export default function ConfirmationBubble({ text }) {
  return (
    <div className="flex items-start gap-3 mb-4">
      <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-white text-sm font-bold shrink-0">
        AI
      </div>
      <div className="bg-indigo-50 border border-indigo-200 rounded-2xl rounded-tl-sm px-4 py-3 max-w-2xl">
        <p className="text-indigo-900 text-sm">{text}</p>
      </div>
    </div>
  );
}
