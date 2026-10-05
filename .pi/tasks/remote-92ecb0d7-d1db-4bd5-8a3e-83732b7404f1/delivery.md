# [Sean] 工作流与互动改进交付

Owner: Sean。2026-10-05。T-ID `remote-92ecb0d7-d1db-4bd5-8a3e-83732b7404f1`。

## 交付

已部署用户界面 4190（PID 101335）与隔离验证界面 4194（PID 101354）；profile 13、叙事基线 v10，均有两种已配置模型。原项目 `5269e95a-d8b7-4c66-b8fd-603be396ef4c` revision 18 未修改；旧隔离图书馆项目 revision 83 未修改。

制作助手去掉重复的一层展开，增加工作流方法、程序修订、诊断日志三个折叠入口。实体公开扩展事实进入 Agent 和固定 LLM；既有引用、快照、声音、前镜锚点与版本保护继续使用。

新增 SQLite 脱敏关联日志及 Agent 查询工具；错误响应包含请求与诊断 ID。新增应用/项目方法 skill 的提案、审阅采用、不可变版本与恢复；固定 LLM 请求冻结方法哈希与版本，Agent 加载相同方法。程序修改限定在短片应用预设服务端文件，先语法检查并保存差异，用户审阅后在临时源码副本做服务端回归，验证通过且源码/运行状态未变化才写入。写入日志覆盖替换源码前后进程中断的状态恢复，第三方源码变化不覆盖。修改需要应用重启；恢复经过同一提案/验证流程。

操作、状态、持久化、失效与恢复契约：[WORKFLOW_IMPROVEMENT.md](../../../film-editor/WORKFLOW_IMPROVEMENT.md)。效果问题继续登记在 WORKFLOW_GOAL.md，由用户判断后单独解决。

## 验证与证据

- `node --test film-editor/server/*.test.mjs`：40 项通过；`npm run build`：通过。
- 临时源码副本程序采用及恢复：均执行完整回归通过，实际应用源码不被该验收脚本修改。脚本：verify-program-workbench.mjs。
- 真实 Agent 根据刻意缺少剧本的失败日志定位前置条件，读取源码验证依据，保存仅本片的方法提案；一次误用总哈希被正确拒绝后恢复。随后明确工具说明并提供 baseHashes，减少误用。
- 浏览器真实点击采用方法、查询失败日志；下一轮真实 Agent 读取同版本，真实固定 LLM 剧本任务成功，systemPrompt 包含已采用的方法，input/response 哈希一致。未提交视频或视觉检查。
- 验收项目 `d6ae53a8-54c0-4a50-9810-fde682b45b29` revision 3，位于 4194；详细 ID 与哈希见 sean-workflow-improvement-acceptance.json。
- 部署前 SQLite 在线备份位于 `experiments/sean_film_agent_20261004/sean-before-delivery-{4190,4194}.sqlite`。部署记录见 sean-workflow-improvement-deployment.json。4190 浏览器验证助手、方法、程序入口及日志查询可用；原项目版本相同。

代码与证据 scoped commit 后提交 Task Center 待验收。未推送远端；SQLite、blobs、日志和历史媒体保留本地实验/运行目录。

## 验收反馈：找不到助手入口

新增页面右上角「制作助手」按钮，点击直接展开并滚动定位到现有面板。构建与4190真实浏览器点击通过（原折叠状态 false → true，发送按钮可见）。静态文件已更新，无需重启后端；原功能、项目和历史不变。
