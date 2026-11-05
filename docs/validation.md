# Validation and limitations — v14

## Frozen standalone output identity

| Output | Bytes | SHA-256 |
|---|---:|---|
| MAIN excluding module CRC | 81853963 | `c8c633ee6afb63bf776fa6c6f7b58b35deada58ef2b7e55790f2b12e1e5d0e01` |
| Full private container | 101876945 | `6dd183e3de23f616d533a1ecf0c2e325cb67715e6a3def11bd65aee0e76a9734` |

Strict source/input checks, compilation, packing and independent readback passed
locally with the documented toolchain. The other five modules remain original.
No firmware or private inputs are published. Identity enrollment was a separate
private preparation step; the final public builder always enforces frozen input,
source and output hashes. These output identities differ from the integrated
v39 package. [v13 validation](history/v13-validation.md) remains historical.

## Current evidence

| Layer | Result | Boundary |
|---|---|---|
| Standalone actual picker C | 16 groups/38 assertions with ASan/UBSan | Original file/UI/allocation functions are explicit mocks |
| Existing synthetic suites | cache2420 assertions, loop3000 cases, callback1000 requests, profile329 cases, format29, tooling16 | Not native sustained-use or device qualification |
| Integrated v39 QEMU | Fresh-process cold parent CUS/current filename, repeated entry, native A/custom switch and post-photo menu passed | One final complete workflow; intermediate failed navigation attempts remain failures |
| Integrated actual photo/audio | One C15 JPEG fully decoded; 9600B prefix and 166080B tail, successful callbacks and completed DMA bytes match source | Not photo-rate, acoustic or all-mode stability qualification |
| User hardware feedback, 2026-11-05 | Integrated v39 audio menu correct after restart | No claimed standalone v14 installation, arbitrary power-loss matrix or long-term run |

The original failure was absent menu-entry restore plus missing filename-model
reconstruction. The new parent callback reconciles confirmed state before
native values refresh. Child marking/focus fixes the remaining stale A/hidden
filename symptom. Tests cover first and direct child entry, audio-first restore,
repeat/no-write behavior, explicit native selection, invalid/disabled CFG, absent
WAV/card, dual-card ambiguity, card2 only, busy deferral and selection beyond20.
Renderer I/O remains forbidden. The additional integrated runtime-ready guard
is tested privately with its own anchor, not transplanted into this fixed-BSS
standalone build.

## Limits retained

Published PCM is immutable and retained until shutdown; at most20 distinct
contents plus scratch. Callback reuse needs native final-return retirement and
clear pending states; completion alone is insufficient and does not free PCM.
Missing-card restore does not automatically retry. An absent card cannot have
its old profile disabled. Full card removal/power-loss cases, all CL/CH rates,
short/repressed Cxx hardware behavior, native sustained use beyond64 requests
and long-term stability remain outside the new acceptance scope.

Historical v13 mixed-shutter/recovery failures remain in its evidence; the
bounded integrated C15 success does not rewrite those old results. QEMU emulation,
RAW capture/retouch and Z8 firmware are not implemented by this repository.
See the [Z8 learning/porting guide](z8-porting.zh-CN.md) for interfaces that need
new target-version evidence.
