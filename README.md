<img width="1488" height="1053" alt="image" src="https://github.com/user-attachments/assets/62c55fcb-bdea-455c-baac-91483e8f5ac5" />

# QuickFinder

QuickFinder 是一款面向 Windows 的本地文件搜索工具。它会在用户选择的磁盘或文件夹中建立本地索引，实现即时文件名搜索。

## 特性

- 即输即搜，支持用空格分隔多个关键词。
- 支持磁盘、自定义文件夹和“仅显示文件夹”筛选。
- 索引使用 SQLite 保存在本机，不执行不安全的对象反序列化。
- 搜索、索引加载和索引构建均在后台执行。
- 无账号、无遥测、无广告，不上传文件名或路径。
- Windows 11 风格的 Liquid Glass 界面。

## 下载

普通用户请在仓库右侧的 **Releases** 页面下载最新的 `QuickFinder_Setup` 安装包。

> 安装包暂未使用商业代码签名证书，Windows SmartScreen 可能显示“未知发布者”。请仅从本仓库的 Releases 页面下载，并核对发布页中的 SHA-256。

## 隐私

QuickFinder 不会连接网络。索引只保存在：

```text
%LOCALAPPDATA%\QuickFinder\quickfinder_index.sqlite3
```

索引包含文件名和完整路径，但不包含文件内容。详细说明见 [PRIVACY.md](PRIVACY.md)。

## 从源代码运行

需要 Windows 和 Python 3.13：

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python quick_finder.pyw
```

## 构建

可复现构建步骤见 [BUILDING.md](BUILDING.md)。安装包使用 NSIS 构建，不再依赖具有非商业限制的安装包编译器。

## 安全

请不要公开披露尚未修复的漏洞。报告方式见 [SECURITY.md](SECURITY.md)。

## 开源许可

QuickFinder 自有源代码采用 [MIT License](LICENSE)。随构建产物分发的第三方组件使用各自许可证，详见 [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md)。

---

QuickFinder is a local, privacy-friendly file name search utility for Windows. It does not upload file names, paths, or file contents.
