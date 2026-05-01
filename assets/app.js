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
  const cls = trust === 'high' ? 'good' : trust === 'medium' || trust === 'medium_high' ? 'warn' : 'bad';
  return `<span class="badge ${cls}">${trust}</span>`;
}

function riskBadge(risk) {
  const cls = risk === 'low' ? 'good' : risk === 'medium' ? 'warn' : 'bad';
  return `<span class="badge ${cls}">${risk}</span>`;
}

function statusBadge(status) {
  const cls = status === 'strong' ? 'good' : status === 'close' ? 'warn' : 'bad';
  return `<span class="badge ${cls}">${status}</span>`;
}

function bucketBadge(bucket) {
  const map = {
    acquisition: 'good',
    retention: 'good',
    brand: 'warn',
    harvesting: 'warn',
    remarketing: 'bad',
    other: 'bad',
  };
  return `<span class="badge ${map[bucket] || 'bad'}">${bucket}</span>`;
}

function top(arr, n) {
  return (arr || []).slice(0, n);
}

function pageTitle(page) {
  const map = {
    home: 'Overview',
    management: 'Management',
    marketing: 'Marketing',
    finance: 'Finance',
    channels: 'Channels',
    audit: 'Audit',
    roivenue: 'Vs. Roivenue',
  };
  return map[page] || 'Overview';
}

function nav(current) {
  const items = [
    ['home', './index.html', 'Overview'],
    ['management', './management.html', 'Management'],
    ['marketing', './marketing.html', 'Marketing'],
    ['finance', './finance.html', 'Finance'],
    ['channels', './channels.html', 'Channels'],
    ['audit', './audit-workspace.html', 'Audit'],
    ['roivenue', './compare-roivenue.html', 'Vs. Roivenue'],
  ];

  return `
    <div class="topbar">
      <div class="brand">
        <div class="brand-mark">DP</div>
        <div>
          <div class="eyebrow">Diamond Plus Revenue Intelligence</div>
          <div class="brand-sub">${pageTitle(current)}</div>
        </div>
      </div>
      <div class="nav">${items.map(([key, href, label]) => `<a class="${key === current ? 'active' : ''}" href="${href}">${label}</a>`).join('')}</div>
    </div>
  `;
}

function metricCard(label, value, sub = '', tone = '') {
  return `
    <div class="metric-card">
      <div class="metric-label">${label}</div>
      <div class="metric-value ${tone}">${value}</div>
      <div class="metric-sub">${sub}</div>
    </div>
  `;
}

function section(title, body, aside = '') {
  return `
    <section class="panel section-block">
      <div class="section-header">
        <h2>${title}</h2>
        ${aside ? `<div class="section-aside">${aside}</div>` : ''}
      </div>
      ${body}
    </section>
  `;
}

