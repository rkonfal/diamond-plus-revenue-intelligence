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

function trustLabel(trust) {
  const map = {
    high: 'vysoká',
    medium_high: 'středně vysoká',
    medium: 'střední',
    low: 'nízká',
  };
  return map[trust] || trust;
}

function riskLabel(risk) {
  const map = {
    low: 'nízké',
    medium: 'střední',
    high: 'vysoké',
  };
  return map[risk] || risk;
}

function bucketLabel(bucket) {
  const map = {
    acquisition: 'akvizice',
    retention: 'retence',
    brand: 'brand',
    harvesting: 'sklízení poptávky',
    remarketing: 'remarketing',
    other: 'ostatní',
  };
  return map[bucket] || bucket;
}

function roleLabel(role) {
  const map = {
    acquisition_and_remarketing_mixed: 'smíšená akvizice a remarketing',
    demand_harvesting_plus_brand: 'sklízení poptávky a brand',
    harvesting_unknown: 'nejasné sklízení poptávky',
    retention: 'retence',
  };
  return map[role] || role;
}

function taxTypeLabel(type) {
  const map = {
    brand_search: 'brandové hledání',
    shopping_or_pmax: 'shopping nebo PMAX',
    competitor_search: 'konkurenční hledání',
    remarketing_search: 'remarketingové hledání',
    dsa_search: 'DSA hledání',
    generic_search: 'obecné hledání',
  };
  return map[type] || type;
}

function trustBadge(trust) {
  const cls = trust === 'high' ? 'good' : trust === 'medium' || trust === 'medium_high' ? 'warn' : 'bad';
  return `<span class="badge ${cls}">${trustLabel(trust)}</span>`;
}

function riskBadge(risk) {
  const cls = risk === 'low' ? 'good' : risk === 'medium' ? 'warn' : 'bad';
  return `<span class="badge ${cls}">${riskLabel(risk)}</span>`;
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
  return `<span class="badge ${map[bucket] || 'bad'}">${bucketLabel(bucket)}</span>`;
}

function top(arr, n) {
  return (arr || []).slice(0, n);
}

function pageTitle(page) {
  const map = {
    home: 'Přehled',
    management: 'Řízení',
    marketing: 'Marketing',
    finance: 'Finance',
    channels: 'Kanály',
    audit: 'Audit',
  };
  return map[page] || 'Přehled';
}

