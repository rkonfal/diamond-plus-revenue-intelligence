export async function loadDataLayer() {
  const manifestRes = await fetch('./data/manifest.json');
  if (!manifestRes.ok) throw new Error('Nepodařilo se načíst manifest');
  const manifest = await manifestRes.json();

  const entries = Object.entries(manifest.datasets);
  const loaded = await Promise.all(entries.map(async ([key, file]) => {
    const res = await fetch(`./data/${file}`);
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
