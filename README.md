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

## 地域別の時系列と年次更新
- `data/company_adoption_regions_2019_2024.json`: 内閣官房が総務省「通信利用動向調査」を再掲した**企業テレワーク導入率**（2019〜2024年、都市部／地方部／全国）。個人の経験率と接続しない。
- 出典： https://www.cas.go.jp/jp/seisaku/chiikihatarakikata/contents/20260319/04_shiryou04.pdf （2ページ）。
- 2024年と2025年の総務省「世帯構成員編 表35」は双方公開済み。ただし2024年の47都道府県の原CSVは全件取得・検証ができていないため、2025年の暫定採録値に対する前年差を表示しない。
- `scripts/watch_prefecture_release.py` と `.github/workflows/watch-prefecture-data.yml`: 毎月1日11:15 JSTに次年度のe-Stat表35を確認し、確かな候補が見つかった場合だけGitHub Issueを作成。新データの**自動取込は行わない**。年次改定・母集団・設問・47地域分の検証後に取り込む。
- GitHub Actionsのcronはベストエフォート実行のため、定刻保証ではありません。出典のアクセス制限・HTML変更で新年度を検知できない場合は、推測値で補完しません。
