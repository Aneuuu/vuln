# 漏洞日报 · 运维安全漏洞中文日报存档

纯静态站点，无需构建工具，浏览器端渲染 Markdown。

## 目录
- `index.html` / `style.css` / `app.js`：页面（时间线 + 单日视图）
- `data/YYYY-MM-DD.md`：每日一份 Markdown（`#` 标题，`##` 分组，`-` 条目，`[文字](链接)`）
- `data/index.json`：日期索引（由脚本自动生成）
- `add_day.sh` / `add_day.py`：追加新的一天
- `serve.sh`：本地启动服务

## 本地部署
1. 需要 Python 3（无第三方依赖）。解压：`unzip vuln-digest.zip && cd vuln-digest`
2. 启动：`./serve.sh 8080`（或 `python3 -m http.server 8080`）
3. 浏览器打开 http://localhost:8080
   注意：不能直接双击打开 index.html（file:// 下 fetch 会被拦截），需通过 HTTP 服务访问。
4. 后台常驻：`setsid nohup ./serve.sh 8080 >/tmp/vuln-digest.log 2>&1 &`

## 添加新的一天
脚本会先从 GitHub 仓库（默认 `Aneuuu/vuln` 的 `main`）拉取 `data/` 到本地，再追加并重建索引：
```
./add_day.sh 某文件.md 2026-10-14   # 拉取 → 追加指定日期 → 重建索引
./add_day.sh 2026-10-14.md          # 从文件名推断日期（否则用今天）
./add_day.sh --rebuild              # 拉取 → 重建索引（手动放入 data/ 后用）
./add_day.sh --pull                 # 只拉取并重建索引
./add_day.sh --rebuild --no-pull    # 离线，跳过拉取
```
- 环境变量：`VULN_REPO`（默认 `Aneuuu/vuln`）、`VULN_BRANCH`（默认 `main`）、`GITHUB_TOKEN`（私有仓库或避免限流时设置）。只用 Python 标准库，不需要装 git。
- 合并规则：本地缺的直接下载；本地自上次同步后没改过的用远端覆盖；本地改过的保留本地；两边都改过时保留本地，远端另存为 `data/<日期>.remote.md`。本次追加的那一天总以传入文件为准；只在本地有的文件不会删；`index.json` 总是本地重建。同步状态记在 `data/.sync.json`。
- 拉取失败（断网、限流）只打警告，不影响追加和重建。

刷新页面即可看到，无需重启服务。

## 公网访问（可选）
`cloudflared tunnel --url http://localhost:8080` 可生成临时 trycloudflare 地址（需出站 TCP 7844）。
