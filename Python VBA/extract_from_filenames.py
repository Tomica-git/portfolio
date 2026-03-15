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

IMAGE_DIR = os.path.join(os.path.dirname(__file__), "..", "dummy_images")


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

    # ---- 結果表示 ----
    print(f"{'測定値':>8}  {'破断状態'}")
    print("-" * 25)
    for r in results:
        print(f"{r['measurement']:>8.2f}  {r['fracture_state']}")

    return results


if __name__ == "__main__":
    main()