function nav(current) {
  const items = [
    ['home', './index.html', 'Přehled'],
    ['management', './management.html', 'Řízení'],
    ['marketing', './marketing.html', 'Marketing'],
    ['finance', './finance.html', 'Finance'],
    ['channels', './channels.html', 'Kanály'],
    ['audit', './audit-workspace.html', 'Audit'],
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
        <h1>Řídicí pohled na tržby</h1>
        <p class="hero-copy">Jedna obrazovka pro business realitu, customer truth, důvěru v kanály a nejbližší rozhodnutí.</p>
        <div class="metric-grid six">
          ${metricCard('Pozorované tržby', money(ex.observedRevenue.value), data.focus.label)}
          ${metricCard('Po marketingu', money(ex.grossMarginAfterMarketing.value), 'referenční finanční měsíc')}
          ${metricCard('Čistá hotovost', money(ex.netCashPosition.value), 'aktuální pozice')}
          ${metricCard('Podíl returning YTD', pct(customer.estimatedNewVsReturning.returningRevenueSharePct), 'měřená customer truth', 'warn')}
          ${metricCard('Blended ROAS', num(ex.blendedRoas.value), 'pozorované tržby / placený spend')}
          ${metricCard('Jistota měření', ex.measurementConfidence.label, 'aktuální jistota reportingu', 'warn')}
        </div>
      </div>
      <div class="hero-side panel">
        <div class="eyebrow">Aktuální čtení</div>
        <ul class="clean-list emphasis-list">
          <li>${data.finalTruthEngine.whatIsTrulyKnown[0]}</li>
          <li>${customer.estimatedNewVsReturning.label}</li>
          <li>${data.finalTruthEngine.whatIsEstimated[0]}</li>
        </ul>
      </div>
    </section>

    <div class="strip-grid">
      <div class="strip panel"><span>Byznysová pravda</span><strong>${money(data.businessTruth.financePreviousMonth.afterMarketing)}</strong><small>po marketingu</small></div>
      <div class="strip panel"><span>Zákaznická pravda</span><strong>${pct(customer.estimatedNewVsReturning.returningRevenueSharePct)}</strong><small>podíl returning revenue YTD</small></div>
      <div class="strip panel"><span>Pravda měření</span><strong>${pct(measurement.reconciliation.unassignedRevenueSharePctOfFocusObserved)}</strong><small>podíl unassigned</small></div>
      <div class="strip panel"><span>Netto přínos</span><strong>${money(netto.ytdEstimated.estimatedAfterMarketing)}</strong><small>odhad po marketingu YTD</small></div>
    </div>

    <div class="two-col">
      ${section('Důvěra v kanály', `
        <div class="table-wrap"><table>
          <thead><tr><th>Kanál</th><th>Platformní revenue</th><th>Pozorované tržby</th><th>Pozorovaný ROAS</th><th>Důvěra</th></tr></thead>
          <tbody>${ch.rows.map(row => `<tr><td><strong>${row.channel}</strong><div class="muted small-row">${row.primaryIssue}</div></td><td>${money(row.platformRevenuePreviousMonth)}</td><td>${money(row.ga4ObservedRevenue)}</td><td>${num(row.ga4ObservedRoas)}</td><td>${trustBadge(row.trustLabel)}</td></tr>`).join('')}</tbody>
        </table></div>
      `, '<span>platforma vs měření</span>')}

      ${section('Nejbližší kroky', `
        <ol class="clean-list ordered-list">${plan.now.map(item => `<li>${item}</li>`).join('')}</ol>
        <div class="divider"></div>
        <div class="mini-caption">Další 2 až 4 týdny</div>
        <ul class="clean-list">${plan.next_2_to_4_weeks.map(item => `<li>${item}</li>`).join('')}</ul>
      `, '<span>prioritní fronta</span>')}
    </div>

    <div class="three-col">
      ${section('Rozpad paid mixu', `
        <div class="table-wrap compact-table"><table>
          <thead><tr><th>Bucket</th><th>Spend</th><th>Revenue</th></tr></thead>
          <tbody>${top(mt.paidMix.bucketSummaryPreviousMonth, 5).map(row => `<tr><td>${bucketBadge(row.bucket)}</td><td>${money(row.spend)}</td><td>${money(row.revenue)}</td></tr>`).join('')}</tbody>
        </table></div>
      `)}
      ${section('Search taxonomie', `
        <div class="table-wrap compact-table"><table>
          <thead><tr><th>Typ</th><th>Spend</th><th>ROAS</th></tr></thead>
          <tbody>${top(mt.searchTaxonomy.summaryPreviousMonth, 5).map(row => `<tr><td>${taxTypeLabel(row.type)}</td><td>${money(row.spend)}</td><td>${num(row.roas)}</td></tr>`).join('')}</tbody>
        </table></div>
      `)}
      ${section('Pozorované kanály', `
        <div class="table-wrap compact-table"><table>
          <thead><tr><th>Kanál</th><th>Revenue</th><th>Sessions</th></tr></thead>
          <tbody>${ga4.map(row => `<tr><td>${row.channel}</td><td>${money(row.purchaseRevenue)}</td><td>${num(row.sessions)}</td></tr>`).join('')}</tbody>
        </table></div>
      `)}
    </div>

    ${section('Netto přínos', `
      <div class="metric-grid four">
        ${metricCard('Net revenue po stornech', money(netto.ytdEstimated.netRevenueAfterCancellations), 'YTD odhad')}
        ${metricCard('Odhad gross margin', money(netto.ytdEstimated.estimatedGrossMargin), 'model podle poměrů')}
        ${metricCard('Odhad po marketingu', money(netto.ytdEstimated.estimatedAfterMarketing), 'model podle poměrů')}
        ${metricCard('Odhad profit contribution', money(netto.ytdEstimated.estimatedProfitContribution), 'model podle poměrů')}
      </div>
      <ul class="clean-list muted-list">${netto.warnings.map(item => `<li>${item}</li>`).join('')}</ul>
    `, '<span>první vrstva založená na poměrech</span>')}
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
            <div class="mini-caption">Fokus</div>
            <ul class="clean-list emphasis-list">${role.focus.map(item => `<li>${item}</li>`).join('')}</ul>
          </div>
          <div>
            <div class="mini-caption">Otázky</div>
            <ul class="clean-list">${role.questions.map(item => `<li>${item}</li>`).join('')}</ul>
          </div>
        </div>
      </div>
    </section>
    <div class="two-col">
      ${section('Okamžité kroky', `<ol class="clean-list ordered-list">${plan.now.map(item => `<li>${item}</li>`).join('')}</ol>`)}
      ${section('Stav netto contribution', `<p class="body-copy">${netto.readiness.label}</p><ul class="clean-list muted-list">${netto.warnings.map(item => `<li>${item}</li>`).join('')}</ul>`)}
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
        <div class="eyebrow">Pohled na kanály</div>
        <h1>Vyhodnocení kanálů</h1>
        <p class="hero-copy">Nejdřív důvěra, potom rozpad spendu a až potom detail kampaní.</p>
      </div>
    </section>

    ${section('Platforma vs měření', `
      <div class="table-wrap"><table>
        <thead><tr><th>Kanál</th><th>Platformní revenue</th><th>Pozorované tržby</th><th>Platformní ROAS</th><th>Pozorovaný ROAS</th><th>Důvěra</th><th>Rozhodovací role</th></tr></thead>
        <tbody>${ch.rows.map(row => `<tr><td><strong>${row.channel}</strong></td><td>${money(row.platformRevenuePreviousMonth)}</td><td>${money(row.ga4ObservedRevenue)}</td><td>${num(row.platformRoasPreviousMonth)}</td><td>${num(row.ga4ObservedRoas)}</td><td>${trustBadge(row.trustLabel)}</td><td class="muted">${roleLabel(row.decisionRole)}</td></tr>`).join('')}</tbody>
      </table></div>
    `)}

    <div class="two-col">
      ${section('Buckety paid mixu', `
        <div class="table-wrap"><table>
          <thead><tr><th>Bucket</th><th>Spend</th><th>Revenue</th><th>ROAS</th><th>Kampaně</th></tr></thead>
          <tbody>${mt.paidMix.bucketSummaryPreviousMonth.map(row => `<tr><td>${bucketBadge(row.bucket)}</td><td>${money(row.spend)}</td><td>${money(row.revenue)}</td><td>${num(row.roas)}</td><td>${num(row.campaigns)}</td></tr>`).join('')}</tbody>
        </table></div>
      `)}
      ${section('Search taxonomie', `
        <div class="table-wrap"><table>
          <thead><tr><th>Typ</th><th>Spend</th><th>Revenue</th><th>ROAS</th><th>Platformy</th></tr></thead>
          <tbody>${mt.searchTaxonomy.summaryPreviousMonth.map(row => `<tr><td>${taxTypeLabel(row.type)}</td><td>${money(row.spend)}</td><td>${money(row.revenue)}</td><td>${num(row.roas)}</td><td class="muted">${row.platforms.join(', ')}</td></tr>`).join('')}</tbody>
        </table></div>
      `)}
    </div>

    ${section('Top kampaně', `
      <div class="table-wrap"><table>
        <thead><tr><th>Platforma</th><th>Kampaň</th><th>Bucket</th><th>Spend</th><th>Revenue</th><th>ROAS</th></tr></thead>
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
        <h1>Auditní workspace kampaní</h1>
      </div>
    </section>

    ${section('Top kampaně podle spendu', `
      <div class="table-wrap"><table>
        <thead><tr><th>Platforma</th><th>Kampaň</th><th>Bucket</th><th>Spend</th><th>Revenue</th><th>ROAS</th><th>Stav</th><th>Riziko</th></tr></thead>
        <tbody>${rows.map(row => `<tr><td>${row.platform}</td><td>${row.name}</td><td>${bucketBadge(row.bucket)}</td><td>${money(row.spend)}</td><td>${money(row.revenue)}</td><td>${num(row.roas)}</td><td class="muted">${row.status || 'n/a'}</td><td>${riskBadge(row.risk)}</td></tr>`).join('')}</tbody>
      </table></div>
    `)}

    ${section('Doporučené auditní kroky', `<ul class="clean-list">${data.auditWorkspace.actions.map(item => `<li>${item}</li>`).join('')}</ul>`)}
  `;
}

loadDataLayer().then(data => {
  const page = document.body.dataset.page || 'home';
  if (page === 'channels') renderChannels(data);
  else if (page === 'audit') renderAudit(data);
  else if (page === 'management') renderRole(data, 'management', 'Řízení');
  else if (page === 'marketing') renderRole(data, 'marketing', 'Marketing');
  else if (page === 'finance') renderRole(data, 'finance', 'Finance');
  else renderHome(data);
}).catch(err => {
  document.getElementById('app').innerHTML = `${nav('home')}<section class="panel section-block"><h2>Nepodařilo se načíst data</h2><p>${err.message}</p></section>`;
});
