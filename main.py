"""
ThaiMaster 泰语学习助手 - 入口文件
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    try:
        from ThaiMaster.gui.app import MainApp
        app = MainApp()
        app.run()
    except ImportError as e:
        print(f"导入模块失败: {e}")
        print("请确保已安装所有依赖包: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"应用启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
