from collections import deque, defaultdict
from typing import Dict, List, Tuple


# Побудова графа як вкладених словників: graph[u][v] = capacity
def build_graph() -> Dict[str, Dict[str, int]]:
    graph = {}

    # Допоміжні функції для додавання ребер (як пряме, так і зворотне)
    def add_edge(u: str, v: str, capacity: int):
        if u not in graph:
            graph[u] = {}
        if v not in graph[u]:
            graph[u][v] = 0
        graph[u][v] += capacity
        # Додаємо зворотню дугу з нульовою пропускною здатністю
        if v not in graph:
            graph[v] = {}
        if u not in graph[v]:
            graph[v][u] = 0

    # Визначені вузли
    source = "Source"
    sink = "Sink"
    # Терминали
    terminals = {
        "Terminal 1": 60,
        "Terminal 2": 55,
    }  # сумарні вихідні пропускні здатності
    # Склади
    warehouses = ["Sklad 1", "Sklad 2", "Sklad 3", "Sklad 4"]
    # Магазини
    shops = [
        "Shop 1",
        "Shop 2",
        "Shop 3",
        "Shop 4",
        "Shop 5",
        "Shop 6",
        "Shop 7",
        "Shop 8",
        "Shop 9",
        "Shop 10",
        "Shop 11",
        "Shop 12",
        "Shop 13",
        "Shop 14",
    ]

    # З'єднуємо Source -> Terminal
    for t, cap in terminals.items():
        add_edge(source, t, cap)

    # З'єднуємо Terminal -> Warehouse за заданими даними
    add_edge("Terminal 1", "Sklad 1", 25)
    add_edge("Terminal 1", "Sklad 2", 20)
    add_edge("Terminal 1", "Sklad 3", 15)
    add_edge("Terminal 2", "Sklad 3", 15)
    add_edge("Terminal 2", "Sklad 4", 30)
    add_edge("Terminal 2", "Sklad 2", 10)

    # З'єднуємо Warehouse -> Shop
    add_edge("Sklad 1", "Shop 1", 15)
    add_edge("Sklad 1", "Shop 2", 10)
    add_edge("Sklad 1", "Shop 3", 20)
    add_edge("Sklad 2", "Shop 4", 15)
    add_edge("Sklad 2", "Shop 5", 10)
    add_edge("Sklad 2", "Shop 6", 25)
    add_edge("Sklad 3", "Shop 7", 20)
    add_edge("Sklad 3", "Shop 8", 15)
    add_edge("Sklad 3", "Shop 9", 10)
    add_edge("Sklad 4", "Shop 10", 20)
    add_edge("Sklad 4", "Shop 11", 10)
    add_edge("Sklad 4", "Shop 12", 15)
    add_edge("Sklad 4", "Shop 13", 5)
    add_edge("Sklad 4", "Shop 14", 10)

    # З'єднуємо Shop -> Sink. Кожне ребро встановлюємо з великою пропускною здатністю.
    for shop in shops:
        add_edge(shop, sink, 10**9)

    return graph


# Реалізація алгоритму Едмондса-Карпа
def edmonds_karp(
    graph: Dict[str, Dict[str, int]], source: str, sink: str
) -> Tuple[int, Dict[str, Dict[str, int]]]:
    # Ініціалізуємо загальний потік та структуру для збереження потоку по ребрах
    max_flow = 0
    flow = {u: {v: 0 for v in graph[u]} for u in graph}

    while True:
        # BFS для знаходження найкоротшого збільшувального шляху в залишковому графі
        parent = {node: None for node in graph}
        parent[source] = source
        q = deque([source])
        # Запам'ятовуємо мінімальну залишкову здатність уздовж шляху
        path_capacity = {node: 0 for node in graph}
        path_capacity[source] = float("inf")

        found_path = False

        while q:
            u = q.popleft()
            for v in graph[u]:
                # Розрахунок залишкової здатності ребра u->v
                residual = graph[u][v] - flow[u][v]
                if residual > 0 and parent[v] is None:
                    parent[v] = u
                    path_capacity[v] = min(path_capacity[u], residual)
                    if v == sink:
                        found_path = True
                        break
                    q.append(v)
            if found_path:
                break

        if not found_path:
            break  # якщо немає додаткового шляху, алгоритм завершується

        augment = path_capacity[sink]
        max_flow += augment

        # Оновлюємо потоки уздовж знайденого шляху
        v = sink
        while v != source:
            u = parent[v]
            flow[u][v] += augment
            flow[v][u] -= augment  # зворотний потік
            v = u

    return max_flow, flow


# Розкладання потоку для отримання інформації про потоки між терміналами та магазинами
def decompose_flows(flow: Dict[str, Dict[str, int]]) -> List[Tuple[str, str, int]]:
    # Ми знаємо, що структура мережі така:
    # Source -> Terminal -> Warehouse -> Shop
    # Для кожного складу (warehouse) ми розподіляємо потік зі входу від терміналів на виходи до магазинів.
    # Спершу об'єднаємо потоки, що надходять до кожного складу з терміналів.
    terminal_to_warehouse = defaultdict(lambda: defaultdict(int))
    for terminal in ["Terminal 1", "Terminal 2"]:
        if terminal in flow:
            for wh in flow[terminal]:
                # Беремо тільки позитивний потік, який був направлений до складів
                if wh.startswith("Sklad") and flow[terminal][wh] > 0:
                    terminal_to_warehouse[wh][terminal] += flow[terminal][wh]

    # Тепер для кожного складу, перерахуємо потік до магазинів із цього складу
    shipments = []  # список кортежів (Terminal, Shop, flow)
    for wh in terminal_to_warehouse:
        # Скопіюємо отримані потоки з терміналів до цього складу
        available = dict(terminal_to_warehouse[wh])
        # Переглянемо вихідні ребра зі складу, які ведуть до магазинів
        if wh in flow:
            for shop in flow[wh]:
                if shop.startswith("Shop") and flow[wh][shop] > 0:
                    remaining = flow[wh][shop]
                    # Розподіляємо потік "remaining" між терміналами, з яких прийшов потік до складу
                    for terminal in available:
                        if remaining <= 0:
                            break
                        if available[terminal] > 0:
                            delta = min(available[terminal], remaining)
                            shipments.append((terminal, shop, delta))
                            available[terminal] -= delta
                            remaining -= delta
    return shipments


def print_shipments_table(shipments: List[Tuple[str, str, int]]):
    # Обчислюємо сумарні потоки між кожним терміналом і магазином
    table = defaultdict(lambda: defaultdict(int))
    for term, shop, amt in shipments:
        table[term][shop] += amt
    print("Термінал\tМагазин\tФактичний Потік (одиниць)")
    for terminal in sorted(table.keys()):
        for shop in sorted(table[terminal].keys()):
            print(f"{terminal}\t{shop}\t{table[terminal][shop]}")


def main():
    graph = build_graph()
    source = "Source"
    sink = "Sink"
    max_flow, flows = edmonds_karp(graph, source, sink)
    print(f"Максимальний потік: {max_flow} одиниць\n")

    # Розкладання потоків для отримання інформації по маршрутах від терміналів до магазинів
    shipments = decompose_flows(flows)
    print_shipments_table(shipments)

    # Аналіз результатів (відповіді на запитання)
    # 1. Які термінали забезпечують найбільший потік товарів до магазинів?
    terminal_totals = defaultdict(int)
    for term, shop, amt in shipments:
        terminal_totals[term] += amt
    print("\nЗагальний потік за терміналами:")
    for terminal, total in terminal_totals.items():
        print(f"{terminal}: {total} одиниць")

    # 2. Які маршрути мають найменшу пропускну здатність?
    # У нашій мережі найменші пропускні здатності мають ребра:
    # Terminal 2 -> Sklad 2 (10) та Sklad 4 -> Shop 13 (5)
    print(
        "\nДо уваги: Найменші пропускні здатності спостерігаються на маршрутах Terminal 2 -> Sklad 2 (10 одиниць) та Sklad 4 -> Shop 13 (5 одиниць)."
    )

    # 3. Які магазини отримали найменше товарів?
    shop_totals = defaultdict(int)
    for _, shop, amt in shipments:
        shop_totals[shop] += amt
    min_shop = min(shop_totals.items(), key=lambda x: x[1])
    print(
        f"\nМагазин з найменшим отриманим потоком: {min_shop[0]} отримав {min_shop[1]} одиниць."
    )
    print(
        "Збільшення пропускної здатності на вузьких маршрутах (наприклад, Sklad 4 -> Shop 13) може покращити постачання цього магазину."
    )

    # 4. Чи є вузькі місця, які можна усунути?
    print(
        "\nАналіз мережі вказує, що вузькими місцями є маршрути з низькою пропускною здатністю, зокрема Terminal 2 -> Sklad 2 та Sklad 4 -> Shop 13."
    )
    print(
        "Їхнє покращення може підвищити загальний потік та ефективність логістичної мережі."
    )


if __name__ == "__main__":
    main()
