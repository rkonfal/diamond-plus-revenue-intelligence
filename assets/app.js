async function loadSnapshot() {
  const res = await fetch('./data/revenue-intelligence-snapshot.json');
  if (!res.ok) throw new Error('Failed to load snapshot');
  return res.json();
}

function money(value) {
  return new Intl.NumberFormat('cs-CZ', { maximumFractionDigits: 0 }).format(value || 0) + ' Kč';
}

function num(value) {
  return new Intl.NumberFormat('cs-CZ', { maximumFractionDigits: 2 }).format(value || 0);
}

function pct(value) {
  if (value == null) return 'n/a';
  return `${num(value)} %`;
}

function trustBadge(trust) {
  const cls = trust === 'medium' ? 'warn' : trust === 'high' ? 'good' : 'bad';
  return `<span class="badge ${cls}">${trust}</span>`;
}

function riskBadge(risk) {
  const cls = risk === 'medium' ? 'warn' : risk === 'low' ? 'good' : 'bad';
  return `<span class="badge ${cls}">${risk}</span>`;
}

function top(arr, n) {
  return (arr || []).slice(0, n);
}

function renderHome(data) {
  const ex = data.executive;
  const biz = data.businessTruth;
  const mt = data.marketingTruth;
  const ga4 = top(data.measurement.ga4Channels, 8);
  const payables = top((biz.financeCurrentMonth && data.businessTruth.financePreviousMonth ? [] : []), 0);

  document.getElementById('app').innerHTML = `
    <section class="hero">
      <div class="pill">Stage 1, live prototype with backend truth foundation</div>
      <h1>Diamond Plus Revenue Intelligence</h1>
      <p>A decision-first revenue operating layer inspired by Roivenue, but designed around our own business truth, measurement skepticism, and management needs. This version already combines marketing, analytics, finance, and order pulse into one operating view.</p>
      <div class="nav">
        <a href="./index.html">Executive Home</a>
        <a href="./channels.html">Channel Intelligence</a>
        <a href="./audit-workspace.html">Audit Workspace</a>
        <a href="https://github.com/rkonfal/diamond-plus-revenue-intelligence">GitHub repo</a>
      </div>
      <div class="grid metrics">
        <div class="metric"><div class="k">Observed revenue</div><div class="v">${money(ex.observedRevenue.value)}</div><div class="sub">${ex.observedRevenue.label}, focus period ${data.focus.label}</div></div>
        <div class="metric"><div class="k">Paid media spend</div><div class="v">${money(ex.mediaSpend.value)}</div><div class="sub">${ex.mediaSpend.label}</div></div>
        <div class="metric"><div class="k">Blended ROAS</div><div class="v">${num(ex.blendedRoas.value)}</div><div class="sub">Observed GA4 revenue divided by paid media spend</div></div>
        <div class="metric"><div class="k">After-marketing result</div><div class="v">${money(ex.grossMarginAfterMarketing.value)}</div><div class="sub">Finance after marketing, previous full month</div></div>
        <div class="metric"><div class="k">Net cash position</div><div class="v">${money(ex.netCashPosition.value)}</div><div class="sub">Current finance truth layer</div></div>
        <div class="metric"><div class="k">Measurement confidence</div><div class="v bad">${ex.measurementConfidence.label}</div><div class="sub">${ex.measurementConfidence.reason}</div></div>
      </div>
    </section>

    <div class="cols-2">
      <section class="card">
        <h2>Immediate management actions</h2>
        <ul class="list">
          ${data.auditWorkspace.actions.map(item => `<li>${item}</li>`).join('')}
        </ul>
      </section>
      <section class="card">
        <h2>What this stage solved</h2>
        <ul class="list">
          ${data.productStage.done.map(item => `<li>${item}</li>`).join('')}
        </ul>
        <h3 style="margin-top:18px">What still comes next</h3>
        <ul class="list">
          ${data.productStage.next.map(item => `<li>${item}</li>`).join('')}
        </ul>
      </section>
    </div>

    <div class="cols-3">
      <section class="card">
        <h2>Finance truth</h2>
        <table>
          <tbody>
            <tr><td class="muted">Revenue</td><td>${money(biz.financePreviousMonth.revenue)}</td></tr>
            <tr><td class="muted">Gross margin</td><td>${money(biz.financePreviousMonth.grossMargin)}</td></tr>
            <tr><td class="muted">After logistics</td><td>${money(biz.financePreviousMonth.afterLogistics)}</td></tr>
            <tr><td class="muted">After marketing</td><td>${money(biz.financePreviousMonth.afterMarketing)}</td></tr>
            <tr><td class="muted">Operating margin</td><td>${money(biz.financePreviousMonth.operatingMargin)}</td></tr>
            <tr><td class="muted">Profit</td><td>${money(biz.financePreviousMonth.profit)}</td></tr>
            <tr><td class="muted">Profit %</td><td>${pct(biz.financePreviousMonth.profitPct)}</td></tr>
          </tbody>
        </table>
      </section>
      <section class="card">
        <h2>Order pulse, previous day</h2>
        <table>
          <tbody>
            <tr><td class="muted">Orders</td><td>${num(biz.previousDayOrders.orders)}</td></tr>
            <tr><td class="muted">Revenue with VAT</td><td>${money(biz.previousDayOrders.revenueWithVat)}</td></tr>
            <tr><td class="muted">Average order value</td><td>${money(biz.previousDayOrders.averageOrderValue)}</td></tr>
            <tr><td class="muted">Cancelled orders</td><td>${num(biz.previousDayOrders.cancelledOrders)}</td></tr>
            <tr><td class="muted">Problematic orders</td><td>${num(biz.previousDayOrders.problematicOrders)}</td></tr>
            <tr><td class="muted">CZ orders</td><td>${num(biz.previousDayOrders.czOrders)}</td></tr>
            <tr><td class="muted">SK orders</td><td>${num(biz.previousDayOrders.skOrders)}</td></tr>
          </tbody>
        </table>
      </section>
      <section class="card">
        <h2>Customer truth layer</h2>
        <p>${ex.newVsReturning.label}</p>
        <ul class="list">
          <li>We already have high-value customer samples and order pulse.</li>
          <li>The next unlock is a full customer fact table with first confirmed purchase date.</li>
          <li>That will power true new vs returning revenue and acquisition truth.</li>
        </ul>
      </section>
    </div>

    <section class="card">
      <h2>Channel truth layer</h2>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Channel</th><th>Spend</th><th>Reported revenue</th><th>ROAS</th><th>Trust</th><th>Interpretation</th></tr></thead>
          <tbody>
            ${mt.channels.map(row => `
            <tr>
              <td><strong>${row.channel}</strong></td>
              <td>${money(row.spend)}</td>
              <td>${money(row.reportedRevenue)}</td>
              <td>${num(row.roas)}</td>
              <td>${trustBadge(row.trust)}</td>
              <td class="muted">${row.notes.join(' • ')}</td>
            </tr>`).join('')}
          </tbody>
        </table>
      </div>
    </section>

    <div class="cols-2">
      <section class="card">
        <h2>Observed GA4 channels</h2>
        <div class="table-wrap">
          <table>
            <thead><tr><th>Channel</th><th>Sessions</th><th>Purchases</th><th>Revenue</th></tr></thead>
            <tbody>
              ${ga4.map(row => `
                <tr>
                  <td>${row.channel}</td>
                  <td>${num(row.sessions)}</td>
                  <td>${num(row.ecommercePurchases)}</td>
                  <td>${money(row.purchaseRevenue)}</td>
                </tr>`).join('')}
            </tbody>
          </table>
        </div>
      </section>
      <section class="card">
        <h2>Measurement warnings</h2>
        <ul class="list">
          ${data.measurement.warnings.map(item => `<li>${item}</li>`).join('')}
        </ul>
      </section>
    </div>

    <section class="card">
      <h2>Top customers sample</h2>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Customer</th><th>Orders</th><th>Revenue</th><th>Average order value</th><th>Last order</th></tr></thead>
          <tbody>
            ${top(biz.topCustomersSample, 8).map(row => `
            <tr>
              <td>${row.label}</td>
              <td>${num(row.orders)}</td>
              <td>${money(row.revenueWithVat)}</td>
              <td>${money(row.averageOrderValue)}</td>
              <td class="muted">${row.lastOrderAt}</td>
            </tr>`).join('')}
          </tbody>
        </table>
      </div>
      <p class="footer-note">Snapshot generated: ${data.generatedAt}</p>
    </section>
  `;
}

