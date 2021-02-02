#! /usr/bin/python3

from plane_sprites import *

# 敌机出现事件
CREATE_ENEMY_EVENT = pygame.USEREVENT
# 英雄发射子弹事件
HERO_FIRE_EVENT = pygame.USEREVENT + 1
# 敌机发射子弹事件
Enemy_FIRE_EVENT = pygame.USEREVENT + 2
# 星出现事件
CREATE_STAR_EVENT = pygame.USEREVENT + 3


class PlaneGame:
    """飞机大战游戏类"""

    def __init__(self):
        print("游戏初始化...")

        pygame.init()

        self.screen = pygame.display.set_mode(SCREEN_RECT.size)
        self.clock = pygame.time.Clock()

        self.__create_sprites()
        PlaneGame.__create_user_events()

        self.info_bar = InfoBar(self.screen, self.hero)

    def __create_sprites(self):
        """创建精灵组"""

        self.back_group = pygame.sprite.Group(Background(), Background(True))

        self.hero = Hero()
        self.hero_group = pygame.sprite.Group(self.hero)

        self.enemy_group = pygame.sprite.Group()
        self.destroy_group = pygame.sprite.Group()

        self.star_group = pygame.sprite.Group()

    @staticmethod
    def __create_user_events():
        """创建用户事件"""

        # 每秒添加一架敌机
        pygame.time.set_timer(CREATE_ENEMY_EVENT, 1000)

        # 英雄每秒发射两次子弹
        pygame.time.set_timer(HERO_FIRE_EVENT, 500)

        # 符合条件的敌机发射子弹
        pygame.time.set_timer(Enemy_FIRE_EVENT, 500)

        # 每60秒添加一个星
        pygame.time.set_timer(CREATE_STAR_EVENT, 60000)

    def start_game(self):
        """开启游戏循环"""

        while True:
            self.clock.tick(60)
            if self.hero.is_can_destroied():
                PlaneGame.__finished_game()
            self.__event_handler()
            self.__update_sprites()
            self.__check_collide()
            pygame.display.update()

    def __check_collide(self):
        """碰撞检测"""

        # 双方子弹抵消
        pygame.sprite.groupcollide(self.hero.bullets, Enemy.bullets, True, True)

        # 英雄得到星
        stars = pygame.sprite.spritecollide(self.hero, self.star_group, True)
        num = len(stars)
        if num > 0:
            self.hero.life_incr(num)

        # 子弹摧毁敌机
        enemies = pygame.sprite.groupcollide(self.enemy_group, self.hero.bullets, False, True).keys()
        for enemy in enemies:
            enemy.life_decr()

            if not enemy.is_life():
                self.__enemy_rm_group(enemy)

        if self.hero.is_life():
            # 敌机子弹撞毁英雄
            enemy_bullets = pygame.sprite.spritecollide(self.hero, Enemy.bullets, True)
            num = len(enemy_bullets)

            # 敌机撞毁英雄
            enemies = pygame.sprite.spritecollide(self.hero, self.enemy_group, False)
            num += len(enemies)

            for enemy in enemies:
                enemy.die()
                self.__enemy_rm_group(enemy)

            if num > 0:
                self.hero.life_decr(num)
                # print(self.hero.life())
                if not self.hero.is_life():
                    print("英雄牺牲了...")
                    self.__hero_rm_group(self.hero)

    def __event_handler(self):
        """事件处理"""

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                PlaneGame.__finished_game()
            elif event.type == HERO_FIRE_EVENT:
                self.hero.fire()
            elif event.type == CREATE_ENEMY_EVENT:
                self.enemy_group.add(Enemy())
            elif event.type == CREATE_STAR_EVENT:
                self.star_group.add(Star())
            elif event.type == Enemy_FIRE_EVENT:
                for enemy in self.enemy_group.sprites():
                    enemy.fire()
            # 按下 b 英雄自爆
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_b:
                self.hero.die()
                self.__hero_rm_group(self.hero)

                # 集体自爆
                for enemy in self.enemy_group.sprites():
                    enemy.die()
                    self.__enemy_rm_group(enemy)

        # 通过 pygame.key 获取用户按键
        keys_pressed = pygame.key.get_pressed()
        dir_x = keys_pressed[pygame.K_RIGHT] - keys_pressed[pygame.K_LEFT]
        dir_y = keys_pressed[pygame.K_DOWN] - keys_pressed[pygame.K_UP]

        # 根据移动方向设置英雄的速度
        self.hero.speedx = dir_x * 2
        self.hero.speedy = dir_y * 2

    def __update_sprites(self):
        """更新/绘制精灵组"""

        for group in [self.back_group, self.hero_group, self.hero.bullets,
                      self.enemy_group, Enemy.bullets, self.destroy_group,
                      self.star_group]:
            group.update()
            group.draw(self.screen)

        self.info_bar.update()

    @staticmethod
    def __finished_game():
        """退出游戏"""

        print("退出游戏")
        pygame.quit()
        exit()

    def __enemy_rm_group(self, enemy: Enemy):
        """敌机移出组"""

        enemy.remove(self.enemy_group)
        enemy.add(self.destroy_group)

    def __hero_rm_group(self, hero: Hero):
        """英雄移出组"""

        hero.remove(self.hero_group)
        hero.add(self.destroy_group)


if __name__ == '__main__':
    PlaneGame().start_game()
