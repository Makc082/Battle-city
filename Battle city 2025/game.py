import pygame
import random
import time
import pygame.mixer

pygame.mixer.init()
pygame.init()

window = pygame.display.set_mode((1200, 800))
pygame.display.set_caption("Танковий Бій")  
STEP = 50
rows = 16
cols = 24

# Завантаження звуків
tank_move_sound = pygame.mixer.Sound("sound/background.ogg")
shot_sound = pygame.mixer.Sound("sound/shot.ogg")
explosion_sound = pygame.mixer.Sound("sound/explosion.ogg")
block_sound = pygame.mixer.Sound("sound/brick.ogg")
block2_sound = pygame.mixer.Sound("sound/brick2.ogg")
flag_sound = pygame.mixer.Sound("sound/flag_explosion.ogg")
game_start_sound = pygame.mixer.Sound("sound/main_theme.ogg")
game_win_sound = pygame.mixer.Sound("sound/win_game.ogg")
game_over_sound = pygame.mixer.Sound("sound/game_over.ogg")

game_start_sound.play()

# Завантаження зображень
images = {
    1: pygame.image.load("image/Blocks/briks.png"),
    2: pygame.image.load("image/Blocks/concretes.png"),
    3: pygame.image.load("image/Blocks/ice-blocks.png"),
    4: pygame.image.load("image/Blocks/woods.png"),
    5: pygame.image.load("image/Blocks/waters.png"),
    6: pygame.image.load("image/Blocks/flag.png"),
    7: pygame.image.load("image/Blocks/flag1.png"),
    "tank1": pygame.image.load("image/Tanks/tank.png"),  
    "tank2": pygame.image.load("image/Tanks/tank.png"),
    "explosion": pygame.image.load("image/boom/boom_b0.png"), 
    "explosion1": pygame.image.load("image/boom/boom_t1.png"), 
    "bullet": pygame.image.load("image/boom/bullet.png"),
    "bot": pygame.image.load("image/e_tanks/e_tank.png")

}
images = {k: pygame.transform.scale(v, (STEP, STEP)) for k, v in images.items()}  # Масштабування зображень

# Генерація ігрового поля 
def generate_matrix():
    matrix = [[0] * cols for _ in range(rows)]

    # Заповнення периметру поля бетонними блоками
    for i in range(rows):
        for j in range(cols):
            if i == 0 or i == rows - 1 or j == 0 or j == cols - 1:
                matrix[i][j] = 2  

    # Бетонні блоки біля країв
    matrix[1] = [0] * cols
    matrix[1][0] = 2  
    matrix[1][-1] = 2 

    # Зона флага
    center = cols // 2 
    matrix[rows - 2][center] = 6  # Центр = 6(флаг)
    matrix[rows - 2][center - 1] = 1  
    matrix[rows - 2][center + 1] = 1  
    matrix[rows - 3][center] = 1
    matrix[rows - 3][center - 1] = 1
    matrix[rows - 3][center + 1] = 1

    # Міста для танків
    matrix[rows - 2][center - 2] = 0
    matrix[rows - 2][center + 2] = 0

    # Заповнення випадковими блоками
    def random_blocks(matrix):
        for _ in range(50):  
            value = random.randint(0, 5)  
            block_height = random.randint(2, 4) 
            block_width = random.randint(2, 4)  
            start_row = random.randint(2, rows - block_height - 2)  
            start_col = random.randint(2, cols - block_width - 2)  

            # Заповнення блоку на полі
            for i in range(block_height):
                for j in range(block_width):
                    if matrix[start_row + i][start_col + j] == 0:
                        matrix[start_row + i][start_col + j] = value

    random_blocks(matrix) 

    return matrix  

# Малювання ігрового поля
def draw_matrix(matrix, window, STEP, images):
    for y, row in enumerate(matrix):
        for x, cell in enumerate(row):
            if cell in images:  
                window.blit(images[cell], (x * STEP, y * STEP))

