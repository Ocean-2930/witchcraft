import pygame

from ui.renderer import Renderer
from importlib import import_module

ItemSlot = import_module("ui.global.item_slot").ItemSlot
ItemWindow = import_module("ui.global.item_window").ItemWindow


class SynthesisPanel(Renderer):
    """합성 입력 슬롯과 원본 장비의 결과 미리보기를 표시한다."""

    draw_layer = -5

    def __init__(self, scene, panel_rect, main_getter, material_getter, on_clear):
        super().__init__(scene, *panel_rect.center, *panel_rect.size)
        self.visible = False
        self.main_getter = main_getter
        self.material_getter = material_getter
        self.label_font = scene.slot_label_font
        self.text_font = scene.item_font
        self.slots = []
        for index, callback in enumerate((None, on_clear, None)):
            slot = ItemSlot(
                scene, "", "", panel_rect.left + 106 + index * 170,
                panel_rect.top + 228, 104, 104, on_click=callback,
            )
            self.slots.append(slot)
        self.info_rect = pygame.Rect(
            panel_rect.left + 570, panel_rect.top + 112, 344, 281
        )
        self.result_window = ItemWindow(
            scene, main_getter, width=self.info_rect.width,
            height=self.info_rect.height,
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
        title = self.label_font.render("장비 합성", True, (232, 238, 243))
        screen.blit(title, (self.rect.left + 54, self.rect.top + 44))
        pygame.draw.line(screen, (105, 119, 133),
                         (self.rect.left + 30, self.rect.top + 104),
                         (self.rect.right - 30, self.rect.top + 104), 2)
        for slot, item in zip(
            self.slots, (self.main_getter(), self.material_getter(), self.main_getter())
        ):
            slot.set_text("", item_instance=item)
        for slot, label in zip(self.slots, ("메인 장비", "재료 장비", "결과")):
            text = self.label_font.render(label, True, (232, 238, 243))
            screen.blit(text, text.get_rect(midbottom=(slot.rect.centerx, slot.rect.top - 14)))
        for index, symbol in enumerate(("+", "→")):
            text = self.label_font.render(symbol, True, (153, 205, 245))
            screen.blit(text, text.get_rect(center=(self.rect.left + 191 + index * 170,
                                                    self.rect.top + 228)))
        guide = self.text_font.render("아래 장비를 눌러 재료 선택 · 재료 칸을 눌러 해제", True, (174, 187, 199))
        screen.blit(guide, (self.rect.left + 54, self.rect.top + 302))
        title = self.label_font.render("인벤토리", True, (232, 238, 243))
        screen.blit(title, (self.rect.left + 75, self.rect.top + 382))

    def destroy(self):
        self.result_window.destroy()
        for slot in self.slots:
            slot.destroy()
        super().destroy()
