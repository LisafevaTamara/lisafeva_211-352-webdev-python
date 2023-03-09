# -*- coding: utf-8 -*-
"""
Задание 6.2b

Сделать копию скрипта задания 6.2a.

Дополнить скрипт: Если адрес был введен неправильно, запросить адрес снова.

Если адрес задан неправильно, выводить сообщение: 'Неправильный IP-адрес'
Сообщение "Неправильный IP-адрес" должно выводиться только один раз,
даже если несколько пунктов выше не выполнены.

Ограничение: Все задания надо выполнять используя только пройденные темы.
"""




f = False
while f!=True:
    ip = input("введите ip-адрес: ")
    ip2 = ip.split(".")
    f = True
    if len(ip2) !=4:
        f = False
    else:
        for i in range(len(ip2)-1):
            if not (ip2[i].isdigit()):
                f = False
                break
            if int(ip2[i]) < 0 or int(ip2[i]) > 255:
                f = False
                break
                

    if f == False:
        print("Неправильный IP-адрес")

if ip == "255.255.255.255":
    print("local broadcast")
elif ip == "0.0.0.0":
    print("unassigned")
elif int(ip2[0])>=1 and int(ip2[0]) <= 223:
    print("unicast")
elif int(ip2[0])>=224 and int(ip2[0]) <= 239:
    print("multicast")
else:
    print("unused")