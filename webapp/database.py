import psycopg2

# DATA BASE
CREATE_REQUESTWORDS_TABLE = (
    "CREATE TABLE IF NOT EXISTS requestWords(id SERIAL PRIMARY KEY, request TEXT);"
)

CREATE_RECIPE_TABLE = """ CREATE TABLE IF NOT EXISTS recipe(request_id INTEGER, recipe_name TEXT UNIQUE, price REAL, 
                            url TEXT,
                            FOREIGN KEY(request_id) REFERENCES requestWords(id) ON DELETE CASCADE);"""

CREATE_INGREDIENTS_TABLE = """ CREATE TABLE IF NOT EXISTS ingredients(id SERIAL PRIMARY KEY, recipe_name TEXT, ingredients_name TEXT, price REAL,
                                FOREIGN KEY(recipe_name) REFERENCES recipe(recipe_name));"""

INSERT_REQUESTWORD_RETURN_ID = "INSERT INTO requestWords (request) VALUES (%s) RETURNING id;"

INSERT_RECIPE = (
    "INSERT INTO recipe(request_id, recipe_name, price, url) VALUES (%s, %s, %s, %s);"
)

INSERT_INGREDIENTS = (
    "INSERT INTO ingredients(recipe_name, ingredients_name, price) VALUES (%s, %s, %s)"
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

SELECT_INGREDIENTS_FROM_INGREDIENTS = (
    "SELECT ingredients_name, price FROM ingredients WHERE recipe_name = (%s)"
)

UPDATE_PRICE = (
    "UPDATE recipe SET price = (%s) WHERE recipe_name = (%s)"
)

class MySQL:
    def __init__(self, host, user, password, port, dbname):
        self.connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            port=port,
            dbname=dbname
        )
        print("[INFO] sql connect")
        self.connection.autocommit = True
        with self.connection.cursor() as cursor:
            cursor.execute(CREATE_REQUESTWORDS_TABLE)
            cursor.execute(CREATE_RECIPE_TABLE)
            cursor.execute(CREATE_INGREDIENTS_TABLE)

    def close(self):
        self.connection.close()

    def get_request_id(self, request_recipe: str):
        with self.connection.cursor() as cursor:
            cursor.execute(SELECT_ID_FROM_REQUESTWORDS, (request_recipe,))
            request_id = cursor.fetchone()
            return request_id if request_id is None else request_id[0]


    def get_recipies(self, recipe_id):
        with self.connection.cursor() as cursor:
            cursor.execute(SELECT_LIST_FROM_RECIPE_ID, (recipe_id,))
            return cursor.fetchall()


    def get_recipe(self, recipe_name):
        with self.connection.cursor() as cursor:
            cursor.execute(SELECT_LIST_FROM_RECIPE_NAME, (recipe_name,))
            return cursor.fetchone()
        

    def get_ingredients(self, recipe_name):
        """
            return: list[name, price]
        """
        with self.connection.cursor() as cursor:
            cursor.execute(SELECT_INGREDIENTS_FROM_INGREDIENTS, (recipe_name, ))
            return cursor.fetchall()


    def insert_request_recipe(self, recipe_name: str):
        with self.connection.cursor() as cursor:
            cursor.execute(INSERT_REQUESTWORD_RETURN_ID, (recipe_name,))
            return cursor.fetchone()[0]


    def insert_recipies(self, recipe_id: int, items: list):
        with self.connection.cursor() as cursor:
            for item in items:
                cursor.execute(INSERT_RECIPE, (recipe_id, item[1], -1, item[0]))
            return


    def insert_igredients(self, recipe_name: str, item: list):
        with self.connection.cursor() as cursor:
            cursor.execute(INSERT_INGREDIENTS, (recipe_name, item[1], item[0]))
            return

    def update_price(self, recipe_name: str, price: int):
        with self.connection.cursor() as cursor:
            cursor.execute(UPDATE_PRICE, (price, recipe_name))
            return
