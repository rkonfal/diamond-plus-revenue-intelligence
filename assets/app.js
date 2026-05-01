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
  const cls = trust === 'medium' || trust === 'medium_high' ? 'warn' : trust === 'high' ? 'good' : 'bad';
  return `<span class="badge ${cls}">${trust}</span>`;
}

function riskBadge(risk) {
  const cls = risk === 'medium' ? 'warn' : risk === 'low' ? 'good' : 'bad';
  return `<span class="badge ${cls}">${risk}</span>`;
}

function statusBadge(status) {
  const cls = status === 'strong' ? 'good' : status === 'close' ? 'warn' : 'bad';
  return `<span class="badge ${cls}">${status}</span>`;
}

function bucketBadge(bucket) {
  const cls = bucket === 'retention' ? 'good' : bucket === 'brand' || bucket === 'harvesting' ? 'warn' : bucket === 'acquisition' ? 'good' : 'bad';
  return `<span class="badge ${cls}">${bucket}</span>`;
}

function top(arr, n) {
  return (arr || []).slice(0, n);
}

function nav() {
  return `
    <div class="nav">
      <a href="./index.html">Shrnutí</a>
      <a href="./management.html">Management</a>
      <a href="./marketing.html">Marketing</a>
      <a href="./finance.html">Finance</a>
      <a href="./channels.html">Kanály</a>
      <a href="./audit-workspace.html">Audit</a>
      <a href="./compare-roivenue.html">Vs. Roivenue</a>
    </div>
  `;
}

function metricCard(label, value, sub, tone = '') {
  return `<div class="metric"><div class="k">${label}</div><div class="v ${tone}">${value}</div><div class="sub">${sub}</div></div>`;
}

