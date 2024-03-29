from contextlib import closing
import io
import logging
from operator import itemgetter
import os
from pickle import HIGHEST_PROTOCOL
import shelve
import urllib
import uuid

from flask import abort, Flask, jsonify, redirect, render_template, send_file, url_for
import graphviz as gv

import machines
from registry import registry


SHELVE_DB = 'shelve'

app = Flask(__name__)
app.config.from_object(__name__)

db = shelve.open(os.path.join(
    app.root_path, app.config['SHELVE_DB']),
    protocol=HIGHEST_PROTOCOL, writeback=True)

app = Flask(__name__)


def init(name, pk):
    key = name + ':' + str(pk)
    obj = registry[name]()
    db.setdefault(key, default=dict(state=obj.state))
    obj.state = obj.fsm.states(db[key]['state'])
    return obj


def update(name, pk, state):
    key = name + ':' + str(pk)
    db[key]['state'] = state


def render(fsm, state):
    styles = {
        'graph': {
            'fontsize': '16',
            'fontcolor': 'white',
            'bgcolor': '#333333',
        },
        'node': {
            'shape': 'box',
            'fontname': 'Helvetica',
            'fontcolor': 'white',
            'color': 'white',
            'style': 'filled',
            'fillcolor': '#006699',
        },
        'selected-node': {
            'shape': 'box',
            'fontname': 'Helvetica',
            'fontcolor': 'white',
            'color': 'white',
            'style': 'filled',
            'fillcolor': '#009900',
        },
        'edge': {
            'style': 'dashed',
            'color': 'white',
            'arrowhead': 'open',
            'fontname': 'Courier',
            'fontsize': '12',
            'fontcolor': 'white',
        },
        'selected-edge': {
            'color': '#009900',
            'arrowhead': 'open',
            'fontname': 'Courier Bold',
            'fontsize': '12',
            'fontcolor': '#009900',
        }
    }

    g = gv.Digraph(format='png')
    for s in fsm.states:
        style = styles['selected-node'] if s == state else styles['node']
        g.node(s.name, **style)
    for state0, state1, event in fsm.edges:
        style = styles['selected-edge'] if state0 == state else styles['edge']
        g.edge(state0.name, state1.name, label=event.name, **style)
    g.graph_attr.update(('graph' in styles and styles['graph']) or {})
    return g.pipe(format='png')


@app.route('/machines/<name>/<uuid:pk>')
def get(name, pk):
    obj = init(name, pk)
    kwargs = dict(
        registry=registry,
        fsm=obj.fsm,
        state=obj.state,
        name=name,
        pk=pk)
    return render_template('machine.html', **kwargs)


@app.route('/machines/<name>/', methods=['GET', 'POST'])
@app.route('/machines/', methods=['GET', 'POST'])
@app.route('/')
def post(name='connections'):
    uuid4 = uuid.uuid4()
    init(name, uuid4)
    return redirect(url_for('get', name=name, pk=uuid4))


@app.route('/favicon.ico')
def favicon():
    abort(404)


@app.route('/api/<name>/<uuid:pk>.png')
def api_state_png(name, pk):
    obj = init(name, pk)
    return send_file(io.BytesIO(render(obj.fsm, obj.state)),
                     attachment_filename=str(obj.state).lower()+'.png',
                     mimetype='image/png')


@app.route('/api/<name>/<uuid:pk>/<event>', methods=['PUT'])
def api_state_update(name, pk, event):
    obj = init(name, pk)
    if obj.fsm.move(obj, obj.fsm.events[event]):
        state1 = obj.state
        update(name, pk, state1)
        events = []
        for edge in obj.fsm.edges:
            state0, _, event = edge
            if state0 == state1:
                events.append(dict(
                    name=event.name,
                    url=url_for('api_state_update', name=name, pk=pk, event=event.name)
                    ))
        return jsonify(dict(
            state=state1.name,
            url=url_for('api_state', name=name, pk=pk),
            image_url=url_for('api_state_png', name=name, pk=pk),
            events=events))
    resp = jsonify({})
    resp.status_code = 409
    return resp


@app.route('/api/<name>/<uuid:pk>')
def api_state(name, pk):
    obj = init(name, pk)
    events = []
    for edge in obj.fsm.edges:
        state0, _, event = edge
        if state0 == obj.state:
            events.append(dict(
                name=event.name,
                url=url_for('api_state_update', name=name, pk=pk, event=event.name)
                ))
    return jsonify(dict(
        state=obj.state.name,
        image_url=url_for('api_state_png', name=name, pk=pk),
        events=events))


@app.route("/api")
def api_root():
    routes = []
    for rule in app.url_map.iter_rules():
        options = {}
        for arg in rule.arguments:
            options[arg] = "[{0}]".format(arg)
        url = urllib.parse.unquote(url_for(rule.endpoint, **options))
        routes.append(dict(
            endpoint=rule.endpoint,
            methods=sorted(list(rule.methods)),
            url=url))
    return jsonify(sorted(routes, key=itemgetter('url')))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    with closing(db):
        app.run(debug=True, threaded=True)
