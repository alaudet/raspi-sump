/* sumpChart.js — uPlot chart helper for raspi-sump
 *
 * initChart(containerId, date)
 *   Single-day chart. date = "YYYY-MM-DD" or null for today.
 *
 * initRangeChart(containerId, start, end)
 *   Arbitrary time-range chart. start/end = "YYYY-MM-DDTHH:MM".
 *
 * downloadChart(containerId, filename)
 *   Save the chart in containerId as a PNG.
 *
 * Charts are stored in the module-level `charts` dict so multi-chart
 * pages (last-N-days view) each have their own downloadable instance.
 */

var charts   = {};    // containerId → uPlot instance
var _registry = {};  // containerId → { type, date?, start?, end? }

/* ── single-day chart ──────────────────────────────────────────────── */

function initChart(containerId, date) {
    _registry[containerId] = { type: 'day', date: date };
    var container = document.getElementById(containerId);
    if (!container) return;
    var url = '/api/readings';
    if (date) url += '?date=' + encodeURIComponent(date);
    _fetchAndRender(url, containerId, false);
}

/* ── arbitrary time-range chart ─────────────────────────────────────── */

function initRangeChart(containerId, start, end) {
    _registry[containerId] = { type: 'range', start: start, end: end };
    var container = document.getElementById(containerId);
    if (!container) return;
    var url = '/api/readings/range?start=' + encodeURIComponent(start) +
              '&end=' + encodeURIComponent(end);
    _fetchAndRender(url, containerId, true);
}

/* ── shared fetch + render ─────────────────────────────────────────── */

function _fetchAndRender(url, containerId, multiDay) {
    var container = document.getElementById(containerId);
    fetch(url)
        .then(function(resp) {
            if (!resp.ok) throw new Error('HTTP ' + resp.status);
            return resp.json();
        })
        .then(function(json) {
            _renderChart(container, json, containerId, multiDay);
        })
        .catch(function(err) {
            container.innerHTML =
                '<p class="chart-missing">Could not load chart data: ' + err.message + '</p>';
        });
}

function _renderChart(container, json, containerId, multiDay) {
    var timestamps = json.data[0];
    var depths     = json.data[1];

    if (!timestamps || timestamps.length === 0) {
        container.innerHTML = '<p class="chart-missing">No data for this period.</p>';
        return;
    }

    var s            = getComputedStyle(document.documentElement);
    var textColor    = s.getPropertyValue('--text').trim()        || '#222';
    var borderColor  = s.getPropertyValue('--border').trim()      || '#ddd';
    var lineColor    = s.getPropertyValue('--chart-line').trim()  || '#000fff';
    var fillColor    = s.getPropertyValue('--chart-fill').trim()  || 'rgba(92,92,251,0.25)';
    var alertColor   = s.getPropertyValue('--chart-alert').trim() || '#c62828';
    var surfaceColor = s.getPropertyValue('--surface').trim()     || '#ffffff';

    var criticalLevel = json.critical_level;
    var yLabel = json.unit || '';

    var uplotData, series;
    if (criticalLevel !== null && criticalLevel !== undefined) {
        var alertSeries = timestamps.map(function() { return criticalLevel; });
        uplotData = [timestamps, depths, alertSeries];
        series = [
            {},
            { label: 'Water Level', stroke: lineColor,  width: 2, fill: fillColor },
            { label: 'Alert Level', stroke: alertColor, width: 3, dash: [6, 3] },
        ];
    } else {
        uplotData = [timestamps, depths];
        series = [
            {},
            { label: 'Water Level', stroke: lineColor, width: 2, fill: fillColor },
        ];
    }

    // X axis: date+time for multi-day ranges, time-only for single day
    var xSpan = timestamps[timestamps.length - 1] - timestamps[0];
    var _MONTHS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    var xValues = (multiDay || xSpan > 86400)
        ? function(u, vals) {
            return vals.map(function(v) {
                if (v === null) return '';
                var d = new Date(v * 1000);
                return _MONTHS[d.getMonth()] + ' ' + String(d.getDate()).padStart(2, '0') +
                       ' ' + String(d.getHours()).padStart(2, '0') + ':' +
                       String(d.getMinutes()).padStart(2, '0');
            });
          }
        : function(u, vals) {
            return vals.map(function(v) {
                if (v === null) return '';
                var d = new Date(v * 1000);
                return String(d.getHours()).padStart(2, '0') + ':' +
                       String(d.getMinutes()).padStart(2, '0');
            });
          };

    var height = parseInt(container.dataset.chartHeight) || 320;

    var opts = {
        width:  container.clientWidth || 600,
        height: height,
        series: series,
        axes: [
            {
                stroke: textColor,
                ticks:  { stroke: borderColor },
                grid:   { stroke: borderColor },
                values: xValues,
            },
            {
                stroke: textColor,
                ticks:  { stroke: borderColor },
                grid:   { stroke: borderColor },
                label:  yLabel,
            },
        ],
        cursor: { points: { size: 6 } },
        hooks: {
            draw: [function(u) {
                u.ctx.save();
                u.ctx.globalCompositeOperation = 'destination-over';
                u.ctx.fillStyle = surfaceColor;
                u.ctx.fillRect(0, 0, u.width, u.height);
                u.ctx.restore();
            }],
        },
    };

    container.innerHTML = '';
    var uplot = new uPlot(opts, uplotData, container);
    charts[containerId] = uplot;

    var ro = new ResizeObserver(function() {
        var w = container.clientWidth;
        if (w > 0 && charts[containerId]) {
            charts[containerId].setSize({ width: w, height: height });
        }
    });
    ro.observe(container);
}

/* ── download ────────────────────────────────────────────────────────── */

function downloadChart(containerId, filename) {
    var c = charts[containerId];
    if (!c) return;
    var a = document.createElement('a');
    a.download = filename || 'waterlevel.png';
    a.href = c.ctx.canvas.toDataURL('image/png');
    a.click();
}

/* ── theme change ────────────────────────────────────────────────────── */

document.addEventListener('themechange', function() {
    Object.keys(_registry).forEach(function(id) {
        var reg = _registry[id];
        if (reg.type === 'day')   initChart(id, reg.date);
        if (reg.type === 'range') initRangeChart(id, reg.start, reg.end);
    });
});
