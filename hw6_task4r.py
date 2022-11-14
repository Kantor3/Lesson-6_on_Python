"""
Задача 4.
Реализуйте RLE алгоритм: реализуйте модуль сжатия и восстановления данных.
Входные и выходные данные хранятся в отдельных текстовых файлах.

Строки для теста:
txt = 'beeeeeeeeeeeeeeer !! 123456789abcdefg уууууууфффффффффффффффффффффффффффффффффффф!'
txt = '11 222 333 123456789 77777777777777777'
txt_code = '1 2 3 123456789 7'

-----------------------------
Есть множество вариантов реализации алгоритма сжатия RLE. Мне понравился этот
(его немного я модифицировал, как понял сам, исходя из особенностей языка Python)
Используемый алгоритм сжатия:
-----------------------------
Представляем все цепочки одинаковых символов собственно этим символом, а в служебном байте,
с которого начинается любая цепочка архива указываем их количество и тип цепочки.
Цепочки разных (не повторяющихся) символов исходного текста в архиве также будут иметь
служебный байт (тип цепочки и длина), после которого следуют все символы исходной цепочки.
Модификация:
Цепочки одинаковых символов нумеруем числами от 2 до 128,
соответственно цепочки различающихся символов - от 129 до 255.
Оставшиеся символы с кодами 0 и 1 используем для переключения режима - включение / отклюячение
режима сжатия: 1 - включить режим сжатия, 0 - отключить режим сжатия
-----------------------------
"""
import my_lib as my

count_max = 0  # Максимальное количество символов в серии. 0 - не определено


# Ввод задания на обработку данных
def arc_task(no_help=None):
    if not no_help: arc_help()
    # print('\nEnter the task to the archiver according to the instructions (no option - exit):')
    print('\nВведите задание для архиватора в соответствии с инструкцией.\n'
          'Для вывода инструкции введите -[h]. Для отказа нажмите [Enter]):')
    while True:
        opt, src, rcv = my.get_inputs('-[arc_option]', '-[source]', '-[receiver]',
                                      type_input=str, end='-', not_mess=True)
        if None in (opt, src, rcv):
            opt = None if opt is None or not opt[:2] in ('-h', '-q') else opt
            return opt, None, None
        if not opt[:2] in ('-h', '-a', '-r', '-q', '--'):
            print(f'this option "{opt}" is not supported by the application')
            continue
        if src[0] == '-' and not src[:2] == '-k':
            print(f'this source "{src}" is not supported by the application')
            continue
        if rcv[0] == '-' and not rcv[:2] == '-c':
            print(f'this receiver "{rcv}" is not supported by the application')
            continue
        return opt, src, rcv


# Вывод краткой инструкции для задания опций на сжатие / восстановление
def arc_help():
    print('\nDescription:')
    print('Data Compression/Recovery. Options: -[arc_option] -[source] -[receiver].'
          '\n-------------------------------------------------------------------------')
    print('[source] (data for compression / recovery):'
          '\n    - "-k" - keyboard input'
          '\n    - [name_file] - the name of the data file for compression / recovery')
    print('[receiver] (output of compression/recovery result):'
          '\n   - "-с" - output of the result to the console'
          '[name_file] - the name of the file to record the result')
    print('[arc_option] (arc_option):'
          '\n   - "-h" - get Help (brief instructions) - this instructions'
          '\n   - "-a" - compressing data to a file'
          '\n   - "-r" - data recovery with output to a terminal or writing to a file'
          '\n   - "--" or "-q" - shut down, exit')
    print('-------------------------------------------------------------------------')


# Получить данные для сжатия / восстановления
def get_data(option):
    return my.get_data_file(option) if not option == '-k' else \
           my.get_input(txt='Введите текст для сжатия / восстановления', type_input=str)


# Инициализация процессов сжатия и восстановления
def init(stream, recovery=None):
    global count_max
    count_max = 127
    len_, result, series_type, count_series, symbols_series, symbol_last = len(stream), '', 0, 0, None, None
    ret = (len_, result, series_type, count_series, symbols_series, symbol_last) if recovery is None else \
          (len_, result, series_type, count_series)
    return ret


# Выполнить сжатие данных
def arc_compression(txt, show=None):
    len_txt, result, series_type, count_series, symbols_series, symbol_last = init(txt)
    if not len_txt:
        return None

    # Формирование серии для записи в результат
    def recording_series(s_type, series, count):
        bin_sign = f'{count_max + 1 :b}'
        bin_sign = int(bin_sign, 2)
        code = chr((0 if s_type > 0 else bin_sign) + count)
        return code + series

    '''
    Собственно сжатие данных
    series_type - вид серии:
      0 - серия не определена (в начале работы или после достижения серии count_max)
      1 - серия повторяющихся символов
     -1 - серия неповторяющихся символов
    Возможное расширение функциональных возможностей алгоритма:
    Использовать дополнительно еще 2-а значения (2 и -2) снизив обычные серии со 127 до 126 символов, 
    но добавив расширенные серии double до 32256, кодируя число в серии дополнительным байтом.
    Добавив дополнительно оценочную функцию разумности использования сжатия на анализируемом участке, можно 
    сделать более гибким сам процесс сжатия, исключив повышения размерности файла, в случае его плохой сжимаемоcти
    '''
    for smb in txt:

        # Учет ограничения длины серии
        if count_series == count_max:
            result += recording_series(series_type, symbols_series, count_series)
            series_type, count_series = 0, 0

        # Перезапуск набора серии после срабатывания ограничения
        if not count_series:
            symbols_series = symbol_last = smb
            count_series = 1
            continue

        # Определение серии для текущего момента
        series_type = series_type if series_type else 1 if smb == symbol_last else -1

        # Отработка для серии повторяющихся символов
        if smb == symbol_last:
            if series_type == -1:       # смена вида серии с неповторяющихся символов на повторяющуюся
                result += recording_series(series_type, symbols_series[:-1], count_series - 1)
                series_type = 1         # запуск серии повторяющихся символов
                count_series = 1
                symbols_series = smb

        # Отработка для серии неповторяющихся символов
        else:
            symbol_last = smb
            if series_type == 1:        # смена вида серии с повторяющихся символов на неповторяющиеся
                result += recording_series(series_type, symbols_series, count_series)
                series_type = -1        # запуск серии неповторяющихся символов
                count_series = 0
                symbols_series = smb
            else:
                symbols_series += smb

        count_series += 1

    result += recording_series(series_type, symbols_series, count_series)

    # Показать статистику сжатия
    if not (show is None):
        len_source = len(txt)
        len_result = len(result)
        perc_compr = round((len_source - len_result) / len_source * 100, 1)
        print(f'\nИсходный размер = {len_source}, Сжатый = {len_result}. Степень сжатия = {perc_compr}%')

    return result


# Выполнить восстановление данных
def arc_recovery(txt):
    len_txt, result, series_type, count_series = init(txt, recovery=True)
    if not len_txt:
        return None

    def get_type(symbol):
        code = ord(symbol)
        return (1, code) if code < count_max + 1 else (-1, code - count_max - 1)

    # Собственно восстановление данных
    ind = 0
    while ind - len_txt:
        series_type, count_series = get_type(txt[ind])
        ind += 1 + (1 if series_type == 1 else count_series)
        symbols_series = txt[ind - 1] * count_series if series_type == 1 else txt[ind - count_series: ind]
        result += symbols_series

    return result


# Вывести результат на консоль
def output_console(txt_src, txt_res, option):
    txt_operation = "Сжатый" if option == '-a' else 'Восстановленный' if option == '-r' else None
    if not (txt_operation is None):
        print(f'Исходный текст: {txt_src}.\n{txt_operation}: {txt_res}')


'''
===================================================================================
Основное тело программы:
source:
- источник данных для сжатия / восстановления:
    - "-k" - ввод с клавиатуры
    - [name_file] - имя файла с данными для сжатия / восстановления
receiver:
- приемник данных - при восстановлении:
    - "-c" - вывод результата сжатия / восстановления на консоль 
    - [name_file] - имя файла записи результата сжатия / восстановления
arc_option:
    - "-h" - вывести Помощь (краткую инструкцию)
    - "-a" - сжатие данных в файл
    - "-r" - восстановление данных с выводом в терминал или записью в файл
    - "--" или "-q" - завершить работу, выход 
===================================================================================
'''
print('Сжатие и восстановление данных, хранящихся в файлах.')

while True:

    arc_option, source, receiver = arc_task(no_help=True)

    if arc_option is None and my.check_exit(True) \
            or arc_option == '--' \
            or arc_option == '-q':  # Выход
        break

    if arc_option == '-h':          # Помощь (краткая инструкция)
        arc_help()
        continue

    txt_source = get_data(source)   # Получить данные для обработки

    if txt_source is None: break    # Операция отменена или источник недоступен
    res = None
    if arc_option == '-a': res = arc_compression(txt_source, show=True)         # Сжатие данных файла
    if arc_option == '-r': res = arc_recovery(txt_source)                       # Восстановление данных из файла

    if not (res is None):
        if receiver == '-c':
            output_console(txt_source, res, arc_option)                         # Вывод результата на консоль
        else:
            my.wr_data_file(receiver, res, message='Данные записаны в файл')    # Запись результата в файл