function renderHome(data) {
  const ex = data.executive;
  const biz = data.businessTruth;
  const mt = data.marketingTruth;
  const customer = data.customerTruth;
  const ch = data.channelIntelligence;
  const acq = data.acquisitionTruth;
  const plan = data.actionPlan;
  const ga4 = top(data.measurement.ga4Channels, 8);
  const paidMix = top(mt.paidMix.bucketSummaryPreviousMonth, 5);
  const searchTax = top(mt.searchTaxonomy.summaryPreviousMonth, 5);

  document.getElementById('app').innerHTML = `
    <section class="hero hero-grid">
      <div>
        <div class="pill">${data.productStage.name}</div>
        <h1>Revenue intelligence, který už jde řídit, ne jen proklikávat.</h1>
        <p>Homepage teď začíná tím, co je opravdu důležité. Business truth, measured customer truth, decision-grade channel truth a jasné další kroky.</p>
        ${nav()}
      </div>
      <div class="hero-aside card inset">
        <h3>Co si má management odnést</h3>
        <ul class="list compact">${ex.reportNarrative.plainLanguage.map(item => `<li>${item}</li>`).join('')}</ul>
      </div>
      <div class="grid metrics full-span">
        ${metricCard('Pozorované tržby', money(ex.observedRevenue.value), data.focus.label)}
        ${metricCard('Paid media spend', money(ex.mediaSpend.value), 'Meta + Google + Sklik')}
        ${metricCard('Blended ROAS', num(ex.blendedRoas.value), 'Pozorované tržby / spend')}
        ${metricCard('Výsledek po marketingu', money(ex.grossMarginAfterMarketing.value), 'Finance, minulý plný měsíc')}
        ${metricCard('Returning share YTD', pct(customer.estimatedNewVsReturning.returningRevenueSharePct), 'Measured customer truth', 'warn')}
        ${metricCard('Jistota měření', ex.measurementConfidence.label, ex.measurementConfidence.reason, 'warn')}
      </div>
    </section>

    <div class="cols-3">
      <section class="card emphasis good-border">
        <h2>Co víme jistě</h2>
        <ul class="list">${data.finalTruthEngine.whatIsTrulyKnown.map(item => `<li>${item}</li>`).join('')}</ul>
      </section>
      <section class="card emphasis warn-border">
        <h2>Co je rozhodovací truth</h2>
        <ul class="list compact">
          <li>Acquisition se musí řídit přes net-new demand, ne přes platform ROAS.</li>
          <li>Brand a harvesting jsou demand capture, ne důkaz inkrementality.</li>
          <li>Retention je samostatný motor repeat revenue, ne součást paid acquisition story.</li>
        </ul>
      </section>
      <section class="card emphasis bad-border">
        <h2>Co ještě chybí</h2>
        <ul class="list">${data.finalTruthEngine.blockingMissingSources.map(item => `<li>${item}</li>`).join('')}</ul>
      </section>
    </div>

    <div class="cols-2 top-gap">
      <section class="card">
        <div class="section-head"><h2>Channel intelligence, první obrazovka</h2><div class="muted small">platform claim vs observed truth</div></div>
        <div class="table-wrap"><table>
          <thead><tr><th>Kanál</th><th>Claim revenue</th><th>Observed revenue</th><th>Claim ROAS</th><th>Observed ROAS</th><th>Důvěra</th></tr></thead>
          <tbody>${ch.rows.map(row => `<tr><td><strong>${row.channel}</strong><div class="muted tiny">${row.primaryIssue}</div></td><td>${money(row.platformRevenuePreviousMonth)}</td><td>${money(row.ga4ObservedRevenue)}</td><td>${num(row.platformRoasPreviousMonth)}</td><td>${num(row.ga4ObservedRoas)}</td><td>${trustBadge(row.trustLabel)}</td></tr>`).join('')}</tbody>
        </table></div>
      </section>
      <section class="card">
        <div class="section-head"><h2>Bucket split, předchozí měsíc</h2><div class="muted small">acquisition vs remarketing vs brand vs retention</div></div>
        <div class="table-wrap"><table>
          <thead><tr><th>Bucket</th><th>Spend</th><th>Revenue</th><th>ROAS</th><th>Kampaně</th></tr></thead>
          <tbody>${paidMix.map(row => `<tr><td>${bucketBadge(row.bucket)}</td><td>${money(row.spend)}</td><td>${money(row.revenue)}</td><td>${num(row.roas)}</td><td>${num(row.campaigns)}</td></tr>`).join('')}</tbody>
        </table></div>
      </section>
    </div>

    <div class="cols-3">
      <section class="card">
        <h2>Customer truth</h2>
        <ul class="list compact">
          <li>Returning revenue YTD: <strong>${money(customer.estimatedNewVsReturning.returningRevenueWithVat)}</strong>.</li>
          <li>New revenue YTD: <strong>${money(customer.estimatedNewVsReturning.newRevenueWithVat)}</strong>.</li>
          <li>Top 10 zákazníků tvoří <strong>${pct(customer.coverage.top10RevenueSharePctOfYtd)}</strong> YTD revenue.</li>
          <li>Heavy repeat customers v top 50: <strong>${num(customer.repeatSignals.heavyRepeatCustomersInTop50)}</strong>.</li>
        </ul>
      </section>
      <section class="card">
        <h2>Measurement truth</h2>
        <ul class="list compact">
          <li>Finance revenue: <strong>${money(data.measurement.truth.reconciliation.financeRevenuePreviousMonth)}</strong>.</li>
          <li>GA4 observed revenue: <strong>${money(data.measurement.truth.reconciliation.ga4ObservedRevenuePreviousMonth)}</strong>.</li>
          <li>Platform claims: <strong>${money(data.measurement.truth.reconciliation.platformClaimedRevenuePreviousMonth)}</strong>.</li>
          <li>Unassigned revenue share: <strong>${pct(data.measurement.truth.reconciliation.unassignedRevenueSharePctOfFocusObserved)}</strong>.</li>
        </ul>
      </section>
      <section class="card">
        <h2>Finance truth</h2>
        <ul class="list compact">
          <li>After marketing: <strong>${money(biz.contributionTruth.previousMonth.afterMarketing)}</strong>.</li>
          <li>Operating margin: <strong>${money(biz.financePreviousMonth.operatingMargin)}</strong>.</li>
          <li>Net cash: <strong>${money(ex.netCashPosition.value)}</strong>.</li>
          <li>Estimated net after cancellations: <strong>${money(biz.orderQuality.estimatedNetRevenueAfterCancellations)}</strong>.</li>
        </ul>
      </section>
    </div>

    <div class="cols-2">
      <section class="card">
        <div class="section-head"><h2>Unified search taxonomy</h2><div class="muted small">Google + Sklik na stejné mapě</div></div>
        <div class="table-wrap"><table>
          <thead><tr><th>Typ</th><th>Spend</th><th>Revenue</th><th>ROAS</th><th>Platformy</th></tr></thead>
          <tbody>${searchTax.map(row => `<tr><td><strong>${row.type}</strong></td><td>${money(row.spend)}</td><td>${money(row.revenue)}</td><td>${num(row.roas)}</td><td class="muted">${row.platforms.join(', ')}</td></tr>`).join('')}</tbody>
        </table></div>
      </section>
      <section class="card">
        <div class="section-head"><h2>Co udělat teď</h2><div class="muted small">action plan dataset</div></div>
        <ul class="list">${plan.now.map(item => `<li>${item}</li>`).join('')}</ul>
        <h3 class="top-gap-small">Další 2 až 4 týdny</h3>
        <ul class="list compact">${plan.next_2_to_4_weeks.map(item => `<li>${item}</li>`).join('')}</ul>
      </section>
    </div>

    <div class="cols-2">
      <section class="card"><h2>GA4 observed channels</h2><div class="table-wrap"><table>
        <thead><tr><th>Channel</th><th>Sessions</th><th>Purchases</th><th>Revenue</th></tr></thead>
        <tbody>${ga4.map(row => `<tr><td>${row.channel}</td><td>${num(row.sessions)}</td><td>${num(row.ecommercePurchases)}</td><td>${money(row.purchaseRevenue)}</td></tr>`).join('')}</tbody>
      </table></div></section>
      <section class="card"><h2>Nejdůležitější omezení</h2><ul class="list">${data.measurement.warnings.map(item => `<li>${item}</li>`).join('')}</ul></section>
    </div>

    <section class="card">
      <h2>Top customers sample</h2>
      <div class="table-wrap"><table>
        <thead><tr><th>Customer</th><th>Orders</th><th>Revenue</th><th>AOV</th><th>Segment</th></tr></thead>
        <tbody>${top(customer.topCustomers, 8).map(row => `<tr><td>${row.label}</td><td>${num(row.orders)}</td><td>${money(row.revenueWithVat)}</td><td>${money(row.averageOrderValue)}</td><td>${row.segment}</td></tr>`).join('')}</tbody>
      </table></div>
      <p class="footer-note">Aktualizováno: ${data.generatedAt}</p>
    </section>
  `;
}

