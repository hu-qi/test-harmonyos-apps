# Test HarmonyOS Apps

`Test HarmonyOS Apps` is a Codex plugin scaffolded as a 1:1 port of `Test Android Apps`, with the Android command chain replaced by HarmonyOS and OpenHarmony device tooling.

## Structure

```text
test-harmonyos-apps/
├─ .codex-plugin/plugin.json
├─ agents/openai.yaml
├─ assets/
├─ skills/harmonyos-device-qa/
│  ├─ SKILL.md
│  ├─ agents/openai.yaml
│  └─ scripts/
│     ├─ ui_pick.py
│     └─ ui_tree_summarize.py
└─ plugin.lock.json
```

## What It Does

- Builds or installs HarmonyOS app packages (`.hap`)
- Launches apps with `hdc shell aa start`
- Inspects installed bundles with `hdc shell bm dump`
- Captures screenshots with `snapshot_display`
- Collects logs with `hilog`
- Dumps the UI tree with `uitest dumpLayout`
- Drives taps, swipes, key events, and text entry with `uitest uiInput`
- Computes tap coordinates from the UI tree instead of from screenshots

## Main Command Mapping

| Android | HarmonyOS / OpenHarmony |
|---|---|
| `adb devices` | `hdc list targets` |
| `adb install` | `hdc install <hap>` |
| `am start` | `hdc shell aa start -b <bundle> -a <ability>` |
| `pm list packages` | `hdc shell bm dump -a` |
| `uiautomator dump` | `hdc shell uitest dumpLayout -p ...` |
| `screencap` | `hdc shell snapshot_display -f ...` |
| `logcat` | `hdc shell hilog` |

## Prerequisites

- `hdc` available in `PATH`
- A connected HarmonyOS or OpenHarmony device or emulator
- `python3` available in `PATH`
- Optional: `hvigorw` when building HAPs from source

## Helper Scripts

- `skills/harmonyos-device-qa/scripts/ui_pick.py`
  - Reads a UI dump and prints the center point of a target node
  - Supports both Android XML and HarmonyOS JSON dumps
- `skills/harmonyos-device-qa/scripts/ui_tree_summarize.py`
  - Produces a compact tree summary from the full UI dump
  - Supports both Android XML and HarmonyOS JSON dumps

## Quick Smoke Test

```bash
python3 skills/harmonyos-device-qa/scripts/ui_pick.py /tmp/ui.json "Settings"
python3 skills/harmonyos-device-qa/scripts/ui_tree_summarize.py /tmp/ui.json /tmp/ui-summary.txt
```

## Notes

- On the tested target, `uitest uiInput` is the stable gesture path and `keyEvent Home` executed successfully.
- `dumpLayout` output format may vary by image and ArkXTest version. The tested device returns JSON with an `attributes` + `children` structure, and the helper scripts are written to tolerate both XML and JSON layouts.
- `snapshot_display` is usually the preferred full-screen capture path for performance.

## Acknowledgements

This project started as a 1:1 port of `Test Android Apps`, then was adapted for HarmonyOS and OpenHarmony device workflows.
