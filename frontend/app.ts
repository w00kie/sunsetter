import maplibregl, { type LngLat, LngLatBounds, type Marker } from "maplibre-gl"

type Point = { lat: number; lng: number }
type MatchResult = { suntype: "Sunrise" | "Sunset"; matches: string[]; labels: string[] }

const map = new maplibregl.Map({
  container: "map",
  style: "https://tiles.openfreemap.org/styles/liberty",
  center: [139.6917, 35.6895],
  zoom: 9,
  attributionControl: false,
})

map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "bottom-right")
map.addControl(new maplibregl.AttributionControl({ compact: true }), "bottom-right")

const state: { pov?: Point; poi?: Point; markers: Marker[] } = { markers: [] }
const status = document.querySelector<HTMLElement>("#status")!
const eyebrow = document.querySelector<HTMLElement>("#eyebrow")!
const result = document.querySelector<HTMLElement>("#result")!
const resetButton = document.querySelector<HTMLButtonElement>("#reset")!
const locateButton = document.querySelector<HTMLButtonElement>("#locate")!
const shareButton = document.querySelector<HTMLButtonElement>("#share")!
const help = document.querySelector<HTMLDialogElement>("#help")!
const helpOpen = document.querySelector<HTMLButtonElement>("#help-open")!
const helpClose = document.querySelector<HTMLButtonElement>("#help-close")!

const toPoint = (position: LngLat): Point => ({ lat: position.lat, lng: position.lng })

function bearing(from: Point, to: Point): number {
  const φ1 = (from.lat * Math.PI) / 180
  const φ2 = (to.lat * Math.PI) / 180
  const Δλ = ((to.lng - from.lng) * Math.PI) / 180
  const y = Math.sin(Δλ) * Math.cos(φ2)
  const x = Math.cos(φ1) * Math.sin(φ2) - Math.sin(φ1) * Math.cos(φ2) * Math.cos(Δλ)
  return ((Math.atan2(y, x) * 180) / Math.PI + 360) % 360
}

function markerElement(kind: "pov" | "poi"): HTMLButtonElement {
  const element = document.createElement("button")
  element.className = `marker marker--${kind}`
  element.type = "button"
  element.setAttribute("aria-label", kind === "pov" ? "Point of view" : "Sun direction")
  element.innerHTML = kind === "pov" ? "<span>YOU</span>" : '<span aria-hidden="true">☀</span>'
  return element
}

function addMarker(kind: "pov" | "poi", point: Point): void {
  const marker = new maplibregl.Marker({ element: markerElement(kind), draggable: true, anchor: "bottom-left" })
    .setLngLat([point.lng, point.lat])
    .addTo(map)

  marker.on("drag", () => {
    state[kind] = toPoint(marker.getLngLat())
    drawLine()
    showPendingResult()
  })
  marker.on("dragend", calculate)
  state.markers.push(marker)
}

function drawLine(): void {
  const source = map.getSource("sightline") as maplibregl.GeoJSONSource | undefined
  const coordinates =
    state.pov && state.poi
      ? [
          [state.pov.lng, state.pov.lat],
          [state.poi.lng, state.poi.lat],
        ]
      : []
  source?.setData({ type: "Feature", properties: {}, geometry: { type: "LineString", coordinates } })
}

function updateInstructions(): void {
  const step = state.poi ? 3 : state.pov ? 2 : 1
  document.body.dataset.step = String(step)
  eyebrow.textContent = `Step ${step} of 3`
  status.textContent =
    step === 1 ? "Choose where you’ll stand" : step === 2 ? "Choose where you’ll look" : "Drag either marker to refine"
  resetButton.hidden = step === 1
  shareButton.hidden = step !== 3
}

function showPendingResult(): void {
  if (!state.pov || !state.poi) return
  result.className = "result result--pending"
  result.innerHTML = `<span>${bearing(state.pov, state.poi).toFixed(1)}° azimuth</span><strong>Release to recalculate</strong>`
}

