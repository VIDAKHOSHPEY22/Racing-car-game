import random
import math

import pygame as pg

from . import constants as const

class WeatherManager:
    def __init__(self):
        self.active_weather = ["clear"]
        self.previous_weather_key = "clear"
        self.weather_intensity = {
            "rain": 0.0,
            "snow": 0.0,
            "fog": 0.0,
            "night": 0.0,
        }
        
        self.weather_strength = {
            "rain": 1.0,
            "snow": 1.0,
            "fog": 1.0,
            "night": 1.0,
        }
        self.slip_remainder = 0.0

        self.rain_particles = []
        self.snow_particles = []

        self.lateral_slip_velocity = 0.0
        self.last_input_direction = 0
        self.last_direction_change_time = 0

        self.weather_skid_velocity = 0.0
        self.weather_skid_direction = 0
        self.last_weather_skid_time = 0

        self.last_braking_state = False
        self.last_speed_sample = const.PLAYER_SPEED_DEFAULT

        self.fog_drift_velocity = 0.0
        self.fog_remainder = 0.0
        self.fog_phase = random.uniform(0.0, math.pi * 2)

        self.micro_slip_phase = random.uniform(0.0, math.pi * 2)

        self.alert_message = ""
        self.alert_until = 0

        self._rain_layer = None
        self._wet_overlay = None
        self._snow_layer = None
        self._cold_overlay = None
        self._night_overlay = None
        self._fog_overlay = None
        self._fog_gradient = None
        self._fog_mist_base = None
        self._glow_cache = {}
        self._fog_headlight_mask_cache = {}

    def _ensure_fog_assets(self):
        if self._fog_gradient is None:
            fog = pg.Surface((const.WIDTH, const.HEIGHT), pg.SRCALPHA).convert_alpha()
            base_alpha = 72
            for y in range(0, const.HEIGHT, 16):
                ratio = y / const.HEIGHT
                alpha = int(base_alpha * (1.05 - ratio * 0.35))
                alpha = max(0, min(150, alpha))
                pg.draw.rect(
                    fog,
                    (190, 198, 205, alpha),
                    (0, y, const.WIDTH, 16),
                )
            self._fog_gradient = fog

        if self._fog_mist_base is None:
            mist = pg.Surface((const.WIDTH, const.HEIGHT), pg.SRCALPHA).convert_alpha()
            mist.fill((220, 225, 230, 255))
            self._fog_mist_base = mist

    def reset(self):
        self.active_weather = ["clear"]
        self.previous_weather_key = "clear"
        self.rain_particles.clear()
        self.snow_particles.clear()
        self.lateral_slip_velocity = 0.0
        self.last_input_direction = 0
        self.last_direction_change_time = 0
        self.weather_skid_velocity = 0.0
        self.weather_skid_direction = 0
        self.last_weather_skid_time = 0
        self.last_braking_state = False
        self.last_speed_sample = const.PLAYER_SPEED_DEFAULT

        self.fog_drift_velocity = 0.0
        self.fog_remainder = 0.0
        self.fog_phase = random.uniform(0.0, math.pi * 2)
        self.micro_slip_phase = random.uniform(0.0, math.pi * 2)
        self.alert_message = ""
        self.alert_until = 0
        self.weather_intensity = {
            "rain": 0.0,
            "snow": 0.0,
            "fog": 0.0,
            "night": 0.0,
        }
        self.weather_strength = {
            "rain": 1.0,
            "snow": 1.0,
            "fog": 1.0,
            "night": 1.0,
        }
        self.slip_remainder = 0.0

        

    def update(
        self,
        current_time,
        dt,
        player,
        keys,
        stage,
        stage_progress_ratio,
        selected_difficulty,
        hazard_slip_active=False,
    ):
        self.update_for_stage(
            stage=stage,
            progress_ratio=stage_progress_ratio,
            selected_difficulty=selected_difficulty,
            current_time=current_time,
        )

        self._update_particles(selected_difficulty, dt)
        self._update_weather_intensity(dt)
        self._update_lateral_slip(
            current_time=current_time,
            dt=dt,
            player=player,
            keys=keys,
            selected_difficulty=selected_difficulty,
            hazard_slip_active=hazard_slip_active,
        )

        self._update_fog_uncertainty(
            current_time=current_time,
            dt=dt,
            player=player,
            keys=keys,
            selected_difficulty=selected_difficulty,
            hazard_slip_active=hazard_slip_active,
        )

    def _apply_lateral_pixels(self, player, slip_amount, remainder_attr="slip_remainder"):
        remainder = float(getattr(self, remainder_attr, 0.0))
        total = float(slip_amount) + remainder

        whole_pixels = math.floor(total) if total >= 0 else math.ceil(total)

        left_bound = getattr(player, "road_boundary_left", None)
        right_bound = getattr(player, "road_boundary_right", None)
        hit_boundary = False
        if left_bound is not None and right_bound is not None and whole_pixels != 0:
            if whole_pixels < 0:
                remaining = int(player.x - left_bound)
                if remaining <= 0:
                    whole_pixels = 0
                    hit_boundary = True
                elif abs(whole_pixels) > remaining:
                    whole_pixels = -remaining
                    hit_boundary = True
            else:
                remaining = int(right_bound - player.x)
                if remaining <= 0:
                    whole_pixels = 0
                    hit_boundary = True
                elif whole_pixels > remaining:
                    whole_pixels = remaining
                    hit_boundary = True

        if hit_boundary:
            setattr(self, remainder_attr, 0.0)

            if remainder_attr == "slip_remainder":
                self.weather_skid_velocity *= 0.4
                self.lateral_slip_velocity *= 0.5
            elif remainder_attr == "fog_remainder":
                self.fog_drift_velocity *= 0.5

            return 0

        setattr(self, remainder_attr, total - whole_pixels)
        player.x += whole_pixels
        return whole_pixels

    def _update_fog_uncertainty(
        self,
        current_time,
        dt,
        player,
        keys,
        selected_difficulty,
        hazard_slip_active=False,
    ):
        if hazard_slip_active:
            self.fog_drift_velocity = 0.0
            self.fog_remainder = 0.0
            return

        intensity = float(self.weather_intensity.get("fog", 0.0))
        if intensity < 0.30:
            self.fog_drift_velocity *= max(0.0, 1.0 - 10.0 * dt)
            self.fog_remainder *= max(0.0, 1.0 - 10.0 * dt)
            return

        try:
            speed = float(player.get_velocity())
        except Exception:
            speed = const.PLAYER_SPEED_DEFAULT

        max_speed = self._get_max_speed(selected_difficulty)
        speed_trigger = 0.65 * max_speed
        if speed < speed_trigger:
            self.fog_drift_velocity *= max(0.0, 1.0 - 10.0 * dt)
            return

        speed_factor = (speed - speed_trigger) / max(1.0, (max_speed - speed_trigger))
        speed_factor = max(0.0, min(1.0, speed_factor))

        direction = self._get_input_direction(keys)

        self.fog_phase += dt * (0.9 + 0.7 * speed_factor)
        wander = math.sin(self.fog_phase) * 0.65 + math.sin(self.fog_phase * 0.53 + 1.2) * 0.35

        base = 26.0
        steer_bias = 22.0
        target = (
            (wander * base) + (direction * steer_bias)
        ) * intensity * (0.35 + 0.65 * speed_factor)

        blend = min(1.0, (6.0 + 5.0 * speed_factor) * dt)
        self.fog_drift_velocity += (target - self.fog_drift_velocity) * blend

        cap = 48.0 * intensity * (0.45 + 0.55 * speed_factor)
        self.fog_drift_velocity = max(-cap, min(cap, self.fog_drift_velocity))

        self._apply_lateral_pixels(
            player,
            slip_amount=self.fog_drift_velocity * dt,
            remainder_attr="fog_remainder",
        )

    def _update_weather_intensity(self, dt):
        fade_in_speed = 1.8
        fade_out_speed = 1.4

        for weather_type in self.weather_intensity:
            target = 1.0 if weather_type in self.active_weather else 0.0
            current = self.weather_intensity[weather_type]

            if current < target:
                current = min(target, current + fade_in_speed * dt)
            elif current > target:
                current = max(target, current - fade_out_speed * dt)

            self.weather_intensity[weather_type] = current
    
    def update_for_stage(self, stage, progress_ratio, selected_difficulty, current_time=None):
        progress_ratio = max(0.0, min(1.0, float(progress_ratio)))
        self._update_weather_strength_for_stage(stage, progress_ratio, selected_difficulty)
        new_weather = self._get_weather_for_stage(stage, progress_ratio, selected_difficulty)

        new_key = "+".join(new_weather)
        if new_key != self.previous_weather_key:
            self.active_weather = new_weather
            self.previous_weather_key = new_key

            if current_time is None:
                current_time = pg.time.get_ticks()

            self.alert_message = self._build_alert_message(selected_difficulty)
            self.alert_until = current_time + const.WEATHER_ALERT_DURATION

    def _get_weather_for_stage(self, stage, progress_ratio, selected_difficulty):
        """
        Weather progression:
        Stage 1  -> Clear
        Stage 2  -> Clear -> Rain -> Clear
        Stage 3  -> Clear -> Fog -> Clear
        Stage 4  -> Clear -> Snow / optional Clear ending for Easy
        Stage 5  -> Clear -> Night
        Stage 6  -> Rain
        Stage 7  -> Fog -> Rain + Fog
        Stage 8  -> Night + Rain
        Stage 9  -> Night -> Night + Snow
        Stage 10+ -> Night + Rain + Fog
        """

        difficulty = selected_difficulty if selected_difficulty in const.DIFFICULTY_SETTINGS else const.DEFAULT_DIFFICULTY

        if stage <= 1:
            return ["clear"]

        if stage == 2:
            windows = {
                "Easy": (0.35, 0.65),
                "Medium": (0.30, 0.75),
                "Hard": (0.20, 0.90),
            }
            start, end = windows[difficulty]
            if progress_ratio < start:
                return ["clear"]
            if progress_ratio < end:
                return ["rain"]
            return ["clear"]

        if stage == 3:
            windows = {
                "Easy": (0.35, 0.65),
                "Medium": (0.25, 0.80),
                "Hard": (0.15, 0.90),
            }
            start, end = windows[difficulty]
            if progress_ratio < start:
                return ["clear"]
            if progress_ratio < end:
                return ["fog"]
            return ["clear"]

        if stage == 4:
            if difficulty == "Easy":
                if progress_ratio < 0.30:
                    return ["clear"]
                if progress_ratio < 0.75:
                    return ["snow"]
                return ["clear"]

            if difficulty == "Medium":
                if progress_ratio < 0.25:
                    return ["clear"]
                return ["snow"]

            if progress_ratio < 0.15:
                return ["clear"]
            return ["snow"]

        if stage == 5:
            start = {
                "Easy": 0.35,
                "Medium": 0.30,
                "Hard": 0.20,
            }[difficulty]
            if progress_ratio < start:
                return ["clear"]
            return ["night"]

        if stage == 6:
            start_clear = {
                "Easy": 0.10,
                "Medium": 0.07,
                "Hard": 0.05,
            }[difficulty]
            if progress_ratio < start_clear:
                return ["clear"]
            return ["rain"]

        if stage == 7:
            switch_point = {
                "Easy": 0.60,
                "Medium": 0.50,
                "Hard": 0.40,
            }[difficulty]
            if progress_ratio < switch_point:
                return ["fog"]
            return ["rain", "fog"]

        if stage == 8:
            return ["night", "rain"]

        if stage == 9:
            switch_point = {
                "Easy": 0.50,
                "Medium": 0.40,
                "Hard": 0.30,
            }[difficulty]
            if progress_ratio < switch_point:
                return ["night"]
            return ["night", "snow"]

        intro_clear = {
            "Easy": 0.12,
            "Medium": 0.10,
            "Hard": 0.08,
        }[difficulty]
        if progress_ratio < intro_clear:
            return ["clear"]

        fog_allowed = (stage >= 14) and (difficulty != "Easy")

        breather_enabled = (stage % 2 == 0) and (difficulty != "Hard" or stage < 18)
        if breather_enabled:
            if difficulty == "Easy":
                breather = (0.46, 0.54)
            elif difficulty == "Medium":
                breather = (0.48, 0.54)
            else:
                breather = (0.49, 0.52)
            if breather[0] <= progress_ratio <= breather[1]:
                return ["clear"]

        triple_stage_ok = fog_allowed and (stage >= (15 if difficulty != "Easy" else 18))
        triple_window = (0.88, 0.94)

        pattern = stage % 7

        if (
            triple_stage_ok
            and pattern in (0, 6)
            and triple_window[0] <= progress_ratio <= triple_window[1]
        ):
            return ["night", "rain", "fog"]

        if pattern == 0:
            if progress_ratio < 0.45:
                return ["clear"]
            if progress_ratio < 0.75:
                return ["rain"]
            if fog_allowed and progress_ratio > 0.85:
                return ["night", "rain", "fog"]
            return ["night", "rain"]

        if pattern == 1:
            if progress_ratio < 0.60:
                return ["night"]
            return ["night", "rain"]

        if pattern == 2:
            if progress_ratio < 0.40:
                return ["rain"]
            if progress_ratio < 0.55 and difficulty != "Hard":
                return ["clear"]
            if progress_ratio < 0.78:
                return ["rain"]
            return ["night", "rain"] if difficulty == "Hard" else ["rain"]

        if pattern == 3:
            if progress_ratio < 0.35:
                return ["night"]
            return ["night", "snow"] if difficulty != "Easy" else ["snow"]

        if pattern == 4:
            if progress_ratio < 0.55:
                return ["clear"]
            return ["night"]

        if pattern == 5:
            if progress_ratio < 0.50:
                return ["rain"]
            return ["night"]

        if not fog_allowed:
            if progress_ratio < 0.70:
                return ["rain"]
            return ["night", "rain"] if difficulty == "Hard" else ["rain"]

        if progress_ratio < 0.60:
            return ["fog"]
        if progress_ratio < 0.82:
            return ["fog", "rain"]
        return ["night", "fog"]

    def _update_weather_strength_for_stage(self, stage, progress_ratio, selected_difficulty):
       
        difficulty = (
            selected_difficulty
            if selected_difficulty in const.DIFFICULTY_SETTINGS
            else const.DEFAULT_DIFFICULTY
        )

        self.weather_strength["rain"] = 1.0
        self.weather_strength["snow"] = 1.0
        self.weather_strength["fog"] = 1.0
        self.weather_strength["night"] = 1.0

        if stage != 6:
            return

        start_clear = {
            "Easy": 0.10,
            "Medium": 0.07,
            "Hard": 0.05,
        }[difficulty]

        heavy_start = {
            "Easy": 0.45,
            "Medium": 0.40,
            "Hard": 0.35,
        }[difficulty]

        heavy_end = {
            "Easy": 0.78,
            "Medium": 0.80,
            "Hard": 0.82,
        }[difficulty]

        if progress_ratio < start_clear:
            self.weather_strength["rain"] = 0.0
            return

        if heavy_start <= progress_ratio <= heavy_end:
            self.weather_strength["rain"] = 1.55
        else:
            self.weather_strength["rain"] = 1.10

    def _get_weather_strength(self, weather_type):
        try:
            return float(self.weather_strength.get(weather_type, 1.0))
        except Exception:
            return 1.0

    def _get_difficulty_modifier(self, selected_difficulty):
        return const.WEATHER_DIFFICULTY_MODIFIERS.get(
            selected_difficulty,
            const.WEATHER_DIFFICULTY_MODIFIERS[const.DEFAULT_DIFFICULTY],
        )

    def _get_max_speed(self, selected_difficulty):
        settings = const.DIFFICULTY_SETTINGS.get(
            selected_difficulty,
            const.DIFFICULTY_SETTINGS[const.DEFAULT_DIFFICULTY],
        )
        return float(settings.get("max_speed", const.MAX_SPEED))

    def _get_safe_speed_info(self, selected_difficulty):
        if "snow" in self.active_weather:
            ratios = const.WEATHER_SPEED_LIMIT_RATIOS["snow"]
            max_speed = self._get_max_speed(selected_difficulty)
            return "Snow", max_speed * ratios["safe"], max_speed * ratios["high_risk"]

        if "rain" in self.active_weather:
            ratios = const.WEATHER_SPEED_LIMIT_RATIOS["rain"]
            max_speed = self._get_max_speed(selected_difficulty)
            return "Rain", max_speed * ratios["safe"], max_speed * ratios["high_risk"]

        return None, None, None

    def _build_alert_message(self, selected_difficulty):
        if self.active_weather == ["clear"]:
            return "Weather Clear - Road Conditions Normal"

        weather_name = " + ".join(w.title() for w in self.active_weather)

        road_type, safe_speed, _ = self._get_safe_speed_info(selected_difficulty)
        if road_type and safe_speed is not None:
            return f"{weather_name} - Safe Speed {safe_speed:.0f} km/h"

        if "fog" in self.active_weather and "night" in self.active_weather:
            return f"{weather_name} - Very Low Visibility"

        if "fog" in self.active_weather:
            return "Fog Ahead - Low Visibility"

        if "night" in self.active_weather:
            return "Night Mode - Headlights Active"

        return weather_name

    def _get_input_direction(self, keys):
        left = keys[pg.K_LEFT] or keys[pg.K_a]
        right = keys[pg.K_RIGHT] or keys[pg.K_d]

        if left and not right:
            return -1
        if right and not left:
            return 1
        return 0

    def _update_lateral_slip(
        self,
        current_time,
        dt,
        player,
        keys,
        selected_difficulty,
        hazard_slip_active=False,
    ):

        if hazard_slip_active:
            self.weather_skid_velocity = 0.0
            self.weather_skid_direction = 0
            self.lateral_slip_velocity = 0.0
            self.slip_remainder = 0.0
            return

        direction = self._get_input_direction(keys)
        braking = keys[pg.K_s] or keys[pg.K_DOWN]
        accelerating = keys[pg.K_w] or keys[pg.K_UP]

        brake_just_pressed = braking and not self.last_braking_state
        self.last_braking_state = braking

        road_type, safe_speed, high_risk_speed = self._get_safe_speed_info(selected_difficulty)

        if road_type is None:
            self.weather_skid_velocity = 0.0
            self.weather_skid_direction = 0
            self.lateral_slip_velocity = 0.0
            self.slip_remainder = 0.0
            self.last_speed_sample = const.PLAYER_SPEED_DEFAULT
            return

        if road_type == "Rain" and self.weather_intensity["rain"] < 0.35:
            self.last_speed_sample = getattr(player, "velocity", const.PLAYER_SPEED_DEFAULT)
            return

        if road_type == "Snow" and self.weather_intensity["snow"] < 0.35:
            self.last_speed_sample = getattr(player, "velocity", const.PLAYER_SPEED_DEFAULT)
            return

        try:
            current_speed = float(player.get_velocity())
        except Exception:
            current_speed = const.PLAYER_SPEED_DEFAULT

        pre_brake_speed = max(float(current_speed), float(getattr(self, "last_speed_sample", current_speed)))

        modifiers = self._get_difficulty_modifier(selected_difficulty)
        difficulty_multiplier = modifiers["slip_multiplier"]

        risk_range = max(1.0, high_risk_speed - safe_speed)
        speed_for_risk = pre_brake_speed if brake_just_pressed else current_speed
        risk_factor = (speed_for_risk - safe_speed) / risk_range
        risk_factor = max(0.0, min(1.0, risk_factor))

        
        if abs(self.weather_skid_velocity) > 1.0:
            input_direction = direction

            recovering = (
                input_direction != 0
                and self.weather_skid_direction != 0
                and input_direction == -self.weather_skid_direction
            )

            feeding_skid = (
                input_direction != 0
                and self.weather_skid_direction != 0
                and input_direction == self.weather_skid_direction
            )

            if road_type == "Snow":
                base_recovery = 138.0
            else:
                base_recovery = 170.0

            if recovering:
                recovery = base_recovery * 2.3
            elif feeding_skid:
                recovery = base_recovery * 0.55
            else:
                recovery = base_recovery

            if self.weather_skid_velocity > 0:
                self.weather_skid_velocity = max(
                    0.0,
                    self.weather_skid_velocity - recovery * dt,
                )
            else:
                self.weather_skid_velocity = min(
                    0.0,
                    self.weather_skid_velocity + recovery * dt,
                )

        else:
            self.weather_skid_velocity = 0.0
            self.weather_skid_direction = 0

       

        weather_key = "rain" if road_type == "Rain" else "snow"
        traction_intensity = float(self.weather_intensity.get(weather_key, 0.0))
        strength_multiplier = max(0.0, min(1.8, self._get_weather_strength(weather_key)))

        if current_speed > safe_speed and traction_intensity > 0.02:
            if road_type == "Snow":
                base_micro = 82.0 * strength_multiplier
                response = 6.2
                wander_scale = 0.30
            else:
                base_micro = 66.0 * strength_multiplier
                response = 7.5
                wander_scale = 0.26

            control_multiplier = 1.0
            if road_type == "Snow" and accelerating:
                control_multiplier = 0.85

            steer_target = (
                direction
                * base_micro
                * traction_intensity
                * (0.30 + 0.70 * risk_factor)
                * difficulty_multiplier
                * control_multiplier
            )
            speed_smooth = 1.0 - 0.35 * risk_factor
            blend = min(1.0, response * dt * speed_smooth)
            self.lateral_slip_velocity += (steer_target - self.lateral_slip_velocity) * blend

            self.micro_slip_phase += dt * (1.1 if road_type == "Rain" else 0.85)
            wander = (
                math.sin(self.micro_slip_phase) * 0.55
                + math.sin(self.micro_slip_phase * 0.61 + 1.7) * 0.45
            )
            wander_velocity = (
                wander
                * base_micro
                * wander_scale
                * traction_intensity
                * (0.25 + 0.95 * risk_factor)
                * difficulty_multiplier
                * control_multiplier
            )

            micro_velocity = self.lateral_slip_velocity + wander_velocity
            if road_type == "Snow":
                micro_cap = 140.0
            else:
                micro_cap = 120.0

            max_micro_velocity = (
                micro_cap
                * traction_intensity
                * strength_multiplier
                * difficulty_multiplier
                * (0.35 + 0.65 * risk_factor)
                * control_multiplier
            )
            if micro_velocity > max_micro_velocity:
                scale = max_micro_velocity / max(1.0, micro_velocity)
                self.lateral_slip_velocity *= scale
                wander_velocity *= scale
            elif micro_velocity < -max_micro_velocity:
                scale = (-max_micro_velocity) / min(-1.0, micro_velocity)
                self.lateral_slip_velocity *= scale
                wander_velocity *= scale
        else:
            self.lateral_slip_velocity *= max(0.0, 1.0 - 9.0 * dt)
            wander_velocity = 0.0

        combined_velocity = self.weather_skid_velocity + self.lateral_slip_velocity + wander_velocity
        if abs(combined_velocity) > 0.01 or abs(self.slip_remainder) > 0.01:
            self._apply_lateral_pixels(
                player,
                slip_amount=combined_velocity * dt,
                remainder_attr="slip_remainder",
            )

       

        sudden_direction_change = False
        if direction != 0 and self.last_input_direction != 0 and direction != self.last_input_direction:
            self.last_direction_change_time = current_time
            sudden_direction_change = True

        if direction != 0:
            self.last_input_direction = direction

        if current_speed <= safe_speed:
            self.last_speed_sample = current_speed
            return

        skid_cooldown = 550 if road_type == "Rain" else 700

        should_start_skid = False
        skid_direction = 0
        reason_multiplier = 1.0

        bypass_cooldown = False
        if brake_just_pressed and pre_brake_speed >= high_risk_speed * 0.98:
            should_start_skid = True
            bypass_cooldown = True
            skid_direction = direction if direction != 0 else random.choice([-1, 1])
            reason_multiplier = 1.40 if pre_brake_speed >= high_risk_speed * 1.08 else 1.25

        if not bypass_cooldown and current_time - self.last_weather_skid_time < skid_cooldown:
            return

        if sudden_direction_change:
            should_start_skid = True
            skid_direction = direction
            reason_multiplier = 1.15

        if braking and current_speed >= high_risk_speed:
            should_start_skid = True
            skid_direction = direction if direction != 0 else random.choice([-1, 1])
            reason_multiplier = 1.35

        if direction != 0 and current_speed >= high_risk_speed and risk_factor > 0.75:
            should_start_skid = True
            skid_direction = direction
            reason_multiplier = max(reason_multiplier, 1.10)

        if not should_start_skid and direction != 0 and risk_factor > 0.20:
            if road_type == "Snow":
                base_rate_per_sec = 1.05
            else:
                base_rate_per_sec = 0.70

            chance = (
                base_rate_per_sec
                * traction_intensity
                * (0.30 + 0.70 * risk_factor)
                * min(1.35, 0.85 + 0.35 * difficulty_multiplier)
                * min(1.35, 0.70 + 0.55 * strength_multiplier)
            )

            if random.random() < chance * dt:
                should_start_skid = True
                skid_direction = direction
                reason_multiplier = 1.10

        if not should_start_skid:
            self.last_speed_sample = current_speed
            return

        if road_type == "Snow":
            base_start_velocity = 270.0 * strength_multiplier
        else:
            base_start_velocity = 215.0 * strength_multiplier

        start_velocity = (
            base_start_velocity
            * (0.65 + risk_factor)
            * difficulty_multiplier
            * reason_multiplier
        )

        max_start_velocity = 410.0 if road_type == "Snow" else 360.0
        if road_type == "Rain":
            max_start_velocity = 330.0
        if bypass_cooldown:
            max_start_velocity *= 0.85
        start_velocity = min(start_velocity, max_start_velocity * difficulty_multiplier)

        self.weather_skid_direction = skid_direction if skid_direction != 0 else random.choice([-1, 1])
        self.weather_skid_velocity = self.weather_skid_direction * start_velocity
        self.last_weather_skid_time = current_time
        self.last_speed_sample = current_speed

    def _target_particle_count(self, weather_type, selected_difficulty):
        base_count = const.WEATHER_BASE_PARTICLES.get(weather_type, 0)
        modifiers = self._get_difficulty_modifier(selected_difficulty)
        strength = max(0.0, self._get_weather_strength(weather_type))
        intensity = float(self.weather_intensity.get(weather_type, 0.0))
        cap = 120
        density_boost = 1.0
        if weather_type == "snow":
            cap = 230
            density_boost = 1.85

        return int(
            min(
                cap,
                base_count * modifiers["particle_multiplier"] * strength * intensity * density_boost,
            )
        )

    def _update_particles(self, selected_difficulty, dt):
        dt_scale = max(0.0, float(dt)) * float(getattr(const, "FPS", 60))

        max_remove_per_frame = max(1, int(10 * dt_scale))

        rain_visible = self.weather_intensity.get("rain", 0.0) > 0.02 or "rain" in self.active_weather
        snow_visible = self.weather_intensity.get("snow", 0.0) > 0.02 or "snow" in self.active_weather

        if rain_visible:
            target = self._target_particle_count("rain", selected_difficulty)
            while len(self.rain_particles) < target:
                self.rain_particles.append(self._new_rain_particle(random_y=True))
            if len(self.rain_particles) > target:
                remove = min(len(self.rain_particles) - target, max_remove_per_frame)
                if remove > 0:
                    del self.rain_particles[-remove:]
        else:
            self.rain_particles.clear()

        if snow_visible:
            target = self._target_particle_count("snow", selected_difficulty)
            while len(self.snow_particles) < target:
                self.snow_particles.append(self._new_snow_particle(random_y=True))
            if len(self.snow_particles) > target:
                remove = min(len(self.snow_particles) - target, max_remove_per_frame)
                if remove > 0:
                    del self.snow_particles[-remove:]
        else:
            self.snow_particles.clear()

        for particle in self.rain_particles:
            particle["x"] += particle["dx"] * dt_scale
            particle["y"] += particle["speed"] * dt_scale
            if particle["y"] > const.HEIGHT + 20 or particle["x"] < -20:
                particle.update(self._new_rain_particle(random_y=False))

        for particle in self.snow_particles:
            depth = float(particle.get("depth", 0.5))
            particle["phase"] += (0.014 + 0.012 * depth) * dt_scale
            particle["x"] += (
                float(particle["wind"]) + math.sin(particle["phase"]) * float(particle["swirl"])
            ) * dt_scale
            flutter = 1.0 + 0.03 * abs(math.sin(particle["phase"] * 0.85 + 0.6))
            particle["y"] += float(particle["speed"]) * flutter * dt_scale
            if (
                particle["y"] > const.HEIGHT + 12
                or particle["x"] < -30
                or particle["x"] > const.WIDTH + 30
            ):
                particle.update(self._new_snow_particle(random_y=False))

    def _new_rain_particle(self, random_y=False):
        depth = random.random()  # 0=far, 1=near
        speed = random.uniform(12.0, 22.0) * (0.75 + 0.65 * depth)
        dx = random.uniform(-3.6, -1.0) * (0.65 + 0.55 * depth)
        length = random.uniform(9.0, 18.0) * (0.75 + 1.05 * depth)
        width = 2 if depth > 0.78 else 1
        alpha = int(85 + 165 * depth)
        if depth > 0.88 and random.random() < 0.05:
            alpha = 255
            width = 2
        return {
            "x": random.randint(0, const.WIDTH),
            "y": random.randint(-const.HEIGHT, const.HEIGHT) if random_y else random.randint(-80, -10),
            "speed": speed,
            "dx": dx,
            "length": length,
            "width": width,
            "alpha": alpha,
            "depth": depth,
        }

    def _new_snow_particle(self, random_y=False):
        depth = random.random()  # 0=far, 1=near
        speed = random.uniform(2.4, 4.2) * (0.75 + 0.70 * depth)
        wind = random.uniform(-0.08, 0.05) * (0.45 + 0.65 * depth)
        swirl = random.uniform(0.02, 0.08) * (0.50 + 0.55 * depth)
        alpha = int(105 + 150 * depth)
        radius = 1 if depth < 0.45 else 2
        if depth > 0.82 and random.random() < 0.14:
            radius = 3
        return {
            "x": random.randint(0, const.WIDTH),
            "y": random.randint(-const.HEIGHT, const.HEIGHT) if random_y else random.randint(-80, -10),
            "speed": speed,
            "wind": wind,
            "swirl": swirl,
            "phase": random.uniform(0, math.pi * 2),
            "radius": radius,
            "alpha": alpha,
            "depth": depth,
        }

    def draw_environment(self, screen, player, selected_difficulty, player_visual_y=None):
        if self.weather_intensity.get("rain", 0.0) > 0.02:
            self._draw_rain(screen)

        if self.weather_intensity.get("snow", 0.0) > 0.02:
            self._draw_snow(screen)

        if self.weather_intensity.get("night", 0.0) > 0.02:
            self._draw_night_overlay(screen, player, selected_difficulty, player_visual_y=player_visual_y)

        if self.weather_intensity.get("fog", 0.0) > 0.02:
            self._draw_fog_overlay(screen, player, selected_difficulty, player_visual_y=player_visual_y)

    def draw_hud(self, screen, small_font, tiny_font, selected_difficulty):
        self._draw_weather_status_panel(screen, small_font, tiny_font, selected_difficulty)
        self._draw_weather_alert(screen, small_font)

    def _draw_rain(self, screen):
        intensity = float(self.weather_intensity.get("rain", 0.0))
        strength = max(0.0, float(self._get_weather_strength("rain")))
        if self._rain_layer is None:
            self._rain_layer = pg.Surface((const.WIDTH, const.HEIGHT), pg.SRCALPHA).convert_alpha()
        rain_layer = self._rain_layer
        rain_layer.fill((0, 0, 0, 0))

        vis = min(1.0, 0.25 + 0.75 * intensity) * min(1.0, 0.70 + 0.30 * strength)
        base_r, base_g, base_b = (150, 190, 230)

        for particle in self.rain_particles:
            x = float(particle["x"])
            y = float(particle["y"])
            depth = float(particle.get("depth", 0.5))
            alpha = int(float(particle.get("alpha", 170)) * vis)
            if alpha <= 0:
                continue

            streak_scale = 1.65 + 0.55 * depth
            start = (int(x), int(y))
            end = (
                int(x + float(particle["dx"]) * streak_scale),
                int(y + float(particle["length"]) * (0.90 + 0.45 * depth)),
            )
            pg.draw.line(
                rain_layer,
                (base_r, base_g, base_b, alpha),
                start,
                end,
                int(particle.get("width", 1)),
            )

        screen.blit(rain_layer, (0, 0))

        if self._wet_overlay is None:
            self._wet_overlay = pg.Surface((const.WIDTH, const.HEIGHT), pg.SRCALPHA).convert_alpha()
            self._wet_overlay.fill((40, 70, 95, 255))
        wet_overlay = self._wet_overlay
        wet_overlay.set_alpha(min(65, int(26 * intensity * strength)))
        screen.blit(wet_overlay, (0, 0))

    def _draw_snow(self, screen):
        intensity = float(self.weather_intensity.get("snow", 0.0))
        strength = max(0.0, float(self._get_weather_strength("snow")))
        if self._snow_layer is None:
            self._snow_layer = pg.Surface((const.WIDTH, const.HEIGHT), pg.SRCALPHA).convert_alpha()
        snow_layer = self._snow_layer
        snow_layer.fill((0, 0, 0, 0))

        vis = min(1.0, 0.28 + 0.72 * intensity) * min(1.0, 0.72 + 0.28 * strength)
        base_r, base_g, base_b = (235, 245, 255)

        for particle in self.snow_particles:
            alpha = int(float(particle.get("alpha", 170)) * vis)
            if alpha <= 0:
                continue
            pg.draw.circle(
                snow_layer,
                (base_r, base_g, base_b, alpha),
                (int(particle["x"]), int(particle["y"])),
                int(particle["radius"]),
            )

        screen.blit(snow_layer, (0, 0))

        if self._cold_overlay is None:
            self._cold_overlay = pg.Surface((const.WIDTH, const.HEIGHT), pg.SRCALPHA).convert_alpha()
            self._cold_overlay.fill((210, 230, 245, 255))
        cold_overlay = self._cold_overlay
        cold_overlay.set_alpha(min(55, int(30 * intensity * max(0.7, strength))))
        screen.blit(cold_overlay, (0, 0))

    def _draw_fog_overlay(self, screen, player, selected_difficulty, player_visual_y=None):
        intensity = self.weather_intensity.get("fog", 0.0)
        if intensity <= 0.02:
            return

        modifiers = self._get_difficulty_modifier(selected_difficulty)
        visibility_multiplier = modifiers["visibility_multiplier"]

        self._ensure_fog_assets()
    

        alpha_scale = max(0.0, min(1.0, float(intensity) * float(visibility_multiplier)))
        fog_alpha = int(255 * alpha_scale)

        if self._fog_overlay is None:
            self._fog_overlay = pg.Surface((const.WIDTH, const.HEIGHT), pg.SRCALPHA).convert_alpha()
        fog_layer = self._fog_overlay
        fog_layer.fill((0, 0, 0, 0))

        self._fog_gradient.set_alpha(fog_alpha)
        fog_layer.blit(self._fog_gradient, (0, 0))

        self._fog_mist_base.set_alpha(int(20 * intensity * visibility_multiplier))
        fog_layer.blit(self._fog_mist_base, (0, 0))

        night_active = self.weather_intensity.get("night", 0.0) > 0.02 or "night" in self.active_weather
        if not night_active:
            self._apply_fog_headlight_cutout(fog_layer, player, player_visual_y=player_visual_y)
        screen.blit(fog_layer, (0, 0))

    def _apply_fog_headlight_cutout(self, fog_layer, player, player_visual_y=None):
        car_center_x = int(player.x + player.width // 2)
        car_front_y = int(player_visual_y if player_visual_y is not None else player.y)

        cone_length = 210
        cone_width = 210
        mask_height = cone_length + 30

        mask_key = (cone_width, cone_length)
        mask = self._fog_headlight_mask_cache.get(mask_key)
        if mask is None:
            mask = pg.Surface((cone_width, mask_height), pg.SRCALPHA).convert_alpha()
            mask.fill((255, 255, 255, 255))

            pg.draw.ellipse(mask, (255, 255, 255, 205), (0, 0, cone_width, cone_length))

            base_y = cone_length + 10
            points = [
                (cone_width // 2 - 28, base_y),
                (cone_width // 2 + 28, base_y),
                (cone_width, 0),
                (0, 0),
            ]
            pg.draw.polygon(mask, (255, 255, 255, 165), points)

            self._fog_headlight_mask_cache[mask_key] = mask

        fog_layer.blit(
            mask,
            (car_center_x - cone_width // 2, max(0, car_front_y - cone_length)),
            special_flags=pg.BLEND_RGBA_MULT,
        )

    def _draw_night_overlay(self, screen, player, selected_difficulty, player_visual_y=None):
        intensity = self.weather_intensity.get("night", 0.0)
        if intensity <= 0.02:
            return

        modifiers = self._get_difficulty_modifier(selected_difficulty)
        visibility_multiplier = modifiers["visibility_multiplier"]

        if self._night_overlay is None:
            self._night_overlay = pg.Surface((const.WIDTH, const.HEIGHT), pg.SRCALPHA).convert_alpha()
        overlay = self._night_overlay

        night_alpha = int(132 * visibility_multiplier * intensity)
        overlay.fill((0, 0, 18, night_alpha))

        self._draw_headlight_cone(overlay, player, mode="night", player_visual_y=player_visual_y)
        screen.blit(overlay, (0, 0))

    def _draw_headlight_cone(self, overlay, player, mode="night", player_visual_y=None):
        car_center_x = int(player.x + player.width // 2)
        car_front_y = int(player_visual_y if player_visual_y is not None else player.y)

        if mode == "fog":
            cone_length = 210
            cone_width = 210
            color = (255, 245, 185, 48)
        else:
            cone_length = 260
            cone_width = 250
            color = (255, 240, 170, 62)

        points = [
            (car_center_x - 28, car_front_y + 10),
            (car_center_x + 28, car_front_y + 10),
            (car_center_x + cone_width // 2, max(0, car_front_y - cone_length)),
            (car_center_x - cone_width // 2, max(0, car_front_y - cone_length)),
        ]

        pg.draw.polygon(overlay, color, points)

        glow_key = (mode, cone_width, cone_length)
        glow = self._glow_cache.get(glow_key)
        if glow is None:
            glow = pg.Surface((cone_width, cone_length), pg.SRCALPHA).convert_alpha()
            if mode == "fog":
                glow_alpha = 10
            else:
                glow_alpha = 16
            pad_x = int(cone_width * 0.06)
            pad_y = int(cone_length * 0.06)
            pg.draw.ellipse(
                glow,
                (255, 240, 180, glow_alpha),
                (pad_x, pad_y, cone_width - pad_x * 2, cone_length - pad_y * 2),
            )
            self._glow_cache[glow_key] = glow
        overlay.blit(
            glow,
            (car_center_x - cone_width // 2, max(0, car_front_y - cone_length)),
        )

    def _draw_weather_status_panel(self, screen, small_font, tiny_font, selected_difficulty):
        weather_label = " + ".join(w.title() for w in self.active_weather)

        road_type, safe_speed, high_risk_speed = self._get_safe_speed_info(selected_difficulty)

        lines = [f"Weather: {weather_label}"]

        if road_type and safe_speed is not None and high_risk_speed is not None:
            lines.append(f"Safe Speed: {safe_speed:.0f} km/h")
            lines.append(f"High Risk: {high_risk_speed:.0f} km/h")
        elif "fog" in self.active_weather:
            lines.append("Low Visibility")
            lines.append("Headlights Active")
        elif "night" in self.active_weather:
            lines.append("Headlights Active")
            lines.append("Limited Vision")
        else:
            lines.append("Road Normal")

        title_color = (130, 220, 255)
        normal_color = const.WHITE

        title = small_font.render(lines[0], True, title_color)
        info_surfaces = [tiny_font.render(line, True, normal_color) for line in lines[1:]]

        max_text_width = title.get_width()
        for surf in info_surfaces:
            if surf.get_width() > max_text_width:
                max_text_width = surf.get_width()

        width = max(230, max_text_width + 26)
        width = min(width, const.WIDTH - 20)
        height = 24 + len(lines) * 20
        x = const.WIDTH // 2 - width // 2
        y = 10

        panel = pg.Surface((width, height), pg.SRCALPHA)
        panel.fill((10, 14, 22, 185))
        pg.draw.rect(panel, (255, 255, 255, 48), (0, 0, width, height), 1, border_radius=12)

        panel.blit(title, (12, 8))

        for index, surf in enumerate(info_surfaces):
            panel.blit(surf, (14, 34 + index * 19))

        screen.blit(panel, (x, y))

    def _draw_weather_alert(self, screen, small_font):
        current_time = pg.time.get_ticks()
        if current_time >= self.alert_until or not self.alert_message:
            return

        text = small_font.render(self.alert_message, True, const.WHITE)
        width = text.get_width() + 38
        height = 42

        x = const.WIDTH // 2 - width // 2
        y = 86

        alert = pg.Surface((width, height), pg.SRCALPHA)
        alert.fill((15, 20, 32, 220))
        pg.draw.rect(alert, (255, 220, 120, 145), (0, 0, width, height), 2, border_radius=16)
        alert.blit(text, (19, 10))

        screen.blit(alert, (x, y))