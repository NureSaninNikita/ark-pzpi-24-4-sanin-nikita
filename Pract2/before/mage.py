from entity import Entity
from effects.spell_data import SPELL_BOOK
from effects.slow import SlowEffect
from physics import Physics
import math
from player_data import player_data

class Mage(Entity):
    def __init__(self, x, y):
        my_color = player_data.get_current_color_rgb()
        super().__init__(x, y, hp=80, max_ap=4, name="High Mage")
        self.color = my_color

    def cast_spell(self, spell_name, target, field):
        spell = SPELL_BOOK.get(spell_name)
        if not spell: return
        if self.ap < spell['ap_cost']:
            self.log("Недостатньо AP!")
            return
        dist = math.sqrt((self.x - target.x) ** 2 + (self.y - target.y) ** 2)
        if dist > spell['range']:
            self.log("Ціль занадто далеко!")
            return
        if target != self and not spell.get('ignore_walls', False):
            if not Physics.has_line_of_sight(self.x, self.y, target.x, target.y, field):
                self.log("Стіна заважає!")
                return
        self.ap -= spell['ap_cost']
        target.hp -= spell['damage']
        if spell['damage'] < 0 and target.hp > target._max_hp:
            target.hp = target._max_hp
        self.log(f"{self.name} кастує {spell_name} в {target.name}")
        if spell_name == "IceShard":
            if hasattr(target, "add_effect"):
                from effects.slow import SlowEffect
                slow = SlowEffect(duration=2)
                target.add_effect(slow)