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
# simulate ticks until zero
steps = 0
while getattr(g, 'nitro_display_charge', 0.0) > 0.0 and steps < 2000:
    steps += 1
    dt = 0.05
    g.update_nitro_boost(now + steps * 50, dt)
    if steps % 50 == 0:
        print('tick', steps, round(g.nitro_display_charge, 3), round(getattr(g, 'nitro_display_pulse', 0.0), 3))

print('final', steps, round(g.nitro_display_charge, 3))
