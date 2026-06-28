#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ThaiMaster 泰语学习助手 - 主入口

启动方式：
    python main.py

项目结构：
    ThaiMaster/
    ├── main.py              # 入口文件
    ├── config.py            # 配置文件
    ├── requirements.txt     # 依赖列表
    ├── gui/
    │   ├── __init__.py
    │   ├── app.py           # 主窗口
    │   └── card_view.py     # 单词卡片界面
    ├── core/
    │   ├── __init__.py
    │   ├── tts.py           # 泰语发音（edge-tts）
    │   ├── asr.py           # 语音识别（faster-whisper）
    │   └── scorer.py        # 发音评分（Levenshtein）
    ├── data/
    │   ├── __init__.py
    │   └── courses.py       # 课程数据结构
    └── utils/
        ├── __init__.py
        └── audio.py         # 录音和播放工具

工作流程：
    选择课程 → 显示泰语卡片 → 听标准发音 → 跟读录音 → AI评分反馈

首次使用须知：
    1. 运行前请先安装依赖：pip install -r requirements.txt
    2. 首次运行时会自动下载 Whisper 语音识别模型（约 1.5GB）
    3. TTS 功能需要互联网连接（调用微软 Edge 在线语音服务）
    4. 音频录制需要麦克风权限
"""

import sys
import os


def check_python_version():
    """
    检查 Python 版本是否符合要求（≥ 3.8）。

    faster-whisper 和 edge-tts 都需要 Python 3.8 以上版本。
    如果版本过低，显示友好提示并退出。
    """
    required_version = (3, 8)
    current_version = sys.version_info[:2]

    if current_version < required_version:
        print(f"错误: 需要 Python {required_version[0]}.{required_version[1]} 或更高版本")
        print(f"当前版本: Python {current_version[0]}.{current_version[1]}")
        print("请从 https://www.python.org/downloads/ 下载最新 Python 版本")
        sys.exit(1)

    print(f"[ThaiMaster] Python 版本检查通过: {sys.version.split()[0]}")


def check_dependencies():
    """
    检查关键依赖是否安装。

    在启动前检查 faster-whisper、edge-tts、sounddevice 等核心依赖，
    如果缺少某些库，给出安装提示而不是直接崩溃。
    """
    missing = []

    try:
        import faster_whisper
        print(f"[ThaiMaster] faster-whisper [OK]")
    except ImportError:
        missing.append("faster-whisper")

    try:
        import edge_tts
        print(f"[ThaiMaster] edge-tts [OK]")
    except ImportError:
        missing.append("edge-tts")

    try:
        import sounddevice
        print(f"[ThaiMaster] sounddevice [OK]")
    except ImportError:
        missing.append("sounddevice")

    try:
        import soundfile
        print(f"[ThaiMaster] soundfile [OK]")
    except ImportError:
        missing.append("soundfile")

    try:
        import pygame
        print(f"[ThaiMaster] pygame [OK]")
    except ImportError:
        missing.append("pygame")

    if missing:
        print(f"\n[!] Missing dependencies: {', '.join(missing)}")
        print(f"Please run: pip install {' '.join(missing)}")
        print("Or run: pip install -r requirements.txt")
        print()

    return len(missing) == 0


def main():
    """
    主函数：启动 ThaiMaster 应用程序。

    执行流程：
    1. 检查 Python 版本
    2. 检查依赖安装情况
    3. 创建应用实例
    4. 启动 GUI 主循环

    异常处理：
    - 如果关键依赖缺失，阻止启动并给出安装提示
    - 如果 GUI 初始化失败，显示错误信息
    """
    print("=" * 50)
    print("  ThaiMaster - Thai Learning Assistant")
    print("=" * 50)
    print()

    # 步骤 1：检查 Python 版本
    check_python_version()

    # 步骤 2：检查依赖
    all_deps_ok = check_dependencies()
    if not all_deps_ok:
        print("[!] Some dependencies missing, but app will try to start (features may be limited)")
        print()

    # 步骤 3：启动应用
    try:
        print("[ThaiMaster] Starting GUI...")
        from gui.app import ThaiMasterApp

        app = ThaiMasterApp()
        print("[ThaiMaster] Application started!")
        app.run()

    except ImportError as e:
        print(f"\n[X] Import error: {e}")
        print("   Please run from project root: python main.py")
        print("   Or install missing dependencies: pip install -r requirements.txt")
        sys.exit(1)

    except Exception as e:
        print(f"\n[X] Startup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
