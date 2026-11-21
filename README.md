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
- `app.js` — データから自然言語の分析と比較グラフを生成、47都道府県選択
- `assets/` — 柴犬総研ロゴ
- `data/indicators.json` — 出典付き検証済み統計の正本
- `data/school_survey_template.csv` — 学校調査テンプレート
- `scripts/update_data.py` — 公式出典の数値差分を安全に検査
- `.github/workflows/refresh-data.yml` — 毎週月曜10:20 JSTに検査

## 指標・出典
- パーソル総合研究所 2026年調査: https://rc.persol-group.co.jp/thinktank/data/telework-survey2026/
- 国土交通省 令和7年度調査: https://www.mlit.go.jp/report/press/toshikankyoteleworkr7.html
- 2016〜2025年の旧系列は出典定義の照合が不十分だったため廃止。現在の表示は `data/indicators.json` のみ。

**重要:** 民間調査の「正社員の実施率」と国交省の「直近1年間の実施率」「制度等に基づく雇用型テレワーカー割合」は異なる定義。比較した単一の時系列を作らないこと。またこれらはフルリモート採用率ではない。

## 今後の調査
`data/school_survey_template.csv` に、学校側に正式な確認・公開同意を得たデータを記載する。個人や特定の卒業生を識別できる情報は公開リポジトリに入れない。報告数を「発生率」と表記しない。

## ブランド素材
`assets/shibainu-soken-logo.svg` と `assets/shibainu-symbol.svg` は公開時の暫定ベクター版です。会話上で承認されたラスターロゴそのものではなく、ブランドを近似した素材です。承認済みロゴへの差し替えが必要です。
## 自動更新の運用
- 毎週月曜10:20 JSTにGitHub Actionsが出典ページをチェックし、同一年度版の数値修正を安全に特定できたときだけデータをコミットします。
- 出典の構造変更やアクセス失敗時は数値を上書きしません。エラーは実行ログに残します。
- 新年度の報告は設問・母集団を確認してから取り込みます。異なる調査定義の系列を自動結合しません。
- 更新がない場合は更新日も変更しません。
- GitHubの Actions > Refresh published statistics > Run workflow から手動実行可能です。
- 冒頭のメッセージはJavaScriptが出典付きJSONから自動生成し、外部AIサービスは必要ありません。
- 学校卒業生の転居実績は未収集のため推計で穴埋めしません。

## 都道府県別データ（2025年）
- `data/prefectures_2025.json`: 47都道府県のテレワーク経験率と二次集計に掲載された回答者数。
- 一次資料：総務省「令和7年通信利用動向調査」世帯構成員編・表35 https://www.e-stat.go.jp/stat-search/files?stat_infid=000040458853
- 転記元：https://aipowerranking.jp/telework-experience-rate-by-prefecture/
- 原統計表のCSVそのものを全件照合できなかったため、値の確定的な検証は未完了です。必ずこの制約を表示してください。
- 指標は「企業等に勤務する人の過去1年のテレワーク経験率」であり、フルリモート求人・地元居住のまま全国就職した数・出社回帰による転居数とは異なります。
- このデータの翌年分は現行の週次自動更新の対象外です。年次の新しい調査表を取得・照合した後に追加してください。
