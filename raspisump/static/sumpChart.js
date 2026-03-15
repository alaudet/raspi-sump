/* sumpChart.js — uPlot chart helper for raspi-sump
 * initChart(containerId, date)
 *   containerId : id of the <div> to render into
 *   date        : "YYYY-MM-DD" string, or null for today
 * Returns the uPlot instance (or null on error / no data).
 */

var chart = null;         // module-level — Download PNG buttons reference this
var _containerId = null;  // stored for theme-change re-init
var _date = null;

function initChart(containerId, date) {
    _containerId = containerId;
    _date = date !== undefined ? date : null;
    var container = document.getElementById(containerId);
    if (!container) return null;

    var url = '/api/readings';
    if (date) url += '?date=' + encodeURIComponent(date);

    fetch(url)
        .then(function(resp) {
            if (!resp.ok) throw new Error('HTTP ' + resp.status);
            return resp.json();
        })
        .then(function(json) {
            _renderChart(container, json, date);
        })
        .catch(function(err) {
            container.innerHTML =
                '<p class="chart-missing">Could not load chart data: ' + err.message + '</p>';
        });

    return null;  // chart assigned asynchronously; Download PNG uses module var
}

function _renderChart(container, json, date) {
    var timestamps = json.data[0];
    var depths     = json.data[1];

    if (!timestamps || timestamps.length === 0) {
        container.innerHTML = '<p class="chart-missing">No data for this date.</p>';
        return;
    }

    // Read colors from CSS custom properties
    var s           = getComputedStyle(document.documentElement);
    var textColor   = s.getPropertyValue('--text').trim()         || '#222';
    var borderColor = s.getPropertyValue('--border').trim()       || '#ddd';
    var lineColor   = s.getPropertyValue('--chart-line').trim()   || '#000fff';
    var fillColor   = s.getPropertyValue('--chart-fill').trim()   || 'rgba(92,92,251,0.25)';
    var alertColor  = s.getPropertyValue('--chart-alert').trim()  || '#c62828';
    var surfaceColor = s.getPropertyValue('--surface').trim()     || '#ffffff';

    var criticalLevel = json.critical_level;
    var yLabel = json.unit || '';

    // Build parallel data arrays; add alert series if available
    var uplotData;
    var series;

    if (criticalLevel !== null && criticalLevel !== undefined) {
        var alertSeries = timestamps.map(function() { return criticalLevel; });
        uplotData = [timestamps, depths, alertSeries];
        series = [
            {},
            { label: 'Water Level', stroke: lineColor,  width: 2, fill: fillColor },
            { label: 'Alert Level', stroke: alertColor, width: 2, dash: [6, 3] },
        ];
    } else {
        uplotData = [timestamps, depths];
        series = [
            {},
            { label: 'Water Level', stroke: lineColor, width: 2, fill: fillColor },
        ];
    }

    var opts = {
        width:  container.clientWidth || 600,
        height: 320,
        series: series,
        axes: [
            {
                stroke: textColor,
                ticks:  { stroke: borderColor },
                grid:   { stroke: borderColor },
                values: function(u, vals) {
                    return vals.map(function(v) {
                        if (v === null) return '';
                        var d = new Date(v * 1000);
                        var hh = String(d.getHours()).padStart(2, '0');
                        var mm = String(d.getMinutes()).padStart(2, '0');
                        return hh + ':' + mm;
                    });
                },
            },
            {
                stroke: textColor,
                ticks:  { stroke: borderColor },
                grid:   { stroke: borderColor },
                label:  yLabel,
            },
        ],
        cursor: {
            points: { size: 6 },
        },
        hooks: {
            draw: [function(u) {
                // Fill canvas background so right-click "Save image" looks right
                u.ctx.save();
                u.ctx.globalCompositeOperation = 'destination-over';
                u.ctx.fillStyle = surfaceColor;
                u.ctx.fillRect(0, 0, u.width, u.height);
                u.ctx.restore();
            }],
        },
    };

    // Clear any previous chart
    container.innerHTML = '';
    chart = new uPlot(opts, uplotData, container);

    // Responsive resize
    var ro = new ResizeObserver(function() {
        var w = container.clientWidth;
        if (w > 0 && chart) chart.setSize({ width: w, height: 320 });
    });
    ro.observe(container);
}

// Re-render chart with new theme colors when user toggles dark mode
document.addEventListener('themechange', function() {
    if (_containerId) initChart(_containerId, _date);
});

function downloadChart(chartInstance, filename) {
    if (!chartInstance) {
        // Try module-level fallback
        chartInstance = chart;
    }
    if (!chartInstance) return;
    var a = document.createElement('a');
    a.download = filename || 'waterlevel.png';
    a.href = chartInstance.ctx.canvas.toDataURL('image/png');
    a.click();
}
