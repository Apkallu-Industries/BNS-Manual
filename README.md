# BNS-Manual

The public pages behind the QR marks on BlackNet Systems (BNS) parts, at the exact addresses the marks encode:

- shared library parts: `/parts/<P/N>/`
- B-3 / B3-A parts: `/b3/parts/<P/N>/`
- B-3 / B3-A cockpit panels: `/b3/panels/<code>/`

Site: https://apkallu-industries.github.io/BNS-Manual/

Rebuild (from `G:\Dev\BNS-Manual`) after the library register or the QR tables change:

    python build.py --register ../BNS-lib-wt-horsemen/Docs/part_number_register.json \
        --scan ../BNS-lib-wt-horsemen/Library/Data/Branding/item_qr.json \
        --scan ../BNS-lib-wt-horsemen/Tools/b3spirit/manual/b3_qr.json --out docs

Only catalogue fields are published (P/N, name, nomenclature, category, status, dash numbers, where-used, programme).
Provenance and source references are never published. The B-2 was retired by the owner on 2026-10-17: no B-2 pages,
names or where-used rows are published.

The marks encode this site since 2026-10-18 (library `Tools/make_item_qr.py`, `Tools/b3spirit/manual/make_b3_qr.py`;
QR version 5, 37 modules). The earlier placeholder base was `https://manual.blacknet.example`.
