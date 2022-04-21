from gc import callbacks
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

def validate_token_to_trade(ctx, param, value):
    if isinstance(value, list):
        return value
    try:
        tokens = value.split(",")
        for token in tokens:
            if int(token) < 0 or  int(token) > 5:
                raise ValueError
        return tokens
    except ValueError:
        raise click.BadParameter("format must be number between 1 to 5 comma separated")

@click.command()
@click.option('--access-token', required=True, envvar='ACCESS_TOKEN')
@click.option('--user-id', required=True, envvar='USER_ID')
@click.option('--base-api-url', default='https://api.cards.shaunz.fr')
@click.option('--token-to-trade', envvar='TOKEN_TO_TRADE', default='2,3', callback=validate_token_to_trade)
def main(access_token, user_id, base_api_url, token_to_trade):
    data = {'accessToken': access_token, 'userId' : user_id}
    login_resp = login(base_api_url, data)
    tokens = login_resp['tokens']
    tokens_list = list(tokens.keys())
    for token_key in reversed(tokens_list):
        token_count = tokens[token_key] 
        for i in range(0,token_count):
            if token_key == '6':
                gamble_pack(base_api_url, data)
                if i == token_count - 1:
                    tokens = login(base_api_url, data)
                continue
            if token_key in token_to_trade or login_resp['hasAllCardsByTier'][token_key]:
                trade_token(base_api_url, data, token_key)
                continue
            get_cards(base_api_url, data, token_key)

if __name__ == '__main__':
    main()


