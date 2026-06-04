export default function ConfirmationPrompt({ confirmation, onYes, onNo, disabled }) {
  return (
    <div className="flex items-start gap-3 mb-4">
      <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-white text-sm font-bold shrink-0">
        AI
      </div>
      <div className="flex flex-col gap-3 max-w-2xl">
        <div className="bg-indigo-50 border border-indigo-200 rounded-2xl rounded-tl-sm px-4 py-3">
          <p className="text-indigo-900 text-sm">{confirmation}</p>
        </div>

        {/* YES / NO buttons */}
        <div className="flex gap-2">
          <button
            onClick={onYes}
            disabled={disabled}
            className="px-6 py-2 rounded-lg bg-indigo-600 text-white text-sm font-semibold hover:bg-indigo-700 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            Yes
          </button>
          <button
            onClick={onNo}
            disabled={disabled}
            className="px-6 py-2 rounded-lg bg-white border border-gray-300 text-gray-700 text-sm font-semibold hover:bg-gray-50 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            No
          </button>
        </div>
      </div>
    </div>
  );
}
