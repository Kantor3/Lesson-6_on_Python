"""
Задача 1.
Напишите программу, удаляющую из текста все слова, содержащие фрагмент ""абв"".
"""
import my_lib as myl

is_fragment = lambda fr, s: s == s.replace(fr, '')

'''
=====================================================================================
Основное тело программы:
# ====================================================================================
'''
print('Удаляем из указанного текста все слова, содержжащие указанный фрагмент')
txt_test = 'привет абв как абвышные дела? абв'

while True:

    fragment_clr = 'абв'
    txt, fragment = myl.get_inputs('Введите любой текст (или "*" для тестирования)',
                                   'Введите фрагмент, слова содержащие который, нужно удалить',
                                   type_input=str, end='-')
    if txt is None and myl.check_exit(txt):
        break

    if txt == "*":
        txt = txt_test
    else:
        fragment_clr = fragment

    txt_cleared = ' '.join(list(filter(lambda word: is_fragment(fragment_clr, word), txt.split())))
    print(f'\nИсходный текст -> "{txt}"',
          f'Фрагмент для поиска и удаления слов -> "{fragment_clr}"',
          f'Очищенный текст -> "{txt_cleared}"', '', sep='\n')
