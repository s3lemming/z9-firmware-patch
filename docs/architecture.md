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

Fast and slow shutter paths retain their original event phases. Cxx starts an infinite native loop over the first min(50 ms, padded clip length), stops through the original stop entry, and queues one finite remainder after actual loop completion and original pending-state clearance. C15 and other Cxx use their distinct original bootstrap entries. The downstream image-frame call remains original, avoiding late whole-clip retriggers. This is a hold/release contract, not one sound per photograph.

Native addresses, field offsets, type signatures and expected structural values describe recovered interfaces. They are version-specific. The original instructions replayed by hooks, original menu rows, and original resources are read from the user's hash-checked module at build time. They are not embedded in the source tree. Generated assembly and disassembly are private build outputs.

The builder records the byte count, address space, consumer, and before/after hash of each integration edit. RAM addresses are used only in the initialized range represented by the exact input. The output's terminal module CRC is separate from its payload. Container reconstruction updates the MAIN length, following module offsets, module CRC, container CRC and integrity header. The other five modules must remain byte-identical.

Published PCM allocations remain immutable until shutdown. A scratch buffer is validated on each choice and compared by complete content against at most 20 published entries. Failed imports and cache hits do not consume new published allocations. Busy selection preserves the prior choice. New card configuration is committed before disabling the previous mounted-card profile.

Callback registrations can be reused only after the upper native final callback returns and the request plus both output pending states are clear. An admitted-request sequence protects against stale API returns. Completion notification alone is insufficient, and rejected submissions lacking final retirement remain reserved. This bounded registration reuse does not establish a PCM DMA reclamation fence.
