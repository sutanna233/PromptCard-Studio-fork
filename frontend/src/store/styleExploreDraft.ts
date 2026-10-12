import { create } from "zustand";
import { DEFAULT_PARAMS } from "./generate";
import type { GenerateParamsPayload, GenerateVibe, StyleExplorePairing } from "../types";

const DRAFT_KEY = "promptcard_style_explore_draft_v1";

type StyleExploreDraft = {
  positive: string;
  negative: string;
  params: GenerateParamsPayload;
  vibes: GenerateVibe[];
  lastSelectedRunId: string;
  pairing: StyleExplorePairing;
};

const defaults = (): StyleExploreDraft => ({ positive: "", negative: "", params: { ...DEFAULT_PARAMS }, vibes: [], lastSelectedRunId: "", pairing: { fixed_artists: [], pairing_mode: "random", samples_per_artist: 1, max_artist_count: 10, seed_mode: "increment" } });

function loadDraft(): StyleExploreDraft {
  try {
    const parsed = JSON.parse(localStorage.getItem(DRAFT_KEY) || "null");
    if (parsed && typeof parsed === "object") return { ...defaults(), ...parsed, params: { ...DEFAULT_PARAMS, ...(parsed.params || {}) }, vibes: Array.isArray(parsed.vibes) ? parsed.vibes : [], pairing: { ...defaults().pairing, ...(parsed.pairing || {}), fixed_artists: Array.isArray(parsed.pairing?.fixed_artists) ? parsed.pairing.fixed_artists : [] } };
  } catch { /* localStorage 不可用时使用内存默认值 */ }
  return defaults();
}

function persist(draft: StyleExploreDraft) {
  try { localStorage.setItem(DRAFT_KEY, JSON.stringify(draft)); } catch { /* ignore */ }
}

type DraftState = StyleExploreDraft & {
  setPrompts: (positive: string, negative: string) => void;
  setParams: (patch: Partial<GenerateParamsPayload>) => void;
  setVibes: (vibes: GenerateVibe[]) => void;
  updateVibe: (id: string, patch: Partial<GenerateVibe>) => void;
  removeVibe: (id: string) => void;
  setLastSelectedRunId: (id: string) => void;
  setPairing: (patch: Partial<StyleExplorePairing>) => void;
  importWorkspaceSnapshot: (positive: string, negative: string, params: GenerateParamsPayload, vibes: GenerateVibe[]) => void;
};

export const useStyleExploreDraft = create<DraftState>((set, get) => ({
  ...loadDraft(),
  setPrompts(positive, negative) { const next = { ...get(), positive, negative }; persist(next); set({ positive, negative }); },
  setParams(patch) { const params = { ...get().params, ...patch }; persist({ ...get(), params }); set({ params }); },
  setVibes(vibes) { persist({ ...get(), vibes }); set({ vibes }); },
  updateVibe(id, patch) { const vibes = get().vibes.map((item) => item.id === id ? { ...item, ...patch } : item); persist({ ...get(), vibes }); set({ vibes }); },
  removeVibe(id) { const vibes = get().vibes.filter((item) => item.id !== id); persist({ ...get(), vibes }); set({ vibes }); },
  setLastSelectedRunId(lastSelectedRunId) { persist({ ...get(), lastSelectedRunId }); set({ lastSelectedRunId }); },
  setPairing(patch) { const pairing = { ...get().pairing, ...patch }; persist({ ...get(), pairing }); set({ pairing }); },
  importWorkspaceSnapshot(positive, negative, params, vibes) {
    const next = { ...get(), positive, negative, params: { ...DEFAULT_PARAMS, ...params }, vibes: [...vibes] };
    persist(next); set({ positive: next.positive, negative: next.negative, params: next.params, vibes: next.vibes });
  },
}));
