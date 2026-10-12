# PromptCard Studio fork 开发约定

- 上游：`monineko/PromptCard-Studio`；用户确认的公开 fork：`sutanna233/PromptCard-Studio-fork`。原私有部署备份仓库保持原样。
- GitHub issue、PR、推送明确指向 fork，不能向上游误发本机部署记录。功能分支使用 `codex/` 前缀。
- 用户确认功能：固定画师搭配探索。允许固定一个或多个画师及权重（例如 lk149），其他画师支持随机搭配和逐个搭配；保存 Card 包含完整画师串。
- 固定画师不得被随机替换、重复抽取或在深度探索中丢失；保留历史任务兼容性和原始提示词。
- Token、config.json、workspace.json、用户卡片/图库/Vibe、运行环境、模型、日志和测试数据不得提交到公开仓库。
- 大文件、环境和构建均在 J 盘。前端使用 Node.js `D:\js\node.exe`、锁文件安装和 `npm run build`；后端测试优先使用已部署便携 Python `J:\ai\PromptCard-Studio\runtime\python\python.exe`。
- 不消耗用户 NovelAI 点数进行验证：用 unittest/mock 检查真实生成调用收到的提示词、候选分布与 Card 内容；浏览器验证界面并停止在生成之前。
- `backend/tests` 是现有 unittest 测试；前端 build 包含 TypeScript 检查。使用 browser-harness 验证实际浏览器界面。
- 上游跟踪 frontend/dist，构建产物必须随前端源码更新提交，使源码包无需 Node.js 也能启动；不要忽略该目录的新资源。
- 新搭配设置保存在各轮 algorithm/algorithm_snapshot；逐个模式完整覆盖池，固定项不计入搭配数量。最多搭配数可设 1，固定项与搭配项共不超过 30。
- 同种子比较选项固化每轮 comparison_seed，包括 seed=0；旧任务继续沿用原有逐张递增或随机行为。
- 2026-10-12 验证：71 项画风探索 unittest、2 项生成协调器 unittest及前端构建通过；浏览器完成固定 lk149、逐个搭配、相同种子、任务创建及追加轮次，未发起付费生成。
- 用户实际使用的 `J:\ai\PromptCard-Studio` 已更新后端与前端到此功能，地址仍为 `http://127.0.0.1:14419`；旧程序文件备份在 `J:\ai\_downloads\PromptCard-Studio\before-fixed-artists-20261012`，用户 config/workspace 文件校验未变化。
