# HarmonyOS Device QA Skill

[中文说明](./README.zh-CN.md)

`harmonyos-device-qa` helps validate app flows on HarmonyOS or OpenHarmony devices and emulators, covering installation, launch, UI targeting, screenshots, log capture, and basic interaction.

## Use Cases

- Reproduce app issues on a device and capture evidence
- Drive taps, swipes, key events, and text input with `hdc`
- Analyze the current UI tree with `uitest dumpLayout` and compute tap coordinates
- Combine `snapshot_display` screenshots with `hilog` output for debugging

## Directory Structure

```text
harmonyos-device-qa/
├── README.md
├── README.zh-CN.md
├── SKILL.md
├── LICENSE.txt
├── agents/
│   └── openai.yaml
└── scripts/
    ├── ui_pick.py
    └── ui_tree_summarize.py
```

## Main Capabilities

- Connect to and select a HarmonyOS/OpenHarmony device target
- Install `.hap` packages and launch apps with `aa start`
- Inspect bundle information with `bm dump`
- Export the UI tree and compute tap coordinates from node bounds
- Capture full-screen screenshots and pull them back locally
- Collect `hilog` output to support debugging

## Quick Start

1. Make sure `hdc` and `python3` are available in your environment.
2. Read the standard workflow in `SKILL.md`.
3. Run `hdc list targets` to confirm that a device or emulator is connected.
4. Use `scripts/ui_pick.py` and `scripts/ui_tree_summarize.py` when you need help parsing the UI tree.

## Inspiration

This skill is inspired by Codex's `test-android-apps` workflow and adapts the Android-side `adb`, `uiautomator`, and `logcat` flow to HarmonyOS / OpenHarmony tooling based on `hdc`, `uitest`, and `hilog`.
