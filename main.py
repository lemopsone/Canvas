import bin.geometry as canvas


def main():
    #  initial placement
    b = canvas.Board()
    circle = canvas.Circle(5, 5, 5)
    moving_circle = canvas.MovingCircle(25, 25, 5, 45, 1)
    point = canvas.Point(30, 30)
    moving_point = canvas.MovingPoint(25, 25, 90, 2)
    while True:
        moving_point.move()
        moving_circle.move()
        b.update()


if __name__ == "__main__":
    main()
