import enemy

bg_size = width, height = 1200, 600


def add_small_enemies(group1, group2, num):
    for i in range(num):
        e1 = enemy.SmallEnemy(bg_size)
        group1.add(e1)
        group2.add(e1)


def add_mid_enemies(group1, group2, num):
    for i in range(num):
        e2 = enemy.MidEnemy(bg_size)
        group1.add(e2)
        group2.add(e2)


def add_big_enemies(group1, group2, num):
    for i in range(num):
        e3 = enemy.BigEnemy(bg_size)
        group1.add(e3)
        group2.add(e3)


def add_plus_enemies(group1, group2, num):
    for i in range(num):
        e4 = enemy.PlusEnemy(bg_size)
        group1.add(e4)
        group2.add(e4)


def inc_speed(target, inc):
    for each in target:
        each.speed += inc
