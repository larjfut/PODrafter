// Client-only Evidence Locker stored in IndexedDB with passphrase-based encryption.
// Important: This is a convenience feature for the survivor on their device only.
// Data is NOT uploaded. If the device is seized or compromised, data may be discovered.

type Entry = { id: string; createdAt: number; date?: string; title: string; details: string }

const DB_NAME = 'podrafter-locker'
const STORE = 'entries'
let cryptoKey: CryptoKey | null = null

async function deriveKey(passphrase: string, salt: Uint8Array): Promise<CryptoKey> {
  const enc = new TextEncoder()
  const keyMaterial = await crypto.subtle.importKey('raw', enc.encode(passphrase), 'PBKDF2', false, ['deriveKey'])
  return crypto.subtle.deriveKey(
    { name: 'PBKDF2', salt, iterations: 150_000, hash: 'SHA-256' },
    keyMaterial,
    { name: 'AES-GCM', length: 256 },
    false,
    ['encrypt', 'decrypt']
  )
}

export async function setPassphrase(passphrase: string) {
  const salt = new Uint8Array([80,79,68,114,97,102,116,101,114,45,108,111,99,107,101,114]) // PODrafter-locker
  cryptoKey = await deriveKey(passphrase, salt)
}

function openDb(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, 1)
    req.onupgradeneeded = () => {
      const db = req.result
      if (!db.objectStoreNames.contains(STORE)) db.createObjectStore(STORE, { keyPath: 'id' })
    }
    req.onsuccess = () => resolve(req.result)
    req.onerror = () => reject(req.error)
  })
}

async function encrypt(obj: any): Promise<{ iv: Uint8Array; data: ArrayBuffer }> {
  if (!cryptoKey) throw new Error('No passphrase set')
  const iv = crypto.getRandomValues(new Uint8Array(12))
  const enc = new TextEncoder()
  const bytes = enc.encode(JSON.stringify(obj))
  const data = await crypto.subtle.encrypt({ name: 'AES-GCM', iv }, cryptoKey, bytes)
  return { iv, data }
}

async function decrypt(iv: Uint8Array, data: ArrayBuffer): Promise<any> {
  if (!cryptoKey) throw new Error('No passphrase set')
  const plain = await crypto.subtle.decrypt({ name: 'AES-GCM', iv }, cryptoKey, data)
  const dec = new TextDecoder()
  return JSON.parse(dec.decode(new Uint8Array(plain)))
}

export async function addEntry(input: Omit<Entry, 'id' | 'createdAt'>): Promise<void> {
  const db = await openDb()
  const tx = db.transaction(STORE, 'readwrite')
  const store = tx.objectStore(STORE)
  const entry = { ...input, id: crypto.randomUUID(), createdAt: Date.now() }
  const { iv, data } = await encrypt(entry)
  await new Promise((resolve, reject) => {
    const req = store.put({ id: entry.id, iv: Array.from(iv), blob: data })
    req.onsuccess = () => resolve(null)
    req.onerror = () => reject(req.error)
  })
  db.close()
}

export async function listEntries(): Promise<Entry[]> {
  const db = await openDb()
  const tx = db.transaction(STORE, 'readonly')
  const store = tx.objectStore(STORE)
  const all: any[] = await new Promise((resolve, reject) => {
    const req = store.getAll()
    req.onsuccess = () => resolve(req.result)
    req.onerror = () => reject(req.error)
  })
  db.close()
  const out: Entry[] = []
  for (const row of all) {
    try {
      const iv = new Uint8Array(row.iv)
      const dec = await decrypt(iv, row.blob)
      out.push(dec as Entry)
    } catch {
      // skip rows that fail to decrypt with current passphrase
    }
  }
  return out.sort((a, b) => b.createdAt - a.createdAt)
}

export async function clearAll(): Promise<void> {
  const db = await openDb()
  const tx = db.transaction(STORE, 'readwrite')
  tx.objectStore(STORE).clear()
  db.close()
}

export type { Entry }
