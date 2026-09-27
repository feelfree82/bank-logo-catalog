# Contributing and maintenance

This is a public beta. Keep review status explicit and do not present unresolved identity, institution status, or provenance as verified.

## Updating one institution

1. Verify the change against an official institution source where possible and record the URL and review date in source metadata.
2. Update the relevant source artwork and export only the changed SVG and PNG. Preserve original exports.
3. Keep the country-prefixed stable project ID for the same institution. Add former names to `aliases`; do not reassign an existing ID.
4. Regenerate `logo_revision` from file content. Add the revision query to catalog logo URLs while keeping the asset path stable.
5. Review the formats, run the inventory, security, and catalog checks, compare the rendered variants, and document the change in `CHANGELOG.md`.
6. After merging the reviewed change, verify the live JSON, SVG, PNG, content types, and a browser fetch from another origin.

Apps that copy logo files must ship their own update. A catalog refresh can expose a new revision URL; it cannot promise immediate cache invalidation.

## Adding a country

1. Keep the supplied source folder read-only and record its provenance.
2. Define the country's expected logo variants and pair files before import.
3. Normalize display names while preserving supplied or former names as aliases.
4. Give every record an ISO country code and a country-prefixed stable ID.
5. Generate a full country catalog, compact search index, and individual records.
6. Hold incomplete, historical, inactive, or uncertain entries for explicit review.

## Correction or removal

Send private correction, removal, or rights-holder requests to [banklogos@amitayre.com](mailto:banklogos@amitayre.com). Identify affected IDs, correct or remove the specific current records and files, publish, and verify the live URLs. Record when the current URL stopped serving the asset and inform the requester. Repository history, forks, downloads, screenshots, and caches can retain older copies; do not promise erasure. A formal demand or lawsuit threat needs qualified legal advice.
