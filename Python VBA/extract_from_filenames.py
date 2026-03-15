"""
dummy_images フォルダ内の画像ファイル名を解析し、
自動入力マクロ.xlsm「貼り付け場所変換」シートと同等のデータを CSV で出力するスクリプト

ファイル名構造:
  84-50TE04①_X.XXum破断状態A.jpg
  │    ││  ││ │    │
  │    ││  ││ │    └── 破断状態（um〜.jpg 間）
  │    ││  ││ └─────── 測定値（_〜um 間）
  │    ││  │└────────── 破断方向（①②③）
  │    ││  └─────────── サンプル番号（8-9文字目）
  │    │└──────────────── 取得位置（6-7文字目）
  └────────────────────── ウェハ型番略称（1-5文字目）
"""

import csv
import os
import re

IMAGE_DIR = os.path.join(os.path.dirname(__file__), "..", "dummy_images")
OUTPUT_CSV = os.path.join(os.path.dirname(__file__), "output.csv")

# ---- 変換テーブル（Excel の IF ネストと同等） ----

MODEL_MAP = {
    "80-50": "DH260507580-50",
    "84-12": "CE260402384-12",
    "84-50": "DCH003484-50",
}

LOCATION_MAP = {
    "TE": "Top Edge",
    "BM": "Bottom Middle",
    "Ct": "Center",
    "LE": "Left Edge",
    "RE": "Right Edge",
}

DIRECTION_CHARS = ("①", "②", "③")


def parse_filename(filename: str) -> dict | None:
    """
    ファイル名を解析して全列の値を返す。
    パターンに合致しない場合は None。

    対応列:
      A: ファイル名
      B: 正式型番
      C: 取得位置
      D: サンプル番号
      E: 破断方向
      F: 測定値
      G: 破断状態
    """
    pattern = r"_([0-9]+\.[0-9]+)um(.+?)\.jpg$"
    match = re.search(pattern, filename, re.IGNORECASE)
    if not match:
        return None

    # B列: 正式型番（先頭5文字で照合）
    model_code = filename[:5]
    official_model = MODEL_MAP.get(model_code, "該当なし")

    # C列: 取得位置（6-7文字目で照合）
    location_code = filename[5:7]
    location = LOCATION_MAP.get(location_code, "該当なし")

    # D列: サンプル番号（8-9文字目を数値に変換）
    sample_num = int(filename[7:9])

    # E列: 破断方向（①②③ を検索して抽出）
    direction = "該当なし"
    for ch in DIRECTION_CHARS:
        idx = filename.find(ch)
        if idx != -1:
            direction = ch
            break

    # F列: 測定値（_ 〜 um 間）
    measurement = float(match.group(1))

    # G列: 破断状態（um 〜 .jpg 間）
    fracture_state = match.group(2)

    return {
        "ファイル名": filename,
        "正式型番": official_model,
        "取得位置": location,
        "サンプル番号": sample_num,
        "破断方向": direction,
        "測定値": measurement,
        "破断状態": fracture_state,
    }


def main():
    image_dir = os.path.abspath(IMAGE_DIR)
    filenames = sorted(
        f for f in os.listdir(image_dir) if f.lower().endswith(".jpg")
    )

    rows = []
    skipped = []
    for fname in filenames:
        row = parse_filename(fname)
        if row:
            rows.append(row)
        else:
            skipped.append(fname)
            print(f"[SKIP] 解析失敗: {fname}")

    # ---- CSV 出力 ----
    csv_path = os.path.abspath(OUTPUT_CSV)
    headers = ["ファイル名", "正式型番", "取得位置", "サンプル番号", "破断方向", "測定値", "破断状態"]
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)

    # ---- コンソール表示 ----
    print(f"{'ファイル名':<35} {'正式型番':<18} {'取得位置':<16} {'番号':>4}  {'方向'}  {'測定値':>6}  {'破断状態'}")
    print("-" * 105)
    for r in rows:
        print(
            f"{r['ファイル名']:<35} {r['正式型番']:<18} {r['取得位置']:<16} "
            f"{r['サンプル番号']:>4}  {r['破断方向']}  {r['測定値']:>6.2f}  {r['破断状態']}"
        )
    print(f"\n結果: {len(rows)}/{len(filenames)} 件 成功  |  スキップ: {len(skipped)} 件")
    print(f"CSV 出力: {csv_path}")


if __name__ == "__main__":
    main()
