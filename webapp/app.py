import sys
from flask import Flask, render_template, url_for, request, redirect
import scrap_functions as functions
import database
import config

# Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'xd'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/choose', methods=["POST"])
def choose():
    if request.method == 'POST':
        print("[INFO] GET A POST METHOD")
        print(request.form)

        recipe_name = request.form.get('recipe_name')
        if recipe_name:
            return price(recipe_name)
            
        request_name = request.form['request_name']
        print(f"[INFO] get a request_name: {request_name}")
        request_name = functions.standardize(request_name)
        print(f"[INFO] standard turned into: {request_name}")

        items = []
        request_id = db_t.get_request_id(request_name)

        if request_id is None:
            request_id = db_t.insert_request_recipe(request_name)
            items = functions.get_recipe_by_request(request_name)
            if items is None:
                print('[INFO] 0 found recipies')
                return redirect(url_for('404.html'))
            
            print('[INFO] insert recipies into table')
            db_t.insert_recipies(request_id, items)

        else:
            print("[INFO] get content from tables to /choose.html")
            items = db_t.get_recipies(request_id)

        return render_template('choose.html', items=items)


@app.route('/choose/<recipe_name>')
def price(recipe_name):
    print("[INFO] GET recipe_name")
    recipe = db_t.get_recipe(recipe_name)
    items = []
    price = -1
    ingredients = []
    url = ''

    if recipe:
        url = functions.recipe_site + recipe[0]

        if recipe[1] == -1:
            tmp = []
            # recipe == [url, price, ingredients[STRING]]
            print("[INFO] update price of recipe")
            price = 0
            ingredients = functions.get_recipies_by_url(recipe[0])
            tmp = ingredients
            ingredients = functions.make_readable(ingredients)          
            print("[INFO] scraping ingredients")

            for ingredient in ingredients:
                items.append(functions.get_price_of_ingredient(ingredient))
                price += items[-1][0]
                tmp.append('{}, цена: {}'.format(items[-1][1], items[-1][0]))
                db_t.insert_igredients(recipe_name, items[-1])
            
            ingredients = tmp
            db_t.update_price(recipe_name, price)
            print(f'[INFO] price for {recipe_name} updated')
        else:
            price = recipe[1]
            items = db_t.get_ingredients(recipe_name)
            for item in items:
                ingredients.append('{}, цена: {}'.format(item[0], item[1]))
            print('[INFO] get price from table')
    else:
        print('[INFO] WRONG NAME!')
    return render_template('item.html', url=url, recipe_name=recipe_name, price=price, ingredients=ingredients)


if __name__ == '__main__':
    try:
        db_t = database.MySQL(
            host=config.db_host,
            user=config.user,
            password=config.password,
            port=config.db_port,
            dbname=config.db_name
        )
        app.run(host=config.app_host, port=config.app_port, debug=True)
    except Exception as ex:
        print("[INFO] some ex", file=sys.stderr)
        print("[ERROR]", ex, file=sys.stderr)
    finally:
        db_t.close()
