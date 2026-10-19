# 小怪兽育儿 App｜v2.8 设计执行与验收包

**目标**：把 v2.7 设计指南的建议转为 Claude 可以逐条实施、复核、交付、拒绝虚假“完成”的工程约束。面向 Android / iOS 的同一产品；**当前代码基线由 Claude 检查仓库后填写**，目前仅掌握用户提供的 v2.6.52 发布说明与 v2.5.51 的 47 屏全览。不得将发布说明当作源码/真机验证。

## 首次交付操作

1. 把整个目录放在仓库 `docs/design/raising-monster-v2.8/`，不要删除其中的 `reference_v2.7/`。
2. 给 Claude Code 发送 `03_CLAUDE_ENFORCEMENT_PROMPT.md` 的完整内容。
3. Claude 先读取仓库和已安装 Skill、填写需求追踪表 `04_REQUIREMENTS.csv` 的代码位置/现状，再按批次修改；每个批次需要变更文件、提交、路径录屏和验证结果。
4. 把真机录屏、截图、日志保存在实际仓库的 `qa/evidence/...` 并写入矩阵。证据列**不可写不存在的文件**。
5. 执行 `python docs/design/raising-monster-v2.8/08_gate_check.py --repo-root . --mode audit` 生成差距报告；发布前使用 `--mode release`。初始未执行测试，因此 release 模式**按预期返回不通过**。

## 文件阅读顺序

| 文件 | 职责 |
|---|---|
| `01_BRAND_NAMING_AND_IP.md` | 三套中英品牌方案、当前名称冻结、商店文案、双怪兽主题与素材规则 |
| `02_DESIGN_SPEC_DELTA.md` | 页面/组件/动效/阅读与跨平台的 v2.8 精修增量规范 |
| `03_CLAUDE_ENFORCEMENT_PROMPT.md` | Claude 的强制实施流程、证据标准和报告模板 |
| `04_REQUIREMENTS.csv` | 需求→屏幕→验收条件→代码→Android/iOS 结果的逐项台账 |
| `05_QA_ANDROID_IOS.csv` | v2.7 原 48 项分平台拆解，补充品牌/应用感/性能等案例 |
| `06_DECISIONS_AND_RELEASE.md` | 已冻结决策、待确认及 P0/P1 发布阻断 |
| `07_IMPLEMENTATION_BATCHES.md` | 实施节奏、批次产物、必须报告的延期项 |
| `08_gate_check.py` | 对 CSV 内容完整度和本地证据路径进行自动门禁；不能证明交互正确 |
| `09_tokens_v2.8.overlay.json` | 叠加式品牌与设计 token，先审计现有代码再合并 |
| `reference_v2.7/` | 原规范、原 47 屏和 48 项测试，不得未经说明覆盖 |

**命名决策状态**：推荐“小怪兽成长簿 / Monster Milestones”，**尚未由用户最终确认**。Claude 不得自动更改 `applicationId`、Bundle ID、应用商店名称、数据库 key 或应用内已有展示文字。批准后另做独立改名批次。

**证据纪律**：设计稿只能证明布局意图；截图只能证明静态状态；单元测试与构建只能证明相应技术检查；实际手势、帧率、可访问性、键盘、硬件权限须设备结果。完成度由证据界定。
