import pygame

from ui.renderer import Renderer
from importlib import import_module

ItemSlot = import_module("ui.global.item_slot").ItemSlot
ItemWindow = import_module("ui.global.item_window").ItemWindow
CurrencyBar = import_module("ui.global.currency_bar").CurrencyBar


class SynthesisPanel(Renderer):
    """합성 입력 슬롯과 합성 결과 미리보기를 표시한다."""

    draw_layer = -5

    def __init__(self, scene, panel_rect, main_getter, material_getter, on_clear,
                 result_getter, result_colors_getter,
                 cost_getter, balance_getter):
        super().__init__(scene, *panel_rect.center, *panel_rect.size)
        self.visible = False
        self.main_getter = main_getter
        self.result_getter = result_getter
        self.cost_getter = cost_getter
        self.balance_getter = balance_getter
        self.cost_icon = CurrencyBar.get_icon("harmony_stone", size=18)
        self.material_getter = material_getter
        self.label_font = scene.slot_label_font
        self.text_font = scene.item_font
        self.slots = []
        for index, callback in enumerate((None, on_clear, None)):
            slot = ItemSlot(
                scene, "", "", panel_rect.left + 106 + index * 170,
                panel_rect.top + 190, 104, 104, on_click=callback,
            )
            self.slots.append(slot)
        self.info_rect = pygame.Rect(
            panel_rect.left + 570, panel_rect.top + 112, 344, 281
        )
        self.result_window = ItemWindow(
            scene, result_getter, width=self.info_rect.width,
            height=self.info_rect.height,
            detail_colors_getter=result_colors_getter,
            scrollable=True,
        )
        self.result_window.set_transform(*self.info_rect.center)
        self.result_window.renderer.draw_layer = 0
        self.set_visible(False)

    def set_visible(self, visible):
        self.visible = visible
        self.result_window.visible = visible
        for slot in self.slots:
            slot.set_visible(visible)

    def draw(self, screen):
        if not self.visible:
            return
        shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        shade.fill((4, 7, 11, 170))
        screen.blit(shade, (0, 0))
        pygame.draw.rect(screen, (22, 28, 36), self.rect, border_radius=8)
        pygame.draw.rect(screen, (132, 148, 164), self.rect, 2, border_radius=8)
        title = self.scene.title_font.render("장비 합성", True, (232, 238, 243))
        title_bounds = title.get_bounding_rect()
        screen.blit(title, (self.rect.left + 32 - title_bounds.left,
                            self.rect.top + 36 - title_bounds.centery))
        pygame.draw.line(screen, (105, 119, 133),
                         (self.rect.left + 30, self.rect.top + 72),
                         (self.rect.right - 30, self.rect.top + 72), 2)
        for slot, item in zip(
            self.slots, (self.main_getter(), self.material_getter(), self.result_getter())
        ):
            slot.set_text("재료 선택" if item is None else "", item_instance=item)
        result_label = "합성 결과" if self.material_getter() is not None else "현재 장비"
        for slot, label in zip(self.slots, ("메인 장비", "재료 장비", result_label)):
            text = self.label_font.render(label, True, (232, 238, 243))
            screen.blit(text, text.get_rect(midbottom=(slot.rect.centerx, slot.rect.top - 14)))
        for index, symbol in enumerate(("+", "→")):
            text = self.label_font.render(symbol, True, (153, 205, 245))
            screen.blit(text, text.get_rect(center=(self.rect.left + 191 + index * 170,
                                                    self.rect.top + 190)))
        guide = self.text_font.render("장비 클릭으로 선택 · 재료 칸 클릭으로 해제", True, (174, 187, 199))
        screen.blit(guide, (self.rect.left + 176, self.rect.top + 383))
        cost = self.cost_getter()
        balance = self.balance_getter()
        cost_text = self.label_font.render(
            f"{cost:,}",
            True, (255, 130, 130) if cost > balance else (235, 240, 245),
        )
        cost_width = 22 + cost_text.get_width()
        cost_left = self.rect.left + 361 - cost_width // 2
        cost_y = self.rect.top + 158
        screen.blit(self.cost_icon, self.cost_icon.get_rect(center=(cost_left + 9, cost_y)))
        screen.blit(cost_text, cost_text.get_rect(midleft=(cost_left + 22, cost_y)))
        heading = self.label_font.render(result_label + " 정보", True, (232, 238, 243))
        screen.blit(heading, (self.info_rect.left, self.rect.top + 82))
        status = "재료 장비를 선택해 주세요" if self.material_getter() is None else "합성 시 재료 장비가 소모됩니다"
        if self.material_getter() is not None and cost > balance:
            status = "조화석이 부족합니다"
        text = self.text_font.render(status, True, (255, 130, 130) if cost > balance else (174, 187, 199))
        screen.blit(text, text.get_rect(center=(self.rect.left + 276, self.rect.top + 315)))
        for x, label, color in (
            (54, "강화", (100, 230, 140)),
            (134, "유지", (240, 244, 247)),
            (214, "추가", (255, 220, 90)),
            (294, "메인 레벨 유지", (255, 110, 110)),
        ):
            text = self.text_font.render("● " + label, True, color)
            screen.blit(text, (self.rect.left + x, self.rect.top + 340))
        pygame.draw.line(screen, (60, 74, 88),
                         (self.rect.left + 54, self.rect.top + 374),
                         (self.rect.left + 510, self.rect.top + 374))
        title = self.label_font.render("인벤토리", True, (232, 238, 243))
        screen.blit(title, (self.rect.left + 75, self.rect.top + 382))

    def destroy(self):
        self.result_window.destroy()
        for slot in self.slots:
            slot.destroy()
        super().destroy()
