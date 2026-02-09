import re

from make_lab2_common_functions import replace_skip, parse_variants_file, variants_redef

def replace_skip___OLD(text, old, new, skip=0, count=None):
    occ = 0 
    def repl(match):
        nonlocal occ
        occ += 1
        if occ <= skip:
            return match.group(0)
        if count is not None and occ > skip + count:
            return match.group(0)
        return new
    
    return re.sub(re.escape(old), repl, text)

def parse_variants_file___OLD(filename):
    variants = []
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            parts = line.split('|')
            if len(parts) == 7:
                number = int(parts[0])
                formula = parts[1]
                type_text = parts[2]
                b_i = parts[3]
                y2 = parts[4]
                Y3 = parts[5]
                C2_ij = parts[6]
                
                variants.append({
                    'number': number,
                    'formula': formula,
                    'type': type_text,
                    'b_i': b_i,
                    'y2': y2,
                    'Y3': Y3,
                    'C2_ij': C2_ij
                })
                
    return variants

def variants_redef___OLD(variants_data, year, group):
    new_variants_data = variants_data

    param_Y_formula_and_type = 17 * (year - 2025);
    param_Y_b_i = 13 * (year - 2025);
    param_Y_y2 = 11 * (year - 2025);
    param_Y_Y3 = 7 * (year - 2025);
    param_Y_C2_ij = 5 * (year - 2025);

    variant_count = len(variants_data);
    for index in range(variant_count):
        print(index)
        new_variants_data[index]['number'] = variants_data[index]['number'];
        new_variants_data[index]['formula'] = variants_data[(index + param_Y_formula_and_type)%variant_count]['formula'];
        new_variants_data[index]['type'] = variants_data[(index + param_Y_formula_and_type)%variant_count]['type'];
        new_variants_data[index]['b_i'] = variants_data[(index + param_Y_b_i)%variant_count]['b_i'];
        new_variants_data[index]['y2'] = variants_data[(index + param_Y_y2)%variant_count]['y2'];
        new_variants_data[index]['Y3'] = variants_data[(index + param_Y_Y3)%variant_count]['Y3'];
        new_variants_data[index]['C2_ij'] = variants_data[(index + param_Y_C2_ij)%variant_count]['C2_ij'];
        
    param_G_A = (group - 300) & 1;
    param_G_B = ((group - 300) & 2) >> 1; # !
    param_G_C = ((group - 300) & 4) >> 2; # !
    param_G_D = ((group - 300) & 8) >> 3; # !

    for v in new_variants_data:
        v['formula'] = replace_skip(v['formula'], '^{2}', '^{2_}', param_G_A, 2 - param_G_B);
        v['formula'] = replace_skip(v['formula'], '^{3}', '^{2}', param_G_A, 2 - param_G_B);
        v['formula'] = replace_skip(v['formula'], '^{2_}', '^{3}', param_G_A, 2 - param_G_B);
        
        v['formula'] = replace_skip(v['formula'], '+', '+_', param_G_C, 2 - param_G_D);
        v['formula'] = replace_skip(v['formula'], '+-', '+', param_G_C, 2 - param_G_D);
        v['formula'] = replace_skip(v['formula'], '+_', '-', param_G_C, 2 - param_G_D);

    return new_variants_data

def convert_MATLAB_formula(formula):
    formula = formula.replace('_{1}', '1')#.replace('_1', '1')
    formula = formula.replace('_{2}', '2')#.replace('_2', '2')
    formula = formula.replace('_{3}', '3')#.replace('_3', '3')
    formula = formula.replace('^{2}', '^2')
    formula = formula.replace('^{3}', '^3')
    formula = formula.replace('^{4}', '^4')
    formula = formula.replace('_{i}', '(i)')#.replace('_i', '(i)')
    formula = formula.replace('_{j}', '(j)')#.replace('_j', '(j)')
    formula = formula.replace('_{ij}', '(i,j)')#.replace('_ij', '(i,j)')
    formula = formula.replace('_{2ij}', '2(i,j)')#.replace('_2ij', '2(i,j)')
    formula = formula.replace("^{'}", "'")
    
    return formula

