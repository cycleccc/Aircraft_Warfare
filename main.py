# main.py
from os import startfile, write
import pygame
import sys
import traceback
import myplane
import enemy
import bullet
import supply
import functions
import time

from pygame.locals import *
from random import *


# pygame 初始化
pygame.init()

# 加载和播放声音模块初始化
pygame.mixer.init()

bg_size = width, height = 1200, 600

# 初始化窗口屏幕显示模块
screen = pygame.display.set_mode(bg_size)
pygame.display.set_caption("飞机大战")

# 设置背景图片
# background = pygame.image.load("images/background.png").convert()
bg1 = pygame.image.load("images/background.png").convert()
bg2 = pygame.image.load("images/background.png").convert()

y1 = 0
y2 = -700


def bg_update():

    global y1, y2

    y1 += 5
    y2 += 5

    screen.blit(bg1, (0, y1))
    screen.blit(bg2, (0, y2))

    if y1 > 700:
        y1 = -700

    if y2 > 700:
        y2 = -700

    return y1, y2


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# 载入游戏的声音和设置音量
pygame.mixer.music.load("sound/game_music.ogg")
pygame.mixer.music.set_volume(0.2)
bullet_sound = pygame.mixer.Sound("sound/bullet.wav")
bullet_sound.set_volume(0.2)
bomb_sound = pygame.mixer.Sound("sound/use_bomb.wav")
bomb_sound.set_volume(0.2)
supply_sound = pygame.mixer.Sound("sound/supply.wav")
supply_sound.set_volume(0.2)
get_blood_sound = pygame.mixer.Sound("sound/get_blood.wav")
get_blood_sound.set_volume(0.2)
get_invincible_sound = pygame.mixer.Sound("sound/get_invincible.wav")
get_invincible_sound.set_volume(0.2)
get_bomb_sound = pygame.mixer.Sound("sound/get_bomb.wav")
get_bomb_sound.set_volume(0.2)
get_bullet_sound = pygame.mixer.Sound("sound/get_bullet.wav")
get_bullet_sound.set_volume(0.2)
upgrade_sound = pygame.mixer.Sound("sound/upgrade.wav")
upgrade_sound.set_volume(0.2)
enemy3_fly_sound = pygame.mixer.Sound("sound/enemy3_flying.wav")
enemy3_fly_sound.set_volume(0.2)
enemy1_down_sound = pygame.mixer.Sound("sound/enemy1_down.wav")
enemy1_down_sound.set_volume(0.2)
enemy2_down_sound = pygame.mixer.Sound("sound/enemy2_down.wav")
enemy2_down_sound.set_volume(0.2)
enemy3_down_sound = pygame.mixer.Sound("sound/enemy3_down.wav")
enemy3_down_sound.set_volume(0.5)
me_down_sound = pygame.mixer.Sound("sound/me_down.wav")
me_down_sound.set_volume(0.2)
start_image = pygame.image.load("images/start.png").convert_alpha()
start_rect = start_image.get_rect()


