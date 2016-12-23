from contextlib import closing
import io
import logging
import os
from pickle import HIGHEST_PROTOCOL
import shelve
import uuid

from flask import Flask, jsonify, redirect, render_template, send_file, url_for
import graphviz as gv

import tcp


SHELVE_DB = 'shelve'

app = Flask(__name__)
app.config.from_object(__name__)

db = shelve.open(os.path.join(
    app.root_path, app.config['SHELVE_DB']),
    protocol=HIGHEST_PROTOCOL, writeback=True)

app = Flask(__name__)


def init(name, pk):
    key = name + ':' + pk
    obj = tcp.Connection()
    db.setdefault(key, default=dict(state=obj.fsm.states.default()))
    obj.state = obj.fsm.states(db[key]['state'])
    return obj


def update(name, pk, state):
    key = name + ':' + pk
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


@app.route('/connections/<uuid>.png')
def state_as_png(uuid):
    obj = init('connections', uuid)
    return send_file(io.BytesIO(render(obj.fsm, obj.state)),
                     attachment_filename=str(obj.state).lower()+'.png',
                     mimetype='image/png')


@app.route('/connections/<uuid>.json')
def state_as_json(uuid):
    obj = init('connections', uuid)
    events = []
    for edge in obj.fsm.edges:
        state0, _, event = edge
        if state0 == obj.state:
            events.append(dict(name=event.name, url=url_for('put', uuid=uuid, event=event.name)))
    return jsonify(dict(
        state=obj.state.name,
        image_url=url_for('state_as_png', uuid=uuid),
        events=events))


@app.route('/connections/<uuid>/<event>', methods=['PUT'])
def put(uuid, event):
    obj = init('connections', uuid)
    if obj.fsm.move(obj, obj.fsm.events[event]):
        state1 = obj.state
        update('connections', uuid, state1)
        events = []
        for edge in obj.fsm.edges:
            state0, _, event = edge
            if state0 == state1:
                events.append(dict(name=event.name, url=url_for('put', uuid=uuid, event=event.name)))
        return jsonify(dict(
            state=state1.name,
            image_url=url_for('state_as_png', uuid=uuid),
            events=events))
    resp = jsonify({})
    resp.status_code = 409
    return resp


@app.route('/connections/<uuid>')
def get(uuid):
    obj = init('connections', uuid)
    return render_template('state.html', fsm=obj.fsm, state=obj.state, uuid=uuid)


@app.route('/connections/', methods=['POST'])
@app.route('/')
def post():
    uuid4 = uuid.uuid4()
    obj = init('connections', uuid)
    return redirect(url_for('get', uuid=uuid4))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    with closing(db):
        app.run(debug=True, threaded=True)
