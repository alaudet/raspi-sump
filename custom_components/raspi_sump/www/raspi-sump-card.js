/* raspi-sump-card.js — the raspi-sump water level chart, inside Home Assistant.
 *
 * Ported from raspisump/static/sumpChart.js so the chart looks and behaves like
 * the raspi-sump web UI, with the raspi-sump CSS custom properties swapped for
 * Home Assistant's theme variables.
 *
 * Readings are fetched over the Home Assistant websocket connection
 * (raspi_sump/readings), which proxies to the Pi.  The browser never talks to
 * the Raspberry Pi directly.
 *
 * Card configuration:
 *   type:       custom:raspi-sump-card
 *   title:      optional heading (default "Raspi-Sump")
 *   show_stats: show the stat tiles under the chart (default true)
 *   height:     chart height in pixels (default 320)
 *   entry_id:   only needed when several raspi-sump instances are configured
 *   device_id:  restrict the stat tiles to one device
 */

const CARD_TAG = "raspi-sump-card";
const STATIC_BASE = "/raspi_sump_static";
const WS_TYPE_READINGS = "raspi_sump/readings";
const PLATFORM = "raspi_sump";
const DEFAULT_HEIGHT = 320;

/* Don't re-fetch the whole series more than once a minute, however often the
 * entities update.  The web UI settles for a refresh every 15 minutes. */
const REFRESH_THROTTLE_MS = 60 * 1000;

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

/* Stat tiles, in the order the raspi-sump homepage shows them.  Entities are
 * matched on the suffix that Home Assistant derives from their translation key. */
const STAT_TILES = [
  { suffix: "_level_min_today", label: "Min Level" },
  { suffix: "_level_max_today", label: "Max Level" },
  { suffix: "_readings_today", label: "Readings", note: "today" },
  { suffix: "_water_level", label: "Last Reading" },
  { suffix: "_pit_empties_today", label: "Pit Empties", note: "today — experimental" },
];

/* ── uPlot loading ──────────────────────────────────────────────────────────
 * The vendored build is an IIFE, so it has to be loaded as a classic script to
 * expose the global; importing it as a module would leave window.uPlot unset. */

let uplotPromise = null;

function loadUplot() {
  if (window.uPlot) return Promise.resolve(window.uPlot);
  if (uplotPromise) return uplotPromise;
  uplotPromise = new Promise((resolve, reject) => {
    const script = document.createElement("script");
    script.src = `${STATIC_BASE}/uplot.iife.min.js`;
    script.onload = () => resolve(window.uPlot);
    script.onerror = () => {
      uplotPromise = null;
      reject(new Error("Could not load uPlot"));
    };
    document.head.appendChild(script);
  });
  return uplotPromise;
}

/* ── date helpers ───────────────────────────────────────────────────────── */

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[c]);
}

