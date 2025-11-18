# core/dialog_scene.py — ФИНАЛЬНАЯ ВЕРСИЯ
# ------------------------------------------------------------
# Поддерживает:
# - Внешний JSON (dialog_script.json)
# - Несколько фонов на сцену
# - Плавные переходы (fade)
# - Печать текста по буквам
# - Меню выбора перед битвой
# - Альтернативную концовку "Падение Империи"
# - Возврат к моменту выбора
# ------------------------------------------------------------

import pygame
import json
import os
from core.battle_scene import run_battle_scene

# ---- Константы оформления ----
FONT_PATH = "assets/fonts/gothic.ttf"
TEXT_COLOR = (20, 10, 0)
SCRIPT_PATH = "assets/data/dialog_script.json"
PANEL_IMAGE = "assets/images/dialog_panel_columns.png"
PANEL_ALPHA = 180
PANEL_HEIGHT = 160
PANEL_BOTTOM_MARGIN = 8
LEFT_MARGIN = 160
RIGHT_MARGIN = 140
TOP_TEXT_OFFSET = 38
LINE_SPACING = 34
TYPE_INTERVAL_MS = 30
FADE_MS = 700


# ---- Загрузка сценария ----
def load_script():
    with open(SCRIPT_PATH, encoding="utf-8") as f:
        return json.load(f)


