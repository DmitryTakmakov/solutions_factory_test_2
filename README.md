# Notifications API

Небольшое сервис для отправки уведомлений. Создано с помощью Django, Django REST Framework, PostgreSQL, Celery. Всё это упаковано в Docker-контейнеры.

## Подготовка к запуску проекта

В любой удобной папке на своем компьютере выполните следующую команду:

`git clone git@gitlab.com:test_tasks2/solutions_factory.git`

Далее перейдите в свежескачанную директорию командой:

`cd solutions_factory`

После этого выполните следующие команды:

`pip install virtualenv`

`python -m venv /solutions_factory/venv`

И активируйте виртуальное окружение:

`source venv/bin/activate`

После этого установите необходимые для проекта зависимости из файла **requirements.txt**.

`pip install -r requirements.txt`

Далее выполните команду для сбора статических файлов:

`python manage.py collectstatic`

Для запуска проекта также потребуются Docker и docker-compose. Установить их можно следующими командами: 

`sudo apt-get install docker-ce docker-ce-cli containerd.io`

`sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose`

`sudo chmod +x /usr/local/bin/docker-compose`

Если после установки команда docker-compose так и не появилось в терминале, то нужно выполнить следующую команду:

`sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose`

## Запуск и использование

Всё готово к запуску, нужно выполнить:

`docker-compose up --build`

После завершения сборки всех контейнеров сервис будет доступен в браузере по адресу `localhost` или `127.0.0.1`.
Список разработанных эндпойнтов:
1. `api/recipient-create/`
2. `api/recipient-update/<int:pk>`
3. `api/recipient-delete/<int:pk>`
4. `api/mailout-create/`
5. `api/mailout-list/`
6. `api/mailout-update/<int:pk>`
7. `api/ mailout-delete/<int:pk>`
8. `api/mailout-info/<int:pk>`
9. `api/manage`

В проекте подключен Browsable API, так что по всем данным эндпойнтам можно перемещаться непосредственно в браузере.
Последний эндпойнт ведет на Router для управления активными рассылками и сообщениями в данных рассылках. Browsable API предоставляет ссылки, по которым можно переместиться дальше из данного корневого эндпойнта. 

## Задания

Выполнены все основные задания, а также несколько дополнительных.
* подготовить docker-compose для запуска всех сервисов проекта одной командой - _очевидно_
* сделать так, чтобы по адресу /docs/ открывалась страница со Swagger UI и в нём отображалось описание разработанного API - _документация доступна по вышеозначенному адресу_
* обработка ошибок удаленного сервиса (задание 9) - _оно, вроде как, есть и в основном задании, но продублировано и в дополнительные. В любом случае ошибки внешнего сервиса обрабатываются, если данный сервис не получает необходимого ответа, сообщения заново добавляются в очередь на отправку с таймаутом в 10 минут_
