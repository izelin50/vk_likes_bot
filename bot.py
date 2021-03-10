import datetime
import time

import requests
import vk


class VK:
    session = vk.Session(
        access_token='your_token')
    vkapi = vk.API(session, v='5.124')

    def getUserId(link, last_chat_id):
        id = link
        if 'vk.com/' in link:  # проверяем эту ссылку
            id = link.split('/')[-1]  # если да, то получаем его последнюю часть
        if not id.replace('id', '').isdigit():  # если в нем после отсечения 'id' сами цифры - это и есть id
            try:
                id = VK.vkapi.utils.resolveScreenName(screen_name=id)[
                    'object_id']  # если нет, получаем id с помощью метода API
            except:
                bot.send_message(last_chat_id, 'Проверь, пожалуйста, что такой пользователь существует!')
                return (-1)

        else:
            id = id.replace('id', '')
        return (int(id))

    def likes(id, last_chat_id):
        try:
            user_id = id  # id пользователя 182713909 286898805
            K = 100  # количество постов для анализа
            Q = K // 100
            K -= Q * 100
            try:
                bot.send_message(last_chat_id,
                                 "Ищу лайки пользователя " + VK.vkapi.users.get(user_ids=user_id)[0][
                                     'first_name'] + ' ' +
                                 VK.vkapi.users.get(user_ids=user_id)[0]['last_name'] + '.')

                subscriptions = VK.vkapi.users.getSubscriptions(user_id=user_id, extended=0)['groups']['items']
            except:
                return (
                    last_chat_id, 'Проверь, пожалуйста, что такой пользователь существует, что у него открыт профиль.')
            subscription = ['-' + str(x) for x in subscriptions]

            try:  # groups
                groups = VK.vkapi.groups.get(user_id=user_id, extended=1)
            except:
                bot.send_message(last_chat_id, "Список групп скрыт")
            group = []
            for f in range(len(groups['items'])):
                try:
                    if not (groups['items'][f]['is_closed'] and not groups['items'][f]['is_member']):
                        group.append("-" + str(groups['items'][f]['id']))
                except:
                    continue
            try:  # friends
                friends = VK.vkapi.friends.get(user_id=user_id, fields='is_closed')
            except:
                bot.send_message(last_chat_id, "Список друзей скрыт")
            friend = []
            for f in range(len(friends['items'])):
                try:
                    if friends['items'][f]['can_access_closed']:
                        friend.append(str(friends['items'][f]['id']))
                except:
                    continue

            subs = subscription + friend + group  # итоговый список источников
            time.sleep(1)
            newsfeed = VK.vkapi.newsfeed.get(filters='post', source_ids=', '.join(subs), count=K)
            for i in range(len(newsfeed['items'])):
                post = newsfeed['items'][i]['post_id']
                owner = newsfeed['items'][i]['source_id']
                isLiked = VK.vkapi.likes.isLiked(user_id=user_id, item_id=post, type='post', owner_id=owner)["liked"]
                time.sleep(0.3)
                if isLiked == 1:
                    bot.send_message(last_chat_id, "https://vk.com/feed?w=wall" + str(owner) + "_" + str(post))

            for j in range(Q):
                try:
                    next_from = newsfeed['next_from']
                except:break
                newsfeed = (
                    VK.vkapi.newsfeed.get(filters='post', source_ids=', '.join(subs), count=100, start_from=next_from))
                for i in range(len(newsfeed['items'])):
                    post = newsfeed['items'][i]['post_id']
                    owner = newsfeed['items'][i]['source_id']
                    isLiked = VK.vkapi.likes.isLiked(user_id=user_id, item_id=post, type='post', owner_id=owner)[
                        "liked"]
                    time.sleep(0.3)
                    if isLiked == 1:
                        bot.send_message(last_chat_id, "https://vk.com/feed?w=wall" + str(owner) + "_" + str(post))
            bot.send_message(last_chat_id,
                             "Похоже, это все лайки из последних ста постов в ленте пользователя. Если выше ничего нет, значит, пользователь не оценил ни один из этих постов.\nМожешь поискать лайки еще кого-нибудь.")
        except:
            bot.send_message(last_chat_id,
                             'Извини, возникла небольшая проблема: ВК не отвечает на запросы. Это та самая ошибка из-за количества запросов, о которой я писал в статье. Попробуй немного позднее.')


class BotHandler:

    def __init__(self, token):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)

    def get_updates(self, offset=None, timeout=30):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset}
        resp = requests.get(self.api_url + method, params)
        result_json = resp.json()['result']
        return result_json

    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text}
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp

    def get_last_update(self):
        get_result = self.get_updates()

        if len(get_result) > 0:
            last_update = get_result[-1]
        else:
            last_update = ''
        return last_update


bot = BotHandler('1337963147:AAGQGxsH-5kB0p3yQ5OdPEWPaAmLnKAMus8')
greetings = ('здравствуй', 'привет', 'ку', 'здорово')
now = datetime.datetime.now()


def main():
    new_offset = None
    while True:
        bot.get_updates(new_offset)
        last_update = bot.get_last_update()
        if(last_update!=''):
            last_update_id = last_update['update_id']
            last_chat_text = last_update['message']['text']
            last_chat_id = last_update['message']['chat']['id']
            last_chat_name = last_update['message']['chat']['first_name']
            bot.send_message(862478401,str(last_chat_id)+" "+last_chat_name+" заказал " + last_chat_text)
        
        else:
            continue
        if (last_chat_text in greetings or last_chat_text == "/start"):
            bot.send_message(last_chat_id,
                             'Привет, {}! Отправь мне id или ссылку на страницу исследуемого пользователя, а в ответ я тебе пришлю последние посты, которые он лайкнул.'.format(
                                 last_chat_name))
        else:
            bot.send_message(last_chat_id, 'Спасибо! Пошёл искать...')
            VK.likes(VK.getUserId(last_chat_text, last_chat_id), last_chat_id)

        new_offset = last_update_id + 1


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
