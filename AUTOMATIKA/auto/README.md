# HamsterKombatFarmer

Пример того, как можно автоматизировать рутину в телеграм боте https://t.me/hamster_kombat_bot

Скрипт умеет:

- Тапать
- Брать буст энергии
- Покупать карточки по наилучшему сочетанию профита к цене карточки
- Если повезет - собирать комбо
- Забирать профит с комбо
- Собирать ежедневную награду ( которая до 5 000 000)
- Разгадывать шифр с морзянкой
- В игру не нужно заходить каждые 3 часа, чтоб собрать пассивный доход
- Мультиаккаунтинг

Все как обычно.

1. Установить Python (https://www.python.org/) 
2. Скачать/склонировать репозиторий к себе в каталог
3. Перейти в каталог со скриптом
4. Накатить зависимости. (в терминале выполнить команду `pip install -r requirements.txt`)
5. Получить токен / токены.
Гайд как получить токен в хомяке.

1. Нужно как-то открыть хомяка в telegram web.
Как? - Решайте сами, я действовал по этому гайду https://dzen.ru/a/ZlsAKWi2bRTmLiNv
Ответственности если что не несу)
2. Дальше уже получение токена 
Открыли приложение, кликнули ПКМ, просмотреть код, Network, Fetch/XMR. я кликал в приложении Mine а потом обратно на Exchange. Появлялся запрос tap, заходим листаем ниже будет строчка Authorization:
Bearer, всё что после Bearer - токен.
6. Записать в `config.py`
7. Для запуска в терминале выполнить команду: `python3 bot.py`


Обсудить можно здесь: https://t.me/+DzfPvutZSetmZWE6

Для донатов: USDT TRC20: TWBrbZxwsTq9EdCfxTbjzriNUWKFEuRx8t
