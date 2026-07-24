# Fork Release Sync

This fork packages `midea_ac_lan` and `midealocal` as two separate repositories
that must be released in order.

## What the HACS release does

The source `manifest.json` keeps a normal development pin:

```json
"requirements": ["midea-local==6.11.0"]
```

When `.github/workflows/release.yml` builds `midea_ac_lan.zip`, it rewrites that
requirement to a wheel hosted in the same GitHub owner's `midealocal` repo:

```text
midea-local @ https://github.com/<owner>/midealocal/releases/download/v6.11.0/midea_local-6.11.0-py3-none-any.whl
```

That means:

1. A fork of `midea_ac_lan` pulls the matching `midealocal` release from the same owner.
2. HACS installs the exact forked library wheel instead of PyPI.
3. The source tree stays usable for development without hardcoding a personal fork URL.

## Release order

1. Release `midealocal` first.
2. Confirm the GitHub release has wheel and sdist assets attached.
3. Release `midea_ac_lan` with the matching dependency version pinned in `manifest.json`.

If the `midealocal` asset does not exist yet, the `midea_ac_lan` release build
fails on purpose instead of publishing a broken HACS zip.
