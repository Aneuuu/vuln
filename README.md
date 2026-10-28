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
```
./add_day.sh 某文件.md 2026-10-14   # 指定日期
./add_day.sh 2026-10-14.md          # 从文件名推断日期（否则用今天）
./add_day.sh --rebuild              # 手动放入 data/ 后重建索引
```
刷新页面即可看到，无需重启服务。

## 公网访问（可选）
`cloudflared tunnel --url http://localhost:8080` 可生成临时 trycloudflare 地址（需出站 TCP 7844）。
