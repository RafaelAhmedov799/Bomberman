import time

import arcade
import random

from Level_2.animated import Animated

SCREEN_TITLE = "Bomberman"
CELL_WIDTH = 60
CELL_HEIGHT = 60
ROW_COUNT = 11
COLUMN_COUNT = 11
SCREEN_WIDTH = CELL_WIDTH * COLUMN_COUNT
SCREEN_HEIGHT = CELL_HEIGHT * ROW_COUNT
BOMBERMAN_SPEED = 2

DIRECTION_UP = 0
DIRECTION_DOWN = 1
DIRECTION_RIGHT = 2
DIRECTION_LEFT = 3


def cell_cx(x):
    c = x // CELL_WIDTH
    return c * CELL_WIDTH + CELL_WIDTH / 2, c


def cell_cy(y):
    r = y // CELL_HEIGHT
    return r * CELL_HEIGHT + CELL_HEIGHT / 2, r


class Flame(Animated):
    def __init__(self, center_x, center_y):
        super().__init__("Flame\Flame_f00.png", 0.7)
        self.creation_time = time.time()
        self.center_x = center_x
        self.center_y = center_y
        for i in range(1, 5):
            self.append_texture(arcade.load_texture(f"Flame/Flame_f0{i}.png"))

    def update(self):
        super().update()
        blocks = arcade.check_for_collision_with_list(self, window.explodable_blocks)
        for b in blocks:
            b.kill()
        if time.time() - self.creation_time > 2:
            self.kill()


BONUS_SPEED = 1
BONUS_RADIUS = 2
BONUS_BOMBS = 3


class Bonus(arcade.Sprite):
    def __init__(self, type, center_x, center_y):
        if type == BONUS_SPEED:
            file_name = "Powerups/SpeedPowerup.png"
        if type == BONUS_RADIUS:
            file_name = "Powerups/FlamePowerup.png"
        if type == BONUS_BOMBS:
            file_name = "Powerups/BombPowerup.png"
        super().__init__(file_name)
        self.center_x = center_x
        self.center_y = center_y
        self.type = type

    def update(self):
        for b in [window.bomberman, window.bomberman2]:
            if arcade.check_for_collision(b, self):
                self.kill()
                if self.type == BONUS_SPEED:
                    b.speed += 1
                if self.type == BONUS_RADIUS:
                    b.radius += 1
                if self.type == BONUS_BOMBS:
                    b.bombs += 1


class Bomb(Animated):
    def __init__(self, center_x, center_y, radius):
        super().__init__("Bomb\Bomb_f00.png", 0.8)
        self.center_x = center_x
        self.center_y = center_y
        self.append_texture(arcade.load_texture("Bomb/Bomb_f01.png"))
        self.creation_time = time.time()
        self.append_texture(arcade.load_texture("Bomb/Bomb_f02.png"))
        self.radius = radius

    def update(self):
        super().update()
        if time.time() - self.creation_time > 3:
            window.flames.append(Flame(self.center_x, self.center_y))
            up = True
            for i in range(1, self.radius):
                flame = Flame(self.center_x, self.center_y + i * CELL_HEIGHT)
                blocks = arcade.check_for_collision_with_list(flame, window.solid_blocks)
                if len(blocks) > 0:
                    up = False
                if not up:
                    break
                window.flames.append(flame)
            down = True
            for i in range(1, self.radius):
                flame = Flame(self.center_x, self.center_y - i * CELL_HEIGHT)
                blocks = arcade.check_for_collision_with_list(flame, window.solid_blocks)
                if len(blocks) > 0:
                    down = False
                if not down:
                    break
                window.flames.append(flame)
            left = True
            for i in range(1, self.radius):
                flame = Flame(self.center_x - i * CELL_WIDTH, self.center_y)
                blocks = arcade.check_for_collision_with_list(flame, window.solid_blocks)
                if len(blocks) > 0:
                    left = False
                if not left:
                    break
                window.flames.append(flame)
            right = True
            for i in range(1, self.radius):
                flame = Flame(self.center_x + i * CELL_WIDTH, self.center_y)
                blocks = arcade.check_for_collision_with_list(flame, window.solid_blocks)
                if len(blocks) > 0:
                    right = False
                if not right:
                    break
                window.flames.append(flame)
            self.kill()


