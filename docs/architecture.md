# Implementation

The camera continues to run its original firmware. Newly authored C integrates a file picker, bounded WAV importer, persistent profile and audio adapter at recovered interfaces. This is targeted binary integration, not a source rebuild of Nikon firmware.

| Component | Responsibility |
|---|---|
| `picker.c` | CUSTOM_SOUND directory enumeration, bounded menu rows, original Type A–E selection, CUS label, import publication and lazy restore |
| `mark2_import.c` | Bounded RIFF parsing, exact PCM geometry, frame/duration limits and padding to a 1 ms / 192-byte audio quantum |
| `mark2_native_file.c` | Recovered original file interface bridge |
| `profile.c`, `profile_native.c` | Two 160-byte configuration banks, CRC, sequence selection and write/readback checks |
| `adapter.c` | Bind cached PCM into the original playback path, immutable callback ownership, bounded Cxx bridge |
| `runtime.c` | Minimal freestanding runtime support |
| `builder.py` | Verified input, compilation, local trampoline/resource generation and minimal integration edits |
| `container.py`, `readback.py` | Separate container construction and verification implementations |

Fast and slow shutter paths have different original audio event phases. The adapter replaces the selected sound while retaining the original request and DMA consumer contracts; it suppresses original middle/tail events when a custom whole clip has already covered that sound. Cxx has additional event/frame bridging and is not assumed equivalent to S/CL/CH. Exact one-sound-per-frame behavior is outside this frozen release.

Native addresses, field offsets, type signatures and expected structural values describe recovered interfaces. They are version-specific. The original instructions replayed by hooks, original menu rows, and original resources are read from the user's hash-checked module at build time. They are not embedded in the source tree. Generated assembly and disassembly are private build outputs.

The builder records the byte count, address space, consumer, and before/after hash of each integration edit. RAM addresses are used only in the initialized range represented by the exact input. The output's terminal module CRC is separate from its payload. Container reconstruction updates the MAIN length, following module offsets, module CRC, container CRC and integrity header. The other five modules must remain byte-identical.

Immutable allocations avoid recycling memory while old asynchronous callbacks may still refer to it. Ownership retirement is not proven sufficiently to remove the 4-import and 64-callback limits. Increasing constants alone is not a complete lifetime-management fix.
