/**
 * Tiny browser/Node client for the static Bank Logo Catalog.
 * It bundles no institution data or logo files.
 */
export class BankLogoCatalog {
  constructor(baseUrl, fetchImpl = globalThis.fetch) {
    if (!baseUrl) throw new TypeError('baseUrl is required');
    if (!fetchImpl) throw new TypeError('fetch is required');
    this.baseUrl = new URL(baseUrl.endsWith('/') ? baseUrl : `${baseUrl}/`);
    this.fetch = fetchImpl;
    this.indexes = new Map();
  }

  url(path) {
    return new URL(path.replace(/^\/+/, ''), this.baseUrl);
  }

  async json(path) {
    const response = await this.fetch(this.url(path));
    if (!response.ok) throw new Error(`Catalog request failed with ${response.status}`);
    return response.json();
  }

  async getInstitution(id) {
    return this.json(`v1/institutions/${encodeURIComponent(id)}.json`);
  }

  async loadSearchIndex(country) {
    const code = country.toLowerCase();
    if (!this.indexes.has(code)) {
      this.indexes.set(code, this.json(`v1/countries/${encodeURIComponent(code)}/search-index.json`));
    }
    return this.indexes.get(code);
  }

  async search(country, query, limit = 10) {
    const term = normalize(query);
    if (!term) return [];
    const index = await this.loadSearchIndex(country);
    return index.institutions
      .map(institution => {
        const names = [institution.name, ...(institution.aliases || [])].map(normalize);
        const rank = names.includes(term) ? 0 : names.some(name => name.startsWith(term)) ? 1 : names.some(name => name.includes(term)) ? 2 : 99;
        return { institution, rank };
      })
      .filter(match => match.rank < 99)
      .sort((a, b) => a.rank - b.rank || a.institution.name.length - b.institution.name.length || a.institution.name.localeCompare(b.institution.name))
      .slice(0, Math.max(1, Math.min(limit, 50)))
      .map(match => match.institution);
  }

  logoUrl(institution, variant = 'icon', format = 'svg') {
    const path = institution.logos?.[variant]?.[format];
    return path ? this.url(path) : null;
  }
}

function normalize(value) {
  return String(value)
    .toLocaleLowerCase()
    .normalize('NFKD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '');
}
