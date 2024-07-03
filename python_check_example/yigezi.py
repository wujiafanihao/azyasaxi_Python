from openpyxl import load_workbook

# 加载工作簿
wb = load_workbook('music.xlsx')
sheet = wb.active

# 获取最大行数
max_row = sheet.max_row

# 遍历每一行
for row in range(1, max_row + 1):
    # 获取A列的单元格内容
    cell_value = sheet.cell(row=row, column=1).value
    
    # 检查A列的单元格内容是否只有一个字符
    if isinstance(cell_value, str) and len(cell_value.strip()) == 1:
        # 删除整行
        sheet.delete_rows(row)
        print(f"删除了第{row}行")
        # 由于删除了行，行号会发生变化，所以我们需要减1以保持正确的行号
        row -= 1
        max_row -= 1

# 保存工作簿
wb.save('music_modified.xlsx')