function renderChannels(data) {
  const mt = data.marketingTruth;
  const ga4 = top(data.measurement.ga4Channels, 12);
  document.getElementById('app').innerHTML = `
    <section class="hero">
      <div class="pill">Channel intelligence</div>
      <h1>Where channel performance looks strong, and where it only looks strong.</h1>
      <p>This view is built for channel reviews, agency control, and future drilldowns. Trust stays visible by default so platform-reported revenue never hides measurement weakness.</p>
      <div class="nav">
        <a href="./index.html">Executive Home</a>
        <a href="./channels.html">Channel Intelligence</a>
        <a href="./audit-workspace.html">Audit Workspace</a>
      </div>
    </section>

    <section class="card">
      <h2>Cross-platform comparison</h2>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Channel</th><th>Spend</th><th>Reported revenue</th><th>ROAS</th><th>Trust</th><th>Interpretation</th></tr></thead>
          <tbody>
            ${mt.channels.map(row => `
              <tr>
                <td><strong>${row.channel}</strong></td>
                <td>${money(row.spend)}</td>
                <td>${money(row.reportedRevenue)}</td>
                <td>${num(row.roas)}</td>
                <td>${trustBadge(row.trust)}</td>
                <td class="muted">${row.notes.join(' • ')}</td>
              </tr>`).join('')}
          </tbody>
        </table>
      </div>
    </section>

    <section class="card">
      <h2>Observed GA4 channels</h2>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Channel</th><th>Sessions</th><th>Purchases</th><th>Revenue</th><th>Revenue / session</th></tr></thead>
          <tbody>
            ${ga4.map(row => `
              <tr>
                <td>${row.channel}</td>
                <td>${num(row.sessions)}</td>
                <td>${num(row.ecommercePurchases)}</td>
                <td>${money(row.purchaseRevenue)}</td>
                <td>${row.revenuePerSession != null ? money(row.revenuePerSession) : '<span class="muted">n/a</span>'}</td>
              </tr>`).join('')}
          </tbody>
        </table>
      </div>
    </section>
  `;
}

