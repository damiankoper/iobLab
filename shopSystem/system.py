from Shop import Shop
from Product import Product

shop = Shop()
shop.products.append(Product("Makaron", 20, 5))
shop.products.append(Product("Papier toaletowy", 1000, 10))

print(str(shop))
print(shop.get_total_price())
print(len(shop)) # Liczba produktów czy liczba instancji produktów? Nieścisłość :(

shop.sell("Makaron")
shop.sell("Makaron")
shop.sell("Makaron")

shop.buy("Makaron")
shop.buy("Papier toaletowy")

print(str(shop))
print(shop.get_total_price())

for product in shop:
    print(product.getName())
    product.setPrice(10)

print(str(shop))
