<div align="center">

# 🚀 HuiJui Toolbox v6.0

**原生 GPU 渲染 · 分布式极客中心**

一款基于 **Python + Flet** 打造的桌面级安卓极客军火库。
深邃极简的暗黑 UI、全局液态玻璃材质、动态壁纸引擎，给你最纯粹的极客操作体验。

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python&logoColor=white)]()
[![Flet](https://img.shields.io/badge/Flet-0.28.3-cyan?style=flat-square)]()
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey?style=flat-square&logo=windows)]()

</div>

---

## 📸 界面预览

<img width="1432" height="911" alt="image" src="https://github.com/user-attachments/assets/bebaa2c6-e7ab-47c2-b1c6-e18f50d9c425" />


---

## ✨ 核心功能 (Features)

- 🛠️ **一键刷机**：自动解包官方 `payload.bin`，全自动 `Fastboot` 刷写，底层防呆拦截。
- 📦 **模块仓库**：内置 971+ 纯净模块，支持国内镜像加速下载，一键推流并自动通过 Root 刷入。
- 💾 **分区备份**：真 Root 权限提取，智能探测 A/B 分区，支持全量基带保命备份（防格机专用）。
- 🚑 **双平台救砖**：高通 9008 / MTK BROM 极速拉起，支持解析 XML 与 Scatter 脚本。
- 📱 **Scrcpy 无边框投屏**：纯无线连接，彻底隐藏终端黑框，丝滑不卡顿。
- 🎨 **极致个性化**：支持自定义壁纸自动裁剪、动态 GIF 引擎、全局毛玻璃/液态玻璃模糊度调节。
- 🔑 **临时 Root & 高级终端**：GhostLock 动态解析引擎，KMI 检测与 OTA 解析闭环。

---

## 📥 如何下载使用 (For Users)

由于本工具箱集成了大量底层依赖（ADB、Fastboot、Scrcpy 等），**普通用户请直接下载编译好的独立 EXE 文件**，无需配置任何 Python 环境。

👉 **请前往右侧的 [Releases](https://github.com/hhcdxii-ship-it/New-repository/releases) 页面，下载最新的 `HuiJui_Toolbox.exe` 双击运行即可。**

> ⚠️ **警告**：由于包含底层刷机工具，杀毒软件（360、Windows Defender 等）极大概率会误报拦截。请务必点击“允许运行”或添加白名单！

---

## 💻 开发者指南 (For Developers)

如果你想基于本源码进行二次开发或自行编译：

**1. 克隆仓库**
```bash
git clone https://github.com/hhcdxii-ship-it/New-repository.git
cd New-repository
