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
