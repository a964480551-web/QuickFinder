# 第三方组件许可说明

QuickFinder 自有代码采用 MIT License。构建和运行依赖以下第三方项目：

| 组件 | 用途 | 许可证与说明 |
| --- | --- | --- |
| Python | 运行时 | Python Software Foundation License |
| PySide6 / Qt for Python | 图形界面 | LGPLv3 / GPLv3 / 商业许可三选一；本项目按 LGPLv3 条款使用 |
| Qt 6 动态库 | 图形界面运行时 | 主要按 LGPLv3 使用；具体模块以随发行包提供的 Qt 许可文件为准 |
| Shiboken6 | Python 与 Qt 绑定 | LGPLv3 / GPLv3 / 商业许可三选一 |
| PyInstaller | Windows 打包 | GPLv2-or-later，并带有允许分发打包程序的特殊例外 |
| NSIS | 安装程序 | zlib/libpng License |

项目源代码和完整构建说明均已公开。安装版采用目录式打包，Qt 动态库以独立文件存在，便于用户依据 LGPL 条款检查或替换相关库。

上表是工程说明，不构成法律意见。各组件的完整许可文本和最新条款以其官方发行包及官方网站为准。