function renderHome(data) {
  const ex = data.executive;
  const customer = data.customerTruth;
  const measurement = data.measurement.truth;
  const ch = data.channelIntelligence;
  const mt = data.marketingTruth;
  const netto = data.nettoContribution;
  const plan = data.actionPlan;
  const ga4 = top(data.measurement.ga4Channels, 6);

  document.getElementById('app').innerHTML = `
    ${nav('home')}

    <section class="hero-shell">
      <div class="hero-main panel">
        <div class="eyebrow">${data.productStage.name}</div>
        <h1>Revenue operating view</h1>
        <p class="hero-copy">Jedna obrazovka pro business reality, customer truth, channel trust a nejbližší rozhodnutí.</p>
        <div class="metric-grid six">
          ${metricCard('Observed revenue', money(ex.observedRevenue.value), data.focus.label)}
          ${metricCard('After marketing', money(ex.grossMarginAfterMarketing.value), 'finance reference month')}
          ${metricCard('Net cash', money(ex.netCashPosition.value), 'current position')}
          ${metricCard('Returning share YTD', pct(customer.estimatedNewVsReturning.returningRevenueSharePct), 'measured customer truth', 'warn')}
          ${metricCard('Blended ROAS', num(ex.blendedRoas.value), 'observed revenue / paid spend')}
          ${metricCard('Measurement confidence', ex.measurementConfidence.label, 'current reporting confidence', 'warn')}
        </div>
      </div>
      <div class="hero-side panel">
        <div class="eyebrow">Current read</div>
        <ul class="clean-list emphasis-list">
          <li>${data.finalTruthEngine.whatIsTrulyKnown[0]}</li>
          <li>${customer.estimatedNewVsReturning.label}</li>
          <li>${data.finalTruthEngine.whatIsEstimated[0]}</li>
        </ul>
      </div>
    </section>

    <div class="strip-grid">
      <div class="strip panel"><span>Business truth</span><strong>${money(data.businessTruth.financePreviousMonth.afterMarketing)}</strong><small>after marketing</small></div>
      <div class="strip panel"><span>Customer truth</span><strong>${pct(customer.estimatedNewVsReturning.returningRevenueSharePct)}</strong><small>returning revenue share YTD</small></div>
      <div class="strip panel"><span>Measurement truth</span><strong>${pct(measurement.reconciliation.unassignedRevenueSharePctOfFocusObserved)}</strong><small>unassigned share</small></div>
      <div class="strip panel"><span>Netto contribution</span><strong>${money(netto.ytdEstimated.estimatedAfterMarketing)}</strong><small>estimated after marketing YTD</small></div>
    </div>

    <div class="two-col">
      ${section('Channel trust', `
        <div class="table-wrap"><table>
          <thead><tr><th>Channel</th><th>Claim revenue</th><th>Observed revenue</th><th>Observed ROAS</th><th>Trust</th></tr></thead>
          <tbody>${ch.rows.map(row => `<tr><td><strong>${row.channel}</strong><div class="muted small-row">${row.primaryIssue}</div></td><td>${money(row.platformRevenuePreviousMonth)}</td><td>${money(row.ga4ObservedRevenue)}</td><td>${num(row.ga4ObservedRoas)}</td><td>${trustBadge(row.trustLabel)}</td></tr>`).join('')}</tbody>
        </table></div>
      `, '<span>claim vs observed</span>')}

      ${section('Next actions', `
        <ol class="clean-list ordered-list">${plan.now.map(item => `<li>${item}</li>`).join('')}</ol>
        <div class="divider"></div>
        <div class="mini-caption">Next 2 to 4 weeks</div>
        <ul class="clean-list">${plan.next_2_to_4_weeks.map(item => `<li>${item}</li>`).join('')}</ul>
      `, '<span>priority queue</span>')}
    </div>

    <div class="three-col">
      ${section('Paid mix', `
        <div class="table-wrap compact-table"><table>
          <thead><tr><th>Bucket</th><th>Spend</th><th>Revenue</th></tr></thead>
          <tbody>${top(mt.paidMix.bucketSummaryPreviousMonth, 5).map(row => `<tr><td>${bucketBadge(row.bucket)}</td><td>${money(row.spend)}</td><td>${money(row.revenue)}</td></tr>`).join('')}</tbody>
        </table></div>
      `)}
      ${section('Search taxonomy', `
        <div class="table-wrap compact-table"><table>
          <thead><tr><th>Type</th><th>Spend</th><th>ROAS</th></tr></thead>
          <tbody>${top(mt.searchTaxonomy.summaryPreviousMonth, 5).map(row => `<tr><td>${row.type}</td><td>${money(row.spend)}</td><td>${num(row.roas)}</td></tr>`).join('')}</tbody>
        </table></div>
      `)}
      ${section('Observed channels', `
        <div class="table-wrap compact-table"><table>
          <thead><tr><th>Channel</th><th>Revenue</th><th>Sessions</th></tr></thead>
          <tbody>${ga4.map(row => `<tr><td>${row.channel}</td><td>${money(row.purchaseRevenue)}</td><td>${num(row.sessions)}</td></tr>`).join('')}</tbody>
        </table></div>
      `)}
    </div>

    ${section('Netto contribution', `
      <div class="metric-grid four">
        ${metricCard('Net revenue after cancellations', money(netto.ytdEstimated.netRevenueAfterCancellations), 'YTD estimate')}
        ${metricCard('Estimated gross margin', money(netto.ytdEstimated.estimatedGrossMargin), 'ratio model')}
        ${metricCard('Estimated after marketing', money(netto.ytdEstimated.estimatedAfterMarketing), 'ratio model')}
        ${metricCard('Estimated profit contribution', money(netto.ytdEstimated.estimatedProfitContribution), 'ratio model')}
      </div>
      <ul class="clean-list muted-list">${netto.warnings.map(item => `<li>${item}</li>`).join('')}</ul>
    `, '<span>ratio-based first layer</span>')}
  `;
}

