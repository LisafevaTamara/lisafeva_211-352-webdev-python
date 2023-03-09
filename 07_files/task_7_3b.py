# -*- coding: utf-8 -*-
"""
Задание 7.3b

Сделать копию скрипта задания 7.3a.

Переделать скрипт:
- Запросить у пользователя ввод номера VLAN.
- Выводить информацию только по указанному VLAN.

Пример работы скрипта:

Enter VLAN number: 10
10       0a1b.1c80.7000      Gi0/4
10       01ab.c5d0.70d0      Gi0/8

Ограничение: Все задания надо выполнять используя только пройденные темы.

"""

serch = input("Введите Vlan: ")
crush = []
with open("07_files/CAM_table.txt") as f:
    for line in f:
        cam_tab = line.split()
        if cam_tab and cam_tab[0].isdigit():
            vlan, mac, _, intef = cam_tab
            crush.append([int(vlan), mac, intef])
for i in range(len(crush)):
    if crush[i][0] == int(serch):
        print(f"{crush[i][0]:<10}{crush[i][1]:20}{crush[i][2]}")