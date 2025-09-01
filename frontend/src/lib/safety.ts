export type Safety = {
  stealth: boolean
  reducedMotion: boolean
  reduceEffects: boolean
}

const SAFETY_KEY = 'po_drafter_safety_v1'

export function loadSafety(): Safety {
  if (typeof localStorage === 'undefined') return { stealth: false, reducedMotion: false, reduceEffects: false }
  try {
    const s = localStorage.getItem(SAFETY_KEY)
    return s ? (JSON.parse(s) as Safety) : { stealth: false, reducedMotion: false, reduceEffects: false }
  } catch {
    return { stealth: false, reducedMotion: false, reduceEffects: false }
  }
}

export function saveSafety(s: Safety): void {
  if (typeof localStorage === 'undefined') return
  localStorage.setItem(SAFETY_KEY, JSON.stringify(s))
}