async function calculate(): Promise<void> {
  if (!state.pov || !state.poi) return
  const azimuth = bearing(state.pov, state.poi)
  result.className = "result result--loading"
  result.innerHTML = `<span>${azimuth.toFixed(1)}° azimuth</span><strong>Reading the year…</strong>`

  try {
    const response = await fetch("/api/matches", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ lat: state.pov.lat, az: azimuth }),
    })
    const data = (await response.json()) as MatchResult & { error?: string }
    if (!response.ok) throw new Error(data.error || "Calculation failed")

    result.className = `result result--ready result--${data.suntype.toLowerCase()}`
    result.innerHTML = data.matches.length
      ? `<span>${data.suntype} · ${azimuth.toFixed(1)}°</span><strong>${data.labels.join(" & ")}</strong><small>The sun aligns with your sightline on these dates.</small>`
      : `<span>${data.suntype} · ${azimuth.toFixed(1)}°</span><strong>No alignment here</strong><small>Try dragging the sun marker closer to east or west.</small>`
    setHash()
  } catch (error) {
    result.className = "result result--error"
    result.innerHTML = `<strong>Couldn’t calculate</strong><small>${error instanceof Error ? error.message : "Try again."}</small>`
  }
}

function selectPoint(point: Point): void {
  if (!state.pov) {
    state.pov = point
    addMarker("pov", point)
  } else if (!state.poi) {
    state.poi = point
    addMarker("poi", point)
    drawLine()
    calculate()
  }
  updateInstructions()
}

function reset(): void {
  state.markers.forEach((marker) => {
    marker.remove()
  })
  state.markers = []
  delete state.pov
  delete state.poi
  drawLine()
  result.className = "result"
  result.innerHTML = "<span>Sun alignment</span><strong>Two points reveal the dates</strong>"
  history.replaceState(null, "", `${location.pathname}${location.search}`)
  updateInstructions()
}

function setHash(): void {
  if (!state.pov || !state.poi) return
  const compact = (point: Point) => `${point.lat.toFixed(6)},${point.lng.toFixed(6)}`
  history.replaceState(null, "", `#pov=${compact(state.pov)}&poi=${compact(state.poi)}`)
}

function readHash(): [Point, Point] | undefined {
  const params = new URLSearchParams(location.hash.slice(1))
  const parse = (value: string | null): Point | undefined => {
    const [lat, lng] = (value || "").split(",").map(Number)
    return Number.isFinite(lat) && Number.isFinite(lng) ? { lat, lng } : undefined
  }
  const pov = parse(params.get("pov"))
  const poi = parse(params.get("poi"))
  return pov && poi ? [pov, poi] : undefined
}

map.on("load", () => {
  map.addSource("sightline", {
    type: "geojson",
    data: { type: "Feature", properties: {}, geometry: { type: "LineString", coordinates: [] } },
  })
  map.addLayer({
    id: "sightline-glow",
    type: "line",
    source: "sightline",
    paint: { "line-color": "#ffb15c", "line-width": 10, "line-opacity": 0.22, "line-blur": 4 },
  })
  map.addLayer({
    id: "sightline",
    type: "line",
    source: "sightline",
    paint: { "line-color": "#f47b3d", "line-width": 3, "line-opacity": 0.95 },
  })

  const saved = readHash()
  if (saved) {
    selectPoint(saved[0])
    selectPoint(saved[1])
    const padding =
      window.innerWidth <= 720
        ? { top: 60, right: 40, bottom: 400, left: 40 }
        : { top: 80, right: 450, bottom: 80, left: 80 }
    map.fitBounds(new LngLatBounds().extend([saved[0].lng, saved[0].lat]).extend([saved[1].lng, saved[1].lat]), {
      padding,
      maxZoom: 13,
    })
  }
})

map.on("click", (event) => selectPoint(toPoint(event.lngLat)))
resetButton.addEventListener("click", reset)
locateButton.addEventListener("click", () =>
  navigator.geolocation?.getCurrentPosition(
    ({ coords }) => map.flyTo({ center: [coords.longitude, coords.latitude], zoom: 12, essential: true }),
    () => {
      status.textContent = "Location access wasn’t available"
    },
    { enableHighAccuracy: true, timeout: 8000 },
  ),
)
shareButton.addEventListener("click", async () => {
  await navigator.clipboard.writeText(location.href)
  shareButton.textContent = "Link copied"
  window.setTimeout(() => {
    shareButton.textContent = "Share view"
  }, 1800)
})
helpOpen.addEventListener("click", () => help.showModal())
helpClose.addEventListener("click", () => help.close())
help.addEventListener("click", (event) => {
  if (event.target === help) help.close()
})

updateInstructions()
