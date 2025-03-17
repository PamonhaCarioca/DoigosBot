import traceback
from abc import ABC
from typing import List

import lugo4py
from settings import get_my_expected_position


class MyBot(lugo4py.Bot, ABC):
    def on_disputing(self, inspector: lugo4py.GameSnapshotInspector) -> List[lugo4py.Order]:
        try:
            print("on disputing")
            me = inspector.get_me()
            ball_position = inspector.get_ball().position
            my_team = inspector.get_my_team_players()
            closest_players = self.get_closest_players(ball_position, my_team)
            n_catchers = 3
            catchers = closest_players[:n_catchers]

            if me in catchers:
                move_order = inspector.make_order_move_max_speed(ball_position)
            else:
                move_order = inspector.make_order_move_max_speed(get_my_expected_position(inspector, self.mapper, self.number))

            catch_order = inspector.make_order_catch()
            return [move_order, catch_order]

        except Exception as e:
            print(f'did not play this turn due to exception {e}')
            traceback.print_exc()

    def on_defending(self, inspector: lugo4py.GameSnapshotInspector) -> List[lugo4py.Order]:
        try:
            print("on defending")
            me = inspector.get_me()
            ball_position = inspector.get_ball().position
            my_team = inspector.get_my_team_players()
            closest_players = self.get_closest_players(ball_position, my_team)
            n_catchers = 3
            catchers = closest_players[:n_catchers]

            if me in catchers:
                move_order = inspector.make_order_move_max_speed(ball_position)
            else:
                move_order = inspector.make_order_move_max_speed(get_my_expected_position(inspector, self.mapper, self.number)) 

            catch_order = inspector.make_order_catch()
            return [move_order, catch_order]
                
        except Exception as e:
            print(f'did not play this turn due to exception {e}')
            traceback.print_exc()

    def on_holding(self, inspector: lugo4py.GameSnapshotInspector) -> List[lugo4py.Order]:
        try:
            print("on holding")
            opponent_goalkeeper = inspector.get_opponent_goalkeeper().position

            me = inspector.get_me()
            opponent_goal = self.mapper.get_attack_goal()

            distance_to_goal = lugo4py.geo.distance_between_points(me.position, opponent_goal.get_center())
            if distance_to_goal <= 2000:
                kick_order = inspector.make_order_kick_max_speed(opponent_goal.get_bottom_pole())
                return [kick_order]
            else:
                move_order = inspector.make_order_move_max_speed(opponent_goalkeeper)
                catch_order = inspector.make_order_catch()
                return [move_order, catch_order]

        except Exception as e:
            print(f'did not play this turn due to exception. {e}')
            traceback.print_exc()

    def on_supporting(self, inspector: lugo4py.GameSnapshotInspector) -> List[lugo4py.Order]:
        try:
            print("on supporting")
            ball_position = inspector.get_ball().position
            move_order = inspector.make_order_move_max_speed(ball_position)
            catch_order = inspector.make_order_catch()

            return [move_order, catch_order]

        except Exception as e:
            print(f'did not play this turn due to exception {e}')
            traceback.print_exc()

    def as_goalkeeper(self, inspector: lugo4py.GameSnapshotInspector, state: lugo4py.PLAYER_STATE) -> List[lugo4py.Order]:
        try:
            ball_position = inspector.get_ball().position
            move_order = inspector.make_order_move_max_speed(ball_position)
            catch_order = inspector.make_order_catch()

            return [move_order, catch_order]

        except Exception as e:
            print(f'did not play this turn due to exception {e}')
            traceback.print_exc()

    def getting_ready(self, snapshot: lugo4py.GameSnapshot):
        print('getting ready')

    def is_near(self, region_origin: lugo4py.mapper.Region, dest_origin: lugo4py.mapper.Region) -> bool:
        max_distance = 2
        return abs(region_origin.get_row() - dest_origin.get_row()) <= max_distance and abs(
            region_origin.get_col() - dest_origin.get_col()) <= max_distance

    def get_closest_players(self, point, player_list):
        def sortkey(player):
            return lugo4py.geo.distance_between_points(point, player.position)
        return sorted(player_list, key=sortkey)