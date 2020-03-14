class Product:
    def __init__(self, name, price, quantity):
        self.price = price
        self.name = name
        self.quantity = quantity

    def getName(self):
        return self.name
    def setName(self, name):
        self.name = name
    def getPrice(self):
        return self.price
    def setPrice(self, price):
        self.price = price
    def getQuantity(self):
        return self.quantity
    def setQuantity(self, quantity):
        self.quantity = quantity

    def __str__(self):
        return "{name: \""+self.name+"\", quantity: "+str(self.quantity)+", price: "+str(self.price)+"}"
