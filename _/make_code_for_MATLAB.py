import re

def parse_variants_file(filename):
    """Парсить файл з варіантами"""
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
                a1 = parts[4]
                a2 = parts[5]
                c_ij = parts[6]
                
                variants.append({
                    'number': number,
                    'formula': formula,
                    'type': type_text,
                    'b_i': b_i,
                    'a1': a1,
                    'a2': a2,
                    'c_ij': c_ij
                })
    return variants

def extract_matlab_formula(formula_str):
    """Конвертує формулу у MATLAB синтаксис"""
    # Заміна індексів
    formula = formula_str.replace('_{', '(').replace('}', '+1)')
    formula = formula.replace('^{', '.^(').replace('}', '+1)')
    formula = formula.replace('*', '.*')
    formula = formula.replace("'", "'")  # транспонування залишаємо
    
    # Заміна змінних для MATLAB
    formula = formula.replace('Y_{3}', 'Y3')
    formula = formula.replace('Y3', 'Y3')
    formula = formula.replace('y_{1}', 'y1')
    formula = formula.replace('y_{2}', 'y2')
    formula = formula.replace('y1', 'y1')
    formula = formula.replace('y2', 'y2')
    
    return formula

def generate_matlab_script(variant_number, variants_data):
    """Генерує MATLAB скрипт для конкретного варіанту"""
    
    # Знаходимо варіант
    variant = None
    for v in variants_data:
        if v['number'] == variant_number:
            variant = v
            break
    
    if not variant:
        return None
    
    # Парсимо формули
    main_formula = extract_matlab_formula(variant['formula'])
    b_i_formula = variant['b_i']
    a1_formula = variant['a1']
    a2_formula = variant['a2']
    c_ij_formula = variant['c_ij']
    
    # Аналізуємо формулу b_i (парні/непарні)
    b_formula_even = "1/(i^2 + 2)"  # за замовчуванням
    b_formula_odd = "1/i"  # за замовчуванням
    
    if "для парних" in b_i_formula:
        parts = b_i_formula.split("для парних")
        b_formula_even = parts[0].replace("b_i=", "").strip()
        
        if "для непарних" in b_i_formula:
            parts2 = b_i_formula.split("для непарних")
            b_formula_odd = parts2[0].split(";")[1].replace("b_i=", "").strip()
    else:
        b_formula_even = b_i_formula.replace("b_i=", "").strip()
        b_formula_odd = b_formula_even

    # Аналізуємо формулу C_ij
    c_formula = "1/(i + j)"  # приклад за замовчуванням
    if "C_ij=" in c_ij_formula:
        c_formula = c_ij_formula.split("C_ij=")[1].strip()
    
    # Генеруємо MATLAB код
    matlab_code = f"""%% Лабораторна робота - Варіант {variant_number}
% Обчислення виразу: {variant['formula']}

clear all; close all; clc;

%% 1. Ввід розмірності
n = input('Введіть розмірність n: ');
while n <= 0
    n = input('Розмірність повинна бути > 0. Введіть n: ');
end

%% 2. Вибір способу вводу даних
disp('Виберіть спосіб вводу даних:');
disp('1 - Ввід з клавіатури');
disp('2 - Випадкова генерація');
choice = input('Ваш вибір (1 або 2): ');

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
    
else
    %% Випадкова генерація
    disp('Генеруються випадкові матриці...');
    A = randn(n);    % Нормальний розподіл
    A1 = rand(n);    % Рівномірний розподіл [0,1]
    A2 = 10*rand(n); % Рівномірний розподіл [0,10]
    B2 = 5*randn(n); % Нормальний розподіл *5
    
    disp('Згенеровані матриці:');
    disp('A = '); disp(A);
    disp('A1 = '); disp(A1);
    disp('A2 = '); disp(A2);
    disp('B2 = '); disp(B2);
end

%% 4. Обчислення вектора b згідно формули
disp('Обчислення вектора b...');
b = zeros(n, 1);
for i = 1:n
    % Формула для b_i
    if mod(i, 2) == 0  % парні
        % Формула для парних: {b_formula_even}
        b_i_val = {b_formula_even.replace('i', 'i').replace('^', '.^')};
    else  % непарні
        % Формула для непарних: {b_formula_odd}
        b_i_val = {b_formula_odd.replace('i', 'i').replace('^', '.^')};
    end
    b(i) = b_i_val;
end

disp('Вектор b:');
disp(b);

%% 5. Обчислення y1 = A*b
y1 = A * b;
disp('Вектор y1 = A*b:');
disp(y1);

%% 6. Вектори b1 та c1
if choice == 1
    %% Ввід з клавіатури
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
    %% Dипадкові значення
    b1 = rand(n, 1);
    c1 = rand(n, 1);
end

%% 7. Обчислення y2 згідно формули: {a1_formula}
disp('Обчислення y2...');
% Формула містить A1, b1, c1
% Аналізуємо формулу
y2_formula = '{a1_formula}';

% Простий парсинг формули y2
if 'b1+c1' in y2_formula:
    y2 = A1 * (b1 + c1);
elseif 'b1+2c1' in y2_formula:
    y2 = A1 * (b1 + 2*c1);
elif '3b1+c1' in y2_formula:
    y2 = A1 * (3*b1 + c1);
elif 'b1-2c1' in y2_formula:
    y2 = A1 * (b1 - 2*c1);
else:
    % За замовчуванням
    y2 = A1 * b1;
end

disp('Вектор y2:');
disp(y2);

%% 8. Обчислення матриці C2 згідно формули: {c_ij_formula}
disp('Обчислення матриці C2...');
C2 = zeros(n);
for i = 1:n
    for j = 1:n
        % Формула для C_ij: {c_formula}
        C2(i,j) = {c_formula.replace('i', 'i').replace('j', 'j').replace('^', '.^')};
    end
end

disp('Матриця C2:');
disp(C2);

%% 9. Обчислення Y3 згідно формули: {a2_formula}
disp('Обчислення матриці Y3...');
% Аналізуємо формулу Y3
y3_formula = '{a2_formula}';

if 'B2-C2' in y3_formula:
    Y3 = A2 * (B2 - C2);
elif 'C2-B2' in y3_formula:
    Y3 = A2 * (C2 - B2);
elif 'B2+C2' in y3_formula:
    Y3 = A2 * (B2 + C2);
elif '10B2+C2' in y3_formula:
    Y3 = A2 * (10*B2 + C2);
elif 'C2+2B2' in y3_formula:
    Y3 = A2 * (C2 + 2*B2);
else:
    % За замовчуванням
    Y3 = A2 * B2;
end

disp('Матриця Y3:');
disp(Y3);

%% 10. Обчислення основного виразу
disp('Обчислення основного виразу...');
% Аналізуємо основну формулу
main_formula_str = '{main_formula}';

if 'Y3^2*y2' in main_formula_str and 'Y3(y1+y2)' in main_formula_str:
    x = Y3^2 * y2 + Y3 * (y1 + y2);
elif 'Y3*y2*y2''' in main_formula_str:
    x = Y3 * y2 * y2' + Y3^3 - Y3 + y2 * y1' + Y3^2 * y1 * y1';
elif 'y2''*y1*Y3^2' in main_formula_str:
    x = y2' * y1 * Y3^2 + y1' * y2 * Y3^2 + y2' * Y3 * y1 * Y3 + Y3;
else:
    % За замовчуванням - спрощена формула
    x = Y3 * y2 + y1;
end

%% 11. Вивід результатів
disp('========================================');
disp('РЕЗУЛЬТАТИ:');
disp('========================================');
fprintf('Варіант: %d\\n', {variant_number});
fprintf('Тип результату: %s\\n', '{variant['type']}');
disp('Вектор y1:');
disp(y1);
disp('Вектор y2:');
disp(y2);
disp('Матриця Y3 (перші 5x5):');
if n > 5
    disp(Y3(1:5, 1:5));
else
    disp(Y3);
end

disp('Результат x:');
if isscalar(x)
    fprintf('x = %f\\n', x);
elseif isvector(x)
    fprintf('Вектор x (перші 5 елементів):\\n');
    if length(x) > 5
        disp(x(1:5));
    else
        disp(x);
    end
else
    fprintf('Матриця x (перші 5x5):\\n');
    [rows, cols] = size(x);
    if rows > 5 or cols > 5
        disp(x(1:min(5,rows), 1:min(5,cols)));
    else
        disp(x);
    end
end

%% 12. Збереження у файл
filename = sprintf('results_variant_%d.mat', {variant_number});
save(filename, 'n', 'A', 'A1', 'A2', 'B2', 'b', 'b1', 'c1', 'C2', 'y1', 'y2', 'Y3', 'x');
fprintf('Результати збережено у файл: %s\\n', filename);

% Експорт у текстовий файл
txt_filename = sprintf('results_variant_%d.txt', {variant_number});
fid = fopen(txt_filename, 'w');
fprintf(fid, 'Результати для варіанту %d\\n\\n', {variant_number});
fprintf(fid, 'Розмірність: n = %d\\n\\n', n);
fprintf(fid, 'Вектор y1:\\n');
for i = 1:min(10, length(y1))
    fprintf(fid, '  y1(%d) = %f\\n', i, y1(i));
end
fprintf(fid, '\\nВектор y2:\\n');
for i = 1:min(10, length(y2))
    fprintf(fid, '  y2(%d) = %f\\n', i, y2(i));
end
fprintf(fid, '\\nМатриця Y3 (перші 5x5):\\n');
for i = 1:min(5, n)
    for j = 1:min(5, n)
        fprintf(fid, '  %10.4f', Y3(i,j));
    end
    fprintf(fid, '\\n');
end
fprintf(fid, '\\nРезультат x:\\n');
if isscalar(x)
    fprintf(fid, '  x = %f\\n', x);
elseif isvector(x)
    for i = 1:min(10, length(x))
        fprintf(fid, '  x(%d) = %f\\n', i, x(i));
    end
else
    for i = 1:min(5, size(x,1))
        for j = 1:min(5, size(x,2))
            fprintf(fid, '  %10.4f', x(i,j));
        end
        fprintf(fid, '\\n');
    end
end
fclose(fid);
fprintf('Текстові результати збережено у файл: %s\\n', txt_filename);

disp('========================================');
disp('Роботу завершено!');
"""
    
    return matlab_code


