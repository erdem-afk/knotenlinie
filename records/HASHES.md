# Record hashes after the public-release scrub

The frozen records in this folder are the project's pre-registration rules (`KURAL.md`, in Turkish)
and frozen selections (`SECIM.json`, `AGIRLIK.json`, `SON_KURULUM.json`, `OLCUM.json`, `TABANLAR.json`, `zemin2.json`).
For this release they were changed only by required scrubs: private traces (local paths, internal process names,
references to internal documents that are not published) and content outside this release's scope. No number that
a kept row depends on was changed.
Where a scrub changed a rule file whose SHA-256 is stored in a selection record, the stored hash was re-anchored
in the same change and the original value kept next to it with the suffix `_kayit` (provenance).

Notes that apply to every record:

- `tools/...` in a record is the earlier name of the package; in this repo it is `knotenlinie/...`.
- `$KNOTENLINIE_DATA/...` (data root) and `$KNOTENLINIE_RUNS/defter/...` (score ledgers) replace the original
  local data paths; JSON records store these paths relative to the data root.
- `[Yayın notu: ...]` marks a sentence added for this release; everything else is the original text.
- Some rules name an addendum file (`<ID>/EK.md`, `<ID>/EK-*.md`) as the place where attempts made after the
  results were seen are written as off-record work. Those addenda are not part of this release; by the rules
  they enter no verdict.
- GEAR1 is not part of this release; the long-term shape candidate U3 is switched off (its frozen weight was 0,
  so the selected Italy shape U0 is unchanged).

Unchanged (byte-identical to the frozen originals): `AB/SON_KURULUM.json`, `AD/SECIM.json`,
`AE/SON_KURULUM.json`, `AJ/SON_KURULUM.json`, `S/KURAL.md`.

| File | SHA-256 before | SHA-256 after | Change |
|---|---|---|---|
| `AA/KURAL.md` | `3d97433e339f280d32db99738780b90946535a9d0b79a9c123a56c349499befd` | `003772de0f25298f6d22a802a2d1fd7d8d3fa02ec93a040b8f4fd25798b54673` | scrubbed private path (ledger directory now `$KNOTENLINIE_RUNS/defter/U/`); removed references to unpublished internal documents; named the maintainer's workstation neutrally ("yerel makine") |
| `AA/SECIM.json` | `21d2821c47d45899351285a4b09ac86ceed09944f807b8d5246d97c6d28c6d75` | `9a9724cc55073e18bb579da0e2797bbde83ef7ea89dff90cb6b0b4de2947b260` | re-anchored `kural_SHA256` to the edited AA/KURAL.md; original kept as `kural_SHA256_kayit` |
| `AB/KURAL.md` | `f005da000c450025c6cd1d8067d34f399893f62ad93737588ccbab6509923b35` | `ce8de6436b9e1a4cd1b720b31a74d244e20a5e5a1cb2e926c6dc5e28f7028fef` | reworded two references to unpublished internal documents |
| `AB/SECIM.json` | `724f485a97acf294ac8f9390b1cdef569bc29fae00fb48e45a7514d9ed3b754e` | `a3e8c8e688c4595faa55cfdb8f2723ed3d09ae954aa4b91b86c99523bdc586cc` | re-anchored `kural_SHA256` to the edited AB/KURAL.md; original kept as `kural_SHA256_kayit` |
| `AD/KURAL.md` | `b3f73d281f78350d56b3961540d2f3bcee05c594361bc58528f503d434f42567` | `5df834ed1bdd004fde359bd4aa67056704f2b1b97256635aa46485b8c92c63d7` | removed content outside this release's scope (one sentence) |
| `AE/KURAL.md` | `eee084be459a93046df4b9436aa250474da5fdfc8c37008f68f70b638bed647e` | `d4971418e808f5662569ae2e7ac21a948e7c0a6a2e71ab917340e19f23131cf8` | removed content outside this release's scope (three sentences; one publication note added); scrubbed private path; removed a reference to an unpublished internal document; named the maintainer's workstation neutrally ("yerel makine") |
| `AE/SECIM.json` | `28201ee376dade7e7e255df0bdf8d1bf319a3aaf9cbc7bbd6130df26ad512381` | `c90d55b424016ba04fad3c96320d3e665c21414b455e62319a83fe02ffdb54e1` | scrubbed private path (`R_x_kaynak` now data-root-relative); re-anchored `kural_SHA256` to the edited AE/KURAL.md; original kept as `kural_SHA256_kayit` |
| `AG/KURAL.md` | `1e534c05fa8e2363856a40188d88b02e9a97cd20080f4d0fd3eadf745dfe988b` | `28fbb68181614ca89a784f1bf4cd2868798141555d1e2cf2f7b299ec910023c0` | removed references to unpublished internal documents and an internal experiment label; scrubbed private path; named the maintainer's workstation neutrally ("yerel makine") |
| `AH/KURAL.md` | `b78b674d2807ba8cc6a90968aaa8201174415742be6ddcfd709e6bc7fa365192` | `c88e29a3d27317bdef632bc4b975827e6450e8d2c10c45716112d560760b48ba` | removed content outside this release's scope (rows and clauses, including part of the selection sum and of Ek 1); removed an internal experiment label; one publication note on the selection |
| `AH/SECIM.json` | `ccc43076bf01c1e5132acc98d11df63692a9dd46aa179db46c11994814ca2018` | `fdf34ca0bd47c94028adf53c0bb66c9d69b6aabbd4d4a68aa7fe72854db9dd0b` | removed content outside this release's scope (one entry); `toplam_logL`, `en_iyi`, `bagli`, `z2_toplam` recomputed from the remaining entries; selected variant unchanged (GR-kapali); note in `yayin_notu` |
| `AJ/KURAL.md` | `875a2333f4be8bc79e3f8954d07624697e257e58404019c83c04d23e383a2bac` | `894170b87d715836469f5488bcc7dd7342fcf3692c031b7dcca6c16f82572c67` | scrubbed private path; removed references to unpublished internal documents |
| `AJ/SECIM.json` | `8341e901725511dfb664d64d44ea55f95d7075481c95e51fa692582338173cc5` | `6122d66868dd173e0c768def2f3952d20722eb83d2a6481b0d1112a5bf4c9709` | scrubbed private path (`R_x_kaynak`); re-anchored `kural_SHA256` to the edited AJ/KURAL.md; original kept as `kural_SHA256_kayit` |
| `C/zemin2.json` | `194aa105590652fdaba581c552db33ba2c3c747593a8e6746a1849b95cdeeb66` | `9660c3d29010ab1b0731fbdd10fe4052bacc86fcbcb5e55b0dcd322d56a8d9fc` | removed content outside this release's scope (one input specification); scrubbed private paths (now data-root-relative); loader renamed `tools.eepas.c2:t_model_yukle` → `knotenlinie.eepas.c2:t_model_yukle` (new package layout) |
| `H/TABANLAR.json` | `eb6dd14808f0546b872d8ceff6e67f22397f94a72d1e8e2e8dfbe0b82c41c0eb` | `6da24fbf9ec1861cbf5ae01bf1fb387115011dcc93994367ee7af7e3dae381ec` | removed content outside this release's scope (two base-model entries, one of which also carried an e-mail address); scrubbed private paths (now data-root-relative); removed an internal experiment label; the MPS04 unit note names the source file as "CSEP models.yml" instead of by an author name |
| `MC2/KURAL.md` | `c6e694ba70e344cf87c5280118c6f041f70d0dbdc89ddeb0e87897185173423f` | `1e79d0522c96fdc4bb4d7afe4c14d3316ef67a69eb10a7469990c7b627ffc6a9` | removed content outside this release's scope (one row); scrubbed private path; task label normalised to the record ID; removed a run-instruction reference and references to unpublished internal documents |
| `U/AGIRLIK.json` | `05df5ce047e25889737eb28c18626ceb83b765cc0435a999b1b35bf47b29780f` | `477a99ddebfb0414b55e07de2896a753835638ba103f0e006e02e70d104a6bac` | re-anchored `kural_SHA256` to the edited U/KURAL.md; original kept as `kural_SHA256_kayit` |
| `U/KURAL.md` | `d66c82245035d35bcd74515b20792508e73ea6e33ab11e8e8e8afcc5fe2b2822` | `5c87af8552be0bd28a8e6eccb3fa50d4ab17fbaafb83c0d730bb72099c3a6c10` | removed references to unpublished internal documents; named the maintainer's workstation neutrally ("yerel makine") |
| `W/KURAL.md` | `c60eaccdc678f28515c0ba800fd5b05ab27049f78fc6e206981073adac189955` | `04f7039767df2f4ea6466c028235e1f86b552d48d4b5d903a8d4f98fd1152615` | scrubbed private path; removed a reference to an unpublished design note |
| `W/SECIM.json` | `946442d5a3939d4b69d697ef3d542f7946a30fc6acac10afe509900ab24c538f` | `e04ce013f3e0d4aeb62ed89ef6141ebf7ec44e52a3328500346954fd98665c3d` | re-anchored `KURAL_SHA256` to the edited W/KURAL.md; original kept as `KURAL_SHA256_kayit` |
| `X/KURAL.md` | `e4bf3c978e90c490af39d98da50bed16192a8310e56d21403ffc54c4207410f5` | `98ade6e2670d2b69011c9579c18a822658efe5c4d442450fa68673212b5d8b1f` | scrubbed private paths; removed references to unpublished internal documents, an internal experiment label and an internal round label |
| `X/SECIM.json` | `4329dcaa3547fb6fe52db75390d87d992570f1a687b50acae4a4a747e1e86498` | `d94ad05bcfca14eca73c49730e93344741bfb3459df9f66b3c248822e4b3f8de` | scrubbed private paths (`parametreler`, `parametreler_olcum`, `gcmt` now data-root-relative); re-anchored `kural_sha256` to the edited X/KURAL.md; original kept as `kural_sha256_kayit` |
| `Y/KURAL.md` | `44a735a9606a0faecd905e335d4edf1b6a3d744c6feb25542508e44d97cf6e13` | `25ce3962a4a7a6bd3edd4e69a1bd98480597f664f3598b466207201d47391571` | scrubbed private path; removed an internal experiment label and a run instruction; named the maintainer's workstation neutrally ("yerel makine") |
| `Z/KURAL.md` | `e95ba5a85caedcf754cc95de05f0e0c6c022973fdcb2bbfbe0cd012bf8e46da7` | `72320429145ef76e19120adf5f9ab26161ef668ddaab7ec0a3d9e82a16693ce0` | removed content outside this release's scope (several rows); scrubbed private path; removed references to unpublished internal documents and an internal experiment label; publication note on the long-term shape candidate U3 (switched off, frozen weight 0, Italy shape U0 unchanged) |
| `Z/OLCUM.json` | `18f61d81010810aabcdb9054446dca72667c8233c2ffe018ef9dde2cd41e2d05` | `935ab2ea2401b2062c946a1d39bbf62079d9de16134e1e68119bf8f50d09b1bb` | removed content outside this release's scope (one entry); the selection (U0-10, U3 weight 0) is unchanged |
| `Z2/KURAL.md` | `ee6da13ae8e5bc30605d94795bc2bfc876ff1d937a81a7206f5bb754c74196af` | `4c96532afa707ecf8e0a71f9e7df88c89c93cab88fe30ec625711fe2fd42c401` | removed content outside this release's scope (one section and several clauses); scrubbed private path; removed a reference to an unpublished design note |

