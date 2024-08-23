from flask import Flask, request, jsonify, g
from dialog_manager import DialogManager

app = Flask(__name__)
dm = None

@app.before_request
def before_request():
    global dm
    if dm is None:
        dm = DialogManager()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('input', '')
    response, buttons = dm.process_input(user_input)
    return jsonify({
        'response': response,
        'buttons': buttons,
        'is_search_result': dm.is_search_result
    })

@app.route('/nodes', methods=['GET'])
def get_all_nodes():
    nodes = dm.kb.get_all_nodes()
    return jsonify(nodes)

@app.route('/node/<int:node_id>', methods=['GET'])
def get_node(node_id):
    node = dm.kb.get_node(node_id)
    if node:
        return jsonify({
            'id': node[0],
            'name': node[1],
            'parent_id': node[2],
            'response': node[3]
        })
    else:
        return jsonify({'error': 'Node not found'}), 404

@app.route('/node/<int:node_id>', methods=['PUT'])
def update_node(node_id):
    new_data = request.json
    success = dm.kb.update_node(node_id, new_data)
    return jsonify({'success': success})

if __name__ == '__main__':
    app.run(debug=True)