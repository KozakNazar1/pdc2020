import random
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from PIL import Image
import io

def create_word_table():
    # Створення документа
    doc = Document()
    
    # Додавання заголовку
    title = doc.add_heading('ВАРІАНТИ ЗАВДАНЬ', level=1)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Створення таблиці: 3 варіанти x 3 рядки кожен + заголовки
    # 9 рядків: заголовок, підзаголовки, дані
    table = doc.add_table(rows=9, cols=5)
    table.style = 'Table Grid'
    
    # Заповнення заголовків таблиці
    # Перший рядок
    table.cell(0, 0).text = "Вариант№"
    table.cell(0, 1).text = "Граф що відображає конфігурацію зв'язків між процесами"
    
    # Об'єднання комірок для заголовку
    table.cell(0, 1).merge(table.cell(0, 4))
    
    # Другий рядок - підзаголовки
    table.cell(1, 1).text = "N1"
    table.cell(1, 2).text = "N2"
    table.cell(1, 3).text = "N3"
    
    # Об'єднання першого стовпця
    table.cell(0, 0).merge(table.cell(1, 0))
    
    # Дані для варіантів
    variants = [
        ("1", " → 3 → 0 → 6 → 8 → 1 → 7 → 4 → 5 → 2 →\n└─────────────────────────┘"),
        ("2", " → 1 → 8 → 0 → 4 → 7 → 2 → 5 → 3 → 6 →\n└─────────────────────────┘"),
        ("3", " → 1 → 6 → 0 → 4 → 2 → 8 → 7 → 3 → 5 →\n└─────────────────────────┘")
    ]
    
    # Цифри для кожного варіанту (N1, N2, N3)
    variant_numbers = [
        ["256", "541", "325"],
        ["300", "112", "214"],
        ["113", "200", "77"]
    ]
    
    # Заповнення даних для кожного варіанту
    for i, (variant_num, graph) in enumerate(variants):
        row_offset = 2 + i * 2
        
        # Номер варіанту
        table.cell(row_offset, 0).text = variant_num
        
        # Граф (об'єднана комірка)
        table.cell(row_offset, 1).text = graph
        table.cell(row_offset, 1).merge(table.cell(row_offset, 4))
        
        # Рядок з числами N1, N2, N3
        numbers_row = row_offset + 1
        for j in range(3):
            table.cell(numbers_row, j + 1).text = variant_numbers[i][j]
    
    # Налаштування стилів таблиці
    for row in table.rows:
        for cell in row.cells:
            # Центрування тексту
            for paragraph in cell.paragraphs:
                paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
            
            # Жирний шрифт для заголовків
            if row == table.rows[0] or row == table.rows[1]:
                for paragraph in cell.paragraphs:
                    for run in paragraph.runs:
                        run.bold = True
                        run.font.size = Pt(11)
    
    # Налаштування ширини стовпців
    table.columns[0].width = Inches(0.8)    # Вариант№
    table.columns[1].width = Inches(2.5)    # Граф
    table.columns[2].width = Inches(0.8)    # N1
    table.columns[3].width = Inches(0.8)    # N2
    table.columns[4].width = Inches(0.8)    # N3
    
    # Збереження документа
    #doc.save('PRO_LAB3_VARIANTS/l4_variants.docx')
    #print("Word документ 'PRO_LAB3_VARIANTS/l4_variants.docx' успішно створено!")
    doc.save('l4_variants.docx')
    print("Word документ 'l4_variants.docx' успішно створено!")
    print("Унікальні випадкові числа від 0 до 8 додані поверх зображення.")

if __name__ == "__main__":
    create_word_table()