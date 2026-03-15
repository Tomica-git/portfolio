"""
dummy_images フォルダ内の画像ファイル名から
測定値（um前）と破断状態（um〜.jpg間）を抽出するスクリプト

ファイル名構造:
  84-50TE04①_X.XXum破断状態A.jpg
                ^^^^  ^^^^^^^^^
                測定値  破断状態
"""

import os
import re
from datetime import datetime

IMAGE_DIR = os.path.join(os.path.dirname(__file__), "..", "dummy_images")
OUTPUT_MD = os.path.join(os.path.dirname(__file__), "extraction_report.md")


def extract_info(filename: str) -> dict | None:
    """
    ファイル名から測定値と破断状態を抽出する。

    例:
      "84-12BM01②_5.34um破断状態B.jpg"
        → {"filename": "84-12BM01②_5.34um破断状態B.jpg",
           "measurement": 5.34, "fracture_state": "破断状態B"}

    抽出できない場合は None を返す。
    """
    # _〜um の間: 測定値  /  um〜.jpg の間: 破断状態
    pattern = r"_([0-9]+\.[0-9]+)um(.+?)\.jpg$"
    match = re.search(pattern, filename, re.IGNORECASE)
    if not match:
        return None

    return {
        "filename": filename,
        "measurement": float(match.group(1)),
        "fracture_state": match.group(2),
    }


def main():
    image_dir = os.path.abspath(IMAGE_DIR)
    filenames = sorted(
        f for f in os.listdir(image_dir) if f.lower().endswith(".jpg")
    )

    results = []
    for fname in filenames:
        info = extract_info(fname)
        if info:
            results.append(info)
        else:
            print(f"[SKIP] 抽出失敗: {fname}")

    total = len(filenames)
    success = len(results)
    skipped = total - success

    # ---- コンソール表示 ----
    print(f"{'測定値':>8}  {'破断状態'}")
    print("-" * 25)
    for r in results:
        print(f"{r['measurement']:>8.2f}  {r['fracture_state']}")
    print(f"\n結果: {success}/{total} 件 抽出成功")

    # ---- MDファイル生成 ----
    write_report(results, skipped_files=[f for f in filenames if extract_info(f) is None])

    return results


def write_report(results: list, skipped_files: list):
    total = len(results) + len(skipped_files)
    success = len(results)
    status = "成功" if len(skipped_files) == 0 else "一部失敗"

    lines = [
        "# 抽出結果レポート",
        "",
        f"実行日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## サマリー",
        "",
        f"| 項目 | 件数 |",
        f"|------|------|",
        f"| 対象ファイル総数 | {total} |",
        f"| 抽出成功 | {success} |",
        f"| 抽出失敗（スキップ） | {len(skipped_files)} |",
        f"| 結果 | **全{total}件 抽出{status}** |" if len(skipped_files) == 0
            else f"| 結果 | {status} |",
        "",
        "## 抽出データ一覧",
        "",
        "| # | ファイル名 | 測定値 (um) | 破断状態 |",
        "|---|-----------|------------|---------|",
    ]

    for i, r in enumerate(results, 1):
        lines.append(f"| {i} | {r['filename']} | {r['measurement']:.2f} | {r['fracture_state']} |")

    if skipped_files:
        lines += [
            "",
            "## 抽出失敗ファイル",
            "",
        ]
        for f in skipped_files:
            lines.append(f"- {f}")

    md_path = os.path.abspath(OUTPUT_MD)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(f"MDファイル生成: {md_path}")


if __name__ == "__main__":
    main()
