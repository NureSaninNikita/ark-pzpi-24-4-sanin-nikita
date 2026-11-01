import pygame
from settings import *

class GameRenderer:
    def __init__(self, screen, font, ui_font, big_font):
        self.screen = screen
        self.font = font
        self.ui_font = ui_font
        self.big_font = big_font

    def draw_game(self, camera, field, player, enemies, turn, log, selected_spell, game_over, victory, coins):
        screen_w, screen_h = self.screen.get_size()
        self.screen.fill(COLOR_BG)

        current_tile_size = TILE_SIZE * camera.zoom

        for y, row in enumerate(field.grid):
            for x, cell in enumerate(row):
                sx, sy = camera.world_to_screen(x, y)
                if -current_tile_size < sx < screen_w and -current_tile_size < sy < screen_h:
                    rect = (sx, sy, current_tile_size + 1, current_tile_size + 1)
                    if cell == 1:
                        pygame.draw.rect(self.screen, (100, 100, 100), rect)
                    else:
                        pygame.draw.rect(self.screen, COLOR_GRID, rect, 1)

        self._draw_entity(player, COLOR_PLAYER, camera, current_tile_size)
        for e in enemies:
            if e.hp > 0: self._draw_entity(e, (200, 50, 50), camera, current_tile_size)

        self._draw_ui(screen_w, screen_h, player, turn, log, selected_spell)

        coin_text = self.ui_font.render(f"Монети: {coins}", True, (255, 215, 0))
        self.screen.blit(coin_text, (screen_w - coin_text.get_width() - 20, 20))

        if game_over:
            self._draw_game_over(screen_w, screen_h, victory)

    def _draw_entity(self, entity, default_color, camera, size):
        sx, sy = camera.world_to_screen(entity.x, entity.y)

        if -size < sx < self.screen.get_width() and -size < sy < self.screen.get_height():
            color = getattr(entity, 'color', default_color)

            scale = getattr(entity, 'scale', 0.8)

            entity_pixel_size = size * scale

            offset = (size - entity_pixel_size) / 2

            rect = (sx + offset, sy + offset, entity_pixel_size, entity_pixel_size)
            pygame.draw.rect(self.screen, color, rect)

            pct = max(0, entity.hp / entity._max_hp)
            hp_y = sy + offset - 6
            pygame.draw.rect(self.screen, (0, 255, 0), (sx + offset, hp_y, entity_pixel_size * pct, 4))

    def _draw_ui(self, sw, sh, player, turn, log, selected_spell):
        ui_y_start = sh - UI_HEIGHT
        skill_width = sw - 140

        pygame.draw.rect(self.screen, COLOR_UI_BG, (0, ui_y_start, sw, UI_HEIGHT))
        pygame.draw.line(self.screen, COLOR_UI_BORDER, (0, ui_y_start), (sw, ui_y_start), 3)

        self.screen.blit(self.ui_font.render(f"ХП: {player.hp}", True, COLOR_UI_TEXT_RED), (20, ui_y_start + 5))
        self.screen.blit(self.ui_font.render(f"АП: {player.ap}", True, COLOR_UI_TEXT_RED), (150, ui_y_start + 5))

        btn_end = pygame.Rect(skill_width, ui_y_start, 140, UI_HEIGHT)
        pygame.draw.rect(self.screen, COLOR_UI_BG, btn_end)
        pygame.draw.rect(self.screen, COLOR_UI_BORDER, btn_end, 3)
        txt = self.ui_font.render("Закінчити хід", True, COLOR_UI_TEXT_RED)
        self.screen.blit(txt, (btn_end.centerx - txt.get_width() // 2, btn_end.centery))

        grid_y = ui_y_start + 25
        grid_cols = 6
        col_w = skill_width // grid_cols
        row_h = (UI_HEIGHT - 25) // 2

        for c in range(grid_cols + 1):
            lx = c * col_w
            pygame.draw.line(self.screen, COLOR_UI_BORDER, (lx, grid_y), (lx, sh), 2)
        # Горизонтальні лінії
        pygame.draw.line(self.screen, COLOR_UI_BORDER, (0, grid_y), (skill_width, grid_y), 2)
        pygame.draw.line(self.screen, COLOR_UI_BORDER, (0, grid_y + row_h), (skill_width, grid_y + row_h), 2)
        pygame.draw.line(self.screen, COLOR_UI_BORDER, (0, sh - 2), (skill_width, sh - 2), 2)

        spells_to_draw = [
            ("Fireball", "(2 АП)", 0, 0),
            ("Heal", "(1 АП)", 1, 0),
            ("IceShard", "(1 АП)", 2, 0),
            ("Lightning", "(2 АП)", 3, 0)
        ]

        for name, cost_txt, col, row in spells_to_draw:
            btn_rect = pygame.Rect(col * col_w, grid_y + row * row_h, col_w, row_h)

            if selected_spell == name:
                s = pygame.Surface(btn_rect.size);
                s.set_alpha(80);
                s.fill(COLOR_PLAYER)
                self.screen.blit(s, btn_rect.topleft)

            t1 = self.ui_font.render(name, True, COLOR_UI_TEXT_RED)
            t2 = self.ui_font.render(cost_txt, True, COLOR_UI_TEXT_RED)
            self.screen.blit(t1, (btn_rect.centerx - t1.get_width() // 2, btn_rect.centery - 10))
            self.screen.blit(t2, (btn_rect.centerx - t2.get_width() // 2, btn_rect.centery + 5))

        # Лог
        for i, msg in enumerate(log[-3:]):
            t = self.font.render(f"> {msg}", True, (255, 255, 255))
            self.screen.blit(t, (20, ui_y_start - 30 - (2 - i) * 20))

    def _draw_game_over(self, sw, sh, victory):
        overlay = pygame.Surface((sw, sh));
        overlay.set_alpha(150);
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        txt = "ПЕРЕМОГА!" if victory else "ПОРАЗКА"
        col = (0, 255, 0) if victory else (255, 0, 0)
        st = self.big_font.render(txt, True, col)
        self.screen.blit(st, (sw // 2 - st.get_width() // 2, sh // 2 - 50))
        ht = self.font.render("Натисніть SPACE", True, (255, 255, 255))
        self.screen.blit(ht, (sw // 2 - ht.get_width() // 2, sh // 2 + 20))