class Bomberman(Animated):
    def __init__(self, window):
        super().__init__("Bomberman/Back/Bman_B_f00.png", 1)
        self.scale = 0.6
        self.window = window
        self.up_textures = []
        self.down_textures = []
        self.right_textures = []
        self.left_textures = []
        self.direction = DIRECTION_UP
        self.is_walking = False
        self.speed = BOMBERMAN_SPEED
        self.radius = 3
        self.bombs = 3
        for i in range(8):
            self.up_textures.append(arcade.load_texture(
                f"Bomberman/Back/Bman_B_f0{i}.png"))
        for i in range(8):
            self.down_textures.append(arcade.load_texture(
                f"Bomberman/Front/Bman_F_f0{i}.png"))
        for i in range(8):
            self.right_textures.append(arcade.load_texture(
                f"Bomberman/Side/Bman_S_f0{i}.png"))
        for i in range(8):
            self.left_textures.append(arcade.load_texture(
                f"Bomberman/Side/Bman_S_f0{i}.png", flipped_horizontally=True))

    def update(self):
        super().update()
        if self.direction == DIRECTION_UP:
            self.textures = self.up_textures
        if self.direction == DIRECTION_DOWN:
            self.textures = self.down_textures
        if self.direction == DIRECTION_RIGHT:
            self.textures = self.right_textures
        if self.direction == DIRECTION_LEFT:
            self.textures = self.left_textures
        self.collide_with_blocks(self.window.solid_blocks)
        self.collide_with_blocks(self.window.explodable_blocks)
        if self.right > SCREEN_WIDTH:
            self.right = SCREEN_WIDTH

        if self.top > SCREEN_HEIGHT:
            self.top = SCREEN_HEIGHT

        if self.bottom < 0:
            self.bottom = 0

        if self.left < 0:
            self.left = 0

    def collide_with_blocks(self, blocks):
        blocks = arcade.check_for_collision_with_list(self, blocks)
        for block in blocks:
            if self.right > block.left and self.direction == DIRECTION_RIGHT:
                self.right = block.left
            if self.top > block.bottom and self.direction == DIRECTION_UP:
                self.top = block.bottom
            if self.left < block.right and self.direction == DIRECTION_LEFT:
                self.left = block.right
            if self.bottom < block.top and self.direction == DIRECTION_DOWN:
                self.bottom = block.top

    def update_animation(self, delta_time):
        if self.is_walking:
            super().update_animation(delta_time)


class SolidBlock(arcade.Sprite):
    def __init__(self, center_x, center_y):
        super().__init__("Blocks/SolidBlock.png", center_x=center_x, center_y=center_y)


class ExplodableBlock(arcade.Sprite):
    def __init__(self, center_x, center_y):
        super().__init__("Blocks/ExplodableBlock.png", center_x=center_x, center_y=center_y)


