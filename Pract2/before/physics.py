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
    def has_line_of_sight(x0, y0, x1, y1, field):
        dist = math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2)
        if dist == 0: return True

        steps = int(dist * 2)

        for i in range(1, steps + 1):
            t = i / steps
            x = x0 + (x1 - x0) * t
            y = y0 + (y1 - y0) * t

            ix = int(round(x))
            iy = int(round(y))

            if ix == x1 and iy == y1:
                return True

            if field.is_wall(ix, iy):
                return False

        return True