class Shop:
    def __init__(self):
        self.products = []

    def get_total_price(self):
        price = 0
        for product in self.products:
            price += product.price * product.quantity
        return price

    def findByName(self, name):
        for product in self.products:
            if product.name == name:
                return product
        return None

    def buy(self, name):
        product = self.findByName(name)
        if product is not None:
            product.quantity = product.quantity-1
            return True
        return False 
        
    def sell(self, name):
        product = self.findByName(name)
        if product is not None:
            product.quantity = product.quantity+1
            return True
        return False

    def __str__(self):
        string = "["
        string += ", ".join(map(lambda p: str(p), self.products))
        string += "]"
        return string

    def __len__(self):
        return len(self.products)

    def __iter__(self):
        return self.products.__iter__()
    
    def __next__(self):
        pass #works without next