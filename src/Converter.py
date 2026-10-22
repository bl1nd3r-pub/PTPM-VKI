class Converter:
    @staticmethod
    def do(x: float) -> int:
        if x >= 100.7:
            return 1000
        elif 0.0 < x < 100.7:
            return int(x)
        elif x == 0.0:
            raise ValueError("А вот ноля тут не надо, ок, да?")
        elif -30.4 <= x < 0.0:
            return int(x) - 5
        elif x < -30.4:
            return -2000