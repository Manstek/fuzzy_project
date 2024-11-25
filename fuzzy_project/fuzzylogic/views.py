# views.py
from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
import numpy as np

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
    given_set = 0
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
                    A1[current_set_name] = current_set_values + [0] * (current_set_length - len(current_set_values))
                elif set == 2:
                    A2[current_set_name] = current_set_values + [0] * (current_set_length - len(current_set_values))
                elif set == 3:
                    A3[current_set_name] = current_set_values + [0] * (current_set_length - len(current_set_values))
                elif set == 4:
                    B[current_set_name] = current_set_values + [0] * (current_set_length - len(current_set_values))

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
                fuzzy_set_values.extend([0] * (current_set_length - len(fuzzy_set_values)))
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
            A1[current_set_name] = current_set_values + [0] * (current_set_length - len(current_set_values))
        elif set == 2:
            A2[current_set_name] = current_set_values + [0] * (current_set_length - len(current_set_values))
        elif set == 3:
            A3[current_set_name] = current_set_values + [0] * (current_set_length - len(current_set_values))
        elif set == 4:
            B[current_set_name] = current_set_values + [0] * (current_set_length - len(current_set_values))

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


def get_outputs(B, rules, name, levels_of_truth):
    outputs = []
    output_strings = []  # Список для хранения строк с выводами
    for r in range(len(rules[name[0]])):
        output = []
        for i in range(len(B[rules[name[0]][r]])):
            output.append(min(B[rules[name[0]][r]][i], levels_of_truth[r]))
        outputs.append(output)
    
    output_strings.append("Выходы правил:")
    for output in outputs:
        output_strings.append(str(output))  # Добавляем строку с выходами
    output_strings.append("")  # Пустая строка для разделения
    
    return outputs, output_strings


def outputs_aggregation(outputs):
    aggregation = []
    aggregation_strings = []  # Список для строк вывода
    
    for i in range(len(outputs[0])):
        # Инициализация максимального значения
        max_output = None
        
        for output in outputs:
            current_value = output[i]
            
            # Если текущий элемент - список, то возьмём максимум в этом списке
            if isinstance(current_value, list):
                current_value = max(current_value)
            
            # Если текущий элемент - число, можно использовать для агрегации
            if isinstance(current_value, (int, float, np.float64)):
                if max_output is None:
                    max_output = current_value
                else:
                    max_output = max(max_output, current_value)
        
        aggregation.append(max_output)

    aggregation_strings.append('Агрегация выходов правил:')
    aggregation_strings.append(str(aggregation))  # Добавляем строку с агрегацией
    aggregation_strings.append("")  # Пустая строка для разделения
    
    return aggregation, aggregation_strings


def defuzzification(A, B, name, given, aggregation):
    # Массивы для хранения результатов для входных и выходных значений
    input_values = []
    output_values = []
    
    # Вычисление четкого значения входа для каждого name[j+1]
    for j in range(3):
        sum_1 = 0
        sum_2 = 0
        for i in range(len(given)):
            if i < len(aggregation):  # Добавлена проверка длины массива aggregation
                aggregation_value = aggregation[i]
                
                # Если aggregation_value - это список, берем первое число или используем логику обработки списка
                if isinstance(aggregation_value, list):
                    aggregation_value = aggregation_value[0]  # Или любая другая логика
                
                # Преобразуем в float, если это число
                if isinstance(aggregation_value, (np.float64, float, int)):
                    aggregation_value = float(aggregation_value)
                else:
                    continue  # Пропускаем, если не число

                # Получаем входное значение
                input_value = A[j+1][name[j+1]][i]
                if isinstance(input_value, (list, np.ndarray)):
                    input_value = input_value[0]  # Если это список или массив, берем первое значение
                input_value = float(input_value) if isinstance(input_value, (np.float64, float, int)) else input_value

                sum_1 += aggregation_value * input_value
                sum_2 += aggregation_value
        
        mid = sum_1 / sum_2 if sum_2 != 0 else 0  # Чтобы избежать деления на ноль
        input_values.append(round(mid))  # Добавляем результат в массив input_values

    # Вычисление четкого значения выхода для name[0]
    sum_1 = 0
    sum_2 = 0
    for i in range(len(aggregation)):
        if i < len(B[name[0]]):  # Добавлена проверка длины массива B[name[0]]
            aggregation_value = aggregation[i]
            
            # Если aggregation_value - это список, берем первое число или используем логику обработки списка
            if isinstance(aggregation_value, list):
                aggregation_value = aggregation_value[0]  # Или любая другая логика

            # Преобразуем в float, если это число
            if isinstance(aggregation_value, (np.float64, float, int)):
                aggregation_value = float(aggregation_value)
            else:
                continue  # Пропускаем, если не число

            output_value = B[name[0]][i]
            if isinstance(output_value, (list, np.ndarray)):
                output_value = output_value[0]  # Если это список или массив, берем первое значение
            output_value = float(output_value) if isinstance(output_value, (np.float64, float, int)) else output_value
            
            sum_1 += aggregation_value * output_value
            sum_2 += aggregation_value
    
    mid = sum_1 / sum_2 if sum_2 != 0 else 0  # Чтобы избежать деления на ноль
    output_values.append(round(mid))  # Добавляем результат в массив output_values

    # Возвращаем массивы с результатами
    return input_values, output_values





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

def execute_logic(request):
    filename = "bd2.txt"
    A, B, rules, given, name = process_file(filename)

    # Получение уровней истинности предпосылок
    levels_of_truth = get_levels_of_truth(A, B, rules, given, name)
    outputs = get_outputs(B, rules, name, levels_of_truth)
    aggregation = outputs_aggregation(outputs)
    defuz = defuzzification(A, B, name, given, aggregation)
    print(type(rules))

    return render(request, 'fuzzy_logic/result.html', {
        'A1': A[1].to_html(),
        'A2': A[2].to_html(),
        'A3': A[3].to_html(),
        'B': B.to_html(),
        'rules': rules.to_html(classes='table table-bordered'),
        'given': given,
        'levels_of_truth': levels_of_truth,
        'names': name,
        # 'outputs': outputs,
        # 'aggregation': aggregation,
        # 'defuzzification': defuz,

    })
