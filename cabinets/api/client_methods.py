import requests
import json


def vk_request(type, name, params, token, v):
    params['access_token'] = token
    params['v'] = v

    if type == 'get':
        r = requests.get('https://api.vk.com/method/' + name, params)
        return r.json()
    if type == 'post':
        r = requests.post('https://api.vk.com/method/' + name, params)
        return r.json()


def getClient(account_id, token, client_id):
    try:
        r = vk_request('get', 'ads.getClients', {
                       'account_id': account_id}, token, '5.131')
        result = {}
        clients = r['response']

        if len(clients) == 0:
            return -1
        for c in clients:
            if str(c['id']) == str(client_id):
                return {'name': c['name'], 'spent': 0, 'status': 1, 'all_limit': c['all_limit'],  'day_limit': c['day_limit']}
        return -1

    except Exception as e:
        print('Failed get client: ' + str(e))
        return -1


# Result = [{id, name, day_limit, all_limit, spent}]
# Error = -1
def getClients(account_id, token):
    try:
        # {id, name, day_limit, all_limit}
        r = vk_request('get', 'ads.getClients', {
                       'account_id': account_id}, token, '5.131')

        result = {}

        clients = r['response']

        if len(clients) == 0:
            return []

        client_ids = ''
        for c in clients:
            client_ids = client_ids + str(c['id']) + ','

            result[c['id']] = {'name': c['name'], 'spent': 0, 'status': 1,
                               'all_limit': c['all_limit'],  'day_limit': c['day_limit']}
        client_ids = client_ids[:-1]

        # {id, type, stats}
        clients_stats = vk_request('get', 'ads.getStatistics', {
                                   'account_id': account_id, 'ids_type': 'client', 'ids': client_ids, 'period': 'overall', 'date_from': '0', 'date_to': '0'}, token, '5.131')
        for c in clients_stats['response']:
            try:
                result[c['id']]['spent'] = c['stats'][0]['spent']
            except Exception as e:
                print('Failed client spent assign: ' + str(e))

        result_list = []
        for key in result:
            result_list.append({'id': int(key), 'spent': result[key]['spent'], 'name': result[key]
                                ['name'], 'day_limit': result[key]['day_limit'], 'all_limit': result[key]['all_limit']})
        return result_list
    except Exception as e:
        print('Failed get clients: ' + str(e))
        return -1


# Result: client_id
# Error: -1
def createClient(account_id, token, name, day_limit, all_limit):
    try:
        r = vk_request('get', 'ads.createClients', {'account_id': account_id, 'data': json.dumps(
            [{'name': name, 'day_limit': str(day_limit), 'all_limit': str(all_limit)}])}, token, '5.131')
        id = r['response'][0]['id']
        return id
    except Exception as e:
        print('Failed create client: ' + str(e))
        return -1


# Result: client_id
# Error: -1
def updateClient(account_id, token, client_id, name, day_limit, all_limit):
    try:
        r = vk_request('get', 'ads.updateClients', {'account_id': account_id, 'data': json.dumps(
            [{'client_id': client_id, 'name': name, 'day_limit': str(day_limit), 'all_limit': str(all_limit)}])}, token, '5.131')
        id = r['response'][0]['id']
        return id
    except Exception as e:
        print('Failed update client: ' + str(e))
        return -1


# Result: 0 | 600
# Error: -1
def deleteClient(account_id, token, client_id):
    try:
        r = vk_request('get', 'ads.deleteClients', {
                       'account_id': account_id, 'ids': json.dumps([client_id])}, token, '5.131')
        return r['response'][0]
    except Exception as e:
        print('Failed delete client: ' + str(e))
        return -1


# Result: {vk_id, photo, name, role}
# Error: -1
def getVkUserInfo(token, user_id):
    try:
        user_data = vk_request('get', 'users.get', {
                               'user_ids': user_id, 'fields': 'photo_200'}, token, '5.124')['response'][0]

        result = {}

        result['vk_id'] = user_data['id']
        result['photo'] = user_data['photo_200']
        result['name'] = user_data['first_name'] + ' ' + user_data['last_name']
        result['role'] = 0

        return result
    except:
        return -1

# [{'user_id': 122058319, 'accesses': [{'client_id': 1606988483, 'role': 'manager'}]


def getOfficeUsers(token, account_id):
    r = vk_request('get', 'ads.getOfficeUsers', {
                   'account_id': account_id}, token, '5.131')
    result = r['response']
    print(result)
    return result

# Input: data = [{user_id: int, role: manager | reports, client_ids: [int]}]
# Response: {'response': [{'user_id': int, 'is_success': boolean}]}


def removeOfficeUsers(token, account_id, ids):
    r = vk_request('post', 'ads.removeOfficeUsers', {
                   'account_id': account_id, 'ids': json.dumps(ids)}, token, '5.131')
    print(r)


def updateOfficeUsers(token, account_id, client_id, users_id):

    def collectData(input, client_id, users_id):
        result = {}
        for item in input:
            user_id = item['user_id']
            temp = []
            for access in item['accesses']:
                if access['role'] != 'admin':
                    temp.append(int(access['client_id']))

            if len(temp) > 0:
                result[user_id] = temp

        for user in result:
            ids = result[user]
            if user in users_id:
                ids.append(client_id)
            else:
                ids = list(filter(lambda x: (x != client_id), ids))

            result[user] = ids

        for user in users_id:
            if user not in result:
                result[user] = [client_id]

        print(result)
        return result

    def prepData(data):
        result = []
        delete = []
        for u in data:
            if len(data[u]) > 0:
                temp = {}
                temp['grant_access_to_all_clients'] = False
                temp['view_budget'] = False
                temp['user_id'] = u
                temp['client_ids'] = data[u]
                temp['role'] = 'reports'
                result.append(temp)
            else:
                delete.append(u)

        if len(delete) > 0:
            removeOfficeUsers(token, account_id, delete)
        print(result)
        return result

    prev_data = getOfficeUsers(token, account_id)
    new_data = collectData(prev_data, client_id, users_id)
    prep_data = prepData(new_data)

    if len(prep_data) > 0:
        r = vk_request('post', 'ads.updateOfficeUsers', {
                       'account_id': account_id, 'data': json.dumps(prep_data)}, token, '5.131')
        print(r)
