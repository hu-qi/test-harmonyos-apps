# HarmonyOS Device QA Skill

`harmonyos-device-qa` helps validate app flows on HarmonyOS or OpenHarmony devices and emulators, covering installation, launch, UI targeting, screenshots, log capture, and basic interaction.

`harmonyos-device-qa` 用于在 HarmonyOS 或 OpenHarmony 真机、模拟器上执行应用验证流程，覆盖安装、启动、界面定位、截图采集、日志抓取和基础交互。

## Use Cases

- Reproduce app issues on a device and capture evidence
- Drive taps, swipes, key events, and text input with `hdc`
- Analyze the current UI tree with `uitest dumpLayout` and compute tap coordinates
- Combine `snapshot_display` screenshots with `hilog` output for debugging

## 适用场景

- 在设备上复现应用问题并保留证据
- 通过 `hdc` 驱动点击、滑动、按键和文本输入
- 使用 `uitest dumpLayout` 分析当前 UI 树并计算点击坐标
- 结合 `snapshot_display` 与 `hilog` 输出排查问题

## Directory Structure

```text
harmonyos-device-qa/
├── README.md
├── SKILL.md
├── LICENSE.txt
├── agents/
│   └── openai.yaml
└── scripts/
    ├── ui_pick.py
    └── ui_tree_summarize.py
```

## 目录结构

```text
harmonyos-device-qa/
├── README.md
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

## 主要能力

- 连接并选择 HarmonyOS/OpenHarmony 设备目标
- 安装 `.hap` 包并通过 `aa start` 启动应用
- 通过 `bm dump` 查看 bundle 信息
- 导出 UI 树并从节点 bounds 计算点击坐标
- 抓取全屏截图并回传到本地
- 采集 `hilog` 日志辅助定位问题

## Quick Start

1. Make sure `hdc` and `python3` are available in your environment.
2. Read the standard workflow in `SKILL.md`.
3. Run `hdc list targets` to confirm that a device or emulator is connected.
4. Use `scripts/ui_pick.py` and `scripts/ui_tree_summarize.py` when you need help parsing the UI tree.

## 快速开始

1. 确认环境中可用 `hdc` 与 `python3`。
2. 阅读 `SKILL.md` 中的标准工作流。
3. 在设备上执行 `hdc list targets` 确认可连接目标。
4. 按需使用 `scripts/ui_pick.py` 和 `scripts/ui_tree_summarize.py` 辅助解析 UI 树。

## Inspiration

This skill is inspired by Codex's `test-android-apps` workflow and adapts the Android-side `adb`, `uiautomator`, and `logcat` flow to HarmonyOS / OpenHarmony tooling based on `hdc`, `uitest`, and `hilog`.

## 灵感来源

该 skill 的工作流灵感来源于 Codex 的 `test-android-apps`，并将 Android 侧的 `adb`、`uiautomator`、`logcat` 流程迁移为 HarmonyOS / OpenHarmony 的 `hdc`、`uitest`、`hilog` 流程。
