import math

class Physics:
    @staticmethod
    def check_move(x, y, field, entities):
        if field.is_wall(x, y):
            return False

        for e in entities:
            if e.hp > 0 and e.x == x and e.y == y:
                return False

        return True

    @staticmethod
    def has_line_of_sight(start, end, field):
        dist = math.sqrt((end.x - start.x) ** 2 + (end.y - start.y) ** 2)
        if dist == 0: return True

        steps = int(dist * 2)

        for i in range(1, steps + 1):
            t = i / steps
            x = start.x + (end.x - start.x) * t
            y = start.y + (end.y - start.y) * t

            ix = int(round(x))
            iy = int(round(y))

            if ix == end.x and iy == end.y:
                return True

            if field.is_wall(ix, iy):
                return False

        return True