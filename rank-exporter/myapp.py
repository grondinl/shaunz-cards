from flask import Flask
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app
from prometheus_client.core import GaugeMetricFamily, REGISTRY
from requests import post 


class CustomCollector(object):
    def collect(self):
        metrics = {
            'points_gauge' : GaugeMetricFamily('papichoulo_cards_score','', labels=['name']),
            'count_gauge' : GaugeMetricFamily('papichoulo_cards_count','', labels=['name'])
        }
        res = post('https://api.cards.shaunz.fr/classement')
        classement = res.json()["classement"]
        for rank in classement: 
            metrics['points_gauge'].add_metric([rank['name']], rank['score'])
            metrics['count_gauge'].add_metric([rank['name']], rank['cards'])
        for metric in metrics.keys():
            yield metrics[metric]

REGISTRY.register(CustomCollector())
# Create my app
app = Flask(__name__)

# Add prometheus wsgi middleware to route /metrics requests
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
    '/metrics': make_wsgi_app()
})