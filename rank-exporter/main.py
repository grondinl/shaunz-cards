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
        }
        res = post('https://api.cards.shaunz.fr/classement')
        classement = res.json()["classement"]
        for rank in classement: 
            sleep(0.1)
            cards_by_tier = post('https://api.cards.shaunz.fr/joueur', data={'userId': rank['id']}).json()['nbCardsByTier']
            metrics['points_gauge'].add_metric([rank['name']], rank['score'])
            metrics['count_gauge'].add_metric([rank['name']], rank['cards'])
            for tier in cards_by_tier.keys():
                metrics['count_gauge_by_tier'].add_metric([rank['name'],tier], cards_by_tier[tier])
        for metric in metrics.keys():
            yield metrics[metric]

REGISTRY.register(CustomCollector())
# Create my app
app = Flask(__name__)

# Add prometheus wsgi middleware to route /metrics requests
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})