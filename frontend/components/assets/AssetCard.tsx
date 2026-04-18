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
    <div className="overflow-hidden rounded-2xl border border-white/[0.06] bg-white/[0.04] backdrop-blur-sm">
      <div className="max-h-32 min-h-[4.5rem] overflow-y-auto bg-black/20 p-3 text-xs leading-relaxed text-slate-400">
        {preview ? (
          preview
        ) : (
          <span className="text-slate-600">No preview</span>
        )}
      </div>
      <div className="p-3">
        <p className="text-sm text-slate-200">{title}</p>
        <button
          type="button"
          onClick={onDownload}
          className="mt-2 text-xs text-violet-400 hover:text-violet-300"
        >
          Download
        </button>
      </div>
    </div>
  );
}