# Рух танків
def move_tank(matrix, pos, direction, player1, player2, bots):
    x, y = pos

    dx, dy = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}.get(direction, (0, 0))

    new_x, new_y = x + dx, y + dy

    # Перевірка на зіткнення з іншими танками або ботами
    if [new_x, new_y] in [player1, player2] or [new_x, new_y] in [bot[:2] for bot in bots]:
        return pos

    if matrix[new_y][new_x] in [0, 3, 4]:
        return new_x, new_y
    else:
        return x, y

# Рух ботів
def move_bots(bots, matrix, player1, player2):
    for bot in bots:
        direction = bot[2]
        x, y = bot[0], bot[1]
        dx, dy = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}.get(direction, (0, 0))
        new_x, new_y = x + dx, y + dy

        # Перевірка на зіткнення з іншими танками або ботами
        if [new_x, new_y] in [player1, player2] or [new_x, new_y] in [bot[:2] for bot in bots]:
            bot[2] = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])  
        elif matrix[new_y][new_x] in [0, 3, 4]:  # Перевірка на порожнє місце
            bot[0], bot[1] = new_x, new_y
        else:
            bot[2] = random.choice(["UP", "DOWN", "LEFT", "RIGHT"]) 

        # Хаотичне змінення напрямку
        if random.random() < 0.1:  
            bot[2] = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])
