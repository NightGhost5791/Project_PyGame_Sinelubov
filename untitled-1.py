import pygame
import os
import sys


WIDTH = 500
HEIGHT = 500


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x = obj.abs_pos[0] + self.dx
        obj.rect.y = obj.abs_pos[1] + self.dy

    # позиционировать камеру на объекте target
    def update(self, _):
        self.dx = 0
        self.dy = 0


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)
        self.abs_pos = (self.rect.x, self.rect.y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_img
        self.rect = self.image.get_rect().move(
            tile_width * pos_x + 10, tile_height * pos_y + 3)
        self.pos = (pos_x, pos_y)

    def move(self, x, y):
        camera.dx -= tile_width * (x - self.pos[0])
        camera.dy -= tile_height * (y - self.pos[1])
        self.pos = (x, y)
        for sprite in tiles_group:
            camera.apply(sprite)


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


pygame.init()
screen_size = (500, 500)
screen = pygame.display.set_mode(screen_size)
clock = pygame.time.Clock()
pygame.display.set_caption('Maze')

FPS = 60


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


tile_images = {
    'wall': load_image('wall.png'),
    'empty': load_image('floor.png'),
    'finish': load_image('finish.png')
}

player_img = pygame.image.load("data\down1.png")

tile_width = tile_height = 50


# основной персонаж
player = None

# группы спрайтов
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
            elif level[y][x] == '%':
                Tile('finish', x, y)


    # вернем игрока, а также размер поля в клетках
    return new_player, x, y


def win():
    fon = pygame.transform.scale(load_image('win.png'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    pygame.mixer.music.stop()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
                return
        pygame.display.flip()

def move(hero, movement):
    x, y = hero.pos
    check = '@.%'
    if movement == "up":
        if y > 0 and level_map[y - 1][x] in check:
            hero.move(x, y - 1)
            if (y > 0 and level_map[y - 1][x]) == check[-1]:
                win()
    elif movement == "down":
        if y < max_y and level_map[y + 1][x] in check:
            if (y < max_y and level_map[y + 1][x]) == check[-1]:
                win()
            hero.move(x, y + 1)
    elif movement == "left":
        if x > 0 and level_map[y][x - 1] in check:
            if (x > 0 and level_map[y][x - 1]) == check[-1]:
                win()
            hero.move(x - 1, y)
    elif movement == "right":
        if x < max_x and level_map[y][x + 1] in check:
            if (x < max_x and level_map[y][x + 1]) == check[-1]:
                win()
            hero.move(x + 1, y)


camera = Camera()
start_screen()
level_map = load_level('map.txt')
player, max_x, max_y = generate_level(level_map)
running = True
camera.update(player)

pygame.mixer.music.load('data\dungeon_music.mp3')
pygame.mixer.music.play(-1)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                move(player, "up")
            elif event.key == pygame.K_DOWN:
                move(player, "down")
            elif event.key == pygame.K_LEFT:
                move(player, "left")
            elif event.key == pygame.K_RIGHT:
                move(player, "right")

    screen.fill(pygame.Color("black"))
    tiles_group.draw(screen)
    player_group.draw(screen)
    clock.tick(FPS)
    pygame.display.flip()

pygame.quit()