function renderRole(data, key, title) {
  const role = data.roleViews[key];
  const netto = data.nettoContribution;
  const plan = data.actionPlan;

  document.getElementById('app').innerHTML = `
    ${nav(key)}
    <section class="hero-shell single">
      <div class="hero-main panel">
        <div class="eyebrow">${title}</div>
        <h1>${role.headline}</h1>
        <div class="two-col top-gap-24">
          <div>
            <div class="mini-caption">Focus</div>
            <ul class="clean-list emphasis-list">${role.focus.map(item => `<li>${item}</li>`).join('')}</ul>
          </div>
          <div>
            <div class="mini-caption">Questions</div>
            <ul class="clean-list">${role.questions.map(item => `<li>${item}</li>`).join('')}</ul>
          </div>
        </div>
      </div>
    </section>
    <div class="two-col">
      ${section('Immediate actions', `<ol class="clean-list ordered-list">${plan.now.map(item => `<li>${item}</li>`).join('')}</ol>`)}
      ${section('Netto contribution status', `<p class="body-copy">${netto.readiness.label}</p><ul class="clean-list muted-list">${netto.warnings.map(item => `<li>${item}</li>`).join('')}</ul>`)}
    </div>
  `;
}

function renderChannels(data) {
  const mt = data.marketingTruth;
  const ch = data.channelIntelligence;

  document.getElementById('app').innerHTML = `
    ${nav('channels')}
    <section class="hero-shell single">
      <div class="hero-main panel">
        <div class="eyebrow">Channel intelligence</div>
        <h1>Channel evaluation</h1>
        <p class="hero-copy">Nejdřív trust, potom rozpad spendu, až potom detail kampaní.</p>
      </div>
    </section>

    ${section('Claim vs observed', `
      <div class="table-wrap"><table>
        <thead><tr><th>Channel</th><th>Claim revenue</th><th>Observed revenue</th><th>Claim ROAS</th><th>Observed ROAS</th><th>Trust</th><th>Decision role</th></tr></thead>
        <tbody>${ch.rows.map(row => `<tr><td><strong>${row.channel}</strong></td><td>${money(row.platformRevenuePreviousMonth)}</td><td>${money(row.ga4ObservedRevenue)}</td><td>${num(row.platformRoasPreviousMonth)}</td><td>${num(row.ga4ObservedRoas)}</td><td>${trustBadge(row.trustLabel)}</td><td class="muted">${row.decisionRole}</td></tr>`).join('')}</tbody>
      </table></div>
    `)}

    <div class="two-col">
      ${section('Paid mix buckets', `
        <div class="table-wrap"><table>
          <thead><tr><th>Bucket</th><th>Spend</th><th>Revenue</th><th>ROAS</th><th>Campaigns</th></tr></thead>
          <tbody>${mt.paidMix.bucketSummaryPreviousMonth.map(row => `<tr><td>${bucketBadge(row.bucket)}</td><td>${money(row.spend)}</td><td>${money(row.revenue)}</td><td>${num(row.roas)}</td><td>${num(row.campaigns)}</td></tr>`).join('')}</tbody>
        </table></div>
      `)}
      ${section('Search taxonomy', `
        <div class="table-wrap"><table>
          <thead><tr><th>Type</th><th>Spend</th><th>Revenue</th><th>ROAS</th><th>Platforms</th></tr></thead>
          <tbody>${mt.searchTaxonomy.summaryPreviousMonth.map(row => `<tr><td>${row.type}</td><td>${money(row.spend)}</td><td>${money(row.revenue)}</td><td>${num(row.roas)}</td><td class="muted">${row.platforms.join(', ')}</td></tr>`).join('')}</tbody>
        </table></div>
      `)}
    </div>

    ${section('Top campaigns', `
      <div class="table-wrap"><table>
        <thead><tr><th>Platform</th><th>Campaign</th><th>Bucket</th><th>Spend</th><th>Revenue</th><th>ROAS</th></tr></thead>
        <tbody>${mt.topCampaigns.map(row => `<tr><td>${row.platform}</td><td>${row.name}</td><td>${bucketBadge(row.bucket)}</td><td>${money(row.spend)}</td><td>${money(row.revenue)}</td><td>${num(row.roas)}</td></tr>`).join('')}</tbody>
      </table></div>
    `)}
  `;
}

