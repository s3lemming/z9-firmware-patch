# Changes

## mark2 v14 — 2026-11-05

- Restore the confirmed persisted custom selection before the native Camera
  sounds parent refresh; prepare the same model on direct Type-child entry.
- Reconstruct filename rows after restore, remove stale A–E marks and focus/mark
  the current full path. Keep a selected file outside the first 20 entries by
  replacing the last row, without increasing the row or PCM bounds.
- Consume initial focus once; repeated entry avoids re-import/re-allocation and
  configuration writes. Explicit native selection remains disabled for custom
  restore. The text renderer remains I/O-free.
- Add one parent callback slot. Standalone integration sites increase 27→28;
  payload and container grow by 480B. Picker remains 6304B in the original
  8192B added BSS, adapter 1536B reservation unchanged. Playback, WAV/profile
  cores and callback lifecycle are byte-identical source from v13.
- Add 16 cold-menu synthetic groups/38 assertions with ASan/UBSan, alongside
  existing cache, loop, callback, profile, format and tooling suites. Strict
  local build/pack/independent readback use new frozen identities.
- Preserve v13 validation as history and add a Z8 porting study in Chinese.
  Integrated v39 audio-menu restart success is user-reported hardware evidence;
  standalone v14 installation and Z8 functionality remain unqualified.


## mark2 v13 — 2026-10-24

This is a patch-project version; the target Nikon firmware remains 5.32.

### Playback changes

- Keep C15's first 50ms prefix and preserve the original nonzero cycle budget. Compensate shorter prefixes against the original 50ms resource so the original consumer supplies the remaining wait. Measured long-prefix loops are about 66.99ms, replacing v12's roughly 50ms loop.
- Use the first 40ms in C30/C60/C120, with measured long-prefix loops about 40.01ms. These modes share a sound-loop contract; this is not 30/60/120 sounds per second or photo-rate qualification.
- After the original stop completes and outputs are idle, play the remainder once: after 50ms in C15 and after 40ms in the other Cxx modes. Clips at or below the relevant boundary loop their entire padded content with no extra tail. A clip shorter than 40ms does not acquire a fixed 40ms period in the other Cxx modes.
- A 45ms clip therefore has a 40ms loop and 5ms remainder in the other Cxx modes; C15 loops all 45ms with cycle-budget compensation and no extra remainder.

### Unchanged behavior

S/CL/CH still restart the selected whole PCM on each actual photo request, using the original fast/slow phases and stop/wait/restart. No fixed Cxx cut is applied to ordinary modes, no playback queue is added, and the final ordinary clip can finish. Menu, imports, cache, profiles, callback retirement and QEMU implementation are unchanged. The four-attempt quota removal, bounded 20-content cache and callback registration reuse were already v12 changes.

### Build and evidence

- Only the Cxx initialization body in authored firmware code changes functionally. Correct stale generic 50ms comments in this public source copy. Source hashes and exact expected outputs are updated together.
- MAIN payload and full private container each grow by 48 bytes. There are still 27 integration sites. Fifteen hook/pointer targets move uniformly by 48 bytes; these are relocation changes, not fifteen additional feature fixes. State/BSS sizes and the other five original modules are unchanged.
- Extend 3000 synthetic padded-length/entry cases to assert C15 budget compensation, 50/40ms boundaries, repeated lower starts, duplicate release and one finite tail.
- Local fixed-1/200 native regression completed 20 photos, 18 custom audio requests, native-sound restoration and final menus/live view. CL1/CL5/CH10 median intervals were 995.653/203.004/103.983ms, within the declared 25% window. Previously completed slow-shutter phases supply separate CL1/CL5/CH10 evidence. This is additional coverage, not an ordinary-mode code fix.
- Retain failed mixed-shutter recipes and C15 recovery failures. Five matching ordinary model/boot-input fresh attempts include four failures and one complete success, not five passed workflows. No camera installation or long-term hardware qualification is implied. See [current validation](docs/validation.md); [v12's evidence](docs/history/v12-validation.md) remains historical.

### 中文摘要

v13只调整Cxx初始化：C15保留前50ms并恢复原周期预算，其他Cxx改为前40ms；松开后剩余部分播放一次。普通S/CL/CH、菜单、导入缓存及配置逻辑未改。新增20张快档完整流程验证，旧快慢切换与C15恢复问题保留；不是五次完整业务或实机验收。构建正文和完整包均增加48字节，源码、配方、哈希和测试同步更新。

## mark2 v12 — 2026-10-24

- Replace the four-import-attempt quota with at most 20 immutable distinct PCM contents plus one scratch allocation; retries and cache hits do not exhaust a four-attempt budget.
- Reuse callback registrations only after native retirement and cleared pending outputs, without freeing published PCM.
- Introduce the hold-prefix/stop/one-tail contract using 50ms for every Cxx mode.
- Commit a valid new-card profile before disabling the previous mounted-card profile.

The v12 source and exact frozen identities remain in Git history at `d1b0c672444c22dbad85137d1d598ecb80fdecf0`.
