# BNS-Manual

The public pages behind the QR marks on BlackNet Systems (BNS) parts: one page per part (`/<airframe>/parts/<P/N>/`)
and per cockpit panel (`/<airframe>/panels/<code>/`), at the same paths the marks already encode.

Site: https://apkallu-industries.github.io/BNS-Manual/

Rebuild (from `G:\Dev\BNS-Manual`):

    python build.py --register ../BNS-lib-wt-horsemen/Docs/part_number_register.json \
        --scan ../BNS-lib-wt-horsemen/Library/Data/Branding --scan ../BNS-lib-wt-horsemen/Tools/b3spirit/manual \
        --scan ../B-2-Spirit-main --out docs

Only catalogue fields are published (P/N, name, nomenclature, category, status, dash numbers, where-used, programme).
Provenance and source references are never published.

**Not live for scans yet:** the marks still encode the placeholder base `https://manual.blacknet.example`. Switching
the shared base to this site (library `item_qr.json`, `Tools/b3spirit/manual/manual_url.json`, the B-2 manual base)
and re-issuing the marks is a separate, coordinated library change.
