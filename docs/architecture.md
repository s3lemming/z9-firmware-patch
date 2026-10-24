# Implementation

The camera continues to run its original firmware. Newly authored C integrates a file picker, bounded WAV importer, persistent profile and audio adapter at recovered interfaces. This is targeted binary integration, not a source rebuild of Nikon firmware.

| Component | Responsibility |
|---|---|
| `picker.c` | CUSTOM_SOUND directory enumeration, bounded menu rows, original Type A–E selection, CUS label, import publication and lazy restore |
| `mark2_import.c` | Bounded RIFF parsing, exact PCM geometry, frame/duration limits and padding to a 1 ms / 192-byte audio quantum |
| `mark2_native_file.c` | Recovered original file interface bridge |
| `profile.c`, `profile_native.c` | Two 160-byte configuration banks, CRC, sequence selection and write/readback checks |
| `adapter.c` | Bind cached PCM into the original playback path, immutable PCM ownership, retired callback reuse and Cxx loop/tail |
| `runtime.c` | Minimal freestanding runtime support |
| `builder.py` | Verified input, compilation, local trampoline/resource generation and minimal integration edits |
| `container.py`, `readback.py` | Separate container construction and verification implementations |

Fast and slow shutter paths retain their original event phases. In S/CL/CH each actual photo request restarts the selected whole PCM through the original stop/wait/restart path, without a queue. The final clip can finish. Configured speed affects request spacing; it does not select a fixed Cxx prefix.

Cxx starts an infinite native loop over min(50ms, padded length) in C15 and min(40ms, padded length) in C30/C60/C120. After actual loop completion, original stop completion and pending-state clearance, it submits one finite remainder. C15's nonzero cycle budget is preserved and adjusted by `50 - prefix_bytes/192`; the original resource consumer supplies the remaining wait. Other Cxx use their original zero budget. Short other-Cxx clips loop their full length, not an artificially padded 40ms cycle. The downstream image-frame call remains original. This is a hold/release contract, not one sound per photograph.

The v13 authored-code delta is confined to Cxx initialization. Code growth relocates 15 existing hook/pointer targets by 48 bytes without changing the 27 integration sites, state/BSS capacities or import/profile/callback logic. See [changes](../CHANGELOG.md).

Native addresses, field offsets, type signatures and expected structural values describe recovered interfaces. They are version-specific. The original instructions replayed by hooks, original menu rows, and original resources are read from the user's hash-checked module at build time. They are not embedded in the source tree. Generated assembly and disassembly are private build outputs.

The builder records the byte count, address space, consumer, and before/after hash of each integration edit. RAM addresses are used only in the initialized range represented by the exact input. The output's terminal module CRC is separate from its payload. Container reconstruction updates the MAIN length, following module offsets, module CRC, container CRC and integrity header. The other five modules must remain byte-identical.

Published PCM allocations remain immutable until shutdown. A scratch buffer is validated on each choice and compared by complete content against at most 20 published entries. Failed imports and cache hits do not consume new published allocations. Busy selection preserves the prior choice. New card configuration is committed before disabling the previous mounted-card profile.

Callback registrations can be reused only after the upper native final callback returns and the request plus both output pending states are clear. An admitted-request sequence protects against stale API returns. Completion notification alone is insufficient, and rejected submissions lacking final retirement remain reserved. This bounded registration reuse does not establish a PCM DMA reclamation fence.
