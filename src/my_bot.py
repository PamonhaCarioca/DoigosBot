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

            # O jogador mais próximo vai atrás da bola
            closest_players = self.get_closest_players(ball_position, inspector.get_my_team_players())[0]
            if me == closest_players:  # Se eu sou o mais próximo
                move_order = inspector.make_order_move_max_speed(ball_position)
            else:
                # os ouutros jogadores seguem a formação
                expected_position = get_my_expected_position(inspector, self.mapper, self.number)
                if expected_position:
                    move_order = inspector.make_order_move_max_speed(expected_position)
                else:
                    move_order = inspector.make_order_move_max_speed(ball_position)

            # tenta pegar a bola sempre
            catch_order = inspector.make_order_catch()
            return [move_order, catch_order]

        except Exception as e:
            print(f'did not play this turn due to exception {e}')
            traceback.print_exc()
            return []

    def on_defending(self, inspector: lugo4py.GameSnapshotInspector) -> List[lugo4py.Order]:
        try:
            print("on defending")
            me = inspector.get_me()
            ball_position = inspector.get_ball().position
            opponent_team = inspector.get_opponent_players()

            # O jogador mais próximo vai atrás da bola
            closest_players = self.get_closest_players(ball_position, inspector.get_my_team_players())[0]
            if me == closest_players:  # Se eu sou o mais próximo
                move_order = inspector.make_order_move_max_speed(ball_position)
            else:
                # outros jogadores marcam os oponetes
                closest_opponent = self.get_closest_players(ball_position, opponent_team)[0]
                intercept_position = self.calculate_intercept_position(ball_position, closest_opponent.position)
                move_order = inspector.make_order_move_max_speed(intercept_position)

            # sempre tenta pegar a bola
            catch_order = inspector.make_order_catch()
            return [move_order, catch_order]

        except Exception as e:
            print(f'did not play this turn due to exception {e}')
            traceback.print_exc()
            return []

    def on_holding(self, inspector: lugo4py.GameSnapshotInspector) -> List[lugo4py.Order]:
        try:
            print("on holding")
            me = inspector.get_me()
            ball = inspector.get_ball()
            opponent_team = inspector.get_opponent_players()
            opponent_goal = self.mapper.get_attack_goal()

            # verifica se ha oponentes próximos
            closest_opponent = self.get_closest_players(me.position, opponent_team)[0]
            dist_to_opponent = lugo4py.geo.distance_between_points(me.position, closest_opponent.position)

            # se o adversário estiver muito perto, passa a bola para um aliado livre
            if dist_to_opponent <= 300:
                free_players = self.get_free_allies(inspector, 500)
                if free_players:
                    closest_ally = self.get_closest_players(me.position, free_players)[0]
                    if closest_ally.number != me.number:  # Evita passar para si mesmo
                        my_order = inspector.make_order_kick_max_speed(closest_ally.position)
                        return [my_order]

            # se houver um aliado avançado e livre, passa a bola
            free_players = self.get_free_allies(inspector, 500)
            closest_to_goal = self.get_closest_players(opponent_goal.get_center(), free_players)[0]
            for ally in closest_to_goal:
                if ally.position.x > me.position.x:  # Aliado está à frente
                    my_order = inspector.make_order_kick_max_speed(ally.position)
                    return [my_order]

            # se estiver perto do gol, chuta para o centro ou canto(tem erro)
            dist_to_goal = lugo4py.geo.distance_between_points(me.position, opponent_goal.get_center())
            if dist_to_goal <= 3000:
                print("Chutando para o centro do gol")
                my_order = inspector.make_order_kick_max_speed(opponent_goal.get_center())

            else:
                # se não houver opçoes, move em direção ao gol
                print("Chutando para o canto do gol")
                my_order = inspector.make_order_move_max_speed(opponent_goal.get_bottom_pole())

            # se não houver opçoes, move em direção ao gol
            #move_order = inspector.make_order_move_max_speed(opponent_goal.get_center())
            return [my_order]

        except Exception as e:
            print(f'did not play this turn due to exception. {e}')
            traceback.print_exc()

    def on_supporting(self, inspector: lugo4py.GameSnapshotInspector) -> List[lugo4py.Order]:
        try:
            print("on supporting")
            # ficar na posição de formação
            expected_position = get_my_expected_position(inspector, self.mapper, self.number)
            if expected_position:
                move_order = inspector.make_order_move_max_speed(expected_position)
            else:
                move_order = inspector.make_order_move_max_speed(inspector.get_ball().position)
            return [move_order]

        except Exception as e:
            print(f'did not play this turn due to exception {e}')
            traceback.print_exc()
            return []

    def as_goalkeeper(self, inspector: lugo4py.GameSnapshotInspector, state: lugo4py.PLAYER_STATE) -> List[lugo4py.Order]:
        try:
            print("as_goalkeeper")
            me = inspector.get_me()
            ball = inspector.get_ball()

            # se tiver com a bola, passa para o aliado mais próximo livre
            if ball.holder and ball.holder.number == me.number:
                free_players = self.get_free_allies(inspector, 500)
                if free_players:
                    closest_ally = self.get_closest_players(me.position, free_players)[0]
                    if closest_ally.number != me.number:  # Evita passar para si mesmo
                        kick_order = inspector.make_order_kick_max_speed(closest_ally.position)
                        return [kick_order]

            # mover para a posição de formação mais próxima da bola
            move_order = inspector.make_order_move_max_speed(ball.position)
            return [move_order, inspector.make_order_catch()]

        except Exception as e:
            print(f'did not play this turn due to exception {e}')
            traceback.print_exc()
            return []

    def getting_ready(self, snapshot: lugo4py.GameSnapshot):
        print('getting ready')

    def is_near(self, region_origin: lugo4py.mapper.Region, dest_origin: lugo4py.mapper.Region) -> bool:
        max_distance = 2
        return abs(region_origin.get_row() - dest_origin.get_row()) <= max_distance and abs(
            region_origin.get_col() - dest_origin.get_col()) <= max_distance

    def get_closest_players(self, point, player_list):
        def sortkey(player):
            return lugo4py.geo.distance_between_points(point, player.position)
        return sorted(player_list, key=sortkey)#calcula a hipotenusa ou e a distancia mais proxima entre os dois fatores

    def get_free_allies(self, inspector: lugo4py.GameSnapshotInspector, dist):
        my_team = inspector.get_my_team_players()
        opponent_team = inspector.get_opponent_players()
        free_players = []

        # testa com o time todo
        for ally in my_team:
            # ignora o próprio jogador 
            if ally.number == inspector.get_me().number: 
                continue

            
            is_free = True
            for opponent in opponent_team:# testa com o time adversario todo
                dist_to_opponent = lugo4py.geo.distance_between_points(ally.position, opponent.position)
                if dist_to_opponent <= dist:#se a distancia for muito proximo a que foi recebida o jogador não esta livre
                    is_free = False
                    break

            if is_free: #insere na lista
                free_players.append(ally)

        return free_players

    def calculate_intercept_position(self, ball_position, opponent_position):
        #Calcula a posição média entre a bola e o oponente
        intercept_x = (ball_position.x + opponent_position.x) / 2
        intercept_y = (ball_position.y + opponent_position.y) / 2
        return lugo4py.Point(intercept_x, intercept_y)