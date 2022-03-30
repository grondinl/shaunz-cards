from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app
from prometheus_client.core import GaugeMetricFamily, REGISTRY
from requests import post
from time import sleep


class CustomCollector(object):
    def collect(self):
        metrics = {
            'points_gauge' : GaugeMetricFamily('papichoulo_cards_score','', labels=['name']),
            'count_gauge' : GaugeMetricFamily('papichoulo_cards_count','', labels=['name']),
            'count_gauge_by_tier' : GaugeMetricFamily('papichoulo_cards_count_by_tier','', labels=['name', 'tier']),
            'shiny_count_gauge' : GaugeMetricFamily('papichoulo_shiny_count','', labels=['name', 'tier']),
            'trophees' : GaugeMetricFamily('papichoulo_trophee','', labels=['name', 'type']),
        }
        res = post('https://api.cards.shaunz.fr/classement')
        classement = res.json()['classement']
        for rank in classement: 
            name = rank['name']
            joueur = post('https://api.cards.shaunz.fr/joueur', data={'userId': rank['id']}).json()
            cards_by_tier = joueur['nbCardsByTier']
            list_cards = joueur['listCards']
            metrics['points_gauge'].add_metric([name], rank['score'])
            metrics['count_gauge'].add_metric([name], rank['cards'])

            for tier, count in cards_by_tier.items():
                metrics['count_gauge_by_tier'].add_metric([name,tier], count)

            has_shiny = False
            for trophee in joueur['trophees']:
                if trophee['name'] == 'shinny':
                    has_shiny = trophee['value']
                    continue
                value = 1 if trophee['value'] else 0
                metrics['trophees'].add_metric([name,trophee['name']], value)
                
            if has_shiny:
                shiny_count_by_tier = {'1':0,'2':0,'3':0,'4':0,'5':0}
                for card in list_cards:
                    if 'shiny' in card:
                        level = str(card['level'])
                        shiny_count_by_tier[level] += 1

                for tier, shiny_count in shiny_count_by_tier.items():
                    if shiny_count != 0:
                        metrics['shiny_count_gauge'].add_metric([name,tier], shiny_count)
             
            sleep(0.1)

        for metric in metrics.keys():
            yield metrics[metric]

REGISTRY.register(CustomCollector())

app = Flask(__name__)

# Add prometheus wsgi middleware to route /metrics requests
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})

@app.route("/")
def index():
    return "ok"