function renderAudit(data) {
  const rows = data.auditWorkspace.topCampaigns;

  document.getElementById('app').innerHTML = `
    ${nav('audit')}
    <section class="hero-shell single">
      <div class="hero-main panel">
        <div class="eyebrow">Audit</div>
        <h1>Campaign audit workspace</h1>
      </div>
    </section>

    ${section('Top campaigns by spend', `
      <div class="table-wrap"><table>
        <thead><tr><th>Platform</th><th>Campaign</th><th>Bucket</th><th>Spend</th><th>Revenue</th><th>ROAS</th><th>Status</th><th>Risk</th></tr></thead>
        <tbody>${rows.map(row => `<tr><td>${row.platform}</td><td>${row.name}</td><td>${bucketBadge(row.bucket)}</td><td>${money(row.spend)}</td><td>${money(row.revenue)}</td><td>${num(row.roas)}</td><td class="muted">${row.status || 'n/a'}</td><td>${riskBadge(row.risk)}</td></tr>`).join('')}</tbody>
      </table></div>
    `)}

    ${section('Recommended audit actions', `<ul class="clean-list">${data.auditWorkspace.actions.map(item => `<li>${item}</li>`).join('')}</ul>`)}
  `;
}

function renderRoivenue(data) {
  const cmp = data.roivenueComparison;

  document.getElementById('app').innerHTML = `
    ${nav('roivenue')}
    <section class="hero-shell single">
      <div class="hero-main panel">
        <div class="eyebrow">Comparison</div>
        <h1>Vs. Roivenue</h1>
      </div>
    </section>

    ${section('Comparison table', `
      <div class="table-wrap"><table>
        <thead><tr><th>Area</th><th>Our product</th><th>Roivenue</th><th>Status</th></tr></thead>
        <tbody>${cmp.rows.map(row => `<tr><td><strong>${row.area}</strong></td><td>${row.ours}</td><td>${row.roivenue}</td><td>${statusBadge(row.status)}</td></tr>`).join('')}</tbody>
      </table></div>
    `)}

    ${section('Summary', `<ul class="clean-list">${cmp.summary.map(item => `<li>${item}</li>`).join('')}</ul>`)}
  `;
}

loadDataLayer().then(data => {
  const page = document.body.dataset.page || 'home';
  if (page === 'channels') renderChannels(data);
  else if (page === 'audit') renderAudit(data);
  else if (page === 'management') renderRole(data, 'management', 'Management');
  else if (page === 'marketing') renderRole(data, 'marketing', 'Marketing');
  else if (page === 'finance') renderRole(data, 'finance', 'Finance');
  else if (page === 'roivenue') renderRoivenue(data);
  else renderHome(data);
}).catch(err => {
  document.getElementById('app').innerHTML = `${nav('home')}<section class="panel section-block"><h2>Failed to load data</h2><p>${err.message}</p></section>`;
});