function renderRole(data, key, title) {
  const role = data.roleViews[key];
  const plan = data.actionPlan;
  document.getElementById('app').innerHTML = `
    <section class="hero">
      <div class="pill">${title}</div>
      <h1>${role.headline}</h1>
      <p>Tahle role-based vrstva zkracuje report na to, co má konkrétní člověk opravdu řešit.</p>
      ${nav()}
    </section>
    <div class="cols-2">
      <section class="card"><h2>Na co se dívat</h2><ul class="list">${role.focus.map(item => `<li>${item}</li>`).join('')}</ul></section>
      <section class="card"><h2>Klíčové otázky</h2><ul class="list">${role.questions.map(item => `<li>${item}</li>`).join('')}</ul></section>
    </div>
    <section class="card"><h2>Nejbližší akce</h2><ul class="list compact">${plan.now.map(item => `<li>${item}</li>`).join('')}</ul></section>
  `;
}

function renderChannels(data) {
  const mt = data.marketingTruth;
  const ch = data.channelIntelligence;
  document.getElementById('app').innerHTML = `
    <section class="hero">
      <div class="pill">Channel intelligence</div>
      <h1>Kanály, které výkon tvoří, versus kanály, které jen dobře vypadají.</h1>
      <p>Nejdřív claim versus observed truth, pak bucket split a až potom detail kampaní.</p>
      ${nav()}
    </section>
    <section class="card"><h2>Claim versus observed</h2><div class="table-wrap"><table>
      <thead><tr><th>Kanál</th><th>Claim revenue</th><th>Observed revenue</th><th>Claim ROAS</th><th>Observed ROAS</th><th>Trust</th><th>Next question</th></tr></thead>
      <tbody>${ch.rows.map(row => `<tr><td><strong>${row.channel}</strong></td><td>${money(row.platformRevenuePreviousMonth)}</td><td>${money(row.ga4ObservedRevenue)}</td><td>${num(row.platformRoasPreviousMonth)}</td><td>${num(row.ga4ObservedRoas)}</td><td>${trustBadge(row.trustLabel)}</td><td class="muted">${row.nextQuestion}</td></tr>`).join('')}</tbody>
    </table></div></section>
    <div class="cols-2">
      <section class="card"><h2>Paid mix buckets</h2><div class="table-wrap"><table>
        <thead><tr><th>Bucket</th><th>Spend</th><th>Revenue</th><th>ROAS</th><th>Kampaně</th></tr></thead>
        <tbody>${mt.paidMix.bucketSummaryPreviousMonth.map(row => `<tr><td>${bucketBadge(row.bucket)}</td><td>${money(row.spend)}</td><td>${money(row.revenue)}</td><td>${num(row.roas)}</td><td>${num(row.campaigns)}</td></tr>`).join('')}</tbody>
      </table></div></section>
      <section class="card"><h2>Search taxonomy</h2><div class="table-wrap"><table>
        <thead><tr><th>Typ</th><th>Spend</th><th>Revenue</th><th>ROAS</th><th>Platformy</th></tr></thead>
        <tbody>${mt.searchTaxonomy.summaryPreviousMonth.map(row => `<tr><td><strong>${row.type}</strong></td><td>${money(row.spend)}</td><td>${money(row.revenue)}</td><td>${num(row.roas)}</td><td class="muted">${row.platforms.join(', ')}</td></tr>`).join('')}</tbody>
      </table></div></section>
    </div>
    <section class="card"><h2>Top campaigns</h2><div class="table-wrap"><table>
      <thead><tr><th>Platform</th><th>Campaign</th><th>Bucket</th><th>Spend</th><th>Revenue</th><th>ROAS</th></tr></thead>
      <tbody>${mt.topCampaigns.map(row => `<tr><td>${row.platform}</td><td>${row.name}</td><td>${bucketBadge(row.bucket)}</td><td>${money(row.spend)}</td><td>${money(row.revenue)}</td><td>${num(row.roas)}</td></tr>`).join('')}</tbody>
    </table></div></section>
  `;
}

