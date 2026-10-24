# Validation and limitations — v13

## Frozen output identity

The documented toolchain and exact original 5.32 input must reproduce:

| Output | Bytes | SHA-256 |
|---|---:|---|
| MAIN payload, excluding module CRC | 81853483 | `7992247104f1d9c3904c501351ab853b1c4d4eac5d7c631d820f47fe0702537b` |
| Full private container | 101876465 | `279d61749d343ce10f39d09e83e72e3efb139a366da26627cd22cf7448be5b3c` |

The independent parser checks lengths, offsets, terminal version, module/container integrity and the unchanged other five modules. Eight damaged private-container variants were rejected. Local byte identity is not camera acceptance. No binaries or private inputs are published. [v12 validation](history/v12-validation.md) is retained as historical evidence, not relabeled as v13.

## Synthetic host tests

Actual authored C is compiled with explicit native-interface mocks and ASan/UBSan. Cache coverage includes 2420 assertions, 1001 selections across nine contents, 400 invalid-import recoveries, busy retry, content changes, dual-card commits, allocation failure and the 20-content bound. Loop coverage includes 3000 padded-length/entry combinations, C15's 66ms budget invariant, mode-dependent 50/40ms prefixes, repeated lower starts, duplicate release and one finite tail. Callback coverage includes 1000 requests without reset, 64 registrations plus 936 reuses, delayed retirement and stale API-return guards. Profile I/O, format/duration and synthetic tooling rejection suites remain included.

These fixtures do not certify physical timing, hardware races, card removal or native sustained use. Short Cxx clips are covered synthetically, not newly qualified on a camera.

## Local native evidence

| Scope | Measured result | Boundary |
|---|---|---|
| Five main Cxx audio runs with the final payload | C15 loop medians 66.996/66.991ms; C30/C60/C120 about 40.011ms; actual PCM, stop and one remainder checked | C15's full menu/live-view recovery still failed |
| One fixed 1/200 ordinary workflow | 20 photos: native before/after, five independent custom S presses, CL1 three photos, CL5 five, CH10 five; 18 custom requests accepted/completed with current-source PCM/clock consumption | One complete workflow, not five successful boots |
| Ordinary speed | CL1/CL5/CH10 median 995.653/203.004/103.983ms, within 25%; last burst clip complete, original sound restored, final menus/live view recovered | Only these configured speeds; not all-rate or acoustic qualification |
| Earlier slow phases | CL1/CL5/CH10 median 996.626/204.515/103.774ms, within 25%; completed phase content/audio checked | Full mixed-shutter recipe did not finish |

Three distinct audio choices were imported through native menus in the fixed-fast run. The final 1.366s clip crossed the finite audio-block boundary. Every custom request had current-source consumption, even where a later photo interrupted the prior clip. Saved incomplete output blocks are not exact acoustic-cut measurements. Both 160-byte configuration banks had valid CRCs and the latest profile disabled custom sound after native restoration.

Five ordinary fresh attempts had matching model/boot-loader, ELF, final payload and RAW fingerprints, but four failed and one completed. Across the development stages there were 13 actual cold-start attempts, including one earlier different payload; two prelaunch refusals were not cold starts. Five main final-payload Cxx runs passed their audio scope. These counts do not imply five full business passes, long-run qualification or native request reuse beyond 64.

## Retained failures

Earlier mixed-shutter recipes stopped when desired 1/200 remained applied 1/40 with parameter pending; restoring a real half press did not resolve it. A separate host-menu guard failure stopped before the shutter adjustment. Correcting that guard does not establish a firmware fix. The later fixed-fast success does not solve the mixed-shutter failure. C15 menu/live-view recovery also remains incomplete; causal independence from this patch is unproved.

v12 separately recorded an unsupported-MMIO failure in both unpatched and patched firmware on the same model. That original-firmware comparison is evidence for that specific gap; it does not automatically explain v13's parameter-pending or C15 recovery failures. QEMU was unchanged for this release.

## Still unqualified

- Native sustained playback beyond 64 requests and long-term camera stability.
- All CL/CH rates, exact 1/50 fast/slow boundary and the full mixed-shutter recipe.
- Short Cxx clips and repressing during an unfinished tail on native hardware.
- Complete dual-card removal/power-loss scenarios and physical loudness calibration.
- Full C15 recovery and five completed business cold starts.
- Camera installation/acceptance of v13; earlier hardware feedback does not qualify this version.

The 20-content cache bound remains; published PCM is not freed. Missing-card restore does not automatically retry. Choosing native sound with an absent card cannot rewrite its old profile. QEMU GPIO-to-stop delays are not hardware latency claims. Publishing source or rebuilding exact bytes adds no device qualification.