def generate_matlab_script(variants_data, year, group, variant_number):
    variant = None
    for v in variants_data:
        if v['number'] == variant_number:
            variant = v
            break
    
    if not variant:
        return None
    
    main_formula = variant['formula']
    b_i_formula = variant['b_i']
    y2_formula = variant['y2']
    Y3_formula = variant['Y3']
    C2_ij_formula = variant['C2_ij']
    
    b_formula_even = "1/(i^2 + 2)"  # за замовчуванням
    b_formula_odd = "1/i"  # за замовчуванням
    
    if "для парних" in b_i_formula:
        parts = b_i_formula.split("для парних")
        b_formula_even = parts[0].replace("b_{i}=", "").strip()
        
        if "для непарних" in b_i_formula:
            parts2 = b_i_formula.split("для непарних")
            b_formula_odd = parts2[0].split(";")[1].replace("b_{i}=", "").strip()
    else:
        b_formula_even = b_i_formula.replace("b_{i}=", "").strip()
        b_formula_odd = b_formula_even

    if "C_{2ij}=" in C2_ij_formula:
        C2_ij_formula = C2_ij_formula.split("C_{2ij}=")[1].strip()
    else:
        C2_ij_formula = "1/(i + j)"
    
    matlab_code = f"""%% Варіант №{variant_number}
% Обчислення виразу: {convert_MATLAB_formula(variant['formula'])}

clear all; close all; clc;

DEFAULT_N = 2;
CHOICE_MANUAL = 1;
CHOICE_RAND = 2;

RESULT_TYPE = '{variant['type']}';

try
%% 1. Ввід розмірності
    n = input('Введіть розмірність n: ');
    while n <= 0
        n = input('Розмірність повинна бути > 0. Введіть n: ');
    end

%% 2. Вибір способу вводу даних
    choice = 0;
    disp('Виберіть спосіб вводу даних:');
    while n != CHOICE_MANUAL && n != CHOICE_RAND
        n = input('%d - ввід з клавіатури, %d - випадкова генерація: ', CHOICE_MANUAL, CHOICE_RAND);
    end
catch
    n = DEFAULT_N;
    choice = CHOICE_RAND;
    printf('%d (значення за замовчуванням, ввід не підтримується системою виконання MATLAB-коду)\\n', n);
end

%% 3. Створення матриць та векторів
if choice == 1
    %% Ввід з клавіатури
    disp('=== Ввід матриці A ===');
    A = zeros(n);
    for i = 1:n
        for j = 1:n
            A(i,j) = input(sprintf('A(%d,%d) = ', i, j));
        end
    end
    
    disp('=== Ввід матриці A1 ===');
    A1 = zeros(n);
    for i = 1:n
        for j = 1:n
            A1(i,j) = input(sprintf('A1(%d,%d) = ', i, j));
        end
    end
    
    disp('=== Ввід матриці A2 ===');
    A2 = zeros(n);
    for i = 1:n
        for j = 1:n
            A2(i,j) = input(sprintf('A2(%d,%d) = ', i, j));
        end
    end
    
    disp('=== Ввід матриці B2 ===');
    B2 = zeros(n);
    for i = 1:n
        for j = 1:n
            B2(i,j) = input(sprintf('B2(%d,%d) = ', i, j));
        end
    end
    
    disp('=== Ввід вектора b1 ===');
    b1 = zeros(n);
    for i = 1:n
        b1(i) = input(sprintf('b1(%d) = ', i));
    end

    disp('=== Ввід вектора c1 ===');
    c1 = zeros(n);
    for i = 1:n
        c1(i) = input(sprintf('c1(%d) = ', i));
    end
else
    %% Випадкова генерація
    disp('Генеруються випадкові матриці та вектори...');
    A = randi([1, 9], n, n);
    A1 = randi([1, 9], n, n)
    A2 = randi([1, 9], n, n)
    B2 = randi([1, 9], n, n)
    b1 = randi([1, 9], n, 1);
    c1 = randi([1, 9], n, 1);
    
    disp('Згенеровані матриці:');
    disp('A = '); disp(A);
    disp('A1 = '); disp(A1);
    disp('A2 = '); disp(A2);
    disp('B2 = '); disp(B2);
    disp('b1 = '); disp(b1);
    disp('c1 = '); disp(c1);
end

%% 4. Обчислення вектора b згідно формули
disp('Обчислення вектора b...');
b = zeros(n, 1);
for i = 1:n
    % Формула для b_i
    if mod(i, 2) == 0
        b(i) = {convert_MATLAB_formula(b_formula_even)}; % для парних i
    else
        b(i) = {convert_MATLAB_formula(b_formula_odd)}; % для непарних i
    end
    %% b(i) = b_i_val;
end

disp('Вектор b:');
disp(b);

%% 5. Обчислення y1 = A*b
y1 = A * b;
disp('Вектор y1 = A*b:');
disp(y1);

%% 6. Обчислення y2:
disp('Обчислення y2...');
% Формула містить A1, b1, c1
y2 = {convert_MATLAB_formula(y2_formula)};

disp('Вектор y2:');
disp(y2);

%% 7. Обчислення матриці C2:
disp('Обчислення матриці C2...');
C2 = zeros(n);
for i = 1:n
    for j = 1:n
        C2(i,j) = {convert_MATLAB_formula(C2_ij_formula)};
    end
end

disp('Матриця C2:');
disp(C2);

%% 8. Обчислення Y3:
disp('Обчислення матриці Y3...');
Y3 = {convert_MATLAB_formula(Y3_formula)};

disp('Матриця Y3:');
disp(Y3);

%% 9. Обчислення x:
disp('Обчислення x...');
{convert_MATLAB_formula(main_formula)};

[r, c] = size(x);

printf('Результат ');
if strcmp(RESULT_TYPE, 'матриця') && r == n && c == n
    printf('матриця'); 
elseif strcmp(RESULT_TYPE, 'стовпець') && r == n && c == 1
    printf('стовпець');
elseif strcmp(RESULT_TYPE, 'рядок') && r == 1 && c == n
    printf('рядок');
elseif strcmp(RESULT_TYPE, 'число') && r == 1 && c == 1
    printf('число');
else 
    printf('неочікуваний формат');
end

printf(' x:\\n');
disp(x);
printf('({year - 1}/{year} н.р., KI-{str(group)}, варіант №{variant_number}: {convert_MATLAB_formula(variant['formula']).replace("'", "''")})');
"""
    
    return matlab_code


def main():    
    # Читаємо базові варіанти
    variants = parse_variants_file('make_lab2_variants_data.txt')

    # Створюємо нові варіанти
    year = 2026
    group = 308
    variants_redef(variants, year, group)
    
    if not variants:
        print("Не знайдено варіантів у файлі")
        return
    
    # Вибір варіанту
    print("Доступні варіанти:")
    for v in variants:
        print(f"Варіант {v['number']}: {v['formula'][:50]}...")
    
    try:
        variant_num = int(input("\nВиберіть номер варіанту: "))
    except:
        print("Невірний номер варіанту")
        return
    
    # Генеруємо MATLAB код
    matlab_code = generate_matlab_script(variants, year, group, variant_num)
    
    if matlab_code:
        # Зберігаємо у файл
        filename = f"variant_{year - 1}{year}_ki{group}_{variant_num}.m"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(matlab_code)
        
        print(f"\nMATLAB скрипт згенеровано: {filename}")
        print(f"\nІнструкція:")
        print(f"1. Відкрийте {filename} у MATLAB")
        print(f"2. Запустіть скрипт")
        print(f"3. Дотримуйтесь інструкцій на екрані")

if __name__ == "__main__":
    main()