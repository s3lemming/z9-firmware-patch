# Publication boundary

Included: newly authored integration C, source recipes, recovered ABI addresses and field definitions, hash/length identity metadata, synthetic tests, documentation and the license.

Excluded: original or modified firmware, binary patches containing vendor bytes, original instructions or resources, decompiled Nikon functions, keys and private format tables, camera calibration/storage readbacks, personal audio, screenshots, device identifiers, host paths, build output, internal logs and earlier Git history.

Only a fresh, audited source tree is published. All build and test outputs must be outside the repository. `tools/audit_publication.py` checks the declared source-only file list, encodings, file types, links, sizes, obvious credential patterns and local paths. It is a practical publication guard, not a legal opinion or proof that all possible sensitive data can be detected. A separate local review checked the actual private inputs without distributing them.

Contributions must not attach firmware or private material. Use synthetic test cases and minimal descriptions of behavior. Keep original firmware and generated assembly/disassembly private. CI runs only synthetic host tests and does not upload artifacts.
