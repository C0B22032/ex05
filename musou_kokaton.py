import math
import random
import sys
import time

import pygame as pg

WIDTH = 1600  # ゲームウィンドウの幅
HEIGHT = 900  # ゲームウィンドウの高さ

# Pygameの初期化と画面設定
pg.init()
screen = pg.display.set_mode((WIDTH, HEIGHT))

# 背景画像（朝・夕・夜）の読込みと拡大
bg_img_morning = pg.transform.scale(pg.image.load("ex05/bg/bg_pattern2_aozora.png").convert(), (WIDTH, HEIGHT))
bg_img_evening = pg.transform.scale(pg.image.load("ex05/bg/bg_pattern3_yuyake.png").convert(), (WIDTH, HEIGHT))
bg_img_night = pg.transform.scale(pg.image.load("ex05/bg/bg_pattern4_yoru.png").convert(), (WIDTH, HEIGHT))

# 背景画像をリストに格納
bg_imgs_lst = [bg_img_morning, bg_img_evening, bg_img_night]

# 表示する背景画像の番号（0:朝 1:夕 2:夜）
bg_img_i = 0

def check_bound(obj: pg.Rect) -> tuple[bool, bool]:
    """
    オブジェクトが画面内か画面外かを判定し，真理値タプルを返す
    引数 obj：オブジェクト（爆弾，こうかとん，ビーム）SurfaceのRect
    戻り値：横方向，縦方向のはみ出し判定結果（画面内：True／画面外：False）
    """
    yoko, tate = True, True
    if obj.left < 0 or WIDTH < obj.right:  # 横方向のはみ出し判定
        yoko = False
    if obj.top < 0 or HEIGHT < obj.bottom:  # 縦方向のはみ出し判定
        tate = False
    return yoko, tate


def calc_orientation(org: pg.Rect, dst: pg.Rect) -> tuple[float, float]:
    """
    orgから見て，dstがどこにあるかを計算し，方向ベクトルをタプルで返す
    引数1 org：爆弾SurfaceのRect
    引数2 dst：こうかとんSurfaceのRect
    戻り値：orgから見たdstの方向ベクトルを表すタプル
    """
    x_diff, y_diff = dst.centerx-org.centerx, dst.centery-org.centery
    norm = math.sqrt(x_diff**2+y_diff**2)
    return x_diff/norm, y_diff/norm


class Bird(pg.sprite.Sprite):
    """
    ゲームキャラクター（こうかとん）に関するクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -1),
        pg.K_DOWN: (0, +1),
        pg.K_LEFT: (-1, 0),
        pg.K_RIGHT: (+1, 0),
    }

    def __init__(self, num: int, xy: tuple[int, int]):
        """
        こうかとん画像Surfaceを生成する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 xy：こうかとん画像の位置座標タプル
        """
        super().__init__()
        img0 = pg.transform.rotozoom(pg.image.load(f"ex05/fig/{num}.png"), 0, 2.0)
        img = pg.transform.flip(img0, True, False)  # デフォルトのこうかとん
        self.imgs = {
            (+1, 0): img,  # 右
            (+1, -1): pg.transform.rotozoom(img, 45, 1.0),  # 右上
            (0, -1): pg.transform.rotozoom(img, 90, 1.0),  # 上
            (-1, -1): pg.transform.rotozoom(img0, -45, 1.0),  # 左上
            (-1, 0): img0,  # 左
            (-1, +1): pg.transform.rotozoom(img0, 45, 1.0),  # 左下
            (0, +1): pg.transform.rotozoom(img, -90, 1.0),  # 下
            (+1, +1): pg.transform.rotozoom(img, -45, 1.0),  # 右下
        }
        self.dire = (+1, 0)
        self.image = self.imgs[self.dire]
        self.rect = self.image.get_rect()
        self.rect.center = xy
        self.speed = 10
        self.state = "normal"
        self.hyper_life = -1

    def change_img(self, num: int, screen: pg.Surface):
        """
        こうかとん画像を切り替え，画面に転送する
        引数1 num：こうかとん画像ファイル名の番号
        引数2 screen：画面Surface
        """
        self.image = pg.transform.rotozoom(pg.image.load(f"ex05/fig/{num}.png"), 0, 2.0)
        screen.blit(self.image, self.rect)
    
    def change_state(self, state: str, hyper_life: int):    # 追加機能3
        """
        追加機能3：肉体強化
        引数1 state：状態str型 (normal or hyper)
        引数2 hyper_life：発動時間int型
        """
        self.state = state
        self.hyper_life = hyper_life
        if (hyper_life >= 0):
            hyper_life -= 1

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        押下キーに応じてこうかとんを移動させる
        引数1 key_lst：押下キーの真理値リスト
        引数2 screen：画面Surface
        """
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                self.rect.move_ip(+self.speed*mv[0], +self.speed*mv[1])
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        if check_bound(self.rect) != (True, True):
            for k, mv in __class__.delta.items():
                if key_lst[k]:
                    self.rect.move_ip(-self.speed*mv[0], -self.speed*mv[1])
        if not (sum_mv[0] == 0 and sum_mv[1] == 0):
            self.dire = tuple(sum_mv)
            self.image = self.imgs[self.dire]
        if (self.state == "hyper"): # 追加機能3
            self.image = pg.transform.laplacian(self.image)
            self.hyper_life -= 1
        if (self.hyper_life < 0):
            self.change_state("normal", -1)
        screen.blit(self.image, self.rect)
    
    def get_direction(self) -> tuple[int, int]:
        return self.dire
    

