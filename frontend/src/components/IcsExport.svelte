<script lang="ts">
  export let title = 'Protective Order Hearing'
  let date = ''
  let time = ''
  let location = ''
  let notes = ''

  function pad(n: number) { return String(n).padStart(2, '0') }
  function toUtc(dt: Date) {
    return (
      dt.getUTCFullYear() +
      pad(dt.getUTCMonth() + 1) +
      pad(dt.getUTCDate()) + 'T' +
      pad(dt.getUTCHours()) +
      pad(dt.getUTCMinutes()) +
      '00Z'
    )
  }

  function downloadIcs() {
    if (!date) return
    const local = new Date(`${date}T${time || '09:00'}`)
    const start = toUtc(local)
    const endDate = new Date(local.getTime() + 60 * 60 * 1000)
    const end = toUtc(endDate)
    const uid = crypto.randomUUID()
    const lines = [
      'BEGIN:VCALENDAR',
      'VERSION:2.0',
      'PRODID:-//PO Drafter//TX//EN',
      'BEGIN:VEVENT',
      `UID:${uid}`,
      `DTSTAMP:${toUtc(new Date())}`,
      `DTSTART:${start}`,
      `DTEND:${end}`,
      `SUMMARY:${title}`,
      location ? `LOCATION:${location.replace(/\n/g, ' ')}` : '',
      notes ? `DESCRIPTION:${notes.replace(/\n/g, ' ')}` : '',
      'END:VEVENT',
      'END:VCALENDAR',
    ].filter(Boolean)
    const blob = new Blob([lines.join('\r\n')], { type: 'text/calendar' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'hearing.ics'
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
  }
</script>

<div class="space-y-2">
  <label class="text-sm font-medium text-[color:var(--muted-ink)]">Court date</label>
  <div class="grid sm:grid-cols-2 gap-2">
    <input type="date" bind:value={date} class="h-11 px-3 rounded-control bg-white/70 border border-slate-300/60 shadow-e1 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400 focus-visible:ring-offset-1" />
    <input type="time" bind:value={time} class="h-11 px-3 rounded-control bg-white/70 border border-slate-300/60 shadow-e1 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400 focus-visible:ring-offset-1" />
  </div>
  <label class="text-sm font-medium text-[color:var(--muted-ink)] mt-2">Location (optional)</label>
  <input bind:value={location} placeholder="Courthouse address" class="h-11 px-3 rounded-control bg-white/70 border border-slate-300/60 shadow-e1 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400 focus-visible:ring-offset-1" />
  <label class="text-sm font-medium text-[color:var(--muted-ink)] mt-2">Notes (optional)</label>
  <textarea bind:value={notes} rows="3" class="px-3 py-2 rounded-control bg-white/70 border border-slate-300/60 shadow-e1 focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400 focus-visible:ring-offset-1" />
  <div>
    <button class="mt-2 bg-[color:var(--mint-deep)] text-white h-11 px-4 rounded-control active:translate-y-[1px]" on:click|preventDefault={downloadIcs}>Download .ics</button>
  </div>
  <p class="text-xs muted">This saves a calendar reminder file to your device. It is not shared.</p>
  </div>
