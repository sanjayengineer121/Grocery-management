from flask import Flask, render_template,jsonify,request,redirect,url_for
import json
from tabulate import tabulate

app = Flask(__name__)


def load_data():
    try:
        with open('inventory.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {"inventry": {"item": []}}

data = load_data()
print(data)

def save_data(data):
    with open('inventory.json', 'w') as file:
        json.dump(data, file, indent=2)

data = load_data()

@app.route('/')
def home():
    l=len(data['inventry']['item'])
    lastitem=data['inventry']['item'][-1]['item']
    inventory_data = load_data()['inventry']['item']
    
    # Calculate the total quantity
    total_quantity = sum(item['Quantity'] for item in inventory_data)

    display_data_in_terminal()

    return render_template('index.html',no_of_iem=l,lastitem=lastitem,total_quantity=total_quantity)

@app.route('/table')
def table():
    inventory_data = load_data()['inventry']['item']
    return render_template('table.html', inventory_data=inventory_data)

@app.route('/add_item')
def add():

    return render_template('add_item.html')

def display_data_in_terminal():
    table_data = []
    for person in data['inventry']['item']:
        table_data.append([person['id'], person['item'], person['Quantity'], person['price']])

    headers = ["ID", "item", "Quantity", "Price"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))


@app.route('/api/inventry/item', methods=['GET'])
def get_persons():
    return jsonify(data['inventry']['item'])

@app.route('/api/inventry/item/<int:item_id>', methods=['GET'])
def get_person(item_id):
    data1 = next((item for item in data['inventry']['item'] if item['id'] == item_id), None)
    if data1 is None:
        return jsonify({'error': 'Person not found'}), 404
    return jsonify({'person': data1})

@app.route('/api/inventry/item', methods=['POST'])
def create_person():
    data_from_request = request.get_json()
    new_item = {
        'id': len(data['inventry']['item']) + 1,
        'item': data_from_request['item'],
        'Quantity': data_from_request['Quantity'],
        'price': data_from_request['price']
    }
    data['inventry']['item'].append(new_item)
    
    # Save updated data to the JSON file
    save_data(data)
    
    return jsonify({'message': 'item added Successfully', 'inventry': new_item}), 201

@app.route("/additem", methods=["POST"])
def additem():
    item_name = request.form.get("item")
    print(item_name)
    quantity = request.form.get("qty")
    print(quantity)
    price = request.form.get("price")
    print()
    
    import requests

    url = "http://127.0.0.1:5000/api/inventry/item"
    data = {
        "item":item_name ,
        "Quantity":int(quantity),
        "price": int(price)
    }

    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=data, headers=headers)

    print("Status Code:", response.status_code)
    print("Response Content:")
    print(response.json())

    

    return redirect(url_for('home'))

@app.route('/api/inventry/item/<int:ite>', methods=['PUT'])
def update_person(person_id):
    person = next((person for person in data['books']['person'] if person['id'] == person_id), None)
    if person is None:
        return jsonify({'error': 'Person not found'}), 404

    data_from_request = request.get_json()
    person['name'] = data_from_request.get('name', person['name'])
    person['age'] = data_from_request.get('age', person['age'])
    person['gender'] = data_from_request.get('gender', person['gender'])

    # Save updated data to the JSON file
    save_data(data)

    return jsonify({'message': 'Person updated', 'person': person})

@app.route('/api/inventry/item/<int:item_id>', methods=['DELETE'])
def delete_person(item_id):
    data1 = next((item for item in data['inventry']['item'] if item['id'] == item_id), None)
    if data1 is None:
        return jsonify({'error': 'item not found'}), 404

    data['inventry']['item'].remove(data1)

    # Save updated data to the JSON file
    save_data(data)

    return jsonify({'message': 'item deleted', 'item': data})

if __name__ == '__main__':
    app.run(debug=True)
