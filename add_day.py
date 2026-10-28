#!/usr/bin/env python3
"""用法: ./add_day.py <file.md> [YYYY-MM-DD]   (无日期则取文件名中的日期, 否则今天)
   ./add_day.py --rebuild   仅重建 data/index.json"""
import sys, os, re, json, shutil, datetime
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
def rebuild():
    days = []
    for f in sorted(os.listdir(D), reverse=True):
        m = re.fullmatch(r"(\d{4}-\d{2}-\d{2})\.md", f)
        if not m: continue
        txt = open(os.path.join(D, f), encoding="utf-8").read()
        t = re.search(r"^#\s+(.+)$", txt, re.M)
        secs = re.findall(r"^##\s+(.+)$", txt, re.M)
        days.append({"date": m[1], "title": t[1].strip() if t else m[1], "sections": secs,
                     "links": len(re.findall(r"\]\(http", txt))})
    json.dump(days, open(os.path.join(D, "index.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"index.json: {len(days)} 天")
if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] != "--rebuild":
        src = a[0]
        date = a[1] if len(a) > 1 else (re.search(r"\d{4}-\d{2}-\d{2}", os.path.basename(src)) or [datetime.date.today().isoformat()])[0]
        datetime.date.fromisoformat(date)
        dst = os.path.join(D, date + ".md")
        if os.path.abspath(src) != dst: shutil.copyfile(src, dst)
        print("已添加", dst)
    elif not a: sys.exit(__doc__)
    rebuild()
