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

def convert_to_normal_formula___________(formula_):
    formula = formula_
    formula = formula.replace('_{1}', '₁')#.replace('_1', '₁')
    formula = formula.replace('_{2}', '₂')#.replace('_2', '₂')
    formula = formula.replace('_{3}', '₃')#.replace('_3', '₃')
    formula = formula.replace('^{2}', '²')#.replace('^2', '²')
    formula = formula.replace('^{3}', '³')#.replace('^3', '³')
    formula = formula.replace('_{i}', 'ᵢ')#.replace('_i', 'ᵢ')
    formula = formula.replace('_{j}', 'ⱼ')#.replace('_j', 'ⱼ')
    formula = formula.replace('_{ij}', 'ᵢⱼ')#.replace('_ij', 'ᵢⱼ')
    #formula = formula.replace("'", "ᵀ")
    
    return formula

def convert_formula_to_MATLAB(formula_):
    """Конвертує формулу у MATLAB синтаксис""" # (+)
    formula = formula_
    formula = formula.replace('_{1}', '1')#.replace('_1', '1')
    formula = formula.replace('_{2}', '2')#.replace('_2', '2')
    formula = formula.replace('_{3}', '3')#.replace('_3', '3')
    formula = formula.replace('^{2}', '^2')
    formula = formula.replace('^{3}', '^3')
    formula = formula.replace('_{i}', '(i)')#.replace('_i', '(i)')
    formula = formula.replace('_{j}', '(j)')#.replace('_j', '(j)')
    formula = formula.replace('_{ij}', '(i,j)')#.replace('_ij', '(i,j)')
    #formula = formula.replace("'", "ᵀ")
    
    return formula

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
    y2_formula = variant['y2']
    #a1_matlab_formula = extract_matlab_formula(a1_formula)
    Y3_formula = variant['Y3']
    C2_ij_formula_ = variant['C2_ij']
    
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

    # Аналізуємо формулу C2_ij
    C2_ij_formula = "1/(i + j)"  # за замовчуванням
    if "C_{2ij}=" in C2_ij_formula_:
        C2_ij_formula = C2_ij_formula_.split("C_{2ij}=")[1].strip()
    
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

%% 6_. Вектори b1 та c1 %%%%%%%%%%%%%%%%%%%% MOVE !!!!!!!!!!!!!!!!!!!!!
%%if choice == 1
%%     %% Ввід з клавіатури
%%     disp('=== Ввід вектора b1 ===');
%%     b1 = zeros(n);
%%     for i = 1:n
%%         b1(i) = input(sprintf('b1(%d) = ', i));
%%     end
%%
%%    disp('=== Ввід вектора c1 ===');
%%    c1 = zeros(n);
%%    for i = 1:n
%%        c1(i) = input(sprintf('c1(%d) = ', i));
%%    end
%%else
%%    %% Dипадкові значення
%%    b1 = rand(n, 1);
%%    c1 = rand(n, 1);
%%end

%% 6. Обчислення y2:
disp('Обчислення y2...');
% Формула містить A1, b1, c1
y2 = {convert_formula_to_MATLAB(y2_formula)};

disp('Вектор y2:');
disp(y2);

%% 7. Обчислення матриці C2:
disp('Обчислення матриці C2...');
C2 = zeros(n);
for i = 1:n
    for j = 1:n
        C2(i,j) = {convert_formula_to_MATLAB(C2_ij_formula)};
    end
end

disp('Матриця C2:');
disp(C2);

%% 8. Обчислення Y3:
disp('Обчислення матриці Y3...');
Y3 = {convert_formula_to_MATLAB(Y3_formula)};

disp('Матриця Y3:');
disp(Y3);

%% 9. Обчислення x:
disp('Обчислення x...');
{convert_formula_to_MATLAB(main_formula)};

disp('Результат x:');
disp(x);
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

if __name__ == "__main__":
    main()