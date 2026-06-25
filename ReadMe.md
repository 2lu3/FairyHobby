# 妖精からの招待状


## ローカル開発 (docker compose)

本番の Google Cloud (Cloud SQL / Cloud Storage / Firebase Auth) に接続して起動します。

```bash
# 1. 接続情報を設定 (初回のみ)
#    - backend/.env に Cloud SQL / GCS / OpenAI 等の設定
#    - backend/ServiceAccountKey.json を配置
#    - cp frontend/.env.example frontend/.env して Firebase 設定を記入

# 2. 起動
docker compose up -d --build

# 3. 停止
docker compose down
```

| サービス | URL |
| --- | --- |
| frontend | http://localhost:5173 |
| backend (API/docs) | http://localhost:8080/docs |

- DB マイグレーション (`alembic upgrade head`) は backend 起動時に自動実行されます。
- 認証は本番の Firebase Auth を使うため、Google アカウントでログインします。

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