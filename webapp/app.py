import sys
from flask import Flask, render_template, url_for, request, redirect
import scrap_functions as functions
import psycopg2

# config DATA BASE
host = 'postgres'
user = 'postgres'
password = '2328'
db_name = 'postgres'
port = 5432

# DATA BASE
CREATE_REQUESTWORDS_TABLE = (
    "CREATE TABLE IF NOT EXISTS requestWords(id SERIAL PRIMARY KEY, request TEXT);"
)

CREATE_RECIPE_TABLE = """ CREATE TABLE IF NOT EXISTS recipe(request_id INTEGER, recipe_name TEXT, price REAL, 
                            url TEXT, FOREIGN KEY(request_id) REFERENCES requestWords(id) ON DELETE CASCADE);"""

INSERT_REQUESTWORD_RETURN_ID = "INSERT INTO requestWords (request) VALUES (%s) RETURNING id;"

INSERT_RECIPE = (
    "INSERT INTO recipe(request_id, recipe_name, price, url) VALUES (%s, %s, %s, %s);"
)

SELECT_ID_FROM_REQUESTWORDS = (
    "SELECT id FROM requestWords WHERE request = (%s)"
)

SELECT_LIST_FROM_RECIPE_ID = (
    "SELECT url, recipe_name FROM recipe WHERE request_id = (%s)"
)

SELECT_LIST_FROM_RECIPE_NAME = (
    "SELECT url, price FROM recipe WHERE recipe_name = (%s)"
)

UPDATE_PRICE = (
    "UPDATE recipe SET price = (%s) WHERE recipe_name = (%s)"
)


def get_request_id(request_recipe: str):
    with connection.cursor() as cursor:
        cursor.execute(SELECT_ID_FROM_REQUESTWORDS, (request_recipe,))
        request_id = cursor.fetchone()
        return request_id if request_id is None else request_id[0]


def get_recipies(recipe_id):
    with connection.cursor() as cursor:
        cursor.execute(SELECT_LIST_FROM_RECIPE_ID, (recipe_id,))
        return cursor.fetchall()


def get_recipe(recipe_name):
    with connection.cursor() as cursor:
        cursor.execute(SELECT_LIST_FROM_RECIPE_NAME, (recipe_name,))
        return cursor.fetchone()


def insert_request_recipe(recipe_name: str):
    with connection.cursor() as cursor:
        cursor.execute(INSERT_REQUESTWORD_RETURN_ID, (recipe_name,))
        return cursor.fetchone()[0]


def insert_recipies(recipe_id: int, items: list):
    with connection.cursor() as cursor:
        for item in items:
            cursor.execute(INSERT_RECIPE, (recipe_id, item[1], -1, item[0]))
        return


def update_price(recipe_name: str, price: int):
    with connection.cursor() as cursor:
        cursor.execute(UPDATE_PRICE, (price, recipe_name))
        return


# Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'xd'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/choose', methods=["POST"])
def choose():
    if request.method == 'POST':
        print(request.form)
        print("[INFO] GET A POST METHOD")
        recipe_name = request.form.get('recipe_name')
        if recipe_name:
            print("[INFO] GET recipe_name")
            recipe = get_recipe(recipe_name)
            if recipe is None:
                print("[INFO] wrong recipe_name")
                return redirect(url_for('suka_blyad', recipe_name="Wrong name", price=-1))
            elif recipe[1] == -1:
                print("[INFO] update price of recipe")
                price = 0
                ingredients = functions.get_recipies_by_url(recipe[0])
                functions.make_readable(ingredients)
                for ingredient in ingredients:
                    price += functions.get_price_of_ingredient(ingredient)[0]
                update_price(recipe_name, price)
                print(f'[INFO] price fo {recipe_name} updated')
            else:
                price = recipe[1]
                print('[INFO] get price from table')
            return redirect(url_for('suka_blyad', recipe_name=recipe_name, price=price))
        request_name = request.form['request_name']
        print(f"[INFO] get a request_name: {request_name}")
        request_name = functions.standardize(request_name)
        print(f"[INFO] standard turned into: {request_name}")
        items = []
        # request_id = get_request_id(request_name)
        request_id = None
        if request_id is None:
            request_id = insert_request_recipe(request_name)
            items = functions.get_recipe_by_request(request_name)
            if items:
                print('[INFO] insert recipies into table')
                insert_recipies(request_id, items)
            else:
                print('[INFO] 0 found recipies')
                return redirect(url_for('404.html'))
        else:
            print("[INFO] get content from tables to /choose.html")
            items = get_recipies(request_id)
        return render_template('choose.html', items=list(enumerate(items)))


@app.route('/choose/<recipe_name>/<price>', methods=["GET"])
def suka_blyad(recipe_name, price):
    return render_template('item.html', recipe_name=recipe_name, price=price)


if __name__ == '__main__':
    try:
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            port=port,
            dbname=db_name
        )
        print("[INFO] sql connect")
        connection.autocommit = True
        with connection.cursor() as cursor:
            cursor.execute(CREATE_REQUESTWORDS_TABLE)
            cursor.execute(CREATE_RECIPE_TABLE)
        app.run(host='0.0.0.0', port='8000', debug=True)
    except Exception as ex:
        print("[INFO] some ex")
        print("[ERROR]", ex, file=sys.stderr)
    finally:
        if connection:
            connection.close()
            print("[INFO] sql connect closed")
