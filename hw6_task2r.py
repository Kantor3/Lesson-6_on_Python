"""
Задача 2.
Создайте программу для игры с конфетами человек против человека.
Условие задачи: На столе лежит 2021 конфета. Играют два игрока
делая ход друг после друга. Первый ход определяется жеребьёвкой.
За один ход можно забрать не более чем 28 конфет.
Все конфеты оппонента достаются сделавшему последний ход.
Сколько конфет нужно взять первому игроку, чтобы забрать все конфеты у своего конкурента?
a) Добавьте игру против бота
b) Подумайте как наделить бота ""интеллектом"".
"""
import time
import random
import my_lib as myl

count_candies, can_removed, players_game = 0, 0, {}
bot_thinking, bot_strategy = 3, None                # Бот будет "думать" 3 сек. Стратегию определим при инициации
player_ref = {1: ('Вы', 'Вами', 'Ваш'),
              2: ('2-й Игрок', '2-м Игроком', '2-го Игрока'),
              0: ('Bot', 'Bot`ом', 'Bot`а')}


# 1, 2, 3. Инициация и старт игры:
#    Провести жеребьевку (кто начинает), сообщить кратко о правилах
#    игры "Всего [number] конфет. За один ход можно взять не более
#    [p] конфет"
def init_game(init_count=None, init_removed=None, series=None, new_set=True):

    global players_game
    global count_candies
    global can_removed
    global bot_strategy
    my_code, human_code, bot_code = tuple(player_ref.keys())

    if series is None:

        # Уточнение параметров игры:
        if new_set:
            #   - число конфет
            count_candies = myl.get_input(10, 3000, default=init_count,
                                          txt=f'Укажите число конфет для игры '
                                              f'(по умолчанию - {init_count})', end='-')
            if count_candies is None: return None

            #   - сколько можно взять за раз, очевидно, что (can_removed < count_candies)
            frm = max(2, count_candies // 100 + 1)
            to = max(frm, (count_candies // 5 + 1))
            default = min(to, init_removed)
            can_removed = myl.get_input(frm, to, default=default,
                                        txt=f'Укажите сколько конфет можно брать '
                                            f'(по умолчанию - {default})', end='-')
            if can_removed is None: return None

        # Новый раунд
        st = count_candies                                # для учета остатка конфет на столе
        mov = 0                                           # для учета числа ходов, сделанных в текущем раунде
        my_code, opp_code = tuple(players_game.keys())
        prime_player = random.choice([my_code, opp_code])

        # Определим оптимальную для бота стратегию (1 - мягкая стратегия; 2 - гарантированная стратегия)
        bot_order = 1 if bot_code == prime_player else 2
        rem = count_candies % (can_removed + 1)
        bot_strategy = 2 if (not rem and bot_order == 2) or (0 < rem < can_removed + 1 and bot_order == 1) else 1

        print(f'\nВсего в игре {count_candies} конфет')
        print(f'Ход осуществляется указанием числа конфет, которое игрок забирает со стола (не более {can_removed})')
        print(f'Первый ход за {player_ref[my_code][1] if prime_player == my_code else player_ref[opp_code][1]}')
        return prime_player, st, mov

    else:
        # 1. Выбрать соперника ("0" - Bot; "2" - Human)
        opp_code = myl.get_input((str(human_code), str(bot_code)), default=str(human_code), type_input=tuple,
                                 txt=f'Выберите соперника ({human_code} - Human; {bot_code} - Bot), '
                                     f'по умолчанию - {human_code}', end='-')
        if opp_code is None: return None

        opp_code = int(opp_code)
        other_player = {my_code: opp_code, opp_code: my_code}[my_code]
        players_game = {my_code: [other_player, 0], other_player: [my_code, 0]}
        rnd = 0                     # для учета числа раундов игры
        return rnd


# 4. Показать текущее состояние игры на доске
def show_board(n_move, st):
    print('-----------')
    if not (n_move is None): print(f'Ход {n_move + 1}')
    print(f'Сейчас на столе {st} конфет (начальное число - {count_candies})')


# 5. Получить ход текущего игрока.
#    Проверить корректность хода. Если ход не корректен (количество в не допустимом диапазоне) повторить запрос.
def get_move(player, st, go_last, mov):

    # "Мозги" (интеллект) Bot'а
    def strategy_bot(m, n):
        if bot_strategy == 1:                   # мягкая стратегия, когда отсутствует гарантированная
            delta = 1 if m < 2 * (n + 1) else 2
            take = int(max(1, m - ((m-delta-0.5)//n * n + delta))) if m > n else st
            r = min(m, take)
            return max(1, r - 1) if ((m - r)//n) % 2 and delta-1 else r
        else:                                   # гарантированная стратегия, которая работает при определенных условиях
            rem = count_candies % (n + 1)
            if rem and not mov:                 # Если остаток от деления rem не равен 0 и если это первый ход
                return rem
            else:
                _, _, bot_code = tuple(player_ref.keys())
                opp_code = players_game[bot_code][0]
                p_last_opp = go_last[opp_code]
                return n + 1 - p_last_opp       # В этой строке вся гарантированная стратегия

    if player == tuple(player_ref.keys())[2]:   # Играет Bot
        # наделяем бота "интеллектом (мягкая стратегия, когда условия для гарантированной стратегии не выполняются):"
        # для выигрыша количество конфет, которое необходимо забирать => T = max(1, C - (C//p * p + 1))
        # где C - остаток конфет на столе; p - максимально количество, которое можно забрать за раз
        print(f'Ход {player_ref[player][2]} -> ... ', end='')
        time.sleep(bot_thinking)                # эмуляция времени "размышления" бота
        go = strategy_bot(st, can_removed)
        print(f'{go}')

    else:                                       # Играет соперник - человек
        go_default = min(st, can_removed, go_last[player] if len(go_last) > 1 else st)
        go = myl.get_input(1, min(st, can_removed), default=go_default,
                           txt=f'Ход {player_ref[player][2]}. '
                               f'Сколько конфет снять (по умолчанию {go_default})?', end='-')

    return go                                   # отправка хода


# 6. Обработать ход:
#   ... - если на столе не осталось конфет:
#    ОПРЕДЕЛИТЬ победителя (игрок сделавший ход последним) - игра завершена.
# Возврат:
# - None - если игра не завершена
# - № игрока, который выиграл, если на доске есть выигрыш.
#   Сообщить о результате игры (п.7)
def is_winnings(player, st):
    return player if not st else None


# 7. Показать статистику игр
#    Сыграно партий - N, из них:
#    Побед: Игрок-1 - x
#           Игрок-2 - y
def show_account(n_move, winner, st):
    pl1_data, pl2_data = tuple(players_game.items())
    pl1, data1 = pl1_data
    pl2, data2 = pl2_data
    print(f'\nРаунд {data1[1] + data2[1]}.')
    show_board(None, st)
    print(f'Сделано ходов {n_move}.')
    print(f'Победитель: {player_ref[winner][0]}')
    print('==================================')
    print('Всего:')
    print(f'Сыграно партий - {data1[1] + data2[1]}, из них:')
    print(f'Побед:  {player_ref[pl1][0]} - {data1[1]}')
    print(f'Побед:  {player_ref[pl2][0]} - {data2[1]}')
    print('==================================')


'''
=====================================================================================
Основное тело программы:
# ====================================================================================
План на реализацию:
----------------------------------------------------------------------
1, 2 - Инициация серии раундов игры
3. Инициация и старт очередного раунда игры:
   Выбрать соперника ("0" - Bot; "2" - Human)
   Провести жеребьевку (кто начинает), сообщить кратко о правилах
   игры "Всего [number] конфет. За один ход  можно взять не более 
   [p] конфет
4. Показать текущее состояние игры:
    - Сколько конфет осталось на столе
    - Чей ход ["Игрок-1 ->"]
5. Получить ход текущего игрока
   Проверить корректность хода. Если ход не корректен 
   (количество не в допустимом диапазоне) повторить запрос.
6. Обработать ход:
   - провести сделанный ход, обновив остаток конфет
   - если на столе не осталось конфет - определить победителя
    (игрок сделавший ход последним) игра завершена.
   Сообщить о результате игры (п.7)

Если игра завершена:
7. Вывести сообщение о результате:
    - Текущий результат (результат текущего раунда):
      Есть выигравший - "Победил игрок - ["Игрок-{}"] 
    - Общий счет:
        сколько сыграно, сколько побед у каждого игрока:
        Сыграно партий - N
        Побед:  Игрок-1 - x
                Игрок-2 - y
8. Уточнить о следующем раунде игры: 
"Еще раз?": - если да - переход на шаг-2; если нет - завершить игру.

Если игра не завершена:
9. Поменять текущего игрока, переход на шаг-4
----------------------------------------------------------------------

b) Думка как наделить бота "интеллектом".
----------------------------------------
Стратегию игры можно определить проведя мысленный эксперимент, проходя игру с конца.
Очевидно, что если к моменту своего хода на столе осталось не более разрешенного 
к взятию конфет [p] (p=28), то это однозначный выигрыш игрока, за кем сейчас ход.
В тоже время, если к моменту хода противника число конфет на столе [p+1], то 
противник однозначно проиграл.
Двигаясь мысленно назад по игре, можно заметить, что для завершения игры последним,
необходимо к моменту хода противника оставлять на столе [p*k] + 1 конфет, где k - 
некоторое целое число = делению остатка конфет на столе [C] на цело на [p], т.е.
Количество конфет, которое необходимо забирать => T = max(1, C - (C//p * p + 1))    
'''

def_count_candies = 2021                # Начальное число конфет
def_can_take = 28                       # можно забрать за один раз (не более чем)).

# 1, 2 Инициация серии раундов игры:
print('Игра НИМ - "Конфетки"')
print('======================')
n_games = init_game(series=True)
if n_games is None: exit()

new = True
while True:

    print(f'\nНачать {n_games+1}-й раунд игры "Конфетки"?', end='')
    if myl.check_exit(txt_req=' ("Y" - ДА) -> '):
        break

    # 3. Инициация и старт очередного раунда игры:
    init_params = init_game(init_count=def_count_candies, init_removed=def_can_take, new_set=new)
    if init_params is None:
        continue
    current_player, status, moves = init_params

    # Игра:
    move_last = {}
    while True:

        # 4. Показать текущее состояние игры (графическое изображение - не сейчас)
        show_board(moves, status)

        # 5. Получить ход текущего игрока (чей ход сейчас) и проверить корректность хода.
        move = get_move(current_player, status, move_last, moves)
        if move is None:
            new = True
            break

        # 6. Обработать ход:
        #    - провести сделанный ход, обновив остаток конфет
        move_last[current_player] = move
        status -= move

        #    - если на столе не осталось конфет - определить победителя (игрок сделавший ход последним) игра завершена.
        #    Сообщить о результате игры (п.7)
        #    иначе, устанавливаем текущего игрока и продолжаем игру (переход к п.4)
        result = is_winnings(current_player, status)

        if result is None:  # --- Если игра не завершена
            # 9. Поменять текущего игрока, определить номер следующего хода, переход на шаг-4
            current_player = players_game[current_player][0]
            moves += 1
            continue

        else:               # --- Если игра завершена:
            # 7. Ведение и вывод статистики игр по данным о результатах игр (result)
            n_games += 1
            players_game[result][1] += 1
            show_account(moves, result, status)

            # 8. уточнить о следующем раунде игры.
            #    "Еще раз?": - если да - переход на шаг-2; если нет - завершить игру.
            special = 'NnТт'
            select_cont = myl.check_exit(special=special, txt_req='\nЕще партию - нажмите кл. [ Y ]. '
                                                                  '\nЕсли желаете изменить вариант игры '
                                                                  '(начальное число конфет, сколько можно снять), '
                                                                  'нажмите кл. [ N ]ew -> ')
            if select_cont:
                if isinstance(select_cont, str):
                    new = select_cont in special
                    break
                exit()
