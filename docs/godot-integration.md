# Godot calendar integration

Feed URL: `https://raw.githubusercontent.com/KadeasL/plakoro-catalog/main/catalog/releases.json`

Schema: `plakoro-calendar-v1`, `catalog_version`, `updated_at`, `releases`.

The Godot calendar already supports HTTPS JSON updates with preview and confirmation. Configure the feed URL in calendar settings, or apply the integration patch based on v1.6.0 Calendar RX Combined.

Currently the online catalog has zero releases: it is a safe initial placeholder, not a verified historical catalog. The program should retain its local seed and personal collection. The Python collector currently has no configured sources; GitHub Actions can run but will not discover releases until adapters or feeds are configured.

Never upload `owned.json` or `wishlist.json`. Review new release entries and image licensing before publishing.
