from requests import post
from json import dumps
import click

def make_call(api_url, data):
    headers = {'Content-type': 'application/json'}
    resp = post(api_url, data=dumps(data), headers=headers)
    if resp.status_code != 200:
        print('failed : {}'.format(resp.text))
        return resp
    print('success')
    return resp

def login(base_api_url, data):
    print('Logging', end=' ')
    resp = make_call(base_api_url + '/login', data)
    if resp.status_code != 200:
        return {}
    print('Logged as {}'.format(resp.json()['name']))
    return resp.json()

def get_cards(base_api_url, data, card_token):
    print('Get card with token {}'.format(card_token), end=' ')
    data['token'] = card_token
    make_call(base_api_url + '/getCard', data)

def trade_token(base_api_url, data, card_token):
    print('Trade token {}'.format(card_token), end=' ')
    data['token'] = card_token
    make_call(base_api_url + '/tradeToken', data)

def gamble_pack(base_api_url, data):
    print('Gambling Pack', end=' ')
    make_call(base_api_url + '/gamblePack', data)

def multi_get_cards(base_api_url, data, token_key, token_count):
    for i in range(0,token_count):
        get_cards(base_api_url, data, token_key)

def multi_trade_token(base_api_url, data, token_key, token_count):
    for i in range(0,int(token_count/3)):
        trade_token(base_api_url, data, token_key)
    return login(base_api_url, data)

def multi_gamble_pack(base_api_url, data, token_count):
    for i in range(0,token_count):
        gamble_pack(base_api_url, data)
    return login(base_api_url, data)

@click.command()
@click.option('--access-token', required=True, envvar='ACCESS_TOKEN')
@click.option('--user-id', required=True, envvar='USER_ID')
@click.option('--base-api-url', default='https://api.cards.shaunz.fr')
def main(access_token, user_id, base_api_url):
    data = {'accessToken': access_token, 'userId' : user_id}
    login_resp = login(base_api_url, data)

    for token_key in ['6','1','2','3','4','5']:
        token_count = login_resp['tokens'][token_key]
        if token_key == '6':
            login_resp = multi_gamble_pack(base_api_url, data, token_count)
            continue
        if token_key == '2' or token_key == '3' or login_resp['hasAllCardsByTier'][token_key]:
            login_resp = multi_trade_token(base_api_url, data, token_key, token_count)
            continue
        multi_get_cards(base_api_url, data, token_key, token_count)

if __name__ == '__main__':
    main()


