# Z9 firmware patch — mark2

Experimental, source-only custom shutter sound patch for **Nikon Z9 firmware 5.32**, frozen at mark2 v11. This repository contains newly authored patch code and offline tools. It does not contain Nikon firmware, Nikon source code, extracted resources, recordings, private format material, camera readbacks, or an installable firmware image.

[中文说明](README.zh-CN.md) · [Architecture](docs/architecture.md) · [Validation and limitations](docs/validation.md) · [Publication boundary](docs/publication.md)

## Feature

Choose a custom shutter sound from the camera menu. Files are scanned only in `CUSTOM_SOUND` at the card root; the folder is created if absent. Up to 20 files are displayed across available cards, with basenames only and no recursive scan. The outer menu shows `CUS` when a custom sound is selected; built-in Type A–E remain available.

Accepted audio is RIFF WAV, PCM format 1, **48 kHz, stereo, 16-bit little-endian**, with **0 < duration ≤ 1.5 seconds**. This is not a general audio converter. Unsupported files are rejected without replacing the previous loaded sound. Basenames must be printable ASCII and at most 111 characters. Configuration is stored in two CRC-protected records in the same folder.

This release has deliberate resource limits: **4 import attempts per boot**, including failed attempts and automatic restoration, and **64 immutable audio callback slots per boot**. The 65th request is rejected by the adapter; audible fallback is not established. It is an experimental baseline, not a production-ready unlimited-use release. Read the [known limitations](docs/validation.md) before using locally generated output.

## Build locally

Tested on Ubuntu 24.04 / WSL with Python 3.12, GCC AArch64 13.3.0 and GNU binutils 2.42. Host tests also need GCC and NumPy. A different compiler may generate different bytes and is rejected by the final payload identity check.

```sh
sudo apt-get install python3 python3-numpy gcc gcc-aarch64-linux-gnu binutils-aarch64-linux-gnu
python3 -B tests/run.py --output /path/outside-repository/new-host-tests
python3 -B patch.py build \
  --module /path/to/your-original/eg1990_053200.bi \
  --output /path/outside-repository/new-private-build
```

You must supply the original MAIN module locally. Only the exact SHA-256 in `profile.json` is accepted. The tool checks source hashes, compiles the new code, reads displaced instructions and resources from your input, applies the integration changes, and verifies the final payload identity. Output includes derived firmware and must remain private and outside this repository. An existing output directory is rejected. Run Python without `-O`.

## Optional full-container tools

Full-container packing additionally requires the exact original 5.32 container and **separately supplied private format material**. Those materials and instructions for obtaining them are not distributed here. The public repository alone therefore cannot produce a complete container from the official download.

`--tables` accepts a private JSON object with `T1`, `T2`, `T3`, each a hexadecimal encoding of 256 bytes. `--integrity-material` accepts a private JSON object with `K8`, a hexadecimal encoding of 8 bytes. No real values are included, downloaded, or printed by the tools.

```sh
python3 -B patch.py pack \
  --stock /private/original.bin --tables /private/tables.json \
  --integrity-material /private/integrity.json \
  --payload /private/build/payload.bin --output /private/new-candidate.bin
python3 -B patch.py verify \
  --stock /private/original.bin --tables /private/tables.json \
  --integrity-material /private/integrity.json \
  --candidate /private/new-candidate.bin
```

Packing preserves the other five modules, recalculates length and integrity fields, and requires a separate readback implementation and the frozen full-container hash to agree before writing output. Integrity checks establish local byte identity, not camera acceptance or safe operation. There are no camera-control, flashing, or automatic installation commands.

## Scope and provenance

The design follows the input identity / source recipe / independently verified output approach demonstrated by [XinmiaoZhao/NikonFirmwarePatch](https://github.com/XinmiaoZhao/NikonFirmwarePatch), reviewed at commit `1a60fc00ff082b6ccc346db0df626662308b3974`. No Z8 patch implementation or private format material was copied. This is a Z9 mark2 sound project; it does not implement Z8 RAW pre-capture, mark3, mark1 VR control, or QEMU hardware emulation changes.

Newly authored code is licensed under **GPL-3.0-or-later**; see [LICENSE](LICENSE) and [NOTICE](NOTICE). This project is independent of Nikon. Do not attach firmware images, private materials, camera dumps, personal recordings or unsanitized local logs to issues or pull requests.
