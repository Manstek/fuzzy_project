import numpy as np

def process_file(file_path):
    """
    Читает файл и извлекает входные данные для выполнения алгоритма.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = file.readlines()

        # Пример обработки: предполагается, что данные файла идут блоками
        A = list(map(float, data[0].strip().split()))
        B = list(map(float, data[1].strip().split()))
        rules = [line.strip().split() for line in data[2:-2]]
        given = list(map(float, data[-2].strip().split()))
        name = data[-1].strip()

        return A, B, rules, given, name
    except Exception as e:
        raise ValueError(f"Ошибка обработки файла: {e}")


def fuzzify(value, universe):
    """
    Выполняет фазы fuzzification.
    """
    memberships = []
    for i in range(len(universe) - 1):
        if universe[i] <= value <= universe[i + 1]:
            memberships.append((value - universe[i]) / (universe[i + 1] - universe[i]))
        else:
            memberships.append(0)
    return memberships


def apply_rules(A, B, rules, given):
    """
    Применяет заданные правила для расчета нечеткого результата.
    """
    results = []
    for rule in rules:
        try:
            rule_index_A, rule_index_B = int(rule[0]), int(rule[1])
            weight = float(rule[2])
            result = min(A[rule_index_A], B[rule_index_B]) * weight
            results.append(result)
        except Exception as e:
            raise ValueError(f"Ошибка применения правила {rule}: {e}")
    return results


def defuzzify(results, universe):
    """
    Преобразует нечеткий результат в четкий (фаза defuzzification).
    """
    crisp_value = sum(r * u for r, u in zip(results, universe)) / sum(results)
    return crisp_value


def execute_logic(A, B, rules, given, name):
    """
    Основная функция, выполняющая обработку данных, применение правил и возвращающая результат.
    """
    try:
        # Fuzzify входные значения
        A_membership = fuzzify(given[0], A)
        B_membership = fuzzify(given[1], B)

        # Apply rules
        rule_results = apply_rules(A_membership, B_membership, rules, given)

        # Defuzzify the result
        final_result = defuzzify(rule_results, A)

        # Формируем лог результата
        log = f"""
        Нечеткий ввод: {given}
        Универсум A: {A}
        Универсум B: {B}
        Примененные правила: {rules}
        Результат после фаз: {rule_results}
        Окончательный четкий результат: {final_result:.2f}
        """
        return log.strip()
    except Exception as e:
        raise RuntimeError(f"Ошибка выполнения нечеткой логики: {e}")
