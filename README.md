# 真・こうかとん無双改
## 実行環境の必要条件
* python >= 3.10
* pygame >= 2.1

## ゲームの概要
真・こうかとん無双改は、第四回までに作成した真・こうかとん無双にさらなる追加機能を加えたものである。
こうかとんを操作して画面上部から出現する敵ビームで撃墜し、スコアを獲得する。敵機は様々な色の爆弾を発射し、こちらを狙ってくる。敵の爆弾はビームを撃って迎撃するか移動で回避しよう。また、こうかとんは獲得したスコアを消費して、重力球を発生させたり無敵になったり、様々な特殊能力を発動することが出来る。一定時間たつとボスが出現し、これを倒すことでゲームクリアとなる。

## 操作方法
* 十字キー：移動
* スペースキー：ビーム
* 左シフトキー＋スペースキー：ビーム五連射
* 左シフトキー＋十字キー：高速移動
* (スコア50以上)でTabキー:重力球

## ゲームの実装
### 共通基本機能
* Bird:主人公キャラクター（こうかとん）に関するクラス
* Beam:主人公キャラクターが発射するビームに関するクラス
* NeoBeam:任意の数のビームをまとめて発射するためのクラス
* Enemy:敵機（UFO）に関するクラス
* Bomb:敵機が投下する爆弾に関するクラス
* Explosion:敵機にビームが当たった時の爆発を発生させるクラス
* Gravity:重力球を発生させるクラス
* Score:スコアを表示するためのクラス

### 担当追加機能
#### 岡部(C0B22032)
一定時間が経過したときにボス戦を開始するものである。ボスは特殊な爆弾を発射する。この爆弾はこうかとんのビームでは撃ち落とすことが出来ず、重力球または無敵状態でのみ撃ち落とすことが出来る。ボスはHPを50持っていて、ビームが直撃するたびに1ダメージ受ける。ボスのHPを0にした場合はスコアを1000加算してゲームを終了する。
* Boss:敵のボスに関するクラス
* Boss_bomb:敵のボスが投下する爆弾に関するクラス

#### 篠崎(C0A22078)
ゲームをスタートしたときに流れる背景BGMの追加とビーム、敵や爆弾を撃破したときの爆発、重力球、やられた時のSEです。

#### 
大野(C0B22028)一定時間後に背景が変化する機能を追加した。背景画像は朝、昼、夜の三種類であり、３０秒ごとに背景画像を切り替えてループする。また、ウィンドウ画面にカウントアップタイマーを追加した。
* change_background関数:表示する背景画像を変更する関数
* Timerクラス:プログラム開始からの経過時間を計算するクラス

#### 宮本(C0B22144)
* 残機に関するクラス：元の残機を３に設定し、スコアが300の倍数に到達すると残機が1増える。敵の攻撃に当たると残機が1減る。
* GAME OVERの表示：残機が0になったら画面の中央にGAME OVERを表示する。

#### 船渡川(C0B20138)
* スコアが１００以上の時、敵の爆弾が壁で跳ね返ります。
* スコアが２００以上の時、壁で爆弾が跳ね返ると加速します。



## 参考文献
* なし