import csv
import timeit
from BTrees._OOBTree import OOBTree


def load_data(filename: str):
    """Завантажує дані з CSV-файлу та повертає список словників."""
    with open(filename, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        data = list(reader)
    return data


def add_item_to_tree(tree: OOBTree, item: dict):
    """
    Додає товар у OOBTree, де ключем є ціна (Price),
    а значенням – список товарів із такою ціною.
    """
    # Перетворюємо ціну до числового формату
    price = float(item["Price"])
    if price in tree:
        tree[price].append(item)
    else:
        tree[price] = [item]


def add_item_to_dict(d: dict, item: dict):
    """
    Додає товар у стандартний словник, де ключем є ID товару,
    а значенням – словник із атрибутами товару.
    """
    d[item["ID"]] = item


def range_query_tree(tree: OOBTree, low: float, high: float):
    """
    Повертає список товарів з OOBTree, ціна яких знаходиться у діапазоні [low, high].
    Використовується метод items(min, max) для швидкого доступу.
    """
    results = []
    for price, items in tree.items(low, high):
        results.extend(items)
    return results


def range_query_dict(d: dict, low: float, high: float):
    """
    Повертає список товарів зі словника, ціна яких знаходиться у діапазоні [low, high].
    Для цього здійснюється лінійний пошук.
    """
    results = []
    for item in d.values():
        p = float(item["Price"])
        if low <= p <= high:
            results.append(item)
    return results


def main():
    # Завантаження даних з CSV-файлу
    data = load_data("generated_items_data.csv")

    # Ініціалізація структур даних
    tree = OOBTree()
    d = {}

    # Додавання даних у обидві структури
    for item in data:
        add_item_to_tree(tree, item)
        add_item_to_dict(d, item)

    # Параметри діапазонного запиту (наприклад, знайти товари з ціною від 10 до 20)
    low_price = 10.0
    high_price = 20.0

    # Виконання 100 діапазонних запитів та вимірювання часу для OOBTree
    tree_time = timeit.timeit(
        lambda: range_query_tree(tree, low_price, high_price), number=100
    )

    # Виконання 100 діапазонних запитів та вимірювання часу для dict
    dict_time = timeit.timeit(
        lambda: range_query_dict(d, low_price, high_price), number=100
    )

    print("Total range_query time for OOBTree: {:.6f} seconds".format(tree_time))
    print("Total range_query time for Dict: {:.6f} seconds".format(dict_time))


if __name__ == "__main__":
    main()