function renderAudit(data) {
  const rows = data.auditWorkspace.topCampaigns;
  document.getElementById('app').innerHTML = `
    <section class="hero">
      <div class="pill">Audit workspace</div>
      <h1>Campaign and platform audit workspace for management and specialist reviews.</h1>
      <p>This page is the operating bridge between leadership and channel teams. It shows where spend concentrates, where reported efficiency needs skepticism, and which changes deserve action first.</p>
      <div class="nav">
        <a href="./index.html">Executive Home</a>
        <a href="./channels.html">Channel Intelligence</a>
        <a href="./audit-workspace.html">Audit Workspace</a>
      </div>
    </section>

    <section class="card">
      <h2>Top campaigns by spend</h2>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Platform</th><th>Campaign</th><th>Spend</th><th>Revenue</th><th>ROAS</th><th>Status</th><th>Risk</th></tr></thead>
          <tbody>
            ${rows.map(row => `
              <tr>
                <td>${row.platform}</td>
                <td>${row.name}</td>
                <td>${money(row.spend)}</td>
                <td>${money(row.revenue)}</td>
                <td>${num(row.roas)}</td>
                <td class="muted">${row.status || 'n/a'}</td>
                <td>${riskBadge(row.risk)}</td>
              </tr>`).join('')}
          </tbody>
        </table>
      </div>
    </section>

    <section class="card">
      <h2>Recommended audit actions</h2>
      <ul class="list">
        ${data.auditWorkspace.actions.map(item => `<li>${item}</li>`).join('')}
      </ul>
    </section>
  `;
}

loadSnapshot().then(data => {
  const page = document.body.dataset.page || 'home';
  if (page === 'channels') renderChannels(data);
  else if (page === 'audit') renderAudit(data);
  else renderHome(data);
}).catch(err => {
  document.getElementById('app').innerHTML = `<section class="card"><h2>Failed to load snapshot</h2><p>${err.message}</p></section>`;
});
