import pygame
from utils import add_log, game_log
from mage import Mage
from enemies.orc import Orc
from enemies.goblin import Goblin
from camera import Camera
from field import GameField
from physics import Physics
from renderer import GameRenderer
from input_manager import InputManager
from player_data import player_data


def play_level(root_screen, level_filename):
    fonts = (
        pygame.font.SysFont('Arial', 18),
        pygame.font.SysFont('Arial', 16, bold=True),
        pygame.font.SysFont('Arial', 60, bold=True)
    )
    camera = Camera()
    field = GameField(level_filename)
    renderer = GameRenderer(root_screen, *fonts)
    input_mgr = InputManager(camera)

    used_pos = set()
    px, py = 1, 1
    if field.is_wall(px, py): px, py = field.get_valid_spawn(used_pos)
    player = Mage(px, py)
    used_pos.add((player.x, player.y))

    enemies = []
    for i in range(3):
        ex, ey = field.get_valid_spawn(used_pos)
        if i % 2 == 0:
            new_enemy = Orc(ex, ey)
        else:
            new_enemy = Goblin(ex, ey)
        enemies.append(new_enemy)
        used_pos.add((ex, ey))

    turn = 1
    selected_spell = None
    game_over = False
    victory = False
    coins_awarded = False
    game_log.clear()
    add_log(f"Рівень: {level_filename}")
    clock = pygame.time.Clock()
    running = True

    while running:
        input_mgr.process_camera_keys()
        for event in pygame.event.get():
            if event.type == pygame.QUIT: return "QUIT"
            action = input_mgr.handle_event(event, root_screen.get_size())

            if action == "MENU": return "MENU"
            if game_over and action == "SPACE": return "MENU"

            if not game_over:
                dx, dy = 0, 0
                if action == "MOVE_UP":
                    dy = -1
                elif action == "MOVE_DOWN":
                    dy = 1
                elif action == "MOVE_LEFT":
                    dx = -1
                elif action == "MOVE_RIGHT":
                    dx = 1

                if (dx or dy) and player.ap > 0:
                    nx, ny = player.x + dx, player.y + dy
                    if Physics.check_move(nx, ny, field, enemies):
                        player.x, player.y = nx, ny
                        player.ap -= 1

                if action == "BTN_END_TURN":
                    turn += 1
                    player.ap = player.max_ap
                    add_log(f"--- Хід {turn} ---")
                    for e in enemies: e.ai_move(player, field.grid, enemies)

                elif action == "BTN_FIREBALL":
                    selected_spell = "Fireball"
                    add_log("Обрано: Fireball")
                elif action == "BTN_HEAL":
                    selected_spell = "Heal"
                    add_log("Обрано: Heal")
                elif action == "BTN_ICESHARD":
                    selected_spell = "IceShard"
                    add_log("Обрано: IceShard")
                elif action == "BTN_LIGHTNING":
                    selected_spell = "Lightning"
                    add_log("Обрано: Lightning")

                elif isinstance(action, tuple) and action[0] == "CLICK_WORLD":
                    gx, gy = action[1], action[2]

                    if selected_spell == "Fireball":
                        target = next((e for e in enemies if e.x == gx and e.y == gy and e.hp > 0), None)
                        if target:
                            player.cast_spell("Fireball", target, field)
                            selected_spell = None
                    elif selected_spell == "IceShard":
                        target = next((e for e in enemies if e.x == gx and e.y == gy and e.hp > 0), None)
                        if target:
                            player.cast_spell("IceShard", target, field)
                            selected_spell = None
                    elif selected_spell == "Lightning":
                        target = next((e for e in enemies if e.x == gx and e.y == gy and e.hp > 0), None)
                        if target:
                            player.cast_spell("Lightning", target, field)
                            selected_spell = None
                    elif selected_spell == "Heal":
                        if gx == player.x and gy == player.y:
                            player.cast_spell("Heal", player, field)
                            selected_spell = None
                        else:
                            add_log("Клікніть на себе!")
                    elif player.ap > 0 and (abs(player.x - gx) + abs(player.y - gy) == 1):
                        if Physics.check_move(gx, gy, field, enemies):
                            player.x, player.y = gx, gy
                            player.ap -= 1

        if not game_over:
            if player.hp <= 0: game_over = True; victory = False; add_log("Ви програли.")
            if not [e for e in enemies if e.hp > 0]:
                game_over = True;
                victory = True;
                add_log("Перемога!")

        if game_over and victory and not coins_awarded:
            player_data.coins += 1
            add_log(f"Отримано монету! Всього: {player_data.coins}")
            coins_awarded = True

        renderer.draw_game(camera, field, player, enemies, turn, game_log, selected_spell, game_over, victory,
                           player_data.coins)
        pygame.display.flip()
        clock.tick(60)