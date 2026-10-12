import { LockKeyhole, Plus, Trash2 } from "lucide-react";
import type { StyleExplorePairing } from "../../types";

const inputClass = "w-full rounded-lg border border-[var(--border)] bg-[var(--input)] px-3 py-2 text-sm outline-none focus:border-[var(--accent)]";
const buttonClass = "inline-flex items-center justify-center gap-1.5 rounded-lg border border-[var(--border)] px-3 py-2 text-sm hover:bg-[var(--hover)] disabled:opacity-45";

export function FixedArtistControls({ pairing, onChange, availableCount, minArtistCount, positive }: {
  pairing: StyleExplorePairing;
  onChange: (patch: Partial<StyleExplorePairing>) => void;
  availableCount: number;
  minArtistCount: number;
  positive: string;
}) {
  const fixed = pairing.fixed_artists;
  const sequential = pairing.pairing_mode === "sequential";
  const total = availableCount * pairing.samples_per_artist;
  const updateArtist = (index: number, patch: Partial<typeof fixed[number]>) => onChange({ fixed_artists: fixed.map((artist, position) => position === index ? { ...artist, ...patch } : artist) });
  const alreadyInPrompt = fixed.some((artist) => artist.id.trim() && positive.split(",").some((tag) => tag.trim() === artist.id.trim() || tag.includes(`::${artist.id.trim()}`)));
  return <section className="glass rounded-2xl p-5" aria-labelledby="fixed-artist-title">
    <div className="flex flex-wrap items-center gap-3">
      <div className="min-w-0 flex-1"><h2 id="fixed-artist-title" className="flex items-center gap-2 font-semibold"><LockKeyhole size={17} />固定画师搭配</h2><p className="mt-1 text-xs leading-5 text-[var(--muted)]">固定画师和权重会保留在每张候选中，包括深度探索与保存的画师串 Card。搭配池会自动排除这些画师。</p></div>
      <button type="button" className={buttonClass} disabled={fixed.length >= 29} onClick={() => onChange({ fixed_artists: [...fixed, { id: "", weight: 0.8 }] })}><Plus size={14} />添加固定画师</button>
    </div>
    {fixed.length === 0 ? <p className="mt-4 text-sm text-[var(--muted)]">尚未固定画师。添加 lk149 后，可以逐个测试它与池中其他画师的搭配。</p> : <div className="mt-4 grid gap-2 sm:grid-cols-2">{fixed.map((artist, index) => <div key={index} className="flex items-end gap-2 rounded-xl border border-[var(--border)] p-3">
      <label className="min-w-0 flex-1 text-xs text-[var(--muted)]">画师 Tag<input className={`${inputClass} mt-1 font-mono`} value={artist.id} aria-label={`固定画师 ${index + 1} Tag`} placeholder="例如 lk149" onChange={(event) => updateArtist(index, { id: event.target.value })} /></label>
      <label className="w-24 text-xs text-[var(--muted)]">固定权重<input className={`${inputClass} mt-1`} type="number" min={-3} max={3} step={0.1} value={artist.weight} aria-label={`固定画师 ${index + 1} 权重`} onChange={(event) => updateArtist(index, { weight: Math.max(-3, Math.min(3, Number(event.target.value))) })} /></label>
      <button type="button" className={`${buttonClass} px-2`} aria-label={`移除固定画师 ${index + 1}`} onClick={() => onChange({ fixed_artists: fixed.filter((_, position) => position !== index) })}><Trash2 size={15} /></button>
    </div>)}</div>}
    {alreadyInPrompt && <p className="mt-3 text-xs text-amber-500" role="alert">正面提示词中也包含固定画师，请移除那里的重复 Tag，避免重复加权。</p>}
    <div className="mt-4 grid items-start gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <label className="text-sm">搭配模式<select className={`${inputClass} mt-1`} value={pairing.pairing_mode} onChange={(event) => onChange({ pairing_mode: event.target.value as StyleExplorePairing["pairing_mode"] })}><option value="random">随机搭配</option><option value="sequential">逐个搭配（每张一个其他画师）</option></select></label>
      {sequential ? <label className="text-sm">每位搭配画师图片数<input className={`${inputClass} mt-1`} type="number" min={1} max={20} value={pairing.samples_per_artist} onChange={(event) => onChange({ samples_per_artist: Math.max(1, Math.min(20, Math.round(Number(event.target.value) || 1))) })} /></label> : <label className="text-sm">最多搭配画师数<input className={`${inputClass} mt-1`} type="number" min={minArtistCount} max={30 - fixed.length} value={pairing.max_artist_count} onChange={(event) => onChange({ max_artist_count: Math.max(1, Math.min(30 - fixed.length, Math.round(Number(event.target.value) || 1))) })} /><span className="mt-1 block text-xs text-[var(--muted)]">不含固定画师；设为 1 可随机测试单画师搭配。</span></label>}
      <label className="flex items-center gap-2 pt-7 text-sm"><input type="checkbox" className="accent-[var(--accent)]" checked={pairing.seed_mode === "fixed"} onChange={(event) => onChange({ seed_mode: event.target.checked ? "fixed" : "increment" })} />本轮使用相同种子对比</label>
    </div>
    <p className="mt-3 text-xs leading-5 text-[var(--muted)]">{sequential ? `按池中顺序覆盖 ${availableCount} 位搭配画师，每位 ${pairing.samples_per_artist} 张，共 ${total} 张。权重仍按下方分布采样；深度探索继续采用交叉与变异。` : `池中有 ${availableCount} 位可搭配画师；下方抽取数量只计算这些画师，固定项单独保留。`}</p>
    {sequential && total > 1000 && <p className="mt-2 text-sm text-amber-500" role="alert">超过每轮 1000 张上限，请使用较小的 ArtistPool 或减少每位图片数。</p>}
    {availableCount === 0 && <p className="mt-2 text-sm text-amber-500" role="alert">当前池中没有可搭配画师，请选择或保存其他 ArtistPool。</p>}
  </section>;
}
