from requests import post
from json import dumps
import click

def make_call(api_url, data):
    headers = {
        'Content-type': 'application/json'
    }
    resp = post(api_url, data=dumps(data), headers=headers)
    return resp

def login(base_api_url, data):
    resp = make_call(base_api_url + '/login', data)
    if resp.status_code != 200:
        print('Logging failed')
        return {}
    print('Logged as {}'.format(resp.json()['name']))
    return resp.json()['tokens']

def get_cards(base_api_url, data, card_token):
    print('Get card with token {}'.format(card_token), end=' ')
    data['token'] = card_token
    resp = make_call(base_api_url + '/getCard', data)
    if resp.status_code != 200:
        print('failed : {}'.format(resp.text))
    print('success')

def trade_token(base_api_url, data, card_token):
    print('Trade token {}'.format(card_token), end=' ')
    data['token'] = card_token
    resp = make_call(base_api_url + '/tradeToken', data)
    if resp.status_code != 200:
        print('failed : {}'.format(resp.text))
    print('success')

def gamble_pack(base_api_url, data):
    print('Gambling Pack', end=' ')
    resp = make_call(base_api_url + '/gamblePack', data)
    if resp.status_code != 200:
        print('failed : {}'.format(resp.text))
    print('success')

@click.command()
@click.option('--access-token', required=True, envvar='ACCESS_TOKEN')
@click.option('--user-id', required=True, envvar='USER_ID')
@click.option('--base-api-url', default='https://api.cards.shaunz.fr')
def main(access_token, user_id, base_api_url):
    data = {'accessToken': access_token, 'userId' : user_id}
    login_resp = login(base_api_url, data)
    tokens = login_resp['tokens']
    tokens_list = ['6','1','2','3','4','5']
    for token_key in tokens_list:
        token_count = tokens[token_key] 
        for i in range(0,token_count):
            if token_key == '6':
                gamble_pack(base_api_url, data)
                if i == token_count - 1:
                    tokens = login(base_api_url, data)
                continue
            if token_key == '2' or token_key == '3' or login_resp['hasAllCardsByTier'][token_key]:
                trade_token(base_api_url, data, token_key)
                continue
            get_cards(base_api_url, data, token_key)

if __name__ == '__main__':
    main()


