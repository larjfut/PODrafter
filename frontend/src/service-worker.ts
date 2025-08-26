/// <reference lib="webworker" />

const CACHE = 'podrafter-cache-v1'
const QUEUE = 'api-queue'
const OFFLINE_URL = '/offline'

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE).then(cache => cache.addAll(['/', OFFLINE_URL]))
  )
  self.skipWaiting()
})

self.addEventListener('activate', event => {
  event.waitUntil(self.clients.claim())
})

self.addEventListener('fetch', event => {
  const request = event.request

  if (request.method !== 'GET') {
    event.respondWith(handleNonGet(request))
    return
  }

  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request).catch(() => caches.match(OFFLINE_URL))
    )
    return
  }

  event.respondWith(fetchAndCache(request))
})

self.addEventListener('sync', event => {
  if (event.tag === QUEUE) {
    event.waitUntil(sendQueued())
  }
})

async function fetchAndCache(request: Request) {
  try {
    const response = await fetch(request)
    const cache = await caches.open(CACHE)
    cache.put(request, response.clone())
    return response
  } catch {
    const cached = await caches.match(request)
    if (cached) return cached
    if (request.mode === 'navigate') return caches.match(OFFLINE_URL)
    throw new Error('Network error')
  }
}

async function handleNonGet(request: Request) {
  try {
    return await fetch(request.clone())
  } catch {
    const body = await request.clone().json().catch(() => null)
    await saveRequest({ url: request.url, method: request.method, body })
    await self.registration.sync.register(QUEUE)
    return new Response(JSON.stringify({ queued: true }), {
      headers: { 'Content-Type': 'application/json' }
    })
  }
}

interface QueuedRequest {
  url: string
  method: string
  body: any
}

function openDB() {
  return new Promise<IDBDatabase>((resolve, reject) => {
    const request = indexedDB.open('bg-sync', 1)
    request.onupgradeneeded = () => {
      request.result.createObjectStore(QUEUE, { autoIncrement: true })
    }
    request.onsuccess = () => resolve(request.result)
    request.onerror = () => reject(request.error)
  })
}

async function saveRequest(data: QueuedRequest) {
  const db = await openDB()
  const tx = db.transaction(QUEUE, 'readwrite')
  tx.objectStore(QUEUE).add(data)
  return new Promise<void>((resolve, reject) => {
    tx.oncomplete = () => resolve()
    tx.onerror = () => reject(tx.error)
  })
}

async function sendQueued() {
  const db = await openDB()
  const tx = db.transaction(QUEUE, 'readwrite')
  const store = tx.objectStore(QUEUE)
  const all = store.getAll()
  const keys = store.getAllKeys()
  await new Promise((resolve, reject) => {
    all.onsuccess = resolve
    all.onerror = reject
  })
  await new Promise((resolve, reject) => {
    keys.onsuccess = resolve
    keys.onerror = reject
  })
  const requests = all.result.map((data, i) => ({ key: keys.result[i], data }))
  for (const { key, data } of requests) {
    await fetch(data.url, {
      method: data.method,
      headers: { 'Content-Type': 'application/json' },
      body: data.body ? JSON.stringify(data.body) : undefined
    })
    store.delete(key)
  }
  return new Promise<void>((resolve, reject) => {
    tx.oncomplete = () => resolve()
    tx.onerror = () => reject(tx.error)
  })
}

