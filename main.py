import random
import time
import os
import bin.canvas as canvas


def main():
    #  initial placement
    b = canvas.Board()
    circles = [
        canvas.Circle(random.randrange(3, 48), random.randrange(3, 48), radius=3,
                      color=30 + i % 8) for i in range(10)]
    for circle in circles:
        circle.set_direction(angle=random.randrange(0, 361),
                             velocity=1, bounce=True, )
    while True:
        for circle in circles:
            circle.move_direction()
        b.update()


if __name__ == "__main__":
    main()
