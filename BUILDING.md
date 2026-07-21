# 构建说明

## 环境

- Windows 10 或 Windows 11，64 位
- Python 3.13
- NSIS 3.12 或兼容版本

## 1. 安装构建依赖

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements-build.txt
```

## 2. 构建目录式应用

目录式发布让 Qt 动态库保持为独立文件，便于遵循 LGPL 的替换要求。

```powershell
.venv\Scripts\pyinstaller --noconfirm --windowed --onedir `
  --name QuickFinder `
  --icon quickfinder.ico `
  --add-data "check.svg;." `
  --version-file version_info.txt `
  quick_finder.pyw
```

## 3. 构建安装程序

```powershell
& "C:\Program Files (x86)\NSIS\makensis.exe" quickfinder_installer.nsi
```

最终安装包位于 `release\installer-nsis`。

## 4. 发布

创建与版本号一致的 GitHub Release，上传安装包和 `SHA256SUMS.txt`。不要把 `dist`、`build`、索引数据库或本机虚拟环境提交到仓库。
