import random
import pygame
import time

# 屏幕尺寸
SCREEN_RECT = pygame.Rect(0, 0, 480, 700)


class GameSprite(pygame.sprite.Sprite):
    """游戏精灵"""

    def __init__(self, image_name: str, speedx: int = 0, speedy: int = 0):
        super().__init__()

        self.image = pygame.image.load(image_name)
        self.rect = self.image.get_rect()
        self.speedx = speedx
        self.speedy = speedy

    def update(self):
        self.rect.top += self.speedy
        self.rect.left += self.speedx

    @staticmethod
    def image_names(prefix: str, count: int) -> list:
        """多张图片"""

        names = []
        for i in range(1, count + 1):
            names.append("./images/" + prefix + str(i) + ".png")

        return names


class Background(GameSprite):
    """背景精灵"""

    __image_path = "./images/background.png"

    def __init__(self, is_alt=False):
        super().__init__(Background.__image_path, 0, 1)

        if is_alt:
            self.rect.bottom = 0

    def update(self):
        super().update()

        if self.rect.top >= SCREEN_RECT.height:
            self.rect.bottom = 0


class PlaneSprite(GameSprite):
    """飞机精灵，包括敌机和英雄"""

    def __init__(self, image_names: list, destroy_names: list, life: int, speedx: int = 0, speedy: int = 0):

        image_name = image_names[0]
        super().__init__(image_name, speedx, speedy)

        # 生命值
        self.__life = life

        # 是否可以被删除
        self.__can_destroied = False

        # 正常图像列表
        self.__life_images = []
        for file_name in image_names:
            image = pygame.image.load(file_name)
            self.__life_images.append(image)

        # 被摧毁图像列表
        self.__destroy_images = []
        for file_name in destroy_names:
            image = pygame.image.load(file_name)
            self.__destroy_images.append(image)

        # 默认播放生存图片
        self.images = self.__life_images
        # 显示图像索引
        self.show_image_index = 0

    def life_decr(self, num=1):
        """生命值减少"""
        self.__life -= num
        if self.__life <= 0:
            self.__destroied()

    def life_incr(self, num=1):
        """生命值增加"""
        self.__life += num

    def life(self):
        """获取生命值"""
        return self.__life

    def die(self):
        """死亡"""
        self.__life = 0
        self.__destroied()

    def is_life(self):
        """是否存活"""
        if self.__life > 0:
            return True
        return False

    def update(self):
        self.__update_images()

        super().update()

        if self.__can_destroied:
            self.kill()

    def __update_images(self):
        """更新图像"""

        pre_index = int(self.show_image_index)
        self.show_image_index += 0.05
        count = len(self.images)

        # 判断是否循环播放
        if self.is_life():
            self.show_image_index %= len(self.images)
        elif self.show_image_index > count - 1:
            self.show_image_index = count - 1
            self.__can_destroied = True

        current_index = int(self.show_image_index)

        if pre_index != current_index:
            self.image = self.images[current_index]

    def __destroied(self):
        """飞机被摧毁"""

        # 默认播放生存图片
        self.images = self.__destroy_images
        # 显示图像索引
        self.show_image_index = 0

    def is_can_destroied(self):
        """是否可以摧毁"""

        return self.__can_destroied


class Hero(PlaneSprite):
    """英雄精灵"""

    __init_life = 3
    __bullet_image_path = "./images/bullet1.png"

    def __init__(self):

        image_names = GameSprite.image_names("me", 2)
        destroy_names = GameSprite.image_names("me_destroy_", 4)

        super().__init__(image_names, destroy_names, Hero.__init_life)

        # 设置初始位置
        self.rect.centerx = SCREEN_RECT.centerx
        self.rect.bottom = SCREEN_RECT.bottom - 120

        # 创建子弹组
        self.bullets = pygame.sprite.Group()

    def update(self):
        if not self.is_life():
            self.speedx = 0
            self.speedy = 0

        super().update()

        # 超出屏幕检测
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_RECT.right:
            self.rect.right = SCREEN_RECT.right
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_RECT.bottom:
            self.rect.bottom = SCREEN_RECT.bottom

    def fire(self):
        """发射子弹"""

        if self.is_life():
            for i in range(0, 3):
                # 创建子弹精灵
                bullet = Bullet(Hero.__bullet_image_path, 0, -3)

                # 设置子弹位置
                bullet.rect.bottom = self.rect.top - i * 20
                bullet.rect.centerx = self.rect.centerx

                # 将子弹添加到精灵组
                self.bullets.add(bullet)


class Bullet(GameSprite):
    """子弹精灵"""

    def update(self):
        super().update()

        # 判断是否超出屏幕
        if self.rect.bottom <= 0 or self.rect.top >= SCREEN_RECT.height:
            self.kill()


class Enemy(PlaneSprite):
    """敌机精灵"""

    __init_life = 2
    __enemy_image_path = "./images/bullet2.png"

    # 创建子弹组
    bullets = pygame.sprite.Group()

    def __init__(self):
        image_names = ["./images/enemy1.png"]
        destroy_names = GameSprite.image_names("enemy1_down", 4)
        super().__init__(image_names, destroy_names, Enemy.__init_life)

        # 随机敌机出现位置
        width = SCREEN_RECT.width - self.rect.width
        self.rect.left = random.randint(0, width)
        self.rect.bottom = 0

        self.speedx = random.randint(-1, 1)
        self.speedy = random.randint(1, 3)

        self.fire_time = None
        self.fire_interval = 5

    def update(self):
        super().update()

        if self.rect.left <= 0 or self.rect.right >= SCREEN_RECT.right:
            self.speedx = -self.speedx

        # 判断敌机是否移出屏幕
        if self.rect.top >= SCREEN_RECT.height:
            # 将精灵从所有组中删除
            self.kill()

    def fire(self):
        """发射子弹"""

        if self.is_life():
            now_time = int(time.time())
            if self.fire_time is None or self.fire_time + self.fire_interval <= now_time:
                # 创建子弹精灵
                bullet = Bullet(Enemy.__enemy_image_path, 0, self.speedy + 1)

                # 设置子弹位置
                bullet.rect.top = self.rect.bottom + 10
                bullet.rect.centerx = self.rect.centerx

                # 将子弹添加到精灵组
                Enemy.bullets.add(bullet)

                self.fire_time = now_time


class Star(GameSprite):
    """星"""

    __image_path = "./images/star.png"

    def __init__(self):
        self.speedx = random.randint(-1, 1)
        self.speedy = random.randint(1, 3)
        super().__init__(Star.__image_path, self.speedx, self.speedy)
        # 随机出现位置
        width = SCREEN_RECT.width - self.rect.width
        self.rect.left = random.randint(0, width)
        self.rect.bottom = 0

    def update(self):
        super().update()

        if self.rect.left <= 0 or self.rect.right >= SCREEN_RECT.right:
            self.speedx = -self.speedx

        # 判断是否移出屏幕
        if self.rect.top >= SCREEN_RECT.height:
            # 将精灵从所有组中删除
            self.kill()
