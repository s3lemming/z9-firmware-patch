# Validation record and limits

This record distinguishes historical QEMU evidence, tests of this extracted project, and physical-camera qualification. Counts are not combined across these categories.

## Extracted project, 2026-10-23

The published source build reproduces frozen v11 exactly:

| Output | Bytes | SHA-256 |
|---|---:|---|
| Payload | 81852857 | `9184a62c803d1d47ca18f11e244b848150287927c6db25ba00385e087a826f91` |
| MAIN module including CRC | 81852859 | `5e4ef5a8f9c1c5e8062a4a45a05ab482430832add21177c27fde452f86d19171` |
| Full container, built privately | 101875839 | `600e95262cdbddc60ea5b5e6d472a379f54ff0eb0b6e1fd5e0a1a9ca74275182` |

Independent readback checks all six module boundaries and CRCs, unchanged non-MAIN modules, full extent, terminal version and payload identity. The full container and private format material are not published.

The host suite compiles the actual C with explicit native-interface mocks. Tests include 883 baseline picker assertions, 34,000 picker operations / 45,646 cumulative assertions, 64,000 audio requests across 1,000 reset epochs, 1,000 expected callback-exhaustion rejections, 329 configuration I/O fault cases, 29 WAV format/duration cases, and 16 synthetic packaging/rejection cases. AddressSanitizer and UndefinedBehaviorSanitizer cover executable C fixture suites; the ctypes importer uses UndefinedBehaviorSanitizer. Epoch resets are simulated state resets, not camera cold boots. No vendor data is needed for these tests.

## Historical native QEMU evidence

- P318 v11: five fresh cold starts, 26 photographs, independent package readback and eight rejected malformed-container cases.
- P319 v11: ten fresh starts, 89 photographs; nine acceptance scenarios passed and C15 post-capture recovery failed.
- C15 audio transport/callback checks passed, but `jpeg_acknowledged` did not remain true for the required two virtual seconds. The subsequent two-menu roundtrip was not reached. This does not establish a menu deadlock or an audio root cause.
- Bounded C30/C60/C120 scenarios passed. Shared final JPEG state observations also appeared in passing scenarios; those observations alone do not establish causality. A paired original-firmware control was not run in that acceptance round.

The extraction round reuses historical native evidence only because the generated payload and container are byte-identical. It does not claim additional QEMU cold starts or photographs.

## Remaining qualification work

- v11 physical-camera acceptance and audible behavior; earlier user feedback concerned v08.
- Physical card removal, shutdown/power loss, volume/acoustic measurements and long-duration operation.
- Safe reclamation of immutable imports and callback slots; the 65th request currently has no established fallback.
- Clear error reporting for failed imports, missing files, unsupported formats and resource exhaustion.
- C15 post-capture recovery, tracked separately from sound transport.
- Exact per-frame Cxx sound synchronization, deferred by project scope.

Removing a card after a successful import may leave the cached sound usable until reboot. Restore is attempted lazily on the first audio request; failure does not continuously retry. A built-in selection made while the card is absent cannot overwrite the card's old enabled profile. These are current behaviors, not qualified hot-unplug guarantees.