def main():
    # 使音乐流无限循环
    pygame.mixer.music.play(-1)

    # 生成我方飞机
    me = myplane.MyPlane(bg_size)

    # 生成敌方特殊飞机
    plus_enemies = enemy.PlusEnemy(bg_size)

    enemies = pygame.sprite.Group()

    # 生成敌方小型飞机
    small_enemies = pygame.sprite.Group()
    functions.add_small_enemies(small_enemies, enemies, 15)

    # 生成敌方中型飞机
    mid_enemies = pygame.sprite.Group()
    functions.add_mid_enemies(mid_enemies, enemies, 4)

    # 生成敌方大型飞机
    big_enemies = pygame.sprite.Group()
    functions.add_big_enemies(big_enemies, enemies, 2)

    # 生成普通子弹
    bullet1 = []
    bullet1_index = 0
    BULLET1_NUM = 20
    for i in range(BULLET1_NUM):
        bullet1.append(bullet.Bullet1(me.rect.midtop))

    # 生成敌方子弹
    bullet3 = []
    bullet3_index = 0
    BULLET3_NUM = 20
    for i in range(BULLET3_NUM):
        bullet3.append(bullet.Bullet_enemy(plus_enemies.rect.midbottom))

    # 生成超级子弹
    bullet2 = []
    bullet2_index = 0
    BULLET2_NUM = 20
    for i in range(BULLET2_NUM // 2):
        bullet2.append(bullet.Bullet2((me.rect.centerx - 33, me.rect.centery)))
        bullet2.append(bullet.Bullet2((me.rect.centerx + 30, me.rect.centery)))

    clock = pygame.time.Clock()

    # 中弹图片索引
    e1_destroy_index = 0
    e2_destroy_index = 0
    e3_destroy_index = 0
    e4_destroy_index = 0
    me_destroy_index = 0

    # 统计得分
    score = 0
    score_font = pygame.font.Font("font/font.ttf", 36)

    # 标志是否暂停游戏
    paused = False
    pause_nor_image = pygame.image.load("images/pause_nor.png").convert_alpha()
    pause_pressed_image = pygame.image.load("images/pause_pressed.png").convert_alpha()
    resume_nor_image = pygame.image.load("images/resume_nor.png").convert_alpha()
    resume_pressed_image = pygame.image.load(
        "images/resume_pressed.png"
    ).convert_alpha()
    paused_rect = pause_nor_image.get_rect()
    paused_rect.left, paused_rect.top = width - paused_rect.width - 10, 10
    paused_image = pause_nor_image

    # 设置难度级别
    level = 1

    # 设置难度显示
    level_font = pygame.font.Font("font/font.ttf", 36)
    # 全屏炸弹
    bomb_image = pygame.image.load("images/bomb.png").convert_alpha()
    bomb_rect = bomb_image.get_rect()
    bomb_font = pygame.font.Font("font/font.ttf", 48)
    bomb_num = 3

    # 每30秒发放一个补给包
    bullet_supply = supply.Bullet_Supply(bg_size)
    bomb_supply = supply.Bomb_Supply(bg_size)
    blood_supply = supply.Blood_Supply(bg_size)
    # angle_supply = supply.Angle_Supply(bg_size)
    invincible_supply = supply.Invincible_Supply(bg_size)
    SUPPLY_TIME = USEREVENT
    pygame.time.set_timer(SUPPLY_TIME, 2 * 1000)

    # 超级子弹定时器
    DOUBLE_BULLET_TIME = USEREVENT + 1

    # 标志是否使用超级子弹
    is_double_bullet = False

    # 解除我方无敌状态定时器
    INVINCIBLE_TIME = USEREVENT + 2

    # 生命数量
    life_image = pygame.image.load("images/life.png").convert_alpha()
    life_rect = life_image.get_rect()
    life_num = 4

    # 用于阻止重复打开记录文件
    recorded = False

    # 游戏结束画面
    gameover_font = pygame.font.Font("font/font.TTF", 48)
    again_image = pygame.image.load("images/again.png").convert_alpha()
    again_rect = again_image.get_rect()
    gameover_image = pygame.image.load("images/gameover.png").convert_alpha()
    gameover_rect = gameover_image.get_rect()

    # 用于切换图片
    switch_image = True

    # 用于延迟
    delay = 100

    running = True

    while running:

        y1, y2 = bg_update()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1 and paused_rect.collidepoint(event.pos):
                    paused = not paused
                    if paused:
                        pygame.time.set_timer(SUPPLY_TIME, 0)
                        pygame.mixer.music.pause()
                        pygame.mixer.pause()
                    else:
                        pygame.time.set_timer(SUPPLY_TIME, 30 * 1000)
                        pygame.mixer.music.unpause()
                        pygame.mixer.unpause()

            elif event.type == MOUSEMOTION:
                if paused_rect.collidepoint(event.pos):
                    if paused:
                        paused_image = resume_pressed_image
                    else:
                        paused_image = pause_pressed_image
                else:
                    if paused:
                        paused_image = resume_nor_image
                    else:
                        paused_image = pause_nor_image

            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    paused = not paused
                    if paused:
                        paused_image = resume_nor_image
                        pygame.time.set_timer(SUPPLY_TIME, 0)
                        pygame.mixer.music.pause()
                        pygame.mixer.pause()
                    else:
                        paused_image = pause_nor_image
                        pygame.time.set_timer(SUPPLY_TIME, 30 * 1000)
                        pygame.mixer.music.unpause()
                        pygame.mixer.unpause()
                if event.key == K_SPACE:
                    if bomb_num:
                        bomb_num -= 1
                        bomb_sound.play()
                        plus_enemies.active = False
                        for each in enemies:
                            if each.rect.bottom > 0:
                                each.active = False

            elif event.type == SUPPLY_TIME:
                supply_sound.play()
                choice = randint(1, 4)
                if choice == 1:
                    bomb_supply.reset()
                elif choice == 2:
                    bullet_supply.reset()
                elif choice == 3:
                    invincible_supply.reset()
                elif choice == 4:
                    print("血包产生了")
                    blood_supply.reset()
            elif event.type == DOUBLE_BULLET_TIME:
                is_double_bullet = False
                pygame.time.set_timer(DOUBLE_BULLET_TIME, 0)

            elif event.type == INVINCIBLE_TIME:
                me.invincible = False
                pygame.time.set_timer(INVINCIBLE_TIME, 0)
        # 根据用户的得分增加难度
        if level == 1 and score > 50000:
            level = 2
            upgrade_sound.play()
            # 增加3架小型敌机、2架中型敌机和1架大型敌机
            functions.add_small_enemies(small_enemies, enemies, 3)
            functions.add_mid_enemies(mid_enemies, enemies, 2)
            functions.add_big_enemies(big_enemies, enemies, 1)
            # 提升小型敌机的速度
            functions.inc_speed(small_enemies, 1)
        elif level == 2 and score > 300000:
            level = 3
            upgrade_sound.play()
            # 增加5架小型敌机、3架中型敌机和2架大型敌机
            functions.add_small_enemies(small_enemies, enemies, 5)
            functions.add_mid_enemies(mid_enemies, enemies, 3)
            functions.add_big_enemies(big_enemies, enemies, 2)
            # 提升小型、中型敌机的速度
            functions.inc_speed(small_enemies, 1)
            functions.inc_speed(mid_enemies, 1)
        elif level == 3 and score > 600000:
            level = 4
            upgrade_sound.play()
            # 增加5架小型敌机、3架中型敌机和2架大型敌机
            functions.add_small_enemies(small_enemies, enemies, 5)
            functions.add_mid_enemies(mid_enemies, enemies, 3)
            functions.add_big_enemies(big_enemies, enemies, 2)
            # 提升小型、中型敌机的速度
            functions.inc_speed(small_enemies, 1)
            functions.inc_speed(mid_enemies, 1)
        elif level == 4 and score > 1000000:
            level = 5
            upgrade_sound.play()
            # 增加5架小型敌机、3架中型敌机和2架大型敌机
            functions.add_small_enemies(small_enemies, enemies, 5)
            functions.add_mid_enemies(mid_enemies, enemies, 3)
            functions.add_big_enemies(big_enemies, enemies, 2)
            # 提升小型、中型敌机的速度
            functions.inc_speed(small_enemies, 1)
            functions.inc_speed(mid_enemies, 1)

        # screen.blit(background, (0, 0))

        if life_num and not paused:
            # 检测用户的键盘操作
            key_pressed = pygame.key.get_pressed()

            if key_pressed[K_w] or key_pressed[K_UP]:
                me.moveUp()
            if key_pressed[K_s] or key_pressed[K_DOWN]:
                me.moveDown()
            if key_pressed[K_a] or key_pressed[K_LEFT]:
                me.moveLeft()
            if key_pressed[K_d] or key_pressed[K_RIGHT]:
                me.moveRight()
            if key_pressed[K_r]:
                main()
            if key_pressed[K_t]:

                # 显示时间和分数
                with open("Score_Time.txt", "r") as f:
                    cnt = 0

                    # 绘制历史得分开头
                    Historical_Score_text1 = gameover_font.render(
                        " Year".ljust(10) + "day".center(10) + "Score".rjust(15),
                        True,
                        (255, 255, 255),
                    )
                    Historical_Score_text1_rect = Historical_Score_text1.get_rect()
                    (
                        Historical_Score_text1_rect.left,
                        Historical_Score_text1_rect.top,
                    ) = (
                        width - Historical_Score_text1_rect.width
                    ) // 2, height // 3 - 100
                    screen.blit(Historical_Score_text1, Historical_Score_text1_rect)
                    lines = f.readlines()
                    for line in lines:
                        cnt += 1
                        # print(cnt)
                        if cnt == 6:
                            break
                        score_time = line.split()
                        Score = score_time[0]
                        Time_year = score_time[1]
                        Time_day = score_time[2]

                        # print(Score + Time_year + Time_day)

                        gameover_text2 = gameover_font.render(
                            Time_year.ljust(10) + Time_day.center(10) + Score.rjust(10),
                            True,
                            (255, 255, 255),
                        )
                        gameover_text2_rect = gameover_text2.get_rect()
                        gameover_text2_rect.left, gameover_text2_rect.top = (
                            width - gameover_text2_rect.width
                        ) // 2, Historical_Score_text1_rect.bottom + 40 * cnt
                        screen.blit(gameover_text2, gameover_text2_rect)
            # 绘制血包补给并检测是否获得
            if blood_supply.active:
                blood_supply.move()
                screen.blit(blood_supply.image, blood_supply.rect)
                if pygame.sprite.collide_mask(blood_supply, me):
                    get_blood_sound.play()
                    if life_num < 10:
                        life_num += 1
                    blood_supply.active = False
            # 绘制无敌星补给并检测是否获得
            if invincible_supply.active:
                invincible_supply.move()
                screen.blit(invincible_supply.image, invincible_supply.rect)
                if pygame.sprite.collide_mask(invincible_supply, me):
                    get_invincible_sound.play()
                    me.invincible = True
                    pygame.time.set_timer(INVINCIBLE_TIME, 5 * 1000)
                    invincible_supply.active = False

            # 绘制全屏炸弹补给并检测是否获得
            if bomb_supply.active:
                bomb_supply.move()
                screen.blit(bomb_supply.image, bomb_supply.rect)
                if pygame.sprite.collide_mask(bomb_supply, me):
                    get_bomb_sound.play()
                    if bomb_num < 10:
                        bomb_num += 1
                    bomb_supply.active = False

            # 绘制超级子弹补给并检测是否获得
            if bullet_supply.active:
                bullet_supply.move()
                screen.blit(bullet_supply.image, bullet_supply.rect)
                if pygame.sprite.collide_mask(bullet_supply, me):
                    get_bullet_sound.play()
                    is_double_bullet = True
                    pygame.time.set_timer(DOUBLE_BULLET_TIME, 18 * 1000)
                    bullet_supply.active = False

            # 发射子弹
            if not (delay % 5):
                bullet_sound.play()
                if is_double_bullet:
                    bullets = bullet2
                    bullets[bullet2_index].reset(
                        (me.rect.centerx - 33, me.rect.centery)
                    )
                    bullets[bullet2_index + 1].reset(
                        (me.rect.centerx + 30, me.rect.centery)
                    )
                    bullet2_index = (bullet2_index + 2) % BULLET2_NUM
                else:
                    bullets = bullet1
                    bullets[bullet1_index].reset(me.rect.midtop)
                    bullet1_index = (bullet1_index + 1) % BULLET1_NUM

            # 敌军发射子弹
            if not (delay % 100):
                bullet_sound.play()
                bullets_enemy = bullet3
                bullets_enemy[bullet3_index].reset(plus_enemies.rect.midbottom)
                bullet3_index = (bullet3_index + 1) % BULLET3_NUM
                # print("执行了")

            # 检测子弹是否击中敌机
            for b in bullets:
                if b.active:
                    b.move()
                    screen.blit(b.image, b.rect)
                    enemy_hit = pygame.sprite.spritecollide(
                        b, enemies, False, pygame.sprite.collide_mask
                    )
                    enemy_plus_hit = pygame.sprite.collide_rect(b, plus_enemies)
                    if enemy_plus_hit:
                        b.active = False
                        plus_enemies.active = False
                    if enemy_hit:
                        b.active = False
                        for e in enemy_hit:
                            if e in mid_enemies or e in big_enemies:
                                e.hit = True
                                e.energy -= 1
                                if e.energy == 0:
                                    e.active = False
                            else:
                                e.active = False

            # 绘制大型敌机
            for each in big_enemies:
                if each.active:
                    each.move()

                    if delay > 50:
                        each.left_move()
                    else:
                        each.right_move()

                    if each.hit:
                        screen.blit(each.image_hit, each.rect)
                        each.hit = False
                    else:
                        if switch_image:
                            screen.blit(each.image1, each.rect)
                        else:
                            screen.blit(each.image2, each.rect)

                    # 绘制血槽
                    pygame.draw.line(
                        screen,
                        BLACK,
                        (each.rect.left, each.rect.top - 5),
                        (each.rect.right, each.rect.top - 5),
                        2,
                    )
                    # 当生命大于20%显示绿色，否则显示红色
                    energy_remain = each.energy / enemy.BigEnemy.energy
                    if energy_remain > 0.2:
                        energy_color = GREEN
                    else:
                        energy_color = RED
                    pygame.draw.line(
                        screen,
                        energy_color,
                        (each.rect.left, each.rect.top - 5),
                        (
                            each.rect.left + each.rect.width * energy_remain,
                            each.rect.top - 5,
                        ),
                        2,
                    )

                    # 即将出现在画面中，播放音效
                    if each.rect.bottom == -50:
                        enemy3_fly_sound.play(-1)
                else:
                    # 毁灭
                    if not (delay % 3):
                        if e3_destroy_index == 0:
                            enemy3_down_sound.play()
                        screen.blit(each.destroy_images[e3_destroy_index], each.rect)
                        e3_destroy_index = (e3_destroy_index + 1) % 6
                        if e3_destroy_index == 0:
                            enemy3_fly_sound.stop()
                            score += 10000
                            each.reset()

            # 绘制中型敌机：
            for each in mid_enemies:
                if each.active:
                    each.move()

                    if delay > 50:
                        each.left_move()
                    else:
                        each.right_move()

                    if each.hit:
                        screen.blit(each.image_hit, each.rect)
                        each.hit = False
                    else:
                        screen.blit(each.image, each.rect)

                    # 绘制血槽
                    pygame.draw.line(
                        screen,
                        BLACK,
                        (each.rect.left, each.rect.top - 5),
                        (each.rect.right, each.rect.top - 5),
                        2,
                    )
                    # 当生命大于20%显示绿色，否则显示红色
                    energy_remain = each.energy / enemy.MidEnemy.energy
                    if energy_remain > 0.2:
                        energy_color = GREEN
                    else:
                        energy_color = RED
                    pygame.draw.line(
                        screen,
                        energy_color,
                        (each.rect.left, each.rect.top - 5),
                        (
                            each.rect.left + each.rect.width * energy_remain,
                            each.rect.top - 5,
                        ),
                        2,
                    )
                else:
                    # 毁灭
                    if not (delay % 3):
                        if e2_destroy_index == 0:
                            enemy2_down_sound.play()
                        screen.blit(each.destroy_images[e2_destroy_index], each.rect)
                        e2_destroy_index = (e2_destroy_index + 1) % 4
                        if e2_destroy_index == 0:
                            score += 6000
                            each.reset()

            # 绘制小型敌机：
            for each in small_enemies:
                if each.active:
                    each.move()

                    if delay > 50:
                        each.left_move()
                    else:
                        each.right_move()
                    screen.blit(each.image, each.rect)
                else:
                    # 毁灭
                    if not (delay % 3):
                        if e1_destroy_index == 0:
                            enemy1_down_sound.play()
                        screen.blit(each.destroy_images[e1_destroy_index], each.rect)
                        e1_destroy_index = (e1_destroy_index + 1) % 4
                        if e1_destroy_index == 0:
                            score += 2000
                            each.reset()

            # 绘制特殊敌机：
            if plus_enemies.active:
                plus_enemies.move()

                if delay > 50:
                    plus_enemies.left_move()
                else:
                    plus_enemies.right_move()

                screen.blit(plus_enemies.image, plus_enemies.rect)
            else:
                # 毁灭
                if not (delay % 3):
                    if e4_destroy_index == 0:
                        enemy1_down_sound.play()
                    screen.blit(
                        plus_enemies.destroy_images[e4_destroy_index], plus_enemies.rect
                    )
                    e4_destroy_index = (e4_destroy_index + 1) % 4
                    if e4_destroy_index == 0:
                        score += 2000
                        plus_enemies.reset()

            # 检测敌军之间是否相撞
            for each_a in enemies:
                for each_b in enemies:
                    if each_a != each_b:
                        enemies_Collide = pygame.sprite.collide_rect(each_a, each_b)
                        if enemies_Collide:
                            if each_a.rect.left < each_b.rect.left:
                                each_a.rect.left -= 5
                                each_b.rect.left += 5
                            else:
                                each_a.rect.left += 5
                                each_b.rect.left -= 5
                for each in enemies:
                    enemies_plus_Collide = pygame.sprite.collide_rect(
                        each, plus_enemies
                    )
                    if enemies_plus_Collide:
                        if plus_enemies.rect.left < each.rect.left:
                            plus_enemies.rect.left -= 5
                            each.rect.left += 5
                        else:
                            plus_enemies.rect.left += 5
                            each.rect.left -= 5

            # 检测我方飞机是否被撞或被击中
            enemies_down = pygame.sprite.spritecollide(
                me, enemies, False, pygame.sprite.collide_mask
            )
            plus_enemies_down = pygame.sprite.collide_rect(plus_enemies, me)
            if plus_enemies_down and not me.invincible:
                me.active = False
                plus_enemies.active = False
            if enemies_down and not me.invincible:
                me.active = False
                for e in enemies_down:
                    e.active = False
            # 检测敌军子弹是否击中友军飞机
            for b in bullets_enemy:
                if b.active:
                    b.move()
                    screen.blit(b.image, b.rect)
                    enemy_bullets_hit = pygame.sprite.collide_rect(b, me)
                    if enemy_bullets_hit and not me.invincible:
                        me.active = False
                        b.active = False

            # 绘制我方飞机
            if me.active:
                if me.invincible:
                    screen.blit(me.image4, me.rect)
                    screen.blit(me.image3, me.rect)
                elif switch_image:
                    screen.blit(me.image1, me.rect)
                else:
                    screen.blit(me.image2, me.rect)
            else:
                # 毁灭
                if not (delay % 3):
                    if me_destroy_index == 0:
                        me_down_sound.play()
                    screen.blit(me.destroy_images[me_destroy_index], me.rect)
                    me_destroy_index = (me_destroy_index + 1) % 4
                    if me_destroy_index == 0:
                        life_num -= 1
                        me.reset()
                        pygame.time.set_timer(INVINCIBLE_TIME, 5 * 1000)

            # 绘制全屏炸弹数量
            bomb_text = bomb_font.render("× %d" % bomb_num, True, WHITE)
            text_rect = bomb_text.get_rect()
            screen.blit(bomb_image, (10, height - 10 - bomb_rect.height))
            screen.blit(
                bomb_text, (20 + bomb_rect.width, height - 5 - text_rect.height)
            )

            # 绘制剩余生命数量
            if life_num:
                for i in range(life_num):
                    screen.blit(
                        life_image,
                        (
                            width - 10 - (i + 1) * life_rect.width,
                            height - 10 - life_rect.height,
                        ),
                    )

            # 绘制得分
            score_text = score_font.render("Score : %s" % str(score), True, WHITE)
            screen.blit(score_text, (10, 5))
            # 绘制难度等级
            level_text = level_font.render("Level : %s" % str(level), True, WHITE)
            screen.blit(level_text, (1000, 5))
        # 绘制游戏结束画面
        elif life_num == 0:
            # 背景音乐停止
            # pygame.mixer.music.stop()

            # 停止全部音效
            pygame.mixer.stop()

            # 停止发放补给
            pygame.time.set_timer(SUPPLY_TIME, 0)

            if not recorded:
                recorded = True
                # 读取历史最高得分
                with open("record.txt", "r") as f:
                    record_score = int(f.read())

                # 如果玩家得分高于历史最高得分，则存档
                if score > record_score:
                    with open("record.txt", "w") as f:
                        f.write(str(score))
                with open("Score_Time.txt", "a+") as f:
                    f.write(
                        str(score)
                        + " "
                        + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                        + "\n"
                    )

            # 绘制结束画面
            record_score_text = score_font.render(
                "Best : %d" % record_score, True, (255, 255, 255)
            )
            screen.blit(record_score_text, (50, 50))

            gameover_text1 = gameover_font.render("Me Score", True, (255, 255, 255))
            gameover_text1_rect = gameover_text1.get_rect()
            gameover_text1_rect.left, gameover_text1_rect.top = (
                width - gameover_text1_rect.width
            ) // 2, height // 3
            screen.blit(gameover_text1, gameover_text1_rect)

            gameover_text2 = gameover_font.render(str(score), True, (255, 255, 255))
            gameover_text2_rect = gameover_text2.get_rect()
            gameover_text2_rect.left, gameover_text2_rect.top = (
                width - gameover_text2_rect.width
            ) // 2, gameover_text1_rect.bottom + 10
            screen.blit(gameover_text2, gameover_text2_rect)

            again_rect.left, again_rect.top = (
                width - again_rect.width
            ) // 2, gameover_text2_rect.bottom + 50
            screen.blit(again_image, again_rect)

            gameover_rect.left, gameover_rect.top = (
                width - again_rect.width
            ) // 2, again_rect.bottom + 10
            screen.blit(gameover_image, gameover_rect)

            # 检测用户的鼠标操作
            # 如果用户按下鼠标左键
            if pygame.mouse.get_pressed()[0]:
                # 获取鼠标坐标
                pos = pygame.mouse.get_pos()
                # 如果用户点击“重新开始”
                if (
                    again_rect.left < pos[0] < again_rect.right
                    and again_rect.top < pos[1] < again_rect.bottom
                ):
                    # 调用main函数，重新开始游戏
                    main()
                # 如果用户点击“结束游戏”
                elif (
                    gameover_rect.left < pos[0] < gameover_rect.right
                    and gameover_rect.top < pos[1] < gameover_rect.bottom
                ):
                    # 退出游戏
                    pygame.quit()
                    sys.exit()

                    # 绘制暂停按钮
        screen.blit(paused_image, paused_rect)

        # 切换图片
        if not (delay % 5):
            switch_image = not switch_image

        delay -= 1
        if not delay:
            delay = 100

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        pass
    except:
        traceback.print_exc()
        pygame.quit()
        input()