# ---- Разбивка текста ----
def wrap_text_to_width(text, font, max_width):
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if font.size(test)[0] <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ---- Плавная смена изображений ----
def fade_between(screen, old_img, new_img, duration_ms=FADE_MS):
    clock = pygame.time.Clock()
    steps = max(1, duration_ms // 16)
    for i in range(steps + 1):
        alpha_new = int(255 * (i / steps))
        alpha_old = 255 - alpha_new
        if old_img:
            old_img.set_alpha(alpha_old)
            screen.blit(old_img, (0, 0))
        new_img.set_alpha(alpha_new)
        screen.blit(new_img, (0, 0))
        pygame.display.flip()
        clock.tick(60)
    if old_img:
        old_img.set_alpha(None)
    new_img.set_alpha(None)


# ---- Распределение строк по картинкам ----
def build_line_to_image(num_lines, num_images):
    if num_images <= 0:
        return [0] * num_lines
    base = num_lines // num_images
    rem = num_lines % num_images
    res = []
    img_idx = 0
    cutoff = base + (1 if rem > 0 else 0)
    for i in range(num_lines):
        res.append(img_idx)
        if (i + 1) == cutoff and img_idx < num_images - 1:
            img_idx += 1
            rem -= 1
            cutoff += base + (1 if rem > 0 else 0)
    return res


# ---- Основная сцена диалога ----
def run_dialog_scene(screen):
    font = pygame.font.Font(FONT_PATH, 28)
    script = load_script()
    screen_w, screen_h = screen.get_size()

    panel_raw = pygame.image.load(PANEL_IMAGE).convert_alpha()
    panel_surface = pygame.transform.scale(panel_raw, (screen_w, PANEL_HEIGHT))
    panel_surface.set_alpha(PANEL_ALPHA)

    text_rect = pygame.Rect(
        LEFT_MARGIN,
        screen_h - PANEL_HEIGHT - PANEL_BOTTOM_MARGIN + TOP_TEXT_OFFSET,
        screen_w - LEFT_MARGIN - RIGHT_MARGIN,
        PANEL_HEIGHT - TOP_TEXT_OFFSET - 16,
    )

    scene_idx = 0
    while scene_idx < len(script):
        scene = script[scene_idx]
        img_files = scene.get("images", [scene.get("bg")])
        images = [
            pygame.transform.scale(
                pygame.image.load(os.path.join("assets/images", f)).convert(),
                (screen_w, screen_h),
            )
            for f in img_files
        ]

        lines = scene["lines"]
        line_to_image = build_line_to_image(len(lines), len(images))

        fade_between(screen, None, images[line_to_image[0]], FADE_MS)
        cur_img_idx = line_to_image[0]

        line_idx = 0
        while line_idx < len(lines):
            line = lines[line_idx]
            shown = ""
            last_tick = pygame.time.get_ticks()
            typing_done = False
            waiting = True

            target_img_idx = line_to_image[line_idx]
            if target_img_idx != cur_img_idx:
                fade_between(
                    screen, images[cur_img_idx], images[target_img_idx], FADE_MS
                )
                cur_img_idx = target_img_idx

            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        raise SystemExit
                    elif event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                        if not typing_done:
                            shown = line
                            typing_done = True
                        else:
                            waiting = False

                now = pygame.time.get_ticks()
                if not typing_done and (now - last_tick >= TYPE_INTERVAL_MS):
                    next_len = len(shown) + 1
                    shown = line[:next_len]
                    if next_len >= len(line):
                        typing_done = True
                    last_tick = now

                screen.blit(images[cur_img_idx], (0, 0))
                screen.blit(
                    panel_surface, (0, screen_h - PANEL_HEIGHT - PANEL_BOTTOM_MARGIN)
                )

                wrapped = wrap_text_to_width(shown, font, text_rect.width)
                y = text_rect.top
                for txt in wrapped:
                    surf = font.render(txt, True, TEXT_COLOR)
                    screen.blit(surf, (text_rect.left, y))
                    y += LINE_SPACING

                pygame.display.flip()
                pygame.time.delay(10)

            line_idx += 1

        next_scene_idx = scene_idx + 1

        # --- После третьей сцены показываем выбор ---
        if scene["title"] == "Весть о войне":
            choice = show_choice_menu(screen, images[cur_img_idx])
            if choice == "fight":
                run_battle_scene(screen)
            elif choice == "flee":
                # Загружаем сцену "Падение Империи" из JSON
                fall_scene_idx = next(
                    (
                        i
                        for i, s in enumerate(script)
                        if s["title"] == "Падение Империи"
                    ),
                    None,
                )
                if fall_scene_idx is not None:
                    run_specific_scene(screen, script[fall_scene_idx])
                return
            return

        if next_scene_idx < len(script):
            next_scene = script[next_scene_idx]
            next_first_img = next_scene.get("images", [next_scene.get("bg")])[0]
            next_img_surface = pygame.transform.scale(
                pygame.image.load(
                    os.path.join("assets/images", next_first_img)
                ).convert(),
                (screen_w, screen_h),
            )
            fade_between(screen, images[cur_img_idx], next_img_surface, FADE_MS)

        scene_idx += 1


# --- Меню выбора --- #
def show_choice_menu(screen, background):
    font = pygame.font.Font(FONT_PATH, 32)
    w, h = screen.get_size()
    buttons = [
        {"text": "Да, начать приготовление", "value": "fight"},
        {"text": "Нет, тайно покинуть лагерь", "value": "flee"},
    ]
    selected = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % len(buttons)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % len(buttons)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    return buttons[selected]["value"]
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                for i, btn in enumerate(buttons):
                    rect = pygame.Rect(w // 2 - 250, h // 2 - 40 + i * 70, 500, 60)
                    if rect.collidepoint(mx, my):
                        return btn["value"]

        screen.blit(background, (0, 0))
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 130))
        screen.blit(overlay, (0, 0))

        title = font.render("Готовы ли вы защитить империю?", True, (255, 255, 255))
        screen.blit(title, (w // 2 - title.get_width() // 2, h // 2 - 150))

        mx, my = pygame.mouse.get_pos()
        for i, btn in enumerate(buttons):
            rect = pygame.Rect(w // 2 - 250, h // 2 - 40 + i * 70, 500, 60)
            hovered = rect.collidepoint(mx, my)
            color = (255, 215, 120) if hovered else (255, 255, 255)
            surf = font.render(btn["text"], True, color)
            screen.blit(surf, rect)

        pygame.display.flip()
        pygame.time.delay(20)


# --- Отдельная сцена (для концовок) --- #
def run_specific_scene(screen, scene):
    font = pygame.font.Font(FONT_PATH, 28)
    screen_w, screen_h = screen.get_size()

    images = [
        pygame.transform.scale(
            pygame.image.load(os.path.join("assets/images", f)).convert(),
            (screen_w, screen_h),
        )
        for f in scene["images"]
    ]
    line_to_image = build_line_to_image(len(scene["lines"]), len(images))
    fade_between(screen, None, images[line_to_image[0]], FADE_MS)
    cur_img_idx = line_to_image[0]

    for i, line in enumerate(scene["lines"]):
        target_img_idx = line_to_image[i]
        if target_img_idx != cur_img_idx:
            fade_between(screen, images[cur_img_idx], images[target_img_idx], FADE_MS)
            cur_img_idx = target_img_idx

        shown = ""
        last_tick = pygame.time.get_ticks()
        typing_done = False
        waiting = True

        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                elif event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    if not typing_done:
                        shown = line
                        typing_done = True
                    else:
                        waiting = False

            now = pygame.time.get_ticks()
            if not typing_done and now - last_tick >= TYPE_INTERVAL_MS:
                next_len = len(shown) + 1
                shown = line[:next_len]
                if next_len >= len(line):
                    typing_done = True
                last_tick = now

            screen.blit(images[cur_img_idx], (0, 0))
            overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            screen.blit(overlay, (0, 0))

            wrapped = wrap_text_to_width(shown, font, screen_w - 200)
            y = screen_h // 2 - len(wrapped) * 18
            for txt in wrapped:
                surf = font.render(txt, True, (230, 220, 210))
                rect = surf.get_rect(center=(screen_w // 2, y))
                screen.blit(surf, rect)
                y += LINE_SPACING
            pygame.display.flip()
            pygame.time.delay(10)

    black = pygame.Surface((screen_w, screen_h))
    black.fill((0, 0, 0))
    fade_between(screen, images[cur_img_idx], black, 2000)
    show_final_choice(screen)


from core.battle_scene import run_battle_scene


# --- Финальное меню --- #
def show_final_choice(screen):
    w, h = screen.get_size()
    font = pygame.font.Font(FONT_PATH, 36)

    title_text = "Хотите изменить историю?"
    buttons = [
        {"text": "Да, изменить историю", "value": "retry"},
        {"text": "Отстраниться", "value": "exit"},
    ]
    selected = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % len(buttons)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % len(buttons)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if buttons[selected]["value"] == "retry":
                        return return_to_choice(screen)
                    else:
                        pygame.quit()
                        raise SystemExit
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                for i, btn in enumerate(buttons):
                    rect = pygame.Rect(w // 2 - 300, h // 2 - 40 + i * 90, 600, 60)
                    if rect.collidepoint(mx, my):
                        if btn["value"] == "retry":
                            return return_to_choice(screen)
                        else:
                            pygame.quit()
                            raise SystemExit

        screen.fill((0, 0, 0))
        mx, my = pygame.mouse.get_pos()

        # Заголовок (всегда белый, не реагирует)
        title_surf = font.render(title_text, True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(w // 2, h // 2 - 120))
        screen.blit(title_surf, title_rect)

        # Кнопки
        for i, btn in enumerate(buttons):
            rect = pygame.Rect(w // 2 - 300, h // 2 - 40 + i * 90, 600, 60)
            hovered = rect.collidepoint(mx, my)
            color = (255, 215, 120) if hovered else (255, 255, 255)
            surf = font.render(btn["text"], True, color)
            surf_rect = surf.get_rect(center=(w // 2, h // 2 + i * 90))
            screen.blit(surf, surf_rect)

        # Между ними надпись "или"
        or_font = pygame.font.Font(FONT_PATH, 30)
        or_surf = or_font.render("или", True, (200, 200, 200))
        or_rect = or_surf.get_rect(center=(w // 2, h // 2 + 45))
        screen.blit(or_surf, or_rect)

        pygame.display.flip()
        pygame.time.delay(20)


# --- Возврат к моменту выбора --- #
def return_to_choice(screen):
    """Возвращает игрока к сцене выбора 'Готовы ли вы защитить империю?'"""
    w, h = screen.get_size()

    fade = pygame.Surface((w, h))
    fade.fill((0, 0, 0))
    screen.blit(fade, (0, 0))
    pygame.display.flip()
    pygame.time.wait(800)

    background = pygame.image.load("assets/images/persian_3.jpg").convert()
    background = pygame.transform.scale(background, (w, h))
    choice = show_choice_menu(screen, background)

    if choice == "fight":
        run_battle_scene(screen)
    elif choice == "flee":
        script = load_script()
        fall_scene_idx = next(
            (i for i, s in enumerate(script) if s["title"] == "Падение Империи"), None
        )
        if fall_scene_idx is not None:
            run_specific_scene(screen, script[fall_scene_idx])
