#!/usr/bin/env python3
"""Build the self-hosted Chinese serif subset used by the Kami-style theme.

The full TsangerJinKai02 TTFs are ~19 MB each, far too large to serve. This
script collects every CJK character and full-width punctuation mark the site
actually renders (posts, pages, layouts, includes, _config.yml) and writes two
small WOFF2 subsets to assets/fonts/.

Re-run it after adding or editing posts, or new characters fall back to the
system font:

    python3 scripts/build_cjk_font_subset.py /path/to/dir-with-ttfs
    python3 scripts/build_cjk_font_subset.py --check   # fail if a char is missing

Source fonts (non-commercial use; personal site is fine):
    https://cdn.jsdelivr.net/gh/tw93/Kami@main/assets/fonts/TsangerJinKai02-W04.ttf
    https://cdn.jsdelivr.net/gh/tw93/Kami@main/assets/fonts/TsangerJinKai02-W05.ttf
Requires: pip install fonttools brotli
"""
import argparse
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "fonts"
WEIGHTS = {"W04": "jinkai-regular.woff2", "W05": "jinkai-medium.woff2"}
SOURCES = ["_posts", "_layouts", "_includes", "blog", "index.md", "_config.yml"]

# Must match the unicode-range in assets/css/custom.css.
RANGES = [
    (0x2E80, 0x2FFF),   # CJK radicals
    (0x3000, 0x303F),   # CJK punctuation
    (0x3400, 0x4DBF),   # CJK ext A
    (0x4E00, 0x9FFF),   # CJK unified ideographs
    (0xF900, 0xFAFF),   # CJK compatibility
    (0xFE30, 0xFE4F),   # CJK compatibility forms
    (0xFF00, 0xFFEF),   # full-width forms
    (0x201C, 0x201D),   # “ ”
    (0x2026, 0x2026),   # …
]


def in_range(ch):
    cp = ord(ch)
    return any(a <= cp <= b for a, b in RANGES)


def site_chars():
    chars = set()
    for name in SOURCES:
        p = ROOT / name
        files = [p] if p.is_file() else [f for f in p.rglob("*") if f.suffix in {".md", ".html", ".yml"}]
        for f in files:
            chars.update(c for c in f.read_text(encoding="utf-8") if in_range(c))
    return chars


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src", nargs="?", help="directory containing TsangerJinKai02-W04/W05.ttf")
    ap.add_argument("--check", action="store_true", help="verify the subsets cover the site")
    args = ap.parse_args()

    from fontTools.ttLib import TTFont
    chars = site_chars()

    if args.check:
        missing = set()
        for out in WEIGHTS.values():
            cmap = TTFont(OUT / out).getBestCmap()
            missing |= {c for c in chars if ord(c) not in cmap}
        if missing:
            print(f"{len(missing)} characters missing from subset: {''.join(sorted(missing))[:200]}")
            print("Re-run: python3 scripts/build_cjk_font_subset.py <dir-with-ttfs>")
            sys.exit(1)
        print(f"OK: subsets cover all {len(chars)} CJK characters on the site")
        return

    if not args.src:
        ap.error("src directory required (or use --check)")
    from fontTools import subset

    OUT.mkdir(parents=True, exist_ok=True)
    text = "".join(sorted(chars))
    for weight, out in WEIGHTS.items():
        opts = subset.Options()
        opts.flavor = "woff2"
        opts.layout_features = ["kern", "liga", "halt", "vhal", "palt"]
        opts.name_IDs = ["*"]
        font = subset.load_font(str(pathlib.Path(args.src) / f"TsangerJinKai02-{weight}.ttf"), opts)
        sub = subset.Subsetter(opts)
        sub.populate(text=text)
        sub.subset(font)
        subset.save_font(font, str(OUT / out), opts)
        print(f"{out}: {len(chars)} chars, {(OUT / out).stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