function isoDate(d) {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

function today() {
  return isoDate(new Date());
}

function shiftDate(date, days) {
  const d = new Date(`${date}T12:00:00`); // midday avoids DST edges
  d.setDate(d.getDate() + days);
  return isoDate(d);
}

/* ── chart helpers ──────────────────────────────────────────────────────── */

// Plain loops rather than Math.max(...arr): a multi-day range can carry tens
// of thousands of points, past the argument limit a spread would hit.
function arrayMin(values) {
  let min = Infinity;
  for (const v of values) if (v < min) min = v;
  return min;
}

function arrayMax(values) {
  let max = -Infinity;
  for (const v of values) if (v > max) max = v;
  return max;
}

// Pin the y-axis so the alert threshold is always in frame, instead of
// leaving it to uPlot's auto-range, which fits only the currently visible
// data and can clip the alert line off the top of the chart. Depth never
// goes negative (raspisump clamps negative readings to 0 before logging),
// so the floor is pinned at 0 rather than auto-fit to the day's minimum.
function computeYRange(depths, criticalLevel) {
  const min = 0;
  let max = Math.max(0, arrayMax(depths));
  if (criticalLevel !== null && criticalLevel !== undefined) {
    max = Math.max(max, criticalLevel);
  }
  // Headroom keeps the peak (or the alert line, if it's the higher of the
  // two) off the very top edge, and guarantees a non-zero span when every
  // reading is identical.
  const span = max - min;
  max += span > 0 ? span * 0.08 : 1;
  return [min, max];
}

/* ── the card ───────────────────────────────────────────────────────────── */

class RaspiSumpCard extends HTMLElement {
  static getStubConfig() {
    return { show_stats: true };
  }

  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._config = {};
    this._hass = null;
    this._date = null;          // null means "today"
    this._chart = null;
    this._resizeObserver = null;
    this._lastFetch = 0;
    this._lastReading = null;
    this._darkMode = null;
    this._payload = null;
    this._built = false;
  }

  setConfig(config) {
    this._config = { title: "Raspi-Sump", show_stats: true, height: DEFAULT_HEIGHT, ...config };
    this._date = null;
    if (this._built) {
      this._renderHeader();
      this._fetch();
    }
  }

  set hass(hass) {
    const first = this._hass === null;
    this._hass = hass;

    if (!this._built) this._build();
    this._renderStats();

    if (first) {
      this._fetch();
      return;
    }

    // Re-draw with new colours when the user flips between light and dark.
    const darkMode = Boolean(hass.themes && hass.themes.darkMode);
    if (this._darkMode !== null && darkMode !== this._darkMode) {
      this._darkMode = darkMode;
      this._draw();
      return;
    }

    // Otherwise refresh only once a new reading has landed.
    const lastReading = this._entityState("_last_reading");
    if (lastReading && lastReading !== this._lastReading) {
      this._lastReading = lastReading;
      if (Date.now() - this._lastFetch > REFRESH_THROTTLE_MS) this._fetch();
    }
  }

  connectedCallback() {
    if (this._built) this._observeResize();
  }

  disconnectedCallback() {
    if (this._resizeObserver) {
      this._resizeObserver.disconnect();
      this._resizeObserver = null;
    }
  }

  getCardSize() {
    return 6;
  }

  getGridOptions() {
    return { rows: 8, columns: 12, min_rows: 4 };
  }

  /* ── entity lookup ────────────────────────────────────────────────────── */

  /* Entities are found by platform rather than by a hard-coded entity_id, so
   * the card keeps working when the device or its entities are renamed. */
  _entityId(suffix) {
    if (!this._hass) return null;

    let candidates = Object.values(this._hass.entities || {})
      .filter((entry) => entry.platform === PLATFORM)
      .filter((entry) => !this._config.device_id || entry.device_id === this._config.device_id)
      .map((entry) => entry.entity_id);

    if (candidates.length === 0) {
      // No entity registry collection, or it doesn't carry the platform:
      // fall back to matching on the entity_id itself.
      candidates = Object.keys(this._hass.states).filter((id) => id.includes(PLATFORM));
    }

    return candidates.find((id) => id.endsWith(suffix)) || null;
  }

  _entityState(suffix) {
    const entityId = this._entityId(suffix);
    if (!entityId) return null;
    const state = this._hass.states[entityId];
    if (!state || state.state === "unknown" || state.state === "unavailable") return null;
    return state.state;
  }

  _entity(suffix) {
    const entityId = this._entityId(suffix);
    return entityId ? this._hass.states[entityId] : null;
  }

  /* ── DOM ──────────────────────────────────────────────────────────────── */

  _build() {
    this.shadowRoot.innerHTML = `
      <link rel="stylesheet" href="${STATIC_BASE}/uplot.min.css">
      <style>
        ha-card { padding: 12px 16px 16px; }
        .header {
          display: flex; align-items: center; justify-content: space-between;
          flex-wrap: wrap; gap: 8px; margin-bottom: 8px;
        }
        .title { font-size: 1.25rem; font-weight: 500; color: var(--primary-text-color); }
        .nav { display: flex; align-items: center; gap: 4px; }
        .nav .date { color: var(--secondary-text-color); font-size: .9rem; min-width: 6.5em; text-align: center; }
        button {
          background: none; border: none; border-radius: 50%;
          color: var(--primary-text-color); cursor: pointer;
          font: inherit; line-height: 1; padding: 6px 8px;
        }
        button:hover:not(:disabled) { background: var(--secondary-background-color); }
        button:disabled { opacity: .38; cursor: default; }
        button.text { border-radius: 16px; font-size: .8rem; padding: 6px 12px; }
        .chart { width: 100%; }
        .message { color: var(--secondary-text-color); padding: 32px 0; text-align: center; }
        /* Column count is set from the number of tiles actually rendered, so
           they always share a single row instead of wrapping into an uneven
           last line when a tile is hidden. */
        .stats { display: grid; gap: 8px; margin-top: 12px; }
        .tile {
          background: var(--secondary-background-color);
          border-radius: 12px; padding: 10px 8px; text-align: center;
          min-width: 0;  /* let grid items shrink below their content width */
        }
        .tile span { display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .tile .label { color: var(--secondary-text-color); font-size: .72rem; }
        .tile .value { color: var(--primary-text-color); font-size: 1.3rem; font-weight: 500; }
        .tile .note { color: var(--secondary-text-color); font-size: .68rem; }
        .u-legend { color: var(--primary-text-color); font-size: .8rem; }
      </style>
      <ha-card>
        <div class="header">
          <div class="title"></div>
          <div class="nav">
            <button class="prev" title="Previous day">&#x2039;</button>
            <span class="date"></span>
            <button class="next" title="Next day">&#x203a;</button>
            <button class="today text">Today</button>
            <button class="download text" title="Download PNG">PNG</button>
          </div>
        </div>
        <div class="chart"></div>
        <div class="stats"></div>
      </ha-card>
    `;

    const root = this.shadowRoot;
    root.querySelector(".prev").addEventListener("click", () => this._step(-1));
    root.querySelector(".next").addEventListener("click", () => this._step(1));
    root.querySelector(".today").addEventListener("click", () => {
      this._date = null;
      this._fetch();
    });
    root.querySelector(".download").addEventListener("click", () => this._download());

    this._built = true;
    this._renderHeader();
    this._observeResize();
  }

  _observeResize() {
    if (this._resizeObserver || !window.ResizeObserver) return;
    const container = this.shadowRoot.querySelector(".chart");
    this._resizeObserver = new ResizeObserver(() => {
      const width = container.clientWidth;
      if (width > 0 && this._chart) {
        this._chart.setSize({ width, height: this._config.height });
      }
    });
    this._resizeObserver.observe(container);
  }

  _renderHeader() {
    const root = this.shadowRoot;
    root.querySelector(".title").textContent = this._config.title;
    const date = this._date || today();
    root.querySelector(".date").textContent = this._date ? date : "Today";
    root.querySelector(".next").disabled = !this._date;
    root.querySelector(".today").disabled = !this._date;
  }

  _renderStats() {
    const stats = this.shadowRoot.querySelector(".stats");
    if (!stats) return;
    if (!this._config.show_stats) {
      stats.innerHTML = "";
      return;
    }

    const tiles = STAT_TILES.map((tile) => {
      const state = this._entity(tile.suffix);
      // Drop tiles with nothing to show rather than rendering a placeholder.
      // Turning a feature off on the Pi (cycle_detection, behind the pit
      // empties count) leaves its entity in Home Assistant's registry with no
      // value, and an empty tile reads as a reading that hasn't arrived yet
      // rather than a feature that is switched off.
      if (!state || state.state === "unknown" || state.state === "unavailable") return "";
      const value = state.state;
      const unit = state.attributes.unit_of_measurement || "";
      const note = unit && tile.note ? `${unit} — ${tile.note}` : tile.note || unit;
      return `
        <div class="tile">
          <span class="label">${escapeHtml(tile.label)}</span>
          <span class="value">${escapeHtml(value)}</span>
          <span class="note">${escapeHtml(note)}</span>
        </div>`;
    }).filter(Boolean);

    // One column per visible tile keeps them on a single row whatever the
    // card's width; minmax(0, ...) lets them shrink rather than overflow.
    stats.style.gridTemplateColumns = `repeat(${tiles.length || 1}, minmax(0, 1fr))`;
    stats.innerHTML = tiles.join("");
  }

  _message(text) {
    this.shadowRoot.querySelector(".chart").innerHTML =
      `<p class="message">${escapeHtml(text)}</p>`;
    if (this._chart) {
      this._chart.destroy();
      this._chart = null;
    }
  }

  /* ── data ─────────────────────────────────────────────────────────────── */

  _step(days) {
    this._date = shiftDate(this._date || today(), days);
    if (this._date >= today()) this._date = null;
    this._fetch();
  }

  async _fetch() {
    if (!this._hass) return;
    this._lastFetch = Date.now();
    this._renderHeader();

    const message = { type: WS_TYPE_READINGS };
    if (this._config.entry_id) message.entry_id = this._config.entry_id;
    if (this._date) message.date = this._date;

    try {
      this._payload = await this._hass.connection.sendMessagePromise(message);
    } catch (err) {
      this._payload = null;
      this._message(`Could not load chart data: ${err.message || err.code || err}`);
      return;
    }
    this._draw();
  }

  async _draw() {
    const payload = this._payload;
    if (!payload) return;

    const [timestamps, depths] = payload.data || [[], []];
    if (!timestamps || timestamps.length === 0) {
      this._message("No data for this period.");
      return;
    }

    let uPlot;
    try {
      uPlot = await loadUplot();
    } catch (err) {
      this._message(err.message);
      return;
    }

    const container = this.shadowRoot.querySelector(".chart");
    const colors = this._colors();
    const criticalLevel = payload.critical_level;

    let data;
    let series;
    if (criticalLevel !== null && criticalLevel !== undefined) {
      data = [timestamps, depths, timestamps.map(() => criticalLevel)];
      series = [
        {},
        { label: "Water Level", stroke: colors.line, width: 2, fill: colors.fill },
        { label: "Alert Level", stroke: colors.alert, width: 3, dash: [6, 3] },
      ];
    } else {
      data = [timestamps, depths];
      series = [
        {},
        { label: "Water Level", stroke: colors.line, width: 2, fill: colors.fill },
      ];
    }

    // X axis: date+time once the span exceeds a day, time-only otherwise.
    const span = timestamps[timestamps.length - 1] - timestamps[0];
    const multiDay = span > 86400;
    const values = multiDay
      ? (u, vals) => vals.map((v) => {
          if (v === null) return "";
          const d = new Date(v * 1000);
          return `${MONTHS[d.getMonth()]} ${String(d.getDate()).padStart(2, "0")} ` +
                 `${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
        })
      : (u, vals) => vals.map((v) => {
          if (v === null) return "";
          const d = new Date(v * 1000);
          return `${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
        });

    const opts = {
      width: container.clientWidth || 600,
      height: this._config.height,
      series,
      scales: {
        y: { range: computeYRange(depths, criticalLevel) },
      },
      axes: [
        {
          stroke: colors.text,
          ticks: { stroke: colors.border },
          grid: { stroke: colors.border },
          values,
          // Minimum px between ticks; wider labels need more room so uPlot
          // drops ticks instead of overlapping them.
          space: multiDay ? 110 : 55,
        },
        {
          stroke: colors.text,
          ticks: { stroke: colors.border },
          grid: { stroke: colors.border },
          label: payload.unit || "",
        },
      ],
      cursor: { points: { size: 6 } },
      hooks: {
        // Paint the card background behind the plot so a downloaded PNG isn't
        // transparent.
        draw: [(u) => {
          u.ctx.save();
          u.ctx.globalCompositeOperation = "destination-over";
          u.ctx.fillStyle = colors.surface;
          u.ctx.fillRect(0, 0, u.width, u.height);
          u.ctx.restore();
        }],
      },
    };

    if (this._chart) this._chart.destroy();
    container.innerHTML = "";
    this._chart = new uPlot(opts, data, container);
    this._darkMode = Boolean(this._hass.themes && this._hass.themes.darkMode);
  }

  _download() {
    if (!this._chart) return;
    const link = document.createElement("a");
    link.download = `waterlevel-${this._date || today()}.png`;
    link.href = this._chart.ctx.canvas.toDataURL("image/png");
    link.click();
  }

  /* uPlot paints on a canvas, which needs concrete colours rather than CSS
   * variables, so the theme values are resolved here. */
  _colors() {
    const style = getComputedStyle(this.shadowRoot.querySelector("ha-card"));
    const resolve = (name, fallback) => style.getPropertyValue(name).trim() || fallback;
    const line = resolve("--primary-color", "#03a9f4");
    return {
      text: resolve("--primary-text-color", "#212121"),
      border: resolve("--divider-color", "#e0e0e0"),
      surface: resolve("--ha-card-background", resolve("--card-background-color", "#ffffff")),
      alert: resolve("--error-color", "#c62828"),
      line,
      fill: this._translucent(line, 0.25),
    };
  }

  /* Turn any CSS colour into rgba() by letting the browser normalise it.
   *
   * The separator has to be permissive: getComputedStyle().color returns the
   * legacy "rgb(3, 169, 244)" in some browsers and the modern space-separated
   * "rgb(3 169 244)" in others.  Matching only commas would fall through and
   * hand uPlot an opaque colour, painting a solid block under the curve
   * instead of a light wash. */
  _translucent(color, alpha) {
    const probe = document.createElement("span");
    probe.style.color = color;
    probe.style.display = "none";
    this.shadowRoot.appendChild(probe);
    const resolved = getComputedStyle(probe).color;
    probe.remove();
    const match = resolved.match(/(\d+)[,\s]+(\d+)[,\s]+(\d+)/);
    // Never return an opaque colour from here — a fill is only ever meant to
    // be a wash, so an unparseable colour degrades to a neutral translucent
    // grey rather than a solid area that hides the plot behind it.
    if (!match) return `rgba(128, 128, 128, ${alpha})`;
    return `rgba(${match[1]}, ${match[2]}, ${match[3]}, ${alpha})`;
  }
}

/* The integration registers this file itself, so a leftover manual Lovelace
 * resource pointing at the same path would load it twice; re-defining the
 * element throws and takes the whole dashboard down with it. */
if (customElements.get(CARD_TAG)) {
  console.warn(`${CARD_TAG} is already registered; skipping duplicate registration.`);
} else {
  customElements.define(CARD_TAG, RaspiSumpCard);

  window.customCards = window.customCards || [];
  window.customCards.push({
    type: CARD_TAG,
    name: "Raspi-Sump",
    description: "Sump pit water level chart and statistics.",
    preview: true,
    documentationURL: "https://raspisumpdocs.linuxnorth.org/home-assistant/",
  });
}