class Bomb(pg.sprite.Sprite):
    """
    爆弾に関するクラス
    """
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]

    def __init__(self, emy: "Enemy", bird: Bird):
        """
        爆弾円Surfaceを生成する
        引数1 emy：爆弾を投下する敵機
        引数2 bird：攻撃対象のこうかとん
        """
        super().__init__()
        rad = random.randint(10, 50)  # 爆弾円の半径：10以上50以下の乱数
        color = random.choice(__class__.colors)  # 爆弾円の色：クラス変数からランダム選択
        self.image = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.image, color, (rad, rad), rad)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        # 爆弾を投下するemyから見た攻撃対象のbirdの方向を計算
        self.vx, self.vy = calc_orientation(emy.rect, bird.rect)  
        self.rect.centerx = emy.rect.centerx
        self.rect.centery = emy.rect.centery+emy.rect.height/2
        self.speed = 6

    def update(self):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(+self.speed*self.vx, +self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()


class Beam(pg.sprite.Sprite):
    """
    ビームに関するクラス
    """
    def __init__(self, bird: Bird, angle0: float=0.0):
        """
        ビーム画像Surfaceを生成する
        引数 bird：ビームを放つこうかとん
        引数 angle0 ビームの回転角度
        """
        super().__init__()
        self.vx, self.vy = bird.get_direction()
        angle = math.degrees(math.atan2(-self.vy, self.vx)) + angle0
        self.image = pg.transform.rotozoom(pg.image.load(f"ex05/fig/beam.png"), angle, 2.0)
        self.vx = math.cos(math.radians(angle))
        self.vy = -math.sin(math.radians(angle))
        self.rect = self.image.get_rect()
        self.rect.centery = bird.rect.centery+bird.rect.height*self.vy
        self.rect.centerx = bird.rect.centerx+bird.rect.width*self.vx
        self.speed = 10

    def update(self):
        """
        ビームを速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(+self.speed*self.vx, +self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()


class NeoBeam:
    """
    複数のビームに関するクラス
    引数 bird:こうかとん
    引数 num:ビームの数
    """
    def __init__(self, bird: Bird, num: int):
        self.num = num
        self.bird = bird
        self.beams = list()

    def gen_beams(self):
        """
        ビームを-50°~+51°の間で角度をつける
        リストbeamsに入れてリストbeamsを返す
        """
        for angle in range(-50, +51, int(100/(self.num-1))):
            self.beams.append(Beam(self.bird, angle))
        return self.beams

class Explosion(pg.sprite.Sprite):
    """
    爆発に関するクラス
    """
    def __init__(self, obj: "Bomb|Enemy", life: int):
        """
        爆弾が爆発するエフェクトを生成する
        引数1 obj：爆発するBombまたは敵機インスタンス
        引数2 life：爆発時間
        """
        super().__init__()
        img = pg.image.load("ex05/fig/explosion.gif")
        self.imgs = [img, pg.transform.flip(img, 1, 1)]
        self.image = self.imgs[0]
        self.rect = self.image.get_rect(center=obj.rect.center)
        self.life = life

    def update(self):
        """
        爆発時間を1減算した爆発経過時間_lifeに応じて爆発画像を切り替えることで
        爆発エフェクトを表現する
        """
        self.life -= 1
        self.image = self.imgs[self.life//10%2]
        if self.life < 0:
            self.kill()


class Enemy(pg.sprite.Sprite):
    """
    敵機に関するクラス
    """
    imgs = [pg.image.load(f"ex05/fig/alien{i}.png") for i in range(1, 4)]
    
    def __init__(self):
        super().__init__()

        self.image = random.choice(__class__.imgs)
        self.rect = self.image.get_rect()
        self.rect.center = random.randint(0, WIDTH), 0
        self.vy = +6
        self.bound = random.randint(50, HEIGHT/2)  # 停止位置
        self.state = "down"  # 降下状態or停止状態
        self.interval = random.randint(50, 300)  # 爆弾投下インターバル

    def update(self):
        """
        敵機を速度ベクトルself.vyに基づき移動（降下）させる
        ランダムに決めた停止位置_boundまで降下したら，_stateを停止状態に変更する
        引数 screen：画面Surface
        """
        if self.rect.centery > self.bound:
            self.vy = 0
            self.state = "stop"
        self.rect.centery += self.vy


class Boss(pg.sprite.Sprite):
    """
    ボスに関するクラス
    """
    img = pg.transform.rotozoom(pg.image.load(f"ex05/fig/alien{1}.png"),0,5.0)#通常の敵の五倍の大きさ
    
    def __init__(self):
        super().__init__()
        self.flag=0#場に一体だけ出現させるためのフラグ
        self.boss_hp=50#ボスのＨＰ
        self.rect = self.img.get_rect()
        self.rect.center = WIDTH/2, 20
        self.image =__class__.img
        
        self.rect.center = WIDTH/2, 0
        self.vy = +6
        self.bound = 200 # 停止位置(固定)
        self.state = "down"  # 降下状態or停止状態
        self.interval = random.randint(20, 100)  # 爆弾投下インターバル

    def damage(self,down):
        self.boss_hp-=1 #ダメージを受けるたびボスのＨＰを減少

    def update(self):
        """
        ボスを速度ベクトルself.vyに基づき移動（降下）させる
        ランダムに決めた停止位置_boundまで降下したら，_stateを停止状態に変更する
        引数 screen：画面Surface
        """
        if self.rect.centery > self.bound: #ここは通常の敵機と同じ
            self.vy = 0
            self.state = "stop"
        self.rect.centery += self.vy


class Boss_bomb(pg.sprite.Sprite):
    """
    ボスが投下する爆弾に関するクラス
    """
    def __init__(self, boss: "Boss", bird: Bird):
        """
        爆弾円Surfaceを生成する
        引数1 boss：爆弾を投下する敵機ボス
        引数2 bird：攻撃対象のこうかとん
        """
        super().__init__()
          # 爆弾円の半径：10以上50以下の乱数
        rads =random.randint(10,50)
        color = (0,0,1)  # 爆弾円の色：黒
        self.image = pg.Surface((2*rads, 2*rads))
        pg.draw.circle(self.image, color, (rads, rads), rads)
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()
        # 爆弾を投下するボスから見た攻撃対象のbirdの方向を計算
        self.vx, self.vy = calc_orientation(boss.rect, bird.rect)  
        self.rect.centerx = boss.rect.centerx+random.randrange(-200,200)
        self.rect.centery = boss.rect.centery+boss.rect.height/2
        self.speed = random.randint(2,10)#爆弾の速度を２～１０の乱数でランダムに設定

    def update(self):
        """
        爆弾を速度ベクトルself.vx, self.vyに基づき移動させる
        引数 screen：画面Surface
        """
        self.rect.move_ip(+self.speed*self.vx, +self.speed*self.vy)
        if check_bound(self.rect) != (True, True):
            self.kill()


class Gravity(pg.sprite.Sprite):
    """
    重力球を発生させるクラス
    """
    delta = {  # 押下キーと移動量の辞書
        pg.K_UP: (0, -1),
        pg.K_DOWN: (0, +1),
        pg.K_LEFT: (-1, 0),
        pg.K_RIGHT: (+1, 0),
    }

    def __init__(self,bird:Bird,life:int):
        """
        引数１：発生対象のこうかとんbird
        引数２：発動時間life
        """
        super().__init__()
        rad = 200
        color = (1,0,0)#(0,0,0)だと透過してしまうため(1,0,0)
        self.image = pg.Surface((2*rad, 2*rad))
        pg.draw.circle(self.image, color, (rad, rad), rad)
        self.image.set_alpha(100)
        self.rect = self.image.get_rect()
        self.image.set_colorkey((0, 0, 0))
        self.rect.center = bird.rect.center#中心,速度をこうかとんと合わせる
        self.life = life
        self.speed = 10

    def update(self, key_lst: list[bool], screen: pg.Surface):
        """
        lifeが０になった場合は消滅する
        こうかとんの移動に追従する
        """
        self.life -= 1
        if self.life < 0:
            self.kill()
        sum_mv = [0, 0]
        for k, mv in __class__.delta.items():
            if key_lst[k]:
                self.rect.move_ip(+self.speed*mv[0], +self.speed*mv[1])
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]  
        screen.blit(self.image, self.rect)


class Score:
    """
    打ち落とした爆弾，敵機の数をスコアとして表示するクラス
    ボスの爆弾はビームではで撃ち落とせない
    爆弾：1点
    敵機：10点
    """
    def __init__(self):
        self.font = pg.font.Font(None, 50)
        self.color = (0, 0, 255)
        self.score = 0
        self.image = self.font.render(f"Score: {self.score}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = 100, HEIGHT-50

    def score_up(self, add):
        self.score += add

    def score_down(self,down):
        self.score -= down

    def update(self, screen: pg.Surface):
        self.image = self.font.render(f"Score: {self.score}", 0, self.color)
        screen.blit(self.image, self.rect)


class Timer:
    """
    プログラム開始からの経過時間を計算するクラス
    """
    def __init__(self):
        self.start_time = time.time()

    # 経過時間を計算
    def get_elapsed_time(self):
        return time.time() - self.start_time


def change_background(screen: pg.Surface, timer: Timer):
    """
    表示する背景画像の番号を変更する関数
    """
    global bg_img_i
    
    # 現在の時刻を取得する
    elapsed_time = timer.get_elapsed_time()
    
    # 30で割った商をグループ数とする
    group_count = int(elapsed_time) // 30
    
    # グループ数を3で割った余りを求める
    group_remainder = group_count % 3

    # 余りが0なら
    if group_remainder == 0:
        # 朝の画像を表示
        bg_img_i = 0
    
    # 余りが1なら
    elif group_remainder == 1:
        # 昼の画像を表示
        bg_img_i = 1
    
    # 余りが2なら
    else:
        # 夜の画像を表示
        bg_img_i = 2


def main():
    pg.display.set_caption("真！こうかとん無双・改")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("ex05/fig/pg_bg.jpg")
    score = Score()
    boss=Boss()
    bird = Bird(3, (900, 400))
    bombs = pg.sprite.Group()
    beams = pg.sprite.Group()
    exps = pg.sprite.Group()
    emys = pg.sprite.Group()
    gravity = pg.sprite.Group()
    boss_mv = pg.sprite.Group()
    boss_bomb = pg.sprite.Group()
    tmr = 0
    clock = pg.time.Clock()
    
    # プログラム開始からの経過時間を初期化する
    timer = Timer()

    while True:
        key_lst = pg.key.get_pressed()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return 0
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                beams.add(Beam(bird))
            if (tmr+1)%1000==0:#ボスは1000ｆ後に出現
                if boss.flag ==0:#複数体出現するのを阻止
                    boss_mv.add(Boss())
                    boss.flag+=1
                else:
                    break
                    
            if event.type == pg.KEYDOWN and event.key == pg.K_RSHIFT:   # 追加機能3
                if (score.score > 100):
                    bird.change_state("hyper", 500)
                    score.score_up(-100)
            if event.type == pg.KEYDOWN and event.key == pg.K_TAB :#Tabキーで重力球の展開
                if score.score>=50:#スコアが５０未満の時は発動しない
                    gravity.add(Gravity(bird,500))#重力球の展開
                    score.score_down(50)#50点消費する
            if event.type == pg.KEYDOWN and event.key == pg.K_LSHIFT:
                bird.speed = 20
            else:
                bird.speed = 10
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE and key_lst[pg.K_LSHIFT]:  # 左シフトキーとスペースキーが同時に押されたとき複数のビームを出す
                nb = NeoBeam(bird, 5)
                beam_lst = nb.gen_beams()
                beams.add(beam_lst)
        screen.blit(bg_img, [0, 0])
        
        # 背景画像を表示する
        screen.blit(bg_imgs_lst[bg_img_i], (0, 0))
        
        # 現在の経過時間を更新する
        elapsed_time = timer.get_elapsed_time()
        
        # 背景画像を時刻に基づき変更する
        change_background(screen, timer)
        
        # 経過時間を画面上に表示する
        elapsed_minutes = int(elapsed_time // 60)  # 分を計算
        elapsed_seconds = int(elapsed_time % 60)  # 秒を計算
        time_text = f"{elapsed_minutes:02d}:{elapsed_seconds:02d}"  # 表示する時刻
        time_image = score.font.render(time_text, 0, score.color)  # 画像に変換
        screen.blit(time_image, (32, 100))  # 時刻を画面に表示

        if tmr%200 == 0:  # 200フレームに1回，敵機を出現させる
            emys.add(Enemy())

        for emy in emys:
            if emy.state == "stop" and tmr%emy.interval == 0:
                # 敵機が停止状態に入ったら，intervalに応じて爆弾投下
                bombs.add(Bomb(emy, bird))
        for bos in boss_mv:
            if bos.state == "stop" and tmr%bos.interval == 0:
                # ボスが停止状態に入ったら，intervalに応じて爆弾投下
                boss_bomb.add(Boss_bomb(bos, bird))
        for emy in pg.sprite.groupcollide(emys, beams, True, True).keys():
            exps.add(Explosion(emy, 100))  # 爆発エフェクト
            score.score_up(10)  # 10点アップ
            bird.change_img(6, screen)  # こうかとん喜びエフェクト
        for bos in pg.sprite.groupcollide(boss_mv, beams, False, True).keys():
            exps.add(Explosion(bos, 100))  # 爆発エフェクト
            score.score_up(5)  # 5点アップ
            boss.damage(1)
        for bomb in pg.sprite.groupcollide(bombs, beams, True, True).keys():
            exps.add(Explosion(bomb, 50))  # 爆発エフェクト
            score.score_up(1)  # 1点アップ
        for bomb in pg.sprite.groupcollide(bombs, gravity, True, False).keys():#重力球と爆弾の接触
            exps.add(Explosion(bomb, 50))  # 爆発エフェクト
            score.score_up(1)  # 1点アップ
        for bomb in pg.sprite.groupcollide(boss_bomb, gravity, True, False).keys():#重力球とボスの爆弾の接触
            exps.add(Explosion(bomb, 50))  # 爆発エフェクト

        for bomb in pg.sprite.spritecollide(bird, bombs, True):
            if (bird.state == "hyper"): # hyperモードの時
                exps.add(Explosion(bomb, 50))  # 爆発エフェクト
                score.score_up(1)  # 1点アップ
            else:   # normalモードの時
                bird.change_img(8, screen) # こうかとん悲しみエフェクト
                score.update(screen)
                pg.display.update()
                time.sleep(2)
                return
            
        for boss_bomb in pg.sprite.spritecollide(bird, boss_bomb, True):
            if (bird.state == "hyper"): # hyperモードの時
                exps.add(Explosion(bomb, 50))   # 爆発エフェクト
                                                # 加点はなし
            else:   # normalモードの時
                bird.change_img(8, screen) # こうかとん悲しみエフェクト
                score.update(screen)
                pg.display.update()
                time.sleep(2)
                return

        if boss.boss_hp<=0:#ボスのＨＰが尽きたら喜びエフェクトを取り終了する
                score.score_up(1000)
                bird.change_img(6, screen)  # こうかとん喜びエフェクト
                score.update(screen)
                pg.display.update()
                time.sleep(2)
                return

        gravity.update(key_lst, screen)
        gravity.draw(screen)
        bird.update(key_lst, screen)
        beams.update()
        beams.draw(screen)
        emys.update()
        emys.draw(screen)
        boss_mv.update()
        boss_mv.draw(screen)
        bombs.update()
        bombs.draw(screen)
        boss_bomb.update()
        boss_bomb.draw(screen)
        exps.update()
        exps.draw(screen)
        score.update(screen)
        pg.display.update()
        tmr += 1
        clock.tick(50)
   

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