Stored rule hashes after re-anchoring (field = SHA-256 of the edited `KURAL.md`; `_kayit` = original):

- `AA/SECIM.json` `kural_SHA256`: `003772de0f25298f6d22a802a2d1fd7d8d3fa02ec93a040b8f4fd25798b54673` (was `3d97433e339f280d32db99738780b90946535a9d0b79a9c123a56c349499befd`)
- `AB/SECIM.json` `kural_SHA256`: `ce8de6436b9e1a4cd1b720b31a74d244e20a5e5a1cb2e926c6dc5e28f7028fef` (was `f005da000c450025c6cd1d8067d34f399893f62ad93737588ccbab6509923b35`)
- `AE/SECIM.json` `kural_SHA256`: `d4971418e808f5662569ae2e7ac21a948e7c0a6a2e71ab917340e19f23131cf8` (was `eee084be459a93046df4b9436aa250474da5fdfc8c37008f68f70b638bed647e`)
- `AJ/SECIM.json` `kural_SHA256`: `894170b87d715836469f5488bcc7dd7342fcf3692c031b7dcca6c16f82572c67` (was `875a2333f4be8bc79e3f8954d07624697e257e58404019c83c04d23e383a2bac`)
- `U/AGIRLIK.json` `kural_SHA256`: `5c87af8552be0bd28a8e6eccb3fa50d4ab17fbaafb83c0d730bb72099c3a6c10` (was `d66c82245035d35bcd74515b20792508e73ea6e33ab11e8e8e8afcc5fe2b2822`)
- `W/SECIM.json` `KURAL_SHA256`: `04f7039767df2f4ea6466c028235e1f86b552d48d4b5d903a8d4f98fd1152615` (was `c60eaccdc678f28515c0ba800fd5b05ab27049f78fc6e206981073adac189955`)
- `X/SECIM.json` `kural_sha256`: `98ade6e2670d2b69011c9579c18a822658efe5c4d442450fa68673212b5d8b1f` (was `e4bf3c978e90c490af39d98da50bed16192a8310e56d21403ffc54c4207410f5`)

Hashes of the selection records themselves are not stored anywhere else in the repo, so no further
re-anchoring is needed. Hash pins on data files (DISS 3.2.0, the common-ground delivery, the C2/C3 input
package) refer to the maintainer's downloaded files; a fresh setup re-anchors them by re-running the
common-ground step (see the data documentation).