def main():
    """Основна функція"""
    
    # Читаємо варіанти
    variants = parse_variants_file('variants_data.txt')
    
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
    matlab_code = generate_matlab_script(variant_num, variants)
    
    if matlab_code:
        # Зберігаємо у файл
        filename = f"variant_{variant_num}.m"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(matlab_code)
        
        print(f"\nMATLAB скрипт згенеровано: {filename}")
        print(f"\nІнструкція:")
        print(f"1. Відкрийте {filename} у MATLAB")
        print(f"2. Запустіть скрипт")
        print(f"3. Дотримуйтесь інструкцій на екрані")
        
        # Також зберігаємо спрощений варіант
        simple_filename = f"variant_{variant_num}_simple.m"
        simple_code = f"""%% Лабораторна робота - Варіант {variant_num}
% Автоматично згенерований скрипт

clear all; close all; clc;

% Основні параметри
n = 3; % Змініть розмірність при необхідності

% Генерація випадкових даних
A = randn(n);
A1 = rand(n);
A2 = 10*rand(n);
B2 = 5*randn(n);
b = rand(n, 1);
b1 = rand(n, 1);
c1 = rand(n, 1);

% Обчислення векторів
y1 = A * b;
y2 = A1 * (b1 + c1); % Приклад, замініть на свою формулу

% Матриця C2 (приклад)
C2 = zeros(n);
for i = 1:n
    for j = 1:n
        C2(i,j) = 1/(i + 2*j); % Приклад, замініть на свою формулу
    end
end

% Матриця Y3
Y3 = A2 * (B2 - C2); % Приклад, замініть на свою формулу

% Основний вираз
x = Y3^2 * y2 + Y3 * (y1 + y2); % Приклад, замініть на свою формулу

% Вивід результатів
disp('Результати:');
disp('y1 = '); disp(y1);
disp('y2 = '); disp(y2);
disp('Y3 = '); disp(Y3);
disp('x = '); disp(x);
"""
        
        with open(simple_filename, 'w', encoding='utf-8') as f:
            f.write(simple_code)
        
        print(f"4. Спрощений скрипт: {simple_filename}")
    else:
        print(f"Варіант {variant_num} не знайдено")

if __name__ == "__main__":
    main()