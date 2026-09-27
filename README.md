# Bank Logo Catalog

One API for bank logos worldwide, growing country by country.

**Designed and maintained by [Amit Ayre](https://labs.amitayre.com).**

[Open the catalog explorer](https://feelfree82.github.io/bank-logo-catalog/)

The catalog helps an app match a bank name and load only the logo it needs. Developers do not need to bundle the full image library, create an account, or use an API key.

## Coverage

| Country | Records | Logo variants | Status |
| --- | ---: | --- | --- |
| India | 72 | icon and wordmark SVG | visual pairs evaluated; provenance review ongoing |
| USA | 693 | icon SVG and PNG | identity, current status, and provenance review ongoing |

Japan and Canada are planned next.

## Quick start

```js
const base = 'https://feelfree82.github.io/bank-logo-catalog/';
const id = 'in-hdfc-bank';

const bank = await fetch(
  new URL(`v1/institutions/${id}.json`, base)
).then(response => response.json());

const iconUrl = new URL(bank.logos.icon.svg, base);
```

If the institution ID is not known, fetch and cache the compact search index for the needed country:

```text
v1/countries/in/search-index.json
v1/countries/us/search-index.json
```

The index contains names, aliases, and IDs. It contains no images. After matching a name, request the individual institution record and then load its icon or wordmark URL.

The zero-dependency helper in [`sdk/logo-catalog.js`](sdk/logo-catalog.js) implements this flow.

## Public files

```text
docs/
  index.html
  v1/
    countries.json
    schema.json
    countries/{code}/institutions.json
    countries/{code}/search-index.json
    institutions/{id}.json
    assets/{country}/{id}/...
```

The site is a static, read-only catalog hosted on GitHub Pages. Logo URLs include a content revision so clients can cache them and receive a new URL after an update.

## Project status

This is a public beta. Records expose review status instead of implying that every identity, institution status, or asset provenance has been fully verified. Corrections are welcome.

This is an independent identification catalog. It is not affiliated with or endorsed by any listed institution. The MIT license applies to the project's original software and documentation. It does not grant rights in third-party names, logos, trademarks, or artwork. See [`ASSETS_AND_MARKS.md`](ASSETS_AND_MARKS.md).

For a private correction, removal request, or rights-holder claim, email [banklogos@amitayre.com](mailto:banklogos@amitayre.com).

## Maintenance

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for stable IDs, updates, new countries, corrections, and removals. Run the catalog validator before publishing a change:

```sh
python3 scripts/validate_release.py --root docs
```