class Game(arcade.Window):
    def __init__(self, width, height, title):
        super().__init__(width, height, title)
        # texture
        self.bg = arcade.load_texture("Blocks/BackgroundTile.png")
        # sprite_lists
        self.solid_blocks = arcade.SpriteList()
        self.explodable_blocks = arcade.SpriteList()
        self.bomberman = Bomberman(self)
        self.bomberman2 = Bomberman(self)
        self.bomberman2.color = arcade.color.RED
        self.bombs = arcade.SpriteList()
        self.bomb_place = arcade.load_sound("bombplace.mp3")
        self.game_music = arcade.load_sound("game_music.mp3")
        self.win_music = arcade.load_sound("win.mp3")
        self.win_yeah = arcade.load_sound("ohyeahwin.mp3")
        self.flames = arcade.SpriteList()
        self.game = True
        self.bonuses = arcade.SpriteList()
        self.bonus_last_time = time.time()

    def draw_background(self):
        for y in range(ROW_COUNT):
            for x in range(COLUMN_COUNT):
                arcade.draw_texture_rectangle(x * CELL_WIDTH + CELL_WIDTH / 2, y * CELL_HEIGHT + CELL_HEIGHT / 2,
                                              CELL_WIDTH, CELL_HEIGHT, self.bg)

    def setup(self):
        self.bomberman.center_x = CELL_WIDTH / 2
        self.bomberman.center_y = CELL_HEIGHT / 2
        self.bomberman2.center_x = SCREEN_WIDTH - CELL_WIDTH / 2
        self.bomberman2.center_y = SCREEN_HEIGHT - CELL_HEIGHT / 2
        self.game_music_player = arcade.play_sound(self.game_music, 0.3)
        for r in range(ROW_COUNT):
            for c in range(COLUMN_COUNT):
                if r % 2 == 1 and c % 2 == 1:
                    self.solid_blocks.append(SolidBlock(
                        c * CELL_WIDTH + CELL_WIDTH / 2, r * CELL_HEIGHT + CELL_HEIGHT / 2))
                else:
                    if 0 <= r <= 2 and c == 0 or r == 0 and 0 <= c <= 2:
                        continue
                    if c == COLUMN_COUNT - 1 and ROW_COUNT - 3 <= r <= ROW_COUNT - 1:
                        continue
                    if COLUMN_COUNT - 3 <= c <= COLUMN_COUNT - 1 and r == ROW_COUNT - 1:
                        continue
                    num = random.randint(1, 2)
                    if num == 1:
                        self.explodable_blocks.append(ExplodableBlock(
                            c * CELL_WIDTH + CELL_WIDTH / 2, r * CELL_HEIGHT + CELL_HEIGHT / 2))

    def on_draw(self):
        self.clear()
        self.draw_background()
        self.solid_blocks.draw()
        self.explodable_blocks.draw()
        self.bomberman.draw()
        self.bomberman2.draw()
        self.bombs.draw()
        self.flames.draw()
        self.bonuses.draw()

    def update(self, delta_time):
        if self.game:
            self.solid_blocks.update()
            self.explodable_blocks.update()
            self.bomberman.update_animation(delta_time)
            self.bomberman.update()
            self.bomberman2.update_animation(delta_time)
            self.bomberman2.update()
            self.bombs.update()
            self.bombs.update_animation(delta_time)
            self.flames.update()
            self.flames.update_animation(delta_time)
            self.bonuses.update()
            if time.time() - self.bonus_last_time > 5:
                b_type = random.choice([BONUS_SPEED, BONUS_RADIUS, BONUS_BOMBS])
                while True:
                    cx, c = cell_cx(random.randint(0, SCREEN_WIDTH))
                    cy, r = cell_cy(random.randint(0, SCREEN_HEIGHT))
                    if not (r % 2 == 1 and c % 2 == 1): break

                self.bonuses.append(Bonus(b_type, cx, cy))

                self.bonus_last_time = time.time()
            for b in [self.bomberman, self.bomberman2]:
                flames = arcade.check_for_collision_with_list(b, self.flames)
                if len(flames) > 0:
                    b.color = arcade.color.BLACK
                    arcade.play_sound(self.win_music, 0.6)
                    arcade.stop_sound(self.game_music_player)
                    arcade.play_sound(self.win_yeah, 1.5)
                    self.game = False

    def on_key_press(self, key, modifiers):
        self.bomberman2.is_walking = True
        self.bomberman2.change_x = 0
        self.bomberman2.change_y = 0
        if key == arcade.key.LEFT:
            self.bomberman2.change_x = -self.bomberman2.speed
            self.bomberman2.direction = DIRECTION_LEFT
        if key == arcade.key.RIGHT:
            self.bomberman2.change_x = self.bomberman2.speed
            self.bomberman2.direction = DIRECTION_RIGHT
        if key == arcade.key.UP:
            self.bomberman2.change_y = self.bomberman2.speed
            self.bomberman2.direction = DIRECTION_UP
        if key == arcade.key.DOWN:
            self.bomberman2.change_y = -self.bomberman2.speed
            self.bomberman2.direction = DIRECTION_DOWN
        self.bomberman.is_walking = True
        self.bomberman.change_x = 0
        self.bomberman.change_y = 0
        if key == arcade.key.A:
            self.bomberman.change_x = -self.bomberman.speed
            self.bomberman.direction = DIRECTION_LEFT
        if key == arcade.key.D:
            self.bomberman.change_x = self.bomberman.speed
            self.bomberman.direction = DIRECTION_RIGHT
        if key == arcade.key.W:
            self.bomberman.change_y = self.bomberman.speed
            self.bomberman.direction = DIRECTION_UP
        if key == arcade.key.S:
            self.bomberman.change_y = -self.bomberman.speed
            self.bomberman.direction = DIRECTION_DOWN
        if key == arcade.key.RCTRL:
            if self.bomberman2.bombs > 0:
                cx, _ = cell_cx(self.bomberman2.center_x)
                cy, _ = cell_cy(self.bomberman2.center_y)
                bomb = Bomb(cx, cy,
                            self.bomberman2.radius)
                self.bombs.append(bomb)
                arcade.play_sound(self.bomb_place, 1)
                self.bomberman2.bombs -= 1
        if key == arcade.key.LCTRL:
            if self.bomberman.bombs > 0:
                center_x, _ = cell_cx(self.bomberman.center_x)
                center_y, _ = cell_cy(self.bomberman.center_y)
                bomb = Bomb(center_x, center_y, self.bomberman.radius)
                self.bombs.append(bomb)
                arcade.play_sound(self.bomb_place, 1)
                self.bomberman.bombs -= 1

    def on_key_release(self, key, modifiers):
        self.bomberman2.is_walking = False
        if key == arcade.key.LEFT:
            self.bomberman2.change_x = 0
        if key == arcade.key.RIGHT:
            self.bomberman2.change_x = 0
        if key == arcade.key.UP:
            self.bomberman2.change_y = 0
        if key == arcade.key.DOWN:
            self.bomberman2.change_y = 0
        self.bomberman.is_walking = False
        if key == arcade.key.A:
            self.bomberman.change_x = 0
        if key == arcade.key.D:
            self.bomberman.change_x = 0
        if key == arcade.key.W:
            self.bomberman.change_y = 0
        if key == arcade.key.S:
            self.bomberman.change_y = 0


window = Game(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
window.setup()
arcade.run()
