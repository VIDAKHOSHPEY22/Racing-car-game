# atari.py Development Checklist

## Open Issues

- [ ] Web deployment (soon)
- [ ] coin lane dedup
- [ ] lane-stripe period mismatch (should be equal lengths)

## Completed — TheM1ddleM1n

- [x] Speed system implemented
- [x] Basic appearance and visuals added
- [x] Fixed incorrect behavior of passing cars
- [x] Improved overall appearance and visual polish
- [x] Gameplay brought up to Atari standard
- [x] Added obstacles to increase difficulty
- [x] Fixed HUD hearts to display as symbols
- [x] Performance improvements for smoother gameplay
- [x] HUD menu arrow key indicators on boot screen
- [x] Fixed linting errors (E701/E702)
- [x] Added additional car skins
- [x] Added power-ups: shield, magnet, and time freeze
- [x] Removed gameplay bottlenecks
- [x] Fixed coin spawning so coins now spawn randomly across lanes
- [x] Added police car that chases the player
- [x] Added weather effects (rain, fog)
- [x] Added car upgrade system
- [x] Re-randomized coin spawn distribution
- [x] Simplified pause menu (Paused / Return to Main Menu, with Yes/No confirmation)
- [x] Removed day/night cycle (cosmetic-only, no gameplay effect)
- [x] Simplified pause controls to a single key (P); removed ESC as a pause/menu shortcut
- [x] Pre-rendered power-up icon labels at creation instead of caching by label at draw time
- [x] Fixed police escape bonus condition so it always awards on a successful escape
- [x] Raised HUD speed bar cap to reflect true max scroll speed (was visually maxing out early)
- [x] Removed police car chase mechanic to simplify core gameplay loop
- [x] Removed Magnet power-up, keeping Shield and Time Freeze
- [x] Removed screen shake effect on collisions and speed bump events
- [x] Removed fog weather and the Speed Bump hazard
- [x] Reduced particle pool size from 300 to 150 to match trimmed effect set
- [x] Corrected README "Responsive UI" claim, since window size is fixed at 800x600
- [x] Removed Cone hazard because it duplicated Barrier gameplay

## Completed — VIDAKHOSHPEY22

- [x] Complete sound system with 5 audio effects using NumPy
- [x] Particle effects for explosions, coin collection, and boost trails
- [x] Boost mechanic activated with the Space key (costs 50 points)
- [x] Screen shake effect on collisions and speed bump events
- [x] Responsive UI layout for all screen resolutions
- [x] Speed bonus display in the car selection menu
- [x] Custom-drawn arrows replacing broken Unicode arrow characters
- [x] Fixed car positioning within the menu selection box
- [x] Road lines now scroll downward to reinforce sense of speed
- [x] Boost glow effect rendered around the player car
- [x] Random free boost reward on coin collection

## Known Limitations (No issues)

- Garage and Game Over screens are mouse-only for navigation; no keyboard shortcut exists to back out of them aside from `R` (restart) on Game Over.
- Window size is fixed at 800x600 and does not currently support live resizing.

## Contact

- Email: vidatwin18@gmail.com
- GitHub: @TheM1ddleM1n or @VIDAKHOSHPEY22

## Contributors

- **TheM1ddleM1n** — Original base game, bug fixes, performance improvements
- **VIDAKHOSHPEY22** — Sound system, particle effects, boost mechanic, responsive UI
