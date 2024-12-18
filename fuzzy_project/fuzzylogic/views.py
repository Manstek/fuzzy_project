# views.py
from django.shortcuts import render
import pandas as pd
import tempfile


def process_file(filename):
    # Матрицы для хранения данных
    A1 = {}
    A2 = {}
    A3 = {}
    B = {}
    rules = []
    given = []
    given1 = []

    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    current_set_name = None
    current_set_values = []
    current_set_length = 0
    set = 0
    a1_name = ''
    a2_name = ''
    a3_name = ''
    b_name = ''

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if not line:
            i += 1
            continue

        elif line.startswith("Множество определения"):
            if current_set_name:
                if set == 1:
                    A1[current_set_name] = current_set_values + [0] * (
                        current_set_length - len(current_set_values))
                elif set == 2:
                    A2[current_set_name] = current_set_values + [0] * (
                        current_set_length - len(current_set_values))
                elif set == 3:
                    A3[current_set_name] = current_set_values + [0] * (
                        current_set_length - len(current_set_values))
                elif set == 4:
                    B[current_set_name] = current_set_values + [0] * (
                        current_set_length - len(current_set_values))

            set += 1

            # Начинаем обработку нового множества
            parts = line.split()
            current_set_name = parts[-1]
            if set == 1:
                a1_name = current_set_name
            elif set == 2:
                a2_name = current_set_name
            elif set == 3:
                a3_name = current_set_name
            elif set == 4:
                b_name = current_set_name
            current_set_values = []
            current_set_length = 0

        elif line.startswith("0") or line.startswith("-") or line[0].isdigit():
            # Считываем числовые значения множества
            values = list(map(float, line.split()))
            if current_set_length == 0:
                current_set_length = len(values)
            current_set_values.extend(values)

        elif line.startswith("Нечеткое множество"):
            # Считываем название нечеткого множества
            parts = line.split()
            fuzzy_set_name = parts[-1]
            i += 1  # Переходим к следующей строке, содержащей значения
            if i < len(lines):
                fuzzy_set_values = list(map(float, lines[i].strip().split()))
                fuzzy_set_values.extend([0] * (current_set_length - len(
                    fuzzy_set_values)))
                if set == 1:
                    A1[fuzzy_set_name] = fuzzy_set_values
                elif set == 2:
                    A2[fuzzy_set_name] = fuzzy_set_values
                elif set == 3:
                    A3[fuzzy_set_name] = fuzzy_set_values
                elif set == 4:
                    B[fuzzy_set_name] = fuzzy_set_values

        elif line.startswith("Если"):
            # Обработка правила
            parts = line.split()
            antecedent1 = parts[2]
            antecedent2 = parts[5]
            antecedent3 = parts[8]
            consequent = parts[-1]
            rules.append((antecedent1, antecedent2, antecedent3, consequent))

        elif line.startswith("Пусть"):
            # Обработка начального состояния
            i += 1
            line = lines[i].strip()
            values = list(map(float, line.split()))
            given1.extend(values)
            given.append(given1)
            given1 = []

        i += 1

    # Обрабатываем последнее множество
    if current_set_name:
        if set == 1:
            A1[current_set_name] = current_set_values + [0] * (
                current_set_length - len(current_set_values))
        elif set == 2:
            A2[current_set_name] = current_set_values + [0] * (
                current_set_length - len(current_set_values))
        elif set == 3:
            A3[current_set_name] = current_set_values + [0] * (
                current_set_length - len(current_set_values))
        elif set == 4:
            B[current_set_name] = current_set_values + [0] * (
                current_set_length - len(current_set_values))

    A1 = pd.DataFrame(A1)
    A2 = pd.DataFrame(A2)
    A3 = pd.DataFrame(A3)
    B = pd.DataFrame(B)

    A = []
    A.append([])  # Для совместимости с индексами
    A.append(A1)
    A.append(A2)
    A.append(A3)

    name = []
    name.append(b_name)
    name.append(a1_name)
    name.append(a2_name)
    name.append(a3_name)

    rules = pd.DataFrame(rules, columns=[a1_name, a2_name, a3_name, b_name])

    return A, B, rules, given, name


def maxmin(a, b):
    row = []
    for i in range(len(a)):
        row.append(min(a[i], b[i]))
    return max(row)


def get_levels_of_truth(A, B, rules, given, name):
    levels_of_truth = []
    for i in range(len(rules[name[0]])):
        a1 = A[1][rules[name[1]][i]]
        a2 = A[2][rules[name[2]][i]]
        a3 = A[3][rules[name[3]][i]]

        level_a1 = maxmin(a1, given[0])
        level_a2 = maxmin(a2, given[1])
        level_a3 = maxmin(a3, given[2])

        level = min(level_a1, level_a2, level_a3)
        levels_of_truth.append(level)
    return levels_of_truth


def get_outputs(B, rules, name, levels_of_truth):
    outputs = []
    for r in range(len(rules[name[0]])):
        output = []
        for i in range(len(B[rules[name[0]][r]])):
            output.append(min(B[rules[name[0]][r]][i], levels_of_truth[r]))
        outputs.append(output)
    return outputs


def outputs_aggregation(outputs):
    aggregation = []
    for i in range(len(outputs[0])):
        max_output = outputs[0][i]
        for output in outputs:
            max_output = max(max_output, output[i])
        aggregation.append(max_output)
    return aggregation


def defuzzification(A, B, name, given, aggregation):
    result = []
    for j in range(len(name) - 1):
        sum_1 = 0
        sum_2 = 0
        for i in range(len(given)):
            sum_1 += given[j][i] * A[j+1][name[j+1]][i]
            sum_2 += given[j][i]
        mid = sum_1/sum_2
        result.append(f"Четкое значение входа {name[j+1]}: {round(mid)}")

    sum_1 = 0
    sum_2 = 0
    for i in range(len(aggregation)):
        sum_1 += aggregation[i] * B[name[0]][i]
        sum_2 += aggregation[i]
    mid = sum_1/sum_2
    result.append(f"Четкое значение выхода {name[0]}: {round(mid)}")
    return result


def execute_logic(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('data_file')
        if uploaded_file:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                for chunk in uploaded_file.chunks():
                    temp_file.write(chunk)
                temp_file_path = temp_file.name

            A, B, rules, given, name = process_file(temp_file_path)
            # Получение уровней истинности предпосылок
            levels_of_truth = get_levels_of_truth(A, B, rules, given, name)
            outputs = get_outputs(B, rules, name, levels_of_truth)
            for i in range(len(outputs)):
                for j in range(len(outputs[i])):
                    outputs[i][j] = float(outputs[i][j])
            aggregation = outputs_aggregation(outputs)
            defuz = defuzzification(A, B, name, given, aggregation)

            return render(request, 'fuzzy_logic/result.html', {
                'A1': A[1].to_html(),
                'A2': A[2].to_html(),
                'A3': A[3].to_html(),
                'B': B.to_html(),
                'rules': rules.to_html(classes='table table-bordered'),
                'given': given,
                'levels_of_truth': [float(el) for el in levels_of_truth],
                'names': name,
                'outputs': outputs,
                'aggregation': aggregation,
                'defuzzification': defuz,
            })

    return render(request, 'fuzzy_logic/index.html')
