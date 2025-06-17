import os
import random
import sys
import time
import pygame as pg


WIDTH, HEIGHT = 1100, 650
DELTA = {  # 移動量辞書
    pg.K_UP: (0, -5),
    pg.K_DOWN: (0, +5),
    pg.K_LEFT: (-5, 0),
    pg.K_RIGHT: (+5, 0),
}
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(rct: pg.Rect) -> tuple[bool, bool]:

    """
    引数：こうかとんRectまたは爆弾Recr
    戻り値：タプル（横方向、縦方向の画面内外判定結果）
    画面内ならTrue,画面外ならFalse
    """
    yoko, tate = True, True  # 初期値：画面内
    if rct.left < 0 or WIDTH < rct.right:  # 横方向画面外判定
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom:  # 縦方向画面外判定
        tate = False
    return yoko, tate

def gameover(screen: pg.Surface) -> None:
    """
    引数:Screen（画面）
    戻り値：なし
    ゲームオーバー時に画面を黒くし、「Game Over」と泣いているこうかとん画像を5秒表示する。
    """
    # 半透明の黒い画面を作成
    blackout = pg.Surface((WIDTH, HEIGHT))  # 画面サイズと同じSurfaceを作成
    blackout.set_alpha(200)  # 透明度決定（透明:0～不透明:255）
    blackout.fill((0, 0, 0))  # 黒色で塗りつぶす（255, 255, 255は白色）

    # 泣いているこうかとん画像
    kk_img_cry = pg.transform.rotozoom(pg.image.load("fig/8.png"), 0, 0.9)
    kk_rct_cry = kk_img_cry.get_rect(center=(WIDTH // 4, HEIGHT // 2))  # 画面左に配置
    kk_rct_cry2 = kk_img_cry.get_rect(center=(WIDTH // 1.3, HEIGHT // 2))  # 画面右に配置

    # 「Game Over」の文字列
    font = pg.font.Font(None, 100)
    text = font.render("Game Over", True, (255, 255, 255))  # 白色でGame Overを描画
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))  # 画面中央に配置

    # 描画
    screen.blit(blackout, (0, 0))
    screen.blit(kk_img_cry, kk_rct_cry)
    screen.blit(kk_img_cry, kk_rct_cry2)
    screen.blit(text, text_rect)
    pg.display.update()  # display.update()する関数
    time.sleep(5)  # 5秒間の表示

def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    サイズの異なる爆弾Surfaceを要素としたリストと加速度リストを返す
    爆弾のSurfaceリスト（サイズは20×1〜20×10）
    加速度リスト（1〜10の整数）
    """
    bb_imgs = []  # 爆弾用のSurfaceリスト
    bb_accs = [a for a in range(1, 11)]  # 加速度リスト 1〜10
#拡大爆弾Surfaceのリストを作成
    for r in range(1, 11):
        bb_img = pg.Surface((20*r, 20*r))
        pg.draw.circle(bb_img, (255, 0, 0), (10*r, 10*r), 10*r)  # 赤い円を描画
        bb_img.set_colorkey((0, 0, 0))  # 黒を透明に
        bb_imgs.append(bb_img)  # 爆弾Surfaceをリストに追加

    return bb_imgs, bb_accs


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200

    bb_img = pg.Surface((20, 20))  # 爆弾用の空のSurfaceを作成
    pg.draw.circle(bb_img,(255, 0, 0),(10, 10), 10)  # 赤い円
    bb_img.set_colorkey((0, 0, 0))  # 黒を透明に
    bb_rct = bb_img.get_rect()  # 爆弾Rectを取得
    bb_rct.center = (random.randint(0, WIDTH), random.randint(0, HEIGHT))  # 横と縦座標の乱数
    vx, vy = +5, +5  # 爆弾の移動速度
    clock = pg.time.Clock()
    tmr = 0

    bb_imgs, bb_accs = init_bb_imgs() 

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                return
        
        avx = vx*bb_accs[min(tmr // 500, 9)] 
        bb_img = bb_imgs[min(tmr//500, 9)] 

        if kk_rct.colliderect(bb_rct):  # こうかとんRectと爆弾Rectの衝突判定
            print("ゲームオーバー")
            gameover(screen)  # ゲームオーバー画面を表示する
            return   
          
        screen.blit(bg_img, [0, 0]) 

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0]
                sum_mv[1] += mv[1]
        #if key_lst[pg.K_UP]:
        #    sum_mv[1] -= 5
        #if key_lst[pg.K_DOWN]:
        #   sum_mv[1] += 5
        #if key_lst[pg.K_LEFT]:
        #    sum_mv[0] -= 5
        #if key_lst[pg.K_RIGHT]:
        #    sum_mv[0] += 5
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])  # 移動をなかったことに
        screen.blit(kk_img, kk_rct)
        bb_rct.move_ip(avx, vy)  # 爆弾の移動
        yoko, tate = check_bound(bb_rct)
        if not yoko:  # 横方向にはみ出ていたら
            vx *= -1
        if not tate:  # 縦方向にはみ出ていたら
            vy *= -1  
        screen.blit(bb_img, bb_rct)  # 爆弾の描画
        pg.display.update()
        tmr += 1
        clock.tick(50)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
