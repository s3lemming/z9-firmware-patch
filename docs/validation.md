# Validation and limitations — v12

## Frozen output identity

With the documented toolchain and exact original 5.32 input, the source recipe must reproduce:

| Output | Bytes | SHA-256 |
|---|---:|---|
| MAIN payload, excluding module CRC | 81853435 | `890193a3d77f55014d498ea007ef19d885efff3a4a0c220f15da27b9a6a1d77e` |
| Full private container | 101876417 | `eb75c697ace75c9cb92d16194862fa73e17ff9f658cc6e7c92c192bc4603dc9a` |

The independent parser checks module lengths, offsets, terminal version, module/container integrity and the unchanged other five modules. Eight deliberately damaged private-container variants were rejected. These checks do not establish camera acceptance. Generated binaries and private inputs are not published.

## Synthetic host tests

The actual C is compiled with explicit native-interface mocks. The v12 suites cover 2420 cache assertions, including 1001 selections across nine distinct contents, 400 invalid imports followed by success, busy retry, changed content at the same path, dual-card configuration, allocation failure and the 20-content limit. Loop tests cover 3000 padded-length/entry combinations, repeated lower starts, duplicate release and short clips without a tail. Callback tests execute 1000 requests without reset, with 64 registrations plus 936 reuses, delayed retirement guards and stale API returns.

ASan/UBSan cover these C fixtures. Existing synthetic profile I/O, WAV format/duration and packaging rejection suites remain included. Mocks do not certify timing, physical card removal, hardware races or native sustained use.

## Local native evidence

Four fresh Cxx runs used the same frozen candidate and unchanged QEMU model at 1/200. Actual DMA data, 50ms prefix repetition, one remainder, original stop and completion were checked. C30/C60/C120 recovered menus and live view; C15 sound passed while its historical JPEG ACK recovery check failed. Matching a historical predicate does not prove complete causal independence.

A partial ordinary run completed nine menu imports with three actual PCM contents, five independent S captures and a five-frame CL phase. Later CH capture stopped at an unsupported image-configuration register. It had 63 custom requests accepted and 62 completed; it did not qualify registration reuse past 64. Sixty-one complete NEF/JPEG pairs were independently checked; this is distinct from recovered phases or completed audio requests.

Unpatched original firmware and the candidate both reached PC `0x40c2001c`, writing `0x4000` to `0x150c0060` on the same QEMU. Thus this failure occurs without this patch and was treated as an existing model gap for candidate packaging. Long continuous capture remains unqualified. A separate 64-record read-only observation budget was also corrected in a new test snapshot; it is not a proof of the register fault's cause.

Seven candidate cold-start attempts were recorded: four Cxx runs, one ordinary failure, and two explicitly stopped zero-photo runs. This is **not five passed complete workflows**. The supplementary 93-photo recipe was not completed. Publishing or packaging does not turn failed or incomplete tests into passes.

## Still unqualified

- Native playback beyond 64 requests and long-term camera stability.
- Complete ordinary fast-shutter regression for this candidate.
- Repressing during an unfinished Cxx tail; native playback of clips at or below 50ms.
- Complete dual-card removal/power-loss scenarios and physical loudness calibration.
- Full C15 post-capture recovery and long continuous bursts on the current model.

The 20-distinct-content cache bound remains. Missing-card restore does not automatically retry; manual selection is available. Choosing a native sound with a missing card cannot rewrite the absent card's old configuration. QEMU GPIO-to-stop delays are not hardware latency claims. Earlier v11 physical feedback motivated these fixes, but it does not qualify v12.
