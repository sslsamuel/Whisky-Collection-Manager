import json

class WhiskyManager:
 
    @classmethod
    def load_data(self):
        try:
            with open('whisky.json', 'r') as file:
                self.data = json.load(file)
        except FileNotFoundError:
            self.data = {}
        return self.data
    
    @classmethod
    def save_data(self, data):
        with open('whisky.json', 'w') as file:
            json.dump(data, file, indent=4)

    @classmethod
    def search_bottles(cls, query, collection=False):
        """
        Return list of bottles matching user's query
        """

        # 'collection' can be the actual user's collection or also the wishlist, depending on what is passed through
        if collection != False:
            return [bottle for bottle in collection if query.lower() in bottle["name"].lower()]
        collection = cls.load_data()
        return [bottle for bottle in collection if query.lower() in bottle["name"].lower()]
    
    @classmethod
    def sort_bottles(cls, sort_by, collection=False):
        """
        Sort bottles by a specified key.
        """
        # 'collection' can be the actual user's collection or also the wishlist, depending on what is passed through

        if collection == False:
            collection = cls.load_data()

        # Sort collection
        if sort_by == 'name_asc':
            sorted_collection = sorted(collection, key=lambda b: b['name'].lower())
        elif sort_by == 'name_desc':
            sorted_collection = sorted(collection, key=lambda b: b['name'].lower(), reverse=True)
        elif sort_by == 'price_low_high':
            sorted_collection = sorted(collection, key=lambda b: b['price'])
        elif sort_by == 'price_high_low':
            sorted_collection = sorted(collection, key=lambda b: b['price'], reverse=True)
        elif sort_by == 'age_low_high':
            sorted_collection = sorted(collection, key=lambda b: b['age'])
        elif sort_by == 'age_high_low':
            sorted_collection = sorted(collection, key=lambda b: b['age'], reverse=True)
        elif sort_by == 'abv_low_high':
            sorted_collection = sorted(collection, key=lambda b: b['abv'])
        elif sort_by == 'abv_high_low':
            sorted_collection = sorted(collection, key=lambda b: b['abv'], reverse=True)
        elif sort_by == 'rating_low_high':
            sorted_collection = sorted(collection, key=lambda b: b['rating'])
        elif sort_by == 'rating_high_low':
            sorted_collection = sorted(collection, key=lambda b: b['rating'], reverse=True)
        else:
            sorted_collection = collection  # Default to no sorting

        return sorted_collection

           

    @classmethod
    def filter_bottles(cls, min_price, max_price, min_age, max_age, distilleries, collection=False):
        """
        Filter bottles by specified criteria.
        """
        if collection == False:
            collection = cls.load_data()

        filtered_collection = collection

        if min_price is not None:
            filtered_collection = [b for b in filtered_collection if b['price'] >= min_price]
        if max_price is not None:
            filtered_collection = [b for b in filtered_collection if b['price'] <= max_price]
        if min_age is not None:
            filtered_collection = [b for b in filtered_collection if b['age'] >= min_age]
        if max_age is not None:
            filtered_collection = [b for b in filtered_collection if b['age'] <= max_age]
        if distilleries:
            filtered_collection = [b for b in filtered_collection if b['distillery'] in distilleries]

        return filtered_collection
    
    @classmethod
    def all_distilleries(cls):
        """
        Returns all distilleries in whisky.json
        """
        data = cls.load_data()
        return sorted({b['distillery'] for b in data}) # {} creates a set to avoid duplicated
        
class User:

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.collection = []
        self.wishlist = []
        self.add_user()

    def add_user(self):
        """Save a user to the database (users.json)"""
        try:
            with open('users.json', 'r') as file:
                users_data = json.load(file)
        except FileNotFoundError:
            users_data = []

        # Append new user data
        if not any(user['username'] == self.username for user in users_data): # Check if the user does not exist
            user = {"username": self.username, "password": self.password, "collection": self.collection, "wishlist": self.wishlist}      
            users_data.append(user)
            User.save_to_json(users_data)

    @staticmethod
    def save_to_json(users_data):
            """Save the users data to the users.json file"""
            with open('users.json', 'w') as file:
                json.dump(users_data, file, indent=4)

    @classmethod
    def amend_collection(cls, user, bottle, add):
        """
        Amend a user's collection.
        """
        # Add the bottle to the collection
        if add == True and type(add) == bool: # if rating is 1, avoid this because 1 is True
            user["collection"].append(bottle)


        # Remove the bottle from the collection
        elif add == False: 
            user["collection"] = [b for b in user["collection"] if b["id"] != bottle["id"]]

        # Edit a bottle's note
        elif type(add) == str:
            for b in user["collection"]:
                if b["id"] == bottle["id"]:
                    b["note"] = add
                    break

        # Edit a bottle's rating
        elif type(add) == int:
            for b in user["collection"]:
                if b["id"] == bottle["id"]:
                    b["rating"] = add
                    break

        users_data = cls.load_users()  # Load the users data
        for user_data in users_data:
            if user_data['username'] == user["username"]:
                user_data['collection'] = user["collection"]  # Update the user's collection
        cls.save_to_json(users_data)  # Save the updated data

    @classmethod
    def amend_wishlist(cls, user, bottle, add):
        """
        Amend a user's wishlist.
        """
        # Add the bottle to the wishlist
        if add == True:
            user["wishlist"].append(bottle)

        # Remove the bottle from the wishlist
        elif add == False: 
            user["wishlist"] = [b for b in user["wishlist"] if b["id"] != bottle["id"]]

        # Edit a bottle's note
        elif type(add) == str:
            for b in user["wishlist"]:
                if b["id"] == bottle["id"]:
                    b["note"] = add
                    break

        users_data = cls.load_users()  # Load the users data
        for user_data in users_data:
            if user_data['username'] == user["username"]:
                user_data['wishlist'] = user["wishlist"]  # Update the user's wishlist
        cls.save_to_json(users_data)  # Save the updated data

    @staticmethod
    def load_users():
        """Load all users from the users.json file"""
        try:
            with open('users.json', 'r') as file:
                users_data = json.load(file)
            return users_data
        except FileNotFoundError:
            return []

  
class Bottle(WhiskyManager):

    def __init__(self, name, distillery, bottle_type, age, abv, price, image_url):

        bottles = WhiskyManager.load_data()
        # Generate the next available ID
        next_id = max([bottle['id'] for bottle in bottles], default=0) + 1

        # Create a new bottle dictionary
        new_bottle = {
            'id': next_id,
            'name': name,
            'distillery': distillery,
            'type': bottle_type,
            'age': age,
            'abv': abv,
            'price': price,
            'image_url': image_url,
            'note': '',
            'rating': 0
        }
        bottles.append(new_bottle)
        super().save_data(bottles)

        


    @classmethod
    def get_bottle_by_id(cls, bottle_id):
        """
        Retrieve a bottle by its ID.
        """
        data = cls.load_data()
        return next((bottle for bottle in data if bottle['id'] == bottle_id), None)






