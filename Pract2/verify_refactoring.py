"""Run with Python 3.8+: python verify_refactoring.py. Pygame is not required."""
from pathlib import Path
from types import SimpleNamespace
import ast
import itertools
import json
import textwrap

ROOT = Path(__file__).resolve().parent

def method_source(file, class_name, method_name):
    tree = ast.parse(file.read_text(encoding="utf-8"))
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == class_name)
    method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == method_name)
    lines = file.read_text(encoding="utf-8").splitlines()
    return textwrap.dedent("\n".join(lines[method.lineno - 1:method.end_lineno]))

class Orc:
    def __init__(self, x, y):
        self.x, self.y = x, y

class Goblin(Orc):
    pass

class SpawnField:
    def __init__(self):
        self.calls = []
    def get_valid_spawn(self, used):
        self.calls.append(sorted(used))
        return next((x, 1) for x in range(20) if (x, 1) not in used)

before_source = (ROOT / "before/game_loop.py").read_text(encoding="utf-8")
block = textwrap.dedent("\n".join(before_source.splitlines()[30:39]))
namespace = {"Orc": Orc, "Goblin": Goblin}
exec("def original_spawn(field, used_pos):\n" + textwrap.indent(block, "    ") + "\n    return enemies", namespace)
after_source = (ROOT / "after/game_loop.py").read_text(encoding="utf-8")
helper = next(n for n in ast.parse(after_source).body if isinstance(n, ast.FunctionDef) and n.name == "create_enemies")
helper_source = "\n".join(after_source.splitlines()[helper.lineno - 1:helper.end_lineno])
exec(helper_source, namespace)
for initial in [set(), {(1, 1)}, {(0, 1), (1, 1), (3, 1)}]:
    first, second = SpawnField(), SpawnField()
    used_first, used_second = initial.copy(), initial.copy()
    a = namespace["original_spawn"](first, used_first)
    b = namespace["create_enemies"](second, used_second)
    assert [(type(e), e.x, e.y) for e in a] == [(type(e), e.x, e.y) for e in b]
    assert used_first == used_second and first.calls == second.calls

class DrawRecorder:
    def __init__(self):
        self.calls = []
    def rect(self, screen, color, rect):
        self.calls.append((color, rect))

recorder = DrawRecorder()
namespace = {"pygame": SimpleNamespace(draw=recorder)}
for version, class_name in [("before", "Before"), ("after", "After")]:
    file = ROOT / version / "renderer.py"
    source = "class " + class_name + ":\n" + textwrap.indent(method_source(file, "GameRenderer", "_draw_entity"), "    ")
    if version == "after":
        source += "\n" + textwrap.indent(method_source(file, "GameRenderer", "_health_ratio"), "    ")
    exec(source, namespace)
screen = SimpleNamespace(get_width=lambda: 800, get_height=lambda: 600)
camera = SimpleNamespace(world_to_screen=lambda x, y: (x * 40, y * 40))
for hp in [-10, 0, 1, 40, 80, 100, 160]:
    entity = SimpleNamespace(x=2, y=3, hp=hp, _max_hp=80)
    first, second = namespace["Before"](), namespace["After"]()
    first.screen = second.screen = screen
    recorder.calls = []
    first._draw_entity(entity, (255, 0, 0), camera, 40)
    expected = recorder.calls.copy()
    recorder.calls = []
    second._draw_entity(entity, (255, 0, 0), camera, 40)
    assert recorder.calls == expected

before, after, position = {}, {}, {}
exec((ROOT / "before/physics.py").read_text(encoding="utf-8"), before)
exec((ROOT / "after/physics.py").read_text(encoding="utf-8"), after)
exec((ROOT / "after/position.py").read_text(encoding="utf-8"), position)
Position = position["Position"]
positions = list(itertools.product(range(5), repeat=2))
visibility_count = 0
for walls in [set(), {(2, 2)}, {(1, 1), (2, 2), (3, 3)}, {(2, y) for y in range(5)}]:
    for start, end in itertools.product(positions, repeat=2):
        first_calls, second_calls = [], []
        first = SimpleNamespace(is_wall=lambda x, y: (first_calls.append((x, y)) or (x, y) in walls))
        second = SimpleNamespace(is_wall=lambda x, y: (second_calls.append((x, y)) or (x, y) in walls))
        expected = before["Physics"].has_line_of_sight(*start, *end, first)
        actual = after["Physics"].has_line_of_sight(Position(*start), Position(*end), second)
        assert expected == actual and first_calls == second_calls
        visibility_count += 1
result = {"spawn_cases": 3, "drawing_cases": 7, "visibility_cases": visibility_count,
          "total": 10 + visibility_count, "status": "passed", "scope": "isolated fragments; no game window"}
print(json.dumps(result, ensure_ascii=False, indent=2))
