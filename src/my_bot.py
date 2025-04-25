
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
            ball_position = inspector.get_ball()
            my_team = inspector.get_my_team_players()
            closest_players = self.get_closest_players(ball_position.position, my_team)
            n_catchers = 1
            catchers = closest_players[:n_catchers]
            if me in catchers:
                move_order = inspector.make_order_move_max_speed(ball_position.position)
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
            ball_position = inspector.get_ball()
            my_team = inspector.get_my_team_players()
            closest_players = self.get_closest_players(ball_position.position, my_team)
            n_catchers = 3
            catchers = closest_players[:n_catchers]
            closest_players = self.get_closest_players(me.position, my_team)
            if me in catchers:
                move_order = inspector.make_order_move_max_speed(ball_position.position)
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
            me = inspector.get_me()
            opponent_goal = self.mapper.get_attack_goal()
            my_team = inspector.get_my_team_players()
            closest_to_goal = self.get_closest_players(opponent_goal.get_center(), my_team)
            free_players = self.get_free_allies(inspector, 800)

            for ally in closest_to_goal:
                ally_to_goal = lugo4py.geo.distance_between_points(ally.position, opponent_goal.get_center())
                me_to_goal = lugo4py.geo.distance_between_points(me.position, opponent_goal.get_center())
                closest_to_me = self.get_closest_players(me.position, my_team)
                n_catchers = 3
                catchers = closest_to_me[:n_catchers]
                opponent_team = inspector.get_opponent_players()
                closest_to_me_opponent = self.get_closest_players(me.position, opponent_team)
                opponent_to_me = lugo4py.geo.distance_between_points(me.position, closest_to_me_opponent[1].position)

                if ally in free_players and (ally.number != me.number) and (me_to_goal > ally_to_goal) and (catchers[1].number == ally.number):
                    move_order = inspector.make_order_move_max_speed(ally.position)
                    kick_order = inspector.make_order_kick(ally.position, 200)
                    return [move_order , kick_order]
                elif ally in free_players and (ally.number != me.number) and (me_to_goal > ally_to_goal) and (lugo4py.geo.distance_between_points(me.position, ally.position) < 3000):
                    move_order = inspector.make_order_move_max_speed(ally.position)
                    kick_order = inspector.make_order_kick_max_speed(ally.position)
                    return [move_order , kick_order]
                

            distance_to_goal = lugo4py.geo.distance_between_points(me.position, opponent_goal.get_center())
            if distance_to_goal <= 3500:
                opponent_goalkeeper = inspector.get_opponent_goalkeeper()
                distance_top_pole_goalkeeper = lugo4py.geo.distance_between_points(opponent_goalkeeper.position, opponent_goal.get_top_pole())
                distance_botton_pole_goalkeeper = lugo4py.geo.distance_between_points(opponent_goalkeeper.position, opponent_goal.get_bottom_pole())
                if distance_top_pole_goalkeeper <= distance_botton_pole_goalkeeper:
                    # chute posicao especifica
                    a = lugo4py.Point(x = opponent_goalkeeper.position.x,  y = 3700)
                    b = lugo4py.Point(x = opponent_goalkeeper.position.x,  y = 4200)
                    move_order = inspector.make_order_move_max_speed(b)
                    kick_order = inspector.make_order_kick(a, 350)
                    return [move_order , kick_order]
                else:
                    
                    # chute posicao especifica
                    a = lugo4py.Point(x = opponent_goalkeeper.position.x,  y = 6400)
                    b = lugo4py.Point(x = opponent_goalkeeper.position.x,  y = 6000)
                    move_order = inspector.make_order_move_max_speed(b)
                    kick_order = inspector.make_order_kick(a, 350)
                    return [move_order , kick_order]   
            else:
                opponent_goalkeeper = inspector.get_opponent_goalkeeper()
                goal_direction = lugo4py.Point(x = opponent_goalkeeper.position.x , y = me.position.y)
                move_order = inspector.make_order_move_max_speed(goal_direction)
                return [move_order]
                
        except Exception as e:
            print(f'did not play this turn due to exception. {e}')
            traceback.print_exc()


    def on_supporting(self, inspector: lugo4py.GameSnapshotInspector) -> List[lugo4py.Order]:
        try:
            print("on disputing")
            me = inspector.get_me()
            ball_position = inspector.get_ball()
            my_team = inspector.get_my_team_players()
            closest_players = self.get_closest_players(ball_position.position, my_team)
            n_catchers = 2
            catchers = closest_players[:n_catchers]
            if me in catchers:
                opponent_goal = self.mapper.get_attack_goal()
                move_order = inspector.make_order_move_max_speed(opponent_goal.get_center())
            else:
                move_order = inspector.make_order_move_max_speed(get_my_expected_position(inspector, self.mapper, self.number))

            catch_order = inspector.make_order_catch()
            return [move_order, catch_order]
        
        except Exception as e:
            print(f'did not play this turn due to exception {e}')
            traceback.print_exc()


    def as_goalkeeper(self, inspector: lugo4py.GameSnapshotInspector, state: lugo4py.PLAYER_STATE) -> List[lugo4py.Order]:
        try:
            ball_position = inspector.get_ball()
            me = inspector.get_me()
            c = lugo4py.Point(x = me.position.x, y = ball_position.position.y)
            a = lugo4py.Point(x=me.position.x, y =3910)
            b = lugo4py.Point(x=me.position.x, y =6140)

            player_ball = inspector.get_ball_holder().number
            if player_ball == me.number:
                my_team = inspector.get_my_team_players()
                closest_to_me = self.get_closest_players(me.position, my_team)
                free_players = self.get_free_allies(inspector, 800)
                for ally in closest_to_me:
                    if ally in free_players and (ally.number != me.number):
                        kick_order = inspector.make_order_kick_max_speed(ally.position)
                        return [kick_order]
                    
            else:
                if ball_position.position.y <= 3450 :
                    move_order = inspector.make_order_move_max_speed(a)
                    catch_order = inspector.make_order_catch()
                    return [move_order, catch_order]
                
                elif ball_position.position.y >= 6600:
                    move_order = inspector.make_order_move_max_speed(b)
                    catch_order = inspector.make_order_catch()
                    return [move_order, catch_order]
                else:
                    move_order = inspector.make_order_move_max_speed(c)
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
   
    def get_free_allies(self, inspector: lugo4py.GameSnapshotInspector, dist = lugo4py.specs.PLAYER_SIZE):
        my_team = inspector.get_my_team_players()
        opponent_team = inspector.get_opponent_players()
        free_players= []

        for ally in my_team:
            is_free = True
            for opponent in opponent_team:
                dist_to_opponent = lugo4py.distance_between_points(ally.position, opponent.position)
                if dist_to_opponent <= dist:
                    is_free = False
            if is_free:
                free_players.append(ally)

        return free_players
