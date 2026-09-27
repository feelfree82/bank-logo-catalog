# Stability policy

`https://banklogos.amitayre.com/` is the permanent public endpoint for the Bank Logo Catalog.

## Compatibility promise

- Published paths under `v1/` keep their current meaning.
- Institution IDs are stable and are never reassigned to a different institution.
- Adding countries, institutions, aliases, or optional fields is backward compatible.
- Corrections may update names, status, metadata, and artwork while preserving the institution ID.
- Removed or merged institutions remain addressable when practical and expose their status or successor.
- A breaking schema or path change will use a new top-level version such as `v2/`.

## Caching

Search indexes and institution records may be cached and refreshed periodically. Asset URLs include a content revision. Apps can cache those assets for a long time because changed artwork receives a different URL.

## Hosting

GitHub is the canonical source and current static host. The branded domain separates the public API address from the hosting provider, so hosting can move without requiring developers to update their apps. Teams that need their own service guarantees may mirror the published `docs/` directory while preserving its paths.

## Availability

The public service is a best-effort open beta with no uptime guarantee. Consumers should cache successful responses and show an initials or neutral fallback if an image cannot be loaded.
