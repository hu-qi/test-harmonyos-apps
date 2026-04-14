---
name: "harmonyos-device-qa"
description: "Use when validating HarmonyOS or OpenHarmony feature flows on a device or emulator with hdc-driven launch, input, UI-tree inspection, screenshots, and hilog capture."
---

# HarmonyOS Device QA

Validate HarmonyOS and OpenHarmony app flows on a real device or emulator using `hdc` for launch, input, UI-tree inspection, screenshots, and logs.

## When to use
- QA a feature flow on a HarmonyOS or OpenHarmony device.
- Reproduce UI bugs by driving navigation with `hdc shell` commands.
- Capture screenshots and `hilog` output while testing.

## Quick start
1) List connected targets and pick one target key:
   - `hdc list targets`
2) Build the target HAP:
   - `./hvigorw assembleHap`
   - If unsure about task names: `./hvigorw tasks | rg -i "hap|assemble"`
3) Install the app:
   - `hdc -t <target> install <path-to-hap>`
4) Launch the app:
   - Stage model common pattern: `hdc -t <target> shell aa start -b <bundle> -a <ability>`
   - If you need installed bundle details first: `hdc -t <target> shell bm dump -n <bundle>`
5) Capture a screenshot for visual verification:
   - `hdc -t <target> shell snapshot_display -f /data/local/tmp/emu.jpeg`
   - `hdc -t <target> file recv /data/local/tmp/emu.jpeg /tmp/emu.jpeg`

## hdc control commands
- Tap (use UI tree-derived coordinates):
  - `hdc -t <target> shell uitest uiInput click <x> <y>`
- Swipe:
  - `hdc -t <target> shell uitest uiInput swipe <x1> <y1> <x2> <y2> [velocity]`
  - Avoid edges (start ~150-200 px from left/right) to reduce accidental back gestures.
- Key events:
  - `hdc -t <target> shell uitest uiInput keyEvent Back`
  - `hdc -t <target> shell uitest uiInput keyEvent Home`
- Text:
  - `hdc -t <target> shell uitest uiInput inputText <x> <y> <text>`
- Force stop app:
  - `hdc -t <target> shell aa force-stop <bundle>`
- UI tree dump:
  - `hdc -t <target> shell uitest dumpLayout -p /data/local/tmp/ui.json`
  - `hdc -t <target> file recv /data/local/tmp/ui.json /tmp/ui.json`

## Coordinate picking (UI tree only)
Always compute tap coordinates from the UI tree, not screenshots.

1) Dump the UI tree to a step-specific file:
   - `hdc -t <target> shell uitest dumpLayout -p /data/local/tmp/ui-settings.json`
   - `hdc -t <target> file recv /data/local/tmp/ui-settings.json /tmp/ui-settings.json`
2) Find the target node and derive center coordinates (`x y`) from bounds:
   - Current HarmonyOS dumps on tested devices use JSON nodes shaped like `{"attributes": {...}, "children": [...]}`.
   - Supported bounds shapes include Android-style `"[x1,y1][x2,y2]"` and common HarmonyOS rect objects.
   - Helper script:
   - `python3 <path-to-skill>/scripts/ui_pick.py /tmp/ui-settings.json "Settings"`
3) If the node is missing and there are scrollable containers:
   - swipe, re-dump, and re-search at least once before concluding the target is missing.
4) Tap the center:
   - `hdc -t <target> shell uitest uiInput click <x> <y>`

## UI tree skeleton (helper)
Use this helper to create a compact, readable overview before inspecting the full dump.

1) Dump the full UI tree:
   - `hdc -t <target> shell uitest dumpLayout -p /data/local/tmp/ui-full.json`
   - `hdc -t <target> file recv /data/local/tmp/ui-full.json /tmp/ui-full.json`
2) Generate a summary:
   - `python3 <path-to-skill>/scripts/ui_tree_summarize.py /tmp/ui-full.json /tmp/ui-summary.txt`
3) Review `/tmp/ui-summary.txt` to choose likely targets, then compute exact bounds from the full dump.

## Logs (hilog)
1) Clear logs:
   - `hdc -t <target> hilog -r`
2) Stream device logs:
   - `hdc -t <target> hilog`
3) Save a bounded capture locally:
   - `timeout 10 hdc -t <target> hilog > /tmp/hilog.txt`
4) If you need app-only filtering, combine `hilog` with bundle or domain filters supported by your image.

## Bundle shortcuts
- List installed bundles:
  - `hdc -t <target> shell bm dump -a`
- Inspect one bundle:
  - `hdc -t <target> shell bm dump -n <bundle>`
- Launch a URL or deeplink for repro:
  - `hdc -t <target> shell aa start -U <url>`

## Notes
- `snapshot_display` is usually faster than `uitest screenCap` for full-screen capture.
- `dumpLayout` output is JSON on the tested device and uses an `attributes` + `children` node shape; helper scripts here support both JSON and XML to stay compatible with mixed environments.
- On the tested device, `uitest uiInput` is the reliable input path and `keyEvent Home` returned `No Error`.
- `snapshot_display -f ...` and `uitest dumpLayout -p ...` both succeeded on the tested device.
- `hilog` control is exposed by top-level `hdc hilog`, not only through `shell`.

## Official references
- HDC tool overview: `https://github.com/openharmony/developtools_hdc_standard`
- `aa` tool: `https://gitee.com/openharmony/docs/blob/master/zh-cn/application-dev/tools/aa-tool.md`
- `bm` tool: `https://gitee.com/openharmony/docs/blob/master/zh-cn/application-dev/tools/bm-tool.md`
- ArkXTest / `dumpLayout` and `screenCap` command references: `https://gitee.com/openharmony/testfwk_arkxtest/blob/master/README_zh.md`
- SmartPerf guidance: `https://gitee.com/openharmony/docs/blob/master/zh-cn/application-dev/application-test/smartperf-guidelines.md`
