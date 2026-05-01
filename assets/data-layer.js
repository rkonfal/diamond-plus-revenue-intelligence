export async function loadDataLayer() {
  const manifestRes = await fetch('./data/manifest.json?v=live-cs-fix-4', { cache: 'no-store' });
  if (!manifestRes.ok) throw new Error('Nepodařilo se načíst manifest');
  const manifest = await manifestRes.json();
  const version = encodeURIComponent(manifest.generatedAt || 'live-cs-fix-4');

  const entries = Object.entries(manifest.datasets);
  const loaded = await Promise.all(entries.map(async ([key, file]) => {
    const res = await fetch(`./data/${file}?v=${version}`, { cache: 'no-store' });
    if (!res.ok) throw new Error(`Nepodařilo se načíst dataset: ${file}`);
    return [key, await res.json()];
  }));

  const datasets = Object.fromEntries(loaded);
  return {
    generatedAt: manifest.generatedAt,
    focus: manifest.focus,
    manifest,
    ...datasets,
  };
}
