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

function deltaClass(value) {
  if (value == null) return 'muted';
  if (value > 0) return 'good';
  if (value < 0) return 'bad';
  return 'warn';
}

function trustBadge(trust) {
  const cls = trust === 'medium' ? 'warn' : trust === 'high' ? 'good' : 'bad';
  return `<span class="badge ${cls}">${trust}</span>`;
}

function renderHome(data) {
  const focus = data.periods.ga4Focus;
  const exec = data.executive;
  const channels = data.channels;
  const ga4Channels = data.ga4Channels.slice(0, 8);
  const landing = data.topLandingPages.slice(0, 8);

  document.getElementById('app').innerHTML = `
    <section class="hero">
      <div class="pill">Diamond Plus Revenue Intelligence, v1 foundation</div>
      <h1>Decision-first revenue operating layer inspired by Roivenue, but built around our own data truth.</h1>
      <p>This first version already separates platform optimism from analytics reality, keeps management attention on confidence and business value, and creates a base for new-vs-returning, margin-aware, and attribution-comparison workflows.</p>
      <div class="nav">
        <a href="./index.html">Executive Home</a>
        <a href="./channels.html">Channel Intelligence</a>
        <a href="https://github.com/rkonfal/diamond-plus-revenue-intelligence">GitHub repo</a>
      </div>
      <div class="grid metrics">
        <div class="metric">
          <div class="k">Focus period</div>
          <div class="v">${focus.label}</div>
          <div class="sub">Using the previous full month when current-month data is too early to interpret.</div>
        </div>
        <div class="metric">
          <div class="k">Observed revenue</div>
          <div class="v">${money(exec.backendStyleRevenueProxy.value)}</div>
          <div class="sub">${exec.backendStyleRevenueProxy.label}</div>
        </div>
        <div class="metric">
          <div class="k">Paid media spend</div>
          <div class="v">${money(exec.paidMediaSpend.value)}</div>
          <div class="sub">Cross-platform spend for the focus period.</div>
        </div>
        <div class="metric">
          <div class="k">Measurement confidence</div>
          <div class="v bad">${exec.measurementConfidence.label}</div>
          <div class="sub">${exec.measurementConfidence.reason}</div>
        </div>
      </div>
    </section>

    <div class="cols-2">
      <section class="card">
        <h2>Immediate decision layer</h2>
        <ul class="list">
          ${data.actions.map(item => `<li>${item}</li>`).join('')}
        </ul>
      </section>
      <section class="card">
        <h2>What the product should make obvious</h2>
        <ul class="list">
          <li>Which channels genuinely create demand and which recycle existing intent.</li>
          <li>How much of reported growth is trustworthy across platform, analytics, and backend views.</li>
          <li>Where new customer contribution is real and where it is overstated.</li>
          <li>Which actions deserve immediate budget reallocation without waiting for another report cycle.</li>
        </ul>
      </section>
    </div>

    <section class="card">
      <h2>Channel truth layer</h2>
      <div class="table-wrap">
        <table>
          <thead>
            <tr><th>Channel</th><th>Spend</th><th>Reported revenue</th><th>ROAS</th><th>Trust</th><th>Key notes</th></tr>
          </thead>
          <tbody>
            ${channels.map(row => `
              <tr>
                <td><strong>${row.channel}</strong></td>
                <td>${money(row.spend)}</td>
                <td>${money(row.reportedRevenue)}</td>
                <td>${num(row.roas)}</td>
                <td>${trustBadge(row.trust)}</td>
                <td class="muted">${row.notes.join(' • ')}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    </section>

    <div class="cols-2">
      <section class="card">
        <h2>GA4 channel view</h2>
        <div class="table-wrap">
          <table>
            <thead><tr><th>Channel</th><th>Sessions</th><th>Purchases</th><th>Revenue</th></tr></thead>
            <tbody>
            ${ga4Channels.map(row => `
              <tr>
                <td>${row.channel}</td>
                <td>${num(row.sessions)}</td>
                <td>${num(row.ecommercePurchases)}</td>
                <td>${money(row.purchaseRevenue)}</td>
              </tr>
            `).join('')}
            </tbody>
          </table>
        </div>
      </section>
      <section class="card">
        <h2>Landing page anomalies</h2>
        <div class="table-wrap">
          <table>
            <thead><tr><th>Landing page</th><th>Sessions</th><th>Purchases</th><th>Revenue</th></tr></thead>
            <tbody>
            ${landing.map(row => `
              <tr>
                <td class="muted">${row.landingPage}</td>
                <td>${num(row.sessions)}</td>
                <td>${num(row.ecommercePurchases)}</td>
                <td>${money(row.purchaseRevenue)}</td>
              </tr>
            `).join('')}
            </tbody>
          </table>
        </div>
      </section>
    </div>

    <section class="card">
      <h2>Product next step</h2>
      <p>The next build should connect backend orders, returns, cancellations, margin logic, and first purchase date classification so this stops being just a clean intelligence shell and becomes a real revenue operating system.</p>
      <p class="footer-note">Snapshot generated: ${data.generatedAt}</p>
    </section>
  `;
}

function renderChannels(data) {
  const channels = data.channels;
  const ga4 = data.ga4Channels.slice(0, 12);
  document.getElementById('app').innerHTML = `
    <section class="hero">
      <div class="pill">Channel intelligence</div>
      <h1>Where marketing performance looks strong, and where it only looks strong.</h1>
      <p>This screen is the base for channel reviews, agency control, and future campaign drilldowns. It keeps the distinction between platform claims and trust level visible by default.</p>
      <div class="nav">
        <a href="./index.html">Executive Home</a>
        <a href="./channels.html">Channel Intelligence</a>
      </div>
    </section>

    <section class="card">
      <h2>Cross-platform comparison</h2>
      <div class="table-wrap">
        <table>
          <thead>
            <tr><th>Channel</th><th>Spend</th><th>Reported revenue</th><th>ROAS</th><th>Trust</th><th>Interpretation</th></tr>
          </thead>
          <tbody>
            ${channels.map(row => `
              <tr>
                <td><strong>${row.channel}</strong></td>
                <td>${money(row.spend)}</td>
                <td>${money(row.reportedRevenue)}</td>
                <td>${num(row.roas)}</td>
                <td>${trustBadge(row.trust)}</td>
                <td class="muted">${row.notes.join(' • ')}</td>
              </tr>
            `).join('')}
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
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    </section>
  `;
}

loadSnapshot().then(data => {
  const page = document.body.dataset.page || 'home';
  if (page === 'channels') renderChannels(data);
  else renderHome(data);
}).catch(err => {
  document.getElementById('app').innerHTML = `<section class="card"><h2>Failed to load snapshot</h2><p>${err.message}</p></section>`;
});
