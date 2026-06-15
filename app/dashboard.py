from __future__ import annotations

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Day 13 Observability Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Segoe UI', sans-serif; background: #0f1117; color: #e0e0e0; }
  header { background: #1a1d2e; padding: 16px 24px; border-bottom: 1px solid #2d3048; display: flex; align-items: center; gap: 12px; }
  header h1 { font-size: 1.2rem; font-weight: 600; color: #7c9eff; }
  #refresh-badge { margin-left: auto; font-size: 0.75rem; color: #888; }
  #refresh-badge span { color: #4ade80; }
  .grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; padding: 20px; }
  .card { background: #1a1d2e; border-radius: 10px; padding: 16px; border: 1px solid #2d3048; }
  .card h2 { font-size: 0.8rem; font-weight: 500; color: #888; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 12px; }
  .card .big-number { font-size: 2.4rem; font-weight: 700; color: #7c9eff; }
  .card .sub { font-size: 0.75rem; color: #666; margin-top: 4px; }
  .slo-badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: 600; margin-top: 8px; }
  .slo-ok { background: #14532d; color: #4ade80; }
  .slo-warn { background: #7c2d12; color: #fb923c; }
  canvas { max-height: 180px; }
  @media (max-width: 900px) { .grid { grid-template-columns: repeat(2, 1fr); } }
</style>
</head>
<body>
<header>
  <h1>&#x1F4CA; Day 13 Observability Lab — Live Dashboard</h1>
  <div id="refresh-badge">Auto-refresh: <span id="countdown">15</span>s</div>
</header>
<div class="grid">
  <!-- Panel 1: Latency -->
  <div class="card">
    <h2>&#x23F1; Latency P50 / P95 / P99</h2>
    <canvas id="latencyChart"></canvas>
    <div class="sub">SLO line at 3 000 ms (P95)</div>
  </div>

  <!-- Panel 2: Traffic -->
  <div class="card" style="display:flex;flex-direction:column;justify-content:center;">
    <h2>&#x1F4E1; Traffic</h2>
    <div class="big-number" id="trafficCount">—</div>
    <div class="sub">total requests since startup</div>
    <div id="trafficSlo" class="slo-badge slo-ok" style="display:none;"></div>
  </div>

  <!-- Panel 3: Error Rate -->
  <div class="card">
    <h2>&#x26A0;&#xFE0F; Error Breakdown</h2>
    <canvas id="errorChart"></canvas>
    <div class="sub">SLO: error rate &lt; 2%</div>
  </div>

  <!-- Panel 4: Cost -->
  <div class="card" style="display:flex;flex-direction:column;justify-content:center;">
    <h2>&#x1F4B0; Cost (USD)</h2>
    <div class="big-number" id="totalCost">—</div>
    <div class="sub" id="avgCostSub">avg per request: —</div>
    <div id="costSlo" class="slo-badge" style="display:none;"></div>
  </div>

  <!-- Panel 5: Tokens In / Out -->
  <div class="card">
    <h2>&#x1F9E0; Tokens In / Out</h2>
    <canvas id="tokenChart"></canvas>
    <div class="sub">cumulative token usage</div>
  </div>

  <!-- Panel 6: Quality Score -->
  <div class="card" style="display:flex;flex-direction:column;justify-content:center;">
    <h2>&#x2B50; Quality Score (avg)</h2>
    <div class="big-number" id="qualityScore">—</div>
    <div class="sub">heuristic proxy 0.0 – 1.0 | SLO: &gt; 0.75</div>
    <div id="qualitySlo" class="slo-badge" style="display:none;"></div>
  </div>
</div>

<script>
const SLO_LATENCY_P95 = 3000;
const SLO_QUALITY = 0.75;
const SLO_ERROR_RATE = 2;
const SLO_COST_DAY = 2.5;
const REFRESH_INTERVAL = 15;

const latencyChart = new Chart(document.getElementById('latencyChart'), {
  type: 'bar',
  data: {
    labels: ['P50', 'P95', 'P99'],
    datasets: [{
      label: 'Latency (ms)',
      data: [0, 0, 0],
      backgroundColor: ['#3b82f6', '#f59e0b', '#ef4444'],
      borderRadius: 4,
    }]
  },
  options: {
    responsive: true, maintainAspectRatio: true,
    plugins: {
      legend: { display: false },
      annotation: { annotations: {
        sloLine: { type: 'line', yMin: SLO_LATENCY_P95, yMax: SLO_LATENCY_P95,
          borderColor: '#ef4444', borderWidth: 1, borderDash: [4, 4],
          label: { content: 'SLO 3000ms', display: true, color: '#ef4444', font: { size: 10 } } }
      }}
    },
    scales: {
      y: { grid: { color: '#2d3048' }, ticks: { color: '#888' } },
      x: { grid: { display: false }, ticks: { color: '#888' } }
    }
  }
});

const errorChart = new Chart(document.getElementById('errorChart'), {
  type: 'doughnut',
  data: { labels: ['OK'], datasets: [{ data: [1], backgroundColor: ['#4ade80'], borderWidth: 0 }] },
  options: {
    responsive: true, maintainAspectRatio: true,
    plugins: { legend: { position: 'right', labels: { color: '#888', font: { size: 10 } } } }
  }
});

const tokenChart = new Chart(document.getElementById('tokenChart'), {
  type: 'bar',
  data: {
    labels: ['Tokens In', 'Tokens Out'],
    datasets: [{ data: [0, 0], backgroundColor: ['#6366f1', '#a855f7'], borderRadius: 4 }]
  },
  options: {
    responsive: true, maintainAspectRatio: true,
    plugins: { legend: { display: false } },
    scales: {
      y: { grid: { color: '#2d3048' }, ticks: { color: '#888' } },
      x: { grid: { display: false }, ticks: { color: '#888' } }
    }
  }
});

function slo(ok, okText, failText) {
  return `<div class="slo-badge ${ok ? 'slo-ok' : 'slo-warn'}">${ok ? '✓ ' + okText : '✗ ' + failText}</div>`;
}

async function fetchMetrics() {
  try {
    const r = await fetch('/metrics');
    const d = await r.json();

    latencyChart.data.datasets[0].data = [d.latency_p50, d.latency_p95, d.latency_p99];
    latencyChart.update();

    document.getElementById('trafficCount').textContent = d.traffic;
    const trafficEl = document.getElementById('trafficSlo');
    trafficEl.style.display = 'inline-block';
    trafficEl.outerHTML = slo(true, `${d.traffic} requests`, '').replace('style="display:none;"','');

    const errorBreakdown = d.error_breakdown || {};
    const errorKeys = Object.keys(errorBreakdown);
    const errorVals = Object.values(errorBreakdown);
    const totalErrors = errorVals.reduce((a, b) => a + b, 0);
    const okCount = Math.max(0, d.traffic - totalErrors);
    const errRate = d.traffic > 0 ? (totalErrors / d.traffic) * 100 : 0;
    if (errorKeys.length > 0) {
      errorChart.data.labels = ['OK', ...errorKeys];
      errorChart.data.datasets[0].data = [okCount, ...errorVals];
      errorChart.data.datasets[0].backgroundColor = ['#4ade80', ...errorKeys.map(() => '#ef4444')];
    } else {
      errorChart.data.labels = ['OK'];
      errorChart.data.datasets[0].data = [Math.max(1, d.traffic)];
      errorChart.data.datasets[0].backgroundColor = ['#4ade80'];
    }
    errorChart.update();

    document.getElementById('totalCost').textContent = '$' + (d.total_cost_usd || 0).toFixed(4);
    document.getElementById('avgCostSub').textContent = 'avg per request: $' + (d.avg_cost_usd || 0).toFixed(6);

    tokenChart.data.datasets[0].data = [d.tokens_in_total, d.tokens_out_total];
    tokenChart.update();

    const q = d.quality_avg || 0;
    document.getElementById('qualityScore').textContent = q.toFixed(3);
    const qSlo = document.getElementById('qualitySlo');
    qSlo.style.display = 'inline-block';
    qSlo.className = 'slo-badge ' + (q >= SLO_QUALITY ? 'slo-ok' : 'slo-warn');
    qSlo.textContent = q >= SLO_QUALITY ? '✓ SLO met (≥ 0.75)' : '✗ SLO breach (< 0.75)';

  } catch(e) {
    console.error('metrics fetch failed', e);
  }
}

let countdown = REFRESH_INTERVAL;
function tick() {
  countdown--;
  document.getElementById('countdown').textContent = countdown;
  if (countdown <= 0) {
    countdown = REFRESH_INTERVAL;
    fetchMetrics();
  }
}
fetchMetrics();
setInterval(tick, 1000);
</script>
</body>
</html>"""


def get_dashboard_html() -> str:
    return DASHBOARD_HTML
