#!/usr/bin/env python3
"""用法:
  ./add_day.py <file.md> [YYYY-MM-DD]   先从 GitHub 拉取 data/，再追加这一天并重建索引
                                        (无日期则取文件名中的日期, 否则今天)
  ./add_day.py --rebuild                先拉取，再重建 data/index.json
  ./add_day.py --pull                   只从 GitHub 拉取 data/ 并重建索引
  加 --no-pull 可跳过拉取（离线时用）

环境变量: VULN_REPO (默认 Aneuuu/vuln)  VULN_BRANCH (默认 main)
          GITHUB_TOKEN (可选；私有仓库或避免限流时设置)

拉取规则(三方合并, 记录在 data/.sync.json):
  - 本地没有的文件: 直接下载
  - 本地自上次同步后没改过: 用远端版本覆盖
  - 本地改过而远端没变: 保留本地
  - 两边都改了: 保留本地, 远端版本另存为 data/<日期>.remote.md 并提示
  - 本次要追加的那一天: 总是以本地传入的文件为准
  - 只在本地存在的文件不会被删除; 远端的 index.json 不下载, 由本地重建
  - 拉取失败(断网/限流)只打警告, 不影响追加和重建"""
import sys, os, re, io, json, shutil, hashlib, tarfile, datetime, urllib.request

BASE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(BASE, "data")
SYNC = os.path.join(D, ".sync.json")
REPO = os.environ.get("VULN_REPO", "Aneuuu/vuln")
BRANCH = os.environ.get("VULN_BRANCH", "main")
DAY_RE = re.compile(r"(\d{4}-\d{2}-\d{2})\.md")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def read_bytes(p):
    with open(p, "rb") as fh:
        return fh.read()


def write_atomic(p, b):
    tmp = p + ".tmp"
    with open(tmp, "wb") as fh:
        fh.write(b)
    os.replace(tmp, p)


def fetch_remote():
    """下载仓库 tarball, 返回 {文件名: bytes}, 只取 data/YYYY-MM-DD.md。"""
    tok = os.environ.get("GITHUB_TOKEN")
    if tok:
        url = f"https://api.github.com/repos/{REPO}/tarball/{BRANCH}"
        hdr = {"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json"}
    else:
        url = f"https://codeload.github.com/{REPO}/tar.gz/refs/heads/{BRANCH}"
        hdr = {}
    hdr["User-Agent"] = "vuln-digest-add-day"
    with urllib.request.urlopen(urllib.request.Request(url, headers=hdr), timeout=60) as r:
        blob = r.read()
    out = {}
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as tf:
        for m in tf.getmembers():
            parts = m.name.split("/")
            # <repo>-<sha>/data/YYYY-MM-DD.md
            if m.isfile() and len(parts) == 3 and parts[1] == "data" and DAY_RE.fullmatch(parts[2]):
                out[parts[2]] = tf.extractfile(m).read()
    return out


def pull(skip=None):
    os.makedirs(D, exist_ok=True)
    try:
        remote = fetch_remote()
    except Exception as e:  # 断网、限流、仓库不可见
        print(f"警告: 从 GitHub 拉取失败, 仅使用本地数据 ({REPO}@{BRANCH}: {e})", file=sys.stderr)
        return False
    state = {}
    if os.path.exists(SYNC):
        try:
            state = json.load(open(SYNC, encoding="utf-8"))
        except Exception:
            state = {}
    added = updated = kept = conflicts = 0
    for name, rb in sorted(remote.items()):
        rh = sha(rb)
        p = os.path.join(D, name)
        if name == skip:
            continue
        if not os.path.exists(p):
            write_atomic(p, rb); added += 1
        else:
            lh = sha(read_bytes(p))
            base = state.get(name)
            if lh == rh:
                pass                                    # 一致
            elif base is not None and lh == base:
                write_atomic(p, rb); updated += 1       # 本地没改过, 用远端
            elif base is not None and rh == base:
                kept += 1; continue                     # 只有本地改过, 保留本地
            else:                                       # 两边都改过, 或首次同步就不同
                write_atomic(os.path.join(D, name[:-3] + ".remote.md"), rb); conflicts += 1
                print(f"  冲突: {name} 本地与远端不同, 已保留本地, 远端另存为 {name[:-3]}.remote.md")
                continue
        state[name] = rh
    json.dump(state, open(SYNC, "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
    print(f"已从 GitHub 拉取 {REPO}@{BRANCH}: 远端 {len(remote)} 天, 新增 {added}, 更新 {updated}, 保留本地改动 {kept}, 冲突 {conflicts}")
    return True


def rebuild():
    days = []
    for f in sorted(os.listdir(D), reverse=True):
        m = DAY_RE.fullmatch(f)
        if not m:
            continue
        txt = open(os.path.join(D, f), encoding="utf-8").read()
        t = re.search(r"^#\s+(.+)$", txt, re.M)
        secs = re.findall(r"^##\s+(.+)$", txt, re.M)
        days.append({"date": m[1], "title": t[1].strip() if t else m[1], "sections": secs,
                     "links": len(re.findall(r"\]\(http", txt))})
    tmp = os.path.join(D, "index.json.tmp")
    json.dump(days, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    os.replace(tmp, os.path.join(D, "index.json"))
    print(f"index.json: {len(days)} 天")


if __name__ == "__main__":
    a = sys.argv[1:]
    no_pull = "--no-pull" in a
    a = [x for x in a if x != "--no-pull"]
    if not a:
        sys.exit(__doc__)
    if a[0] in ("--rebuild", "--pull"):
        if not no_pull:
            pull()
    else:
        src = a[0]
        date = a[1] if len(a) > 1 else (re.search(r"\d{4}-\d{2}-\d{2}", os.path.basename(src)) or [datetime.date.today().isoformat()])[0]
        datetime.date.fromisoformat(date)
        os.makedirs(D, exist_ok=True)
        dst = os.path.join(D, date + ".md")
        body = read_bytes(src)  # 先读入, 防止拉取时被覆盖
        if not no_pull:
            pull(skip=date + ".md")
        write_atomic(dst, body)
        print("已添加", dst)
    rebuild()
