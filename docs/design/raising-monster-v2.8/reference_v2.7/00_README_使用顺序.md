# Raising Monster v2.7｜Claude 可执行设计包

**适配基线**：《全览.pdf》记录的 Android 2.5.51（47 屏）；用户提供的 Claude 2.6.52 发布记录。当前包未直接审查 2.6.52 的源码或真机，因此不能替代实测验收。

## 给 Claude 的最快使用方式

把本文件夹放进仓库 `docs/design/raising-monster-v2.7/`，在 Claude Code 中提交以下指令：

> 请把当前仓库的 2.6.52 版本作为真实事实来源。完整阅读 `docs/design/raising-monster-v2.7/` 内全部文档，并加载当前环境可读取的 ui-ux-pro-max 与其他设计 Skill。先核对 47 屏覆盖范围、已实现/未实现差异、组件与路由，再按照 `02_Claude_Execution_Prompt_v2.7.md` 小批次落实。底部四个 IP Tab、小怪兽出场、成长地图与完整插画必须保留；活动、观察、接种儿保与手帐事件的状态语义不得混用。每批提交真实修改文件、截图/录屏和测试依据；没有设备测试的项保持未执行，禁止用模拟器构建代替真机验收。

## 文件说明

| 文件 | 使用时机 |
|---|---|
| `01_Raising_Monster_Design_Experience_v2.7.md` | 主规范：页面、信息层级、视觉、动效、双平台与发布门槛 |
| `02_Claude_Execution_Prompt_v2.7.md` | 给 Claude 的执行顺序、边界与交付格式 |
| `03_Acceptance_Test_Cases.csv` | 48 条跨平台可复现测试与结果记录（目前全部未执行） |
| `04_47_Screen_Coverage.csv` | 47 屏原产品功能覆盖，供 Claude 填映射与证据 |
| `05_Decision_Log_and_Release_Gates.md` | 决策冻结、待确认事项、证据分级与阻断条件 |
| `06_Design_Tokens_v2.7.json` | 语义化色彩、字体、间距、动效、状态的建议起点 |
| `07_Component_Behavior_and_Microcopy.md` | UI 组件行为表、页面短文案、空/错/离线状态与 IP Tab 细节 |

**提醒**：CSV 是验收模板，设计图是方向示意。代码实现、数据迁移和正式发行状态只以实际仓库、测试日志与平台审核结果为准。
