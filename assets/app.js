import { loadDataLayer } from './data-layer.js';

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
  const customer = data.customerTruth;
  const ga4 = top(data.measurement.ga4Channels, 8);

  document.getElementById('app').innerHTML = `
    <section class="hero">
      <div class="pill">${data.productStage.name}</div>
      <h1>Revenue report, který jde normálně číst.</h1>
      <p>Tahle verze odděluje to, co je jistý business truth, od toho, co je jen marketingové tvrzení. A nahoře rovnou říká, co si z reportu má management odnést.</p>
      <div class="nav">
        <a href="./index.html">Shrnutí</a>
        <a href="./channels.html">Kanály</a>
        <a href="./audit-workspace.html">Audit</a>
        <a href="https://github.com/rkonfal/diamond-plus-revenue-intelligence">GitHub repo</a>
      </div>
      <div class="grid metrics">
        <div class="metric"><div class="k">Pozorované tržby</div><div class="v">${money(ex.observedRevenue.value)}</div><div class="sub">${data.focus.label}</div></div>
        <div class="metric"><div class="k">Paid media spend</div><div class="v">${money(ex.mediaSpend.value)}</div><div class="sub">Meta + Google + Sklik</div></div>
        <div class="metric"><div class="k">Blended ROAS</div><div class="v">${num(ex.blendedRoas.value)}</div><div class="sub">Pozorované tržby / spend</div></div>
        <div class="metric"><div class="k">Výsledek po marketingu</div><div class="v">${money(ex.grossMarginAfterMarketing.value)}</div><div class="sub">Finance, minulý plný měsíc</div></div>
        <div class="metric"><div class="k">Net cash</div><div class="v">${money(ex.netCashPosition.value)}</div><div class="sub">Aktuální finanční realita</div></div>
        <div class="metric"><div class="k">Jistota měření</div><div class="v bad">${ex.measurementConfidence.label}</div><div class="sub">${ex.measurementConfidence.reason}</div></div>
      </div>
    </section>

    <div class="cols-3">
      <section class="card">
        <h2>Co ten report říká</h2>
        <ul class="list">
          ${ex.reportNarrative.plainLanguage.map(item => `<li>${item}</li>`).join('')}
        </ul>
      </section>
      <section class="card">
        <h2>Co je dobrá zpráva</h2>
        <ul class="list">
          <li>Po marketingu vychází ve financích <strong>${money(biz.contributionTruth.previousMonth.afterMarketing)}</strong>.</li>
          <li>Net cash je <strong>${money(ex.netCashPosition.value)}</strong>.</li>
          <li>Repeat zákaznická báze je <strong>${customer.estimatedNewVsReturning.returningBaseStrength}</strong>.</li>
        </ul>
      </section>
      <section class="card">
        <h2>Na co si dát pozor</h2>
        <ul class="list">
          <li>Stále nemáme plný historical order fact pro celý customer universe.</li>
          <li>Platform revenue je optimističtější než analytická a backend realita.</li>
          <li>True new vs returning je zatím částečně proxy, ne finální pravda.</li>
        </ul>
      </section>
    </div>

    <div class="cols-2">
      <section class="card">
        <h2>Co udělat hned</h2>
        <ul class="list">
          ${ex.reportNarrative.whatToDoNow.map(item => `<li>${item}</li>`).join('')}
        </ul>
      </section>
      <section class="card">
        <h2>Automatická aktualizace</h2>
        <ul class="list">
          <li>Data se teď dají obnovovat automaticky z preview repa.</li>
          <li>V repu je připravený GitHub Actions refresh pipeline.</li>
          <li>Report už není ruční jednorázovka, ale aktualizovatelný produktový základ.</li>
        </ul>
      </section>
    </div>

    <div class="cols-3">
      <section class="card">
        <h2>Finance truth</h2>
        <table><tbody>
          <tr><td class="muted">Revenue</td><td>${money(biz.financePreviousMonth.revenue)}</td></tr>
          <tr><td class="muted">Gross margin</td><td>${money(biz.financePreviousMonth.grossMargin)}</td></tr>
          <tr><td class="muted">After marketing</td><td>${money(biz.financePreviousMonth.afterMarketing)}</td></tr>
          <tr><td class="muted">Operating margin</td><td>${money(biz.financePreviousMonth.operatingMargin)}</td></tr>
          <tr><td class="muted">Profit %</td><td>${pct(biz.financePreviousMonth.profitPct)}</td></tr>
        </tbody></table>
      </section>
      <section class="card">
        <h2>Order quality</h2>
        <table><tbody>
          <tr><td class="muted">Orders</td><td>${num(biz.previousDayOrders.orders)}</td></tr>
          <tr><td class="muted">Cancelled rate</td><td>${pct(biz.orderQuality.cancelledRatePct)}</td></tr>
          <tr><td class="muted">Problematic rate</td><td>${pct(biz.orderQuality.problematicRatePct)}</td></tr>
          <tr><td class="muted">Estimated net after cancellations</td><td>${money(biz.orderQuality.estimatedNetRevenueAfterCancellations)}</td></tr>
        </tbody></table>
      </section>
      <section class="card">
        <h2>Customer truth</h2>
        <ul class="list">
          <li>Top 10 zákazníků = <strong>${pct(customer.coverage.top10RevenueSharePctOfYtd)}</strong> YTD revenue.</li>
          <li>Top 50 zákazníků = <strong>${pct(customer.coverage.top50RevenueSharePctOfYtd)}</strong> YTD revenue.</li>
          <li>Heavy repeat customers v top 50: <strong>${num(customer.repeatSignals.heavyRepeatCustomersInTop50)}</strong>.</li>
          <li>${customer.readiness.nextUnlock}</li>
        </ul>
      </section>
    </div>

    <section class="card">
      <h2>Channel truth layer</h2>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Kanál</th><th>Spend</th><th>Reported revenue</th><th>ROAS</th><th>Důvěra</th><th>Výklad</th></tr></thead>
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
        <h2>GA4 observed channels</h2>
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
        <h2>Nejdůležitější omezení</h2>
        <ul class="list">
          ${data.measurement.warnings.map(item => `<li>${item}</li>`).join('')}
        </ul>
      </section>
    </div>

    <section class="card">
      <h2>Top customers sample</h2>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Customer</th><th>Orders</th><th>Revenue</th><th>AOV</th><th>Last order</th></tr></thead>
          <tbody>
            ${top(customer.topCustomers, 8).map(row => `
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
      <p class="footer-note">Aktualizováno: ${data.generatedAt}</p>
    </section>
  `;
}

function renderChannels(data) {
  const mt = data.marketingTruth;
  const ga4 = top(data.measurement.ga4Channels, 12);
  document.getElementById('app').innerHTML = `
    <section class="hero">
      <div class="pill">Channel intelligence</div>
      <h1>Kanály, které výkon tvoří, versus kanály, které jen dobře vypadají.</h1>
      <p>Tahle stránka má být čitelná i pro člověka, který nežije v reklamních platformách. Proto je u každého kanálu rovnou i interpretace a důvěra v data.</p>
      <div class="nav">
        <a href="./index.html">Shrnutí</a>
        <a href="./channels.html">Kanály</a>
        <a href="./audit-workspace.html">Audit</a>
      </div>
    </section>

    <section class="card">
      <h2>Cross-platform comparison</h2>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Channel</th><th>Spend</th><th>Reported revenue</th><th>ROAS</th><th>Důvěra</th><th>Interpretace</th></tr></thead>
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
      <h1>Audit kampaní a platforem.</h1>
      <p>Tady je pracovní plocha pro detailnější kontrolu. Má odpovědět na otázku, kde je největší spend, kde je riziko a kde se má zasáhnout jako první.</p>
      <div class="nav">
        <a href="./index.html">Shrnutí</a>
        <a href="./channels.html">Kanály</a>
        <a href="./audit-workspace.html">Audit</a>
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

loadDataLayer().then(data => {
  const page = document.body.dataset.page || 'home';
  if (page === 'channels') renderChannels(data);
  else if (page === 'audit') renderAudit(data);
  else renderHome(data);
}).catch(err => {
  document.getElementById('app').innerHTML = `<section class="card"><h2>Failed to load data layer</h2><p>${err.message}</p></section>`;
});
