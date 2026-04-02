type AssetCardProps = {
  title?: string;
  /** Optional text preview (e.g. copy variation). */
  preview?: string;
  onDownload?: () => void;
};

export function AssetCard({
  title = "Ad creative",
  preview,
  onDownload,
}: AssetCardProps) {
  return (
    <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white">
      <div className="max-h-32 min-h-[4.5rem] overflow-y-auto bg-slate-100 p-3 text-xs leading-relaxed text-slate-700">
        {preview ? (
          preview
        ) : (
          <span className="text-gray-600">No preview</span>
        )}
      </div>
      <div className="p-3">
        <p className="text-sm text-slate-800">{title}</p>
        <button
          type="button"
          onClick={onDownload}
          className="mt-2 text-xs text-violet-600 hover:text-violet-700"
        >
          Download
        </button>
      </div>
    </div>
  );
}