function renderAudit(data) {
  const rows = data.auditWorkspace.topCampaigns;
  document.getElementById('app').innerHTML = `
    <section class="hero">
      <div class="pill">Audit workspace</div>
      <h1>Audit kampaní a platforem.</h1>
      <p>Tady je pracovní plocha pro detailnější kontrolu, už včetně bucket klasifikace.</p>
      ${nav()}
    </section>
    <section class="card"><h2>Top campaigns by spend</h2><div class="table-wrap"><table>
      <thead><tr><th>Platform</th><th>Campaign</th><th>Bucket</th><th>Spend</th><th>Revenue</th><th>ROAS</th><th>Status</th><th>Risk</th></tr></thead>
      <tbody>${rows.map(row => `<tr><td>${row.platform}</td><td>${row.name}</td><td>${bucketBadge(row.bucket)}</td><td>${money(row.spend)}</td><td>${money(row.revenue)}</td><td>${num(row.roas)}</td><td class="muted">${row.status || 'n/a'}</td><td>${riskBadge(row.risk)}</td></tr>`).join('')}</tbody>
    </table></div></section>
    <section class="card"><h2>Recommended audit actions</h2><ul class="list">${data.auditWorkspace.actions.map(item => `<li>${item}</li>`).join('')}</ul></section>
  `;
}

function renderRoivenue(data) {
  const cmp = data.roivenueComparison;
  document.getElementById('app').innerHTML = `
    <section class="hero">
      <div class="pill">Vs. Roivenue</div>
      <h1>${cmp.headline}</h1>
      <p>Tohle srovnání je upřímné. Ukazuje, kde je náš produkt už teď lepší pro Diamond Plus a kde ještě zaostává.</p>
      ${nav()}
    </section>
    <section class="card"><h2>Srovnání</h2><div class="table-wrap"><table>
      <thead><tr><th>Oblast</th><th>Náš produkt</th><th>Roivenue</th><th>Stav</th></tr></thead>
      <tbody>${cmp.rows.map(row => `<tr><td><strong>${row.area}</strong></td><td>${row.ours}</td><td>${row.roivenue}</td><td>${statusBadge(row.status)}</td></tr>`).join('')}</tbody>
    </table></div></section>
    <section class="card"><h2>Závěr</h2><ul class="list">${cmp.summary.map(item => `<li>${item}</li>`).join('')}</ul></section>
  `;
}

loadDataLayer().then(data => {
  const page = document.body.dataset.page || 'home';
  if (page === 'channels') renderChannels(data);
  else if (page === 'audit') renderAudit(data);
  else if (page === 'management') renderRole(data, 'management', 'Management view');
  else if (page === 'marketing') renderRole(data, 'marketing', 'Marketing view');
  else if (page === 'finance') renderRole(data, 'finance', 'Finance view');
  else if (page === 'roivenue') renderRoivenue(data);
  else renderHome(data);
}).catch(err => {
  document.getElementById('app').innerHTML = `<section class="card"><h2>Failed to load data layer</h2><p>${err.message}</p></section>`;
});
