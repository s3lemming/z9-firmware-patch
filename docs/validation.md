# Validation and limitations — v15

## Frozen standalone output identity

| Output | Bytes | SHA-256 |
|---|---:|---|
| MAIN excluding module CRC | 81854203 | `3411b21ec875ba3326f9e0a4c6e1ecadc81a696d15b0e2af9f3b0ebe052801bc` |
| Full private container | 101877185 | `1885ee0660bee56e6d3a4d359d70b00f7fbeba932fc6c22f104eb20d76581fe4` |

These are standalone mark2 v15 outputs targeting original Z9 5.32, not the
integrated development 5.61 package. The public builder checks the exact original
module, authored-source hashes and final payload identity. Private packing and
independent readback preserve the other five modules. Original firmware and
private materials remain local; no generated firmware is published.

## Current evidence

| Layer | Result | Boundary |
|---|---|---|
| Actual ordinary-restart predicate | 576 ownership/state combinations, ASan/UBSan; no state mutation | Native kind0 qualification occurs upstream; this is not a scheduler simulation |
| Production gate on AArch64 | 8 synthetic cases, both paths; X0–X30, NZCV, SP alignment/restoration and displaced ADDS replay checked | User-mode instruction execution with a clobbering ABI stub; no Nikon firmware or camera guest |
| Existing synthetic suites | cold-menu16/38; cache2420 assertions; loop3000 cases; callback1000 requests; profile329; format29; tooling16 | Component results do not grant sustained native or hardware qualification |
| Standalone strict build/pack/readback | Frozen identity enforced, including after gate-generator extraction | Not installation or standalone hardware acceptance |
| Integrated c4 QEMU, 2026-11-12 | One fresh no-lens CH20/M1/250 run, two1s contacts, 34 JPEG/34 PCM; repeat press and released tail checked | Approximately65ms cadence; bad-baseline short-reuse window was not reproduced |
| User hardware feedback, 2026-11-12 | Current integrated c4 development5.61 CH20 sound reported normal | User report, not device readback or an exhaustive exposure/lens/long-term matrix; standalone v15 not installed |

The accepted integrated package SHA-256 is
`96a395f1f8f64da4d30468edf66fd5070551ee5f2e096a0ed28fe4cd9c714c85`,
with MAIN `c4fd921106add69148dcd16e96389dbc9b472e85074ffeb944a0da77e512ef44`.
It includes other projects and a heap/ready-anchor contract. Standalone v15 uses
its existing fixed BSS. The restart ownership predicate and native targets are
adapted here; whole firmware identities and installation acceptance are separate.

## Failure history and remaining limits

Earlier integrated development5.61 and the terminal-kind-family experiment still
had the user-reported CH20 symptom: normal interrupted prefixes at1/200, repeated
whole clips at1/250. The accepted c4 uses the ordinary kind0 restart gate and does
not include that kind-family extension. The passing old QEMU runs did not cover
the physical bad branch. See the [CH20 analysis](ch20-restart.zh-CN.md).

An earlier same-c4 QEMU attempt stopped at a native frontend failure; the later
fresh34-photo success does not erase it. Further official-stock/no-lens/native-A
control produced33 JPEG/33 PCM at1/250, with median intervals65.64/62.67ms. No
emulator repair, rated20fps or physical failure reproduction is claimed here.

Published PCM remains immutable until shutdown; at most20 contents plus scratch.
The64 callback registrations require original final-return retirement and idle
outputs, not only completion. All rates, all tones and lens combinations,
rapid Cxx/tail repress, full card/power-loss matrices and long-term hardware
remain outside this new acceptance. The v15 gate preserves Cxx/tail ownership.
Native A–E and all previously retained cache, menu and lifecycle limits apply.

[v14 validation](history/v14-validation.md) and [v13 validation](history/v13-validation.md)
remain historical. Their old mixed-shutter/recovery failures are not reclassified.
The [Z8 guide](z8-porting.zh-CN.md) requires separate target ABI and device evidence.
