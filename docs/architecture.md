# Implementation

The camera continues to run its original firmware. Newly authored C integrates a file picker, bounded WAV importer, persistent profile and audio adapter at recovered interfaces. This is targeted binary integration, not a source rebuild of Nikon firmware.

| Component | Responsibility |
|---|---|
| `picker.c` | CUSTOM_SOUND directory enumeration, bounded menu rows, original Type A–E selection, CUS label, import publication, cold-menu reconciliation and lazy audio restore |
| `mark2_import.c` | Bounded RIFF parsing, exact PCM geometry, frame/duration limits and padding to a 1 ms / 192-byte audio quantum |
| `mark2_native_file.c` | Recovered original file interface bridge |
| `profile.c`, `profile_native.c` | Two 160-byte configuration banks, CRC, sequence selection and write/readback checks |
| `adapter.c` | Bind cached PCM into the original playback path, immutable PCM ownership, retired callback reuse and Cxx loop/tail |
| `runtime.c` | Minimal freestanding runtime support |
| `builder.py` | Verified input, compilation, local trampoline/resource generation and minimal integration edits |
| `container.py`, `readback.py` | Separate container construction and verification implementations |

Fast and slow shutter paths retain their original event phases. In S/CL/CH each actual photo request restarts the selected whole PCM through the original stop/wait/restart path, without a queue. The final clip can finish. Configured speed affects request spacing; it does not select a fixed Cxx prefix.

Cxx starts an infinite native loop over min(50ms, padded length) in C15 and min(40ms, padded length) in C30/C60/C120. After actual loop completion, original stop completion and pending-state clearance, it submits one finite remainder. C15's nonzero cycle budget is preserved and adjusted by `50 - prefix_bytes/192`; the original resource consumer supplies the remaining wait. Other Cxx use their original zero budget. Short other-Cxx clips loop their full length, not an artificially padded 40ms cycle. The downstream image-frame call remains original. This is a hold/release contract, not one sound per photograph.

The historical v13 authored-code delta is confined to Cxx initialization. Code growth relocates 15 existing hook/pointer targets by 48 bytes without changing the 27 integration sites, state/BSS capacities or import/profile/callback logic. See [changes](../CHANGELOG.md).

v14 adds one parent-page entry wrapper before the original refresh. A confirmed
saved choice restores PCM and a bounded filename model; child entry clears
native A–E marks then marks/focuses the matching complete path. The first rebuilt
focus is consumed once. An already selected file beyond the first 20 directory
entries replaces the last visible row. No I/O occurs inside the text sink and
restoration does not persist a new choice. Direct child entry uses the same
preparation, including when audio had already restored before menu entry.

The standalone picker remains 6304B using existing tail padding for focus state.
The 8192B added BSS and 1536B adapter reservation remain unchanged; there are
28 integration sites, including the new parent callback. Integrated v39 uses
a different heap/ready-anchor contract and is not byte-identical to standalone
v14. The [Z8 study](z8-porting.zh-CN.md) explains why neither memory layout nor
the Z9 address table can be copied to another model.

Native addresses, field offsets, type signatures and expected structural values describe recovered interfaces. They are version-specific. The original instructions replayed by hooks, original menu rows, and original resources are read from the user's hash-checked module at build time. They are not embedded in the source tree. Generated assembly and disassembly are private build outputs.

The builder records the byte count, address space, consumer, and before/after hash of each integration edit. RAM addresses are used only in the initialized range represented by the exact input. The output's terminal module CRC is separate from its payload. Container reconstruction updates the MAIN length, following module offsets, module CRC, container CRC and integrity header. The other five modules must remain byte-identical.

Published PCM allocations remain immutable until shutdown. A scratch buffer is validated on each choice and compared by complete content against at most 20 published entries. Failed imports and cache hits do not consume new published allocations. Busy selection preserves the prior choice. New card configuration is committed before disabling the previous mounted-card profile.

Callback registrations can be reused only after the upper native final callback returns and the request plus both output pending states are clear. An admitted-request sequence protects against stale API returns. Completion notification alone is insufficient, and rejected submissions lacking final retirement remain reserved. This bounded registration reuse does not establish a PCM DMA reclamation fence.

## v15 ordinary-CUS gate

The original scheduler has already selected ordinary kind0 before ROM40F9F9B8.
`m2_ordinary_restart_required` reads published selection and Cxx/tail ownership
only. Selected CUS with all three Cxx/tail fields clear branches to original
40F9FA4C (stop/wait/new request). Otherwise the locally read displaced word is
replayed and original40F9F9BC continues. State from the previous request, such as
`kind`, `route`, `active` or `armed`, is not a substitute for native admission.

The176B aligned gate saves X0–X18/X30 and NZCV around the C predicate; remaining
registers follow AAPCS64. The shared generator is exercised with an authored ADDS
fixture and an ABI-clobbering stub on AArch64. Original module words are never
committed. The fixed-BSS standalone needs no integrated heap-ready probe; ports
using dynamic state must separately prove availability before dereferencing it.
There are now29 integration sites, with existing allocations and capacities.