# Постріл ботів
def bots_fire(bots, bullets_bots):
    for bot in bots:
        if random.random() < 0.02:  
            direction = bot[2]
            x, y = bot[0], bot[1]
            bullet_start_positions = {
                "UP": (x * STEP + STEP // 2, y * STEP),
                "DOWN": (x * STEP + STEP // 2, y * STEP + STEP),
                "LEFT": (x * STEP, y * STEP + STEP // 2),
                "RIGHT": (x * STEP + STEP, y * STEP + STEP // 2),
            }

            bx, by = bullet_start_positions.get(direction, (x * STEP, y * STEP))
            bullets_bots.append([bx, by, direction])  # Додаємо кулю в список

# Постріл кулі
def fire_bullet(pos, direction, bullets, last_shot):
    if not last_shot: 
        x, y = pos
        bullet_size = STEP // 5  # Розмір кулі

        # Визначаємо стартову позицію кулі
        bullet_start_positions = {
            "UP": (x * STEP + STEP // 2 - bullet_size // 2, y * STEP),
            "DOWN": (x * STEP + STEP // 2 - bullet_size // 2, y * STEP + STEP - bullet_size),
            "LEFT": (x * STEP, y * STEP + STEP // 2 - bullet_size // 2),
            "RIGHT": (x * STEP + STEP - bullet_size, y * STEP + STEP // 2 - bullet_size // 2),
        }             

        bx, by = bullet_start_positions.get(direction, (x * STEP, y * STEP))
        bullets.append([bx, by, direction]) 
        return True  
    return False  

# Створення нових списків для куль
def move_bullets(bullets1, bullets2, bullets_bots, matrix, window, images, STEP):
    new_bullets1 = []  
    new_bullets2 = []  
    new_bullets_bots = []  

    for bullet in bullets1:
        x, y, direction = bullet
        dx, dy = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}.get(direction, (0, 0))

        # Рухаємо кулю вперед
        x += dx * STEP   # Швидкість руху
        y += dy * STEP 

        # Виход кулі за межі екрану
        if 0 <= x < len(matrix[0]) * STEP and 0 <= y < len(matrix) * STEP:
            new_bullets1.append([x, y, direction])  

            # Відображення кулі
            bullet_image = pygame.transform.scale(images["bullet"], (STEP // 5, STEP // 5))
            window.blit(bullet_image, (x, y))

    for bullet in bullets2:
        x, y, direction = bullet
        dx, dy = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}.get(direction, (0, 0))

        # Рух кулі вперед
        x += dx * STEP   
        y += dy * STEP 

        if 0 <= x < len(matrix[0]) * STEP and 0 <= y < len(matrix) * STEP:
            new_bullets2.append([x, y, direction])  # Додаємо оновлену кулю у список

            bullet_image = pygame.transform.scale(images["bullet"], (STEP // 5, STEP // 5))
            window.blit(bullet_image, (x, y))

    for bullet in bullets_bots:
        x, y, direction = bullet
        dx, dy = {"UP": (0, -1), "DOWN": (0, 1), "LEFT": (-1, 0), "RIGHT": (1, 0)}.get(direction, (0, 0))

        x += dx * STEP // 2 
        y += dy * STEP // 2

        if 0 <= x < len(matrix[0]) * STEP and 0 <= y < len(matrix) * STEP:
            new_bullets_bots.append([x, y, direction])  
            bullet_image = pygame.transform.scale(images["bullet"], (STEP // 5, STEP // 5))
            window.blit(bullet_image, (x, y))

    # Оновлюємо списки куль
    bullets1[:] = new_bullets1
    bullets2[:] = new_bullets2
    bullets_bots[:] = new_bullets_bots

def bullet_collision(bullets1, bullets2, bullets_bots, matrix, bots, player1, player2, player1_lives, player2_lives):
        
    try:    
        for bullet in bullets1[:]:  # Проходимось по списку куль
            bullet_x, bullet_y, _ = bullet  # Отримуємо координати кулі (в пікселях)
            x, y = bullet_x // STEP, bullet_y // STEP  # Перетворюємо у координати матриці
            if matrix[y][x] == 1:
                bullets1.remove(bullet)
                window.blit(images["explosion"], (x * STEP, y * STEP))
                block_sound.play()
                matrix[y][x] = 0
            elif matrix[y][x] == 6:
                bullets1.remove(bullet)
                window.blit(images["explosion"], (x * STEP, y * STEP))
                flag_sound.play()
                matrix[y][x] = 7
            elif matrix[y][x] == 2:
                bullets1.remove(bullet)
                window.blit(images["explosion1"], (x * STEP, y * STEP))
                block2_sound.play()
            elif [x, y] in [bot[:2] for bot in bots] :
                bullets1.remove(bullet)
                window.blit(images["explosion"], (x * STEP, y * STEP))
                explosion_sound.play()
                bots[:] = [bot for bot in bots if bot[:2]!= [x, y]]
            elif [x, y] == [player2[0], player2[1]]:
                bullets1.remove(bullet)
                window.blit(images["explosion"], (x * STEP, y * STEP))
                explosion_sound.play()
                player2_lives -= 1
                if player2_lives > 0:
                    player2[0], player2[1] = [14, 14]
    except IndexError:
            # Якщо куля виходить за межі екрану
            bullets1.remove(bullet)

    try:
        for bullet in bullets2[:]: 
            bullet_x, bullet_y, _ = bullet
            x, y = bullet_x // STEP, bullet_y // STEP  
            if matrix[y][x] == 1:
                bullets2.remove(bullet)
                window.blit(images["explosion"], (x * STEP, y * STEP))
                block_sound.play()
                matrix[y][x] = 0
            elif matrix[y][x] == 6:
                bullets2.remove(bullet)
                window.blit(images["explosion"], (x * STEP, y * STEP))
                flag_sound.play()
                matrix[y][x] = 7
            elif matrix[y][x] == 2:
                bullets2.remove(bullet)
                window.blit(images["explosion1"], (x * STEP, y * STEP))
                block2_sound.play()
            elif [x, y] in [bot[:2] for bot in bots]:
                bullets2.remove(bullet)
                window.blit(images["explosion"], (x * STEP, y * STEP))
                explosion_sound.play()
                bots[:] = [bot for bot in bots if bot[:2]!= [x, y]]
            elif [x, y] == [player1[0], player1[1]]:
                bullets2.remove(bullet)
                window.blit(images["explosion"], (x * STEP, y * STEP))
                explosion_sound.play()
                player1_lives -= 1
                if player1_lives > 0:
                    player1[0], player1[1] = [10, 14]
    except IndexError:
            bullets2.remove(bullet)

    try:
        for bullet in bullets_bots[:]:  
            bullet_x, bullet_y, _ = bullet 
            x, y = bullet_x // STEP, bullet_y // STEP  
            if matrix[y][x] == 1:
                bullets_bots.remove(bullet)
                window.blit(images["explosion"], (x * STEP, y * STEP))
                block_sound.play()
                matrix[y][x] = 0
            elif matrix[y][x] == 6:
                bullets_bots.remove(bullet)
                window.blit(images["explosion"], (x * STEP, y * STEP))
                flag_sound.play()
                matrix[y][x] = 7
            elif matrix[y][x] == 2:
                bullets_bots.remove(bullet)
                window.blit(images["explosion1"], (x * STEP, y * STEP))
                block2_sound.play()
            elif [x, y] == [player1[0], player1[1]]:
                bullets_bots.remove(bullet)
                window.blit(images["explosion"], (x * STEP, y * STEP))
                explosion_sound.play()
                player1_lives -= 1
                if player1_lives > 0:
                    player1[0], player1[1] = [10, 14]
            elif [x, y] == [player2[0], player2[1]]:
                bullets_bots.remove(bullet)
                window.blit(images["explosion"], (x * STEP, y * STEP))
                explosion_sound.play()
                player2_lives -= 1
                if player2_lives > 0:
                    player2[0], player2[1] = [14, 14]
    except IndexError:
            bullets_bots.remove(bullet)

def main():   
    matrix = generate_matrix()

    # Початкові позиції танків
    player1 = [10, 14]
    player2 = [14, 14]
    direction1 = "UP"  # Початковий напрямок танків
    direction2 = "UP"  
    bullets1 = [] # Списки куль
    bullets2 = []
    bullets_bots = []
    bots = [[5, 2, "DOWN"], [18, 2, "DOWN"], [11, 2, "DOWN"]]  
    max_bots = 4 # Максимальна кількість появ ботів
    bot_spawns = 0  # Кількість появ ботів
    last_bot_spawn_time = time.time()  # Час останньої появи бота
    bot_spawn_delay = 10  # Затримка між появою ботів
    bot_move_counter = 0
    player1_lives = 5
    player2_lives = 5
    clock = pygame.time.Clock()  # Таймер для гри
    running = True
    last_shot1 = False
    last_shot2 = False
    SPEED = 5
    while running:
        window.fill((0, 0, 0))  # Очищаєм екран
        draw_matrix(matrix, window, STEP, images)  # Малюєм поле

        # Відображення танків 
        window.blit(pygame.transform.rotate(images["tank1"], {"UP": 0, "DOWN": 180, "LEFT": 90, "RIGHT": 270}[direction1]), 
                    (player1[0] * STEP, player1[1] * STEP))  
        window.blit(pygame.transform.rotate(images["tank2"], {"UP": 0, "DOWN": 180, "LEFT": 90, "RIGHT": 270}[direction2]), 
                    (player2[0] * STEP, player2[1] * STEP)) 
        
        # Відображення ботів
        for bot in bots:
            window.blit(pygame.transform.rotate(images["bot"], {"UP": 0, "DOWN": 180, "LEFT": 90, "RIGHT": 270}[bot[2]]), 
                        (bot[0] * STEP, bot[1] * STEP))

        # Поява ботів з затримкою
        if time.time() - last_bot_spawn_time > bot_spawn_delay and bot_spawns < max_bots:
            bots.append([random.choice([2, 12, 22]), 1, random.choice(["UP", "DOWN", "LEFT", "RIGHT"])])  # Спавн бота в випадковому місці
            bot_spawns += 1
            last_bot_spawn_time = time.time()  # Оновлюємо час появи

        # Рух ботів і стрільба
        if len(bots)>0 and bot_move_counter % 10 == 0: 
            move_bots(bots, matrix, player1, player2)
            bots_fire(bots, bullets_bots)
            bot_move_counter += SPEED
        else:
            bot_move_counter += SPEED


        move_bullets(bullets1, bullets2, bullets_bots, matrix, window, images, STEP)
        bullet_collision(bullets1, bullets2, bullets_bots, matrix, bots, player1, player2, player1_lives, player2_lives)

        pygame.display.update()  # Оновлюємо екран
        clock.tick(10)  # Кількість кадрів на секунду
        bot_move_counter += SPEED  # Оновлюємо лічильник руху ботів

        # варіанти закінчення гри
        if not bots:
            game_win_sound.play()
            window.fill((0, 0, 0))
            game_over_image = pygame.image.load("image/boom/game_over.png")  
            game_over_image = pygame.transform.scale(game_over_image, (1200, 800))
            window.blit(game_over_image, (0, 0))
            pygame.display.update()
            pygame.time.delay(int(game_win_sound.get_length() * 1000)) 
            running = False
        if player1_lives <= 0 and player2_lives <= 0:
            game_over_sound.play()
            window.fill((0, 0, 0))
            game_over_image = pygame.image.load("image/boom/game_over.png")  
            game_over_image = pygame.transform.scale(game_over_image, (1200, 800))
            window.blit(game_over_image, (0, 0))
            pygame.display.update()
            pygame.time.delay(int(game_over_sound.get_length() * 1000))  
            running = False
        if any(7 in row for row in matrix): 
            game_over_sound.play()
            window.fill((0, 0, 0))
            game_over_image = pygame.image.load("image/boom/game_over.png")  
            game_over_image = pygame.transform.scale(game_over_image, (1200, 800))
            window.blit(game_over_image, (0, 0))
            pygame.display.update()
            pygame.time.delay(int(game_over_sound.get_length() * 1000)) 
            running = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Закриття вікна
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    last_shot1 = fire_bullet(player1, direction1, bullets1, last_shot1)  # Постріл танка 
                    shot_sound.play()
                elif event.key == pygame.K_SPACE:
                    last_shot2 = fire_bullet(player2, direction2, bullets2, last_shot2)  
                    shot_sound.play()
        
        # управління танками
        keys = pygame.key.get_pressed()  
        if keys[pygame.K_w]:
            tank_move_sound.play()
            if direction1!= "UP":
                direction1 = "UP"
            else:
                player1 = list(move_tank(matrix, player1, "UP", player1, player2, bots))  # Рух танка 1 вгору
        if keys[pygame.K_s]:
            tank_move_sound.play()
            if direction1!= "DOWN":
                direction1 = "DOWN"
            else:
                player1 = list(move_tank(matrix, player1, "DOWN", player1, player2, bots))  # Рух танка 1 вниз
        if keys[pygame.K_a]:
            tank_move_sound.play()
            if direction1!= "LEFT":
                direction1 = "LEFT"
            else:
                player1 = list(move_tank(matrix, player1, "LEFT", player1, player2, bots))  # Рух танка 1 вліво
        if keys[pygame.K_d]:
            tank_move_sound.play()
            if direction1!= "RIGHT":
                direction1 = "RIGHT"
            else:
                player1 = list(move_tank(matrix, player1, "RIGHT", player1, player2, bots))  # Рух танка 1 вправо
             

        if keys[pygame.K_UP]:
            tank_move_sound.play()
            if direction2!= "UP":
                direction2 = "UP"
            else:
                player2 = list(move_tank(matrix, player2, "UP", player1, player2, bots))  
        if keys[pygame.K_DOWN]:
            tank_move_sound.play()
            if direction2!= "DOWN":
                direction2 = "DOWN"
            else:
                player2 = list(move_tank(matrix, player2, "DOWN", player1, player2, bots)) 
        if keys[pygame.K_LEFT]:
            tank_move_sound.play()
            if direction2!= "LEFT":
                direction2 = "LEFT"
            else:
                player2 = list(move_tank(matrix, player2, "LEFT", player1, player2, bots))  
        if keys[pygame.K_RIGHT]:
            tank_move_sound.play()
            if direction2!= "RIGHT":
                direction2 = "RIGHT"
            else: 
                player2 = list(move_tank(matrix, player2, "RIGHT", player1, player2, bots))  
           

    pygame.quit() # завершення гри
    pygame.mixer.quit()

# Запуск гри
if __name__ == "__main__":
    main()