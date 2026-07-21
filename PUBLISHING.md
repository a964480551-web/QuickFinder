# GitHub 发布操作说明

这份仓库已经整理完成，不需要再修改代码。

## 第一步：发布源代码仓库

推荐使用 GitHub Desktop：

1. 登录 GitHub Desktop。
2. 选择 **File → Add local repository**。
3. 选择准备好的 `QuickFinder_GitHub_Repository` 文件夹。
4. 点击 **Publish repository**。
5. Repository name 填写 `QuickFinder`。
6. 取消勾选 **Keep this code private**，然后发布。

## 第二步：发布安装包

1. 在浏览器打开刚发布的仓库。
2. 点击右侧 **Releases → Create a new release**。
3. 在 **Choose a tag** 中输入 `v2.1.0`，选择创建新标签。
4. Release title 填写 `QuickFinder 2.1.0`。
5. 将 `RELEASE_NOTES_2.1.0.md` 的内容粘贴到发布说明。
6. 上传以下两个文件：
   - `QuickFinder_Setup_2.1.0.exe`
   - `SHA256SUMS.txt`
7. 点击 **Publish release**。

## 第三步：建议开启安全报告

进入仓库 **Settings → Code security and analysis**，开启 **Private vulnerability reporting**。这样别人发现漏洞时可以私下报告，不会直接公开利用细节。

不要上传旧版 `2.0.0` 安装包、索引数据库、`.workbuddy`、`.trash`、`dist` 或 `release` 目录。
