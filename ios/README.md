# 养小怪兽 iOS 版（准备中）

iOS 版与安卓版使用同一套离线页面（`app/src/main/assets/site`），用 WKWebView 加载，原生部分提供：分享、导出与导入文件、接种儿保和手帐提醒（本地通知）、触感反馈、桌面小组件（距上次喂奶实时计时、四个快捷记录按钮、夜间模式入口）、两套桌面图标切换。

## 现状

- 每次修改 `ios/` 后，GitHub Actions 的「Build iOS (simulator check)」会在 macOS 上生成 Xcode 工程并编译（模拟器、不签名），用来确认代码可以编译。
- 安装到 iPhone 或上架 App Store 还需要：Apple 开发者账号（个人账号每年 99 美元）、在 Xcode 中设置签名团队，以及 App Group `group.cn.growthhandbook.app`（应用和小组件共享数据用）。

## 在 Mac 上打开

```
brew install xcodegen
python3 ios/scripts/prepare_assets.py
cd ios && xcodegen generate --spec project.yml
open MonsterRaising.xcodeproj
```

在 Xcode 的 Signing & Capabilities 里选择自己的开发团队，连接 iPhone 后运行即可。

## 发布到 TestFlight（准备好 Apple 开发者账号后）

1. 在 App Store Connect 新建 App，套装 ID 填 `cn.growthhandbook.app`（小组件为 `cn.growthhandbook.app.widget`，构建时自动注册）。
2. 在 App Store Connect › 用户和访问 › 集成 › App Store Connect API 新建一个「管理」权限的密钥，下载 `.p8` 文件。
3. 在 GitHub 仓库 Settings › Secrets and variables › Actions 添加四个密钥：
   - `APPLE_TEAM_ID`：开发者账号的团队 ID
   - `ASC_KEY_ID`、`ASC_ISSUER_ID`：上一步密钥页面显示的 Key ID 和 Issuer ID
   - `ASC_KEY_P8`：`.p8` 文件内容的 base64（`base64 -i AuthKey_XXXX.p8`）
4. 在 Actions › iOS to TestFlight 点 Run workflow。完成后，构建会出现在 App Store Connect 的 TestFlight 里，邀请家人用 TestFlight 安装。

版本号与安卓一致采用「主版本.次版本.构建号」，主版本和次版本来自仓库根目录的 `VERSION` 文件。
