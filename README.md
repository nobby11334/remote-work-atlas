# 地域雇用・リモートワーク Atlas

柴犬総研 / Shibainu Soken による公開データと学校現場の課題を扱う静的サイトMVP。

## 公開方法（GitHub Pages）
1. リポジトリ `nobby11334/remote-work-atlas` にサイトファイルは反映済み。
2. `main` ブランチ直下の `index.html` を公開対象にする。
3. Settings → Pages → Build and deployment → Deploy from a branch → `main` / `(root)` を指定する。
4. 数分後に `https://<ユーザー名>.github.io/remote-work-atlas/` で公開される。

## 構成
- `index.html` — 本文・出典リンク・調査項目
- `styles.css` — レスポンシブデザイン
- `app.js` — 2016–2025年の国交省データ可視化、47都道府県選択
- `assets/` — 柴犬総研ロゴ
- `data/` — データの記録と今後の入力用テンプレート

## 指標・出典
- パーソル総合研究所 2026年調査: https://rc.persol-group.co.jp/thinktank/data/telework-survey2026/
- 国土交通省 令和7年度調査: https://www.mlit.go.jp/report/press/toshikankyoteleworkr7.html
- 国交省「制度等に基づく雇用型テレワーカー割合」年次推移（2016–2025）: https://www.mlit.go.jp/report/press/content/001989216.pdf

**重要:** 民間調査の「正社員の実施率」と国交省の「直近1年間の実施率」「制度等に基づく雇用型テレワーカー割合」は異なる定義。比較した単一の時系列を作らないこと。またこれらはフルリモート採用率ではない。

## 今後の調査
`data/school_survey_template.csv` に、学校側に正式な確認・公開同意を得たデータを記載する。個人や特定の卒業生を識別できる情報は公開リポジトリに入れない。報告数を「発生率」と表記しない。

## ブランド素材
`assets/shibainu-soken-logo.svg` と `assets/shibainu-symbol.svg` は公開時の暫定ベクター版です。会話上で承認されたラスターロゴそのものではなく、ブランドを近似した素材です。承認済みロゴへの差し替えが必要です。