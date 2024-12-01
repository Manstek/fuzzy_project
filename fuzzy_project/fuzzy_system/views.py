from django.shortcuts import render
import pandas as pd


def process_file(uploaded_file):
    A = {}
    B = {}
    rules = []
    given = []

    # Чтение содержимого файла
    lines = uploaded_file.read().decode('utf-8').splitlines()

    current_set_name = None
    current_set_values = []
    current_set_length = 0
    A_set = False
    a_name = ''
    b_name = ''

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if not line:
            i += 1
            continue

        elif line.startswith("Множество определения"):
            if current_set_name:
                if A_set:
                    A[current_set_name] = current_set_values + [0] * (
                        current_set_length - len(current_set_values))
                else:
                    B[current_set_name] = current_set_values + [0] * (
                        current_set_length - len(current_set_values))

            A_set = not A_set
            parts = line.split()
            current_set_name = parts[-1]
            if A_set:
                a_name = current_set_name
            else:
                b_name = current_set_name
            current_set_values = []
            current_set_length = 0

        elif line.startswith("0") or line.startswith("-") or line[0].isdigit():
            values = list(map(float, line.split()))
            if current_set_length == 0:
                current_set_length = len(values)
            current_set_values.extend(values)

        elif line.startswith("Нечеткое множество"):
            parts = line.split()
            fuzzy_set_name = parts[-1]
            i += 1
            if i < len(lines):
                fuzzy_set_values = list(map(float, lines[i].strip().split()))
                fuzzy_set_values.extend([0] * (current_set_length - len(
                    fuzzy_set_values)))
                if A_set:
                    A[fuzzy_set_name] = fuzzy_set_values
                else:
                    B[fuzzy_set_name] = fuzzy_set_values

        elif line.startswith("Если"):
            parts = line.split()
            antecedent = parts[2]
            consequent = parts[-1]
            rules.append((antecedent, consequent))

        elif line.startswith("Пусть"):
            i += 1
            line = lines[i].strip()
            values = list(map(float, line.split()))
            given.extend(values)

        i += 1

    if current_set_name:
        if A_set:
            A[current_set_name] = current_set_values
        else:
            B[current_set_name] = current_set_values

    A = pd.DataFrame(A)
    B = pd.DataFrame(B)
    rules = pd.DataFrame(rules, columns=["Условие", "Следствие"])

    return A, B, rules, given, a_name, b_name


def get_correspondences_Mamdani(A, B, rules):
    correspondences = []
    for r in range(len(rules["Условие"])):
        correspondence = []
        for i in range(len(A)):
            row = []
            for j in range(len(B)):
                row.append(min(A[rules["Условие"][r]][i],
                               B[rules["Следствие"][r]][j]))
            correspondence.append(row)
        correspondences.append(correspondence)
    return correspondences


def get_correspondences_Larsen(A, B, rules):
    correspondences = []
    for r in range(len(rules["Условие"])):
        correspondence = []
        for i in range(len(A)):
            row = []
            for j in range(len(B)):
                row.append(round(A[
                    rules["Условие"][r]][i] * B[rules["Следствие"][r]][j], 2))
            correspondence.append(row)
        correspondences.append(correspondence)
    return correspondences


def outputs_aggregation(correspondences, rules, given):
    outputs = []
    for correspondence in correspondences:
        output = []
        for i in range(len(correspondence[0])):
            column = []
            for j in range(len(given)):
                column.append(min(given[j], correspondence[j][i]))
            output.append(max(column))
        outputs.append(output)

    aggregation = []
    for i in range(len(outputs[0])):
        foo = 0
        for output in outputs:
            foo = max(foo, output[i])
        aggregation.append(foo)

    return aggregation


def rules_aggregation(correspondences, given):
    aggregation = correspondences[0]
    for correspondence in correspondences:
        for i in range(len(aggregation)):
            for j in range(len(aggregation[0])):
                aggregation[i][j] = max(
                    aggregation[i][j], correspondence[i][j])

    output = []
    for i in range(len(aggregation[0])):
        column = []
        for j in range(len(given)):
            column.append(min(given[j], aggregation[j][i]))
        output.append(max(column))

    return output


def defuzzification(output, values):
    sum_1 = sum(o * v for o, v in zip(output, values))
    sum_2 = sum(output)
    if sum_2 == 0:
        return 0
    return sum_1 / sum_2


def index(request):
    if request.method == 'POST':
        file = request.FILES.get('data_file')
        implication_method = request.POST.get('implication_method', 'Mamdani')
        aggregation_method = request.POST.get('aggregation_method', 'outputs')

        if file:
            A, B, rules, given, a_name, b_name = process_file(file)

            if implication_method == 'Mamdani':
                correspondences = get_correspondences_Mamdani(A, B, rules)
            else:
                correspondences = get_correspondences_Larsen(A, B, rules)

            if aggregation_method == 'outputs':
                output = outputs_aggregation(correspondences, rules, given)
            else:
                output = rules_aggregation(correspondences, given)

            defuzz_value = defuzzification(output, B[b_name])

            context = {
                'A': A.to_html(),
                'B': B.to_html(),
                'rules': rules.to_html(),
                'given': given,
                'output': output,
                'defuzz_value': defuzz_value,
            }
            return render(request, 'fuzzy_system/result.html', context)

    return render(request, 'fuzzy_system/index.html')
