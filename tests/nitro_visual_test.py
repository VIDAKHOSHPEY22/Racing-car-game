import pygame as pg
from game.game import Game

pg.init()
try:
    pg.display.init()
    pg.display.set_mode((1,1))
except Exception:
    pass

g = Game()
# initial values
g.nitro_charge = 40.0
g.nitro_display_charge = 40.0

# simulate collect
p = type('P', (), {'charge_value': 34.0})()
now = pg.time.get_ticks()
g.collect_nitro_pickup(p, now)
print('after_collect', g.nitro_charge, round(g.nitro_display_charge, 3), round(getattr(g, 'nitro_display_pulse', 0.0), 3))
# simulate a few ticks
for i in range(1, 11):
    dt = 0.05
    g.update_nitro_boost(now + i * 50, dt)
    print('tick', i, round(g.nitro_display_charge, 3), round(getattr(g, 'nitro_display_pulse', 0.0), 3))

print('done')
