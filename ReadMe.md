# 妖精からの招待状


## ローカル開発 (docker compose)

Google Cloud (Cloud SQL / Cloud Storage / Firebase Auth) をすべてローカルのコンテナで代替して起動できます。

```bash
# 1. 秘密情報を設定 (初回のみ)
cp .env.example .env   # SESSION_SECRET_KEY / OPENAI_API_KEY を記入

# 2. 起動
docker compose up -d --build

# 3. 停止 (データを消す場合は -v も付ける)
docker compose down
```

| サービス | URL | 代替対象 |
| --- | --- | --- |
| frontend | http://localhost:5173 | - |
| backend (API/docs) | http://localhost:8080/docs | - |
| PostgreSQL | localhost:5432 | Cloud SQL |
| fake-gcs-server | http://localhost:4443 | Cloud Storage |
| Firebase Auth Emulator | http://localhost:9099 | Firebase Authentication |
| Emulator UI | http://localhost:4000 | - |

- DB マイグレーション (`alembic upgrade head`) は backend 起動時に自動実行されます。
- 認証は Firebase Auth Emulator を使うため、ログインは画面のエミュレータ用ダイアログで適当なアカウントを作成すれば通ります。

## 解決したい課題

人は自分が知っている趣味しか選べない。

* YouTubeやSNSは過去の好みに最適化される
* Amazonや楽天も欲しいものを買う場所
* 「まだ知らない好きなこと」に出会えない
* 結果として休日の過ごし方が固定化する
* 趣味で検索してもよくある趣味しかない（実質AIのtemperature=0.9とか）

妖精は「ユーザーが選ばなかったはずの体験」を提案する。

## 流れ

* 個性を持った妖精が色々いる
  * マグロ料理が好きな妖精
  * 釣りが好きな妖精
  * 人間観察が好きな妖精
  * 自然体験が好きな妖精
* ただし、妖精の好みはユーザーには表示されない
* ユーザーは妖精を選び、空いている日とと予算を入力するとその妖精が選んだプランが予約される
* その旅を終えたユーザーはレビューを投稿する
  * レビューを書くと、そのレビューを参考に予約した人の料金の一部が還元される
* さらに、ユーザーは自分の趣味を「本」として書くことができる
  * これも還元される

## 設計

* User
* Fairy
* Plan
  * Activityの集合体
* Hobby：趣味(実質タグ)
  * 名前
* Activity：趣味の中での具体的な楽しみ方
  * 名前
  * 説明
  * 場所(GPS)
  * 所要時間
* Review
  * ユーザーが投稿したレビュー
* Notebook
  * ユーザーが書いた自分の趣味