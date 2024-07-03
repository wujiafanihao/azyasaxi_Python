import openpyxl

def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=50, fill='█', print_end="\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=print_end)
    if iteration == total:
        print()

def calculate_accuracy(sheet):
    accuracy = 0
    total = 0
    for row in sheet.iter_rows(min_row=2, max_col=6):
        model_answer = row[4].value
        rect_answer = row[5].value
        if model_answer is not None and rect_answer is not None:
            total += 1
            if model_answer == rect_answer:
                accuracy += 1
    return accuracy / total if total > 0 else 0

excel_file = "baichuan4.xlsx"
max_sheets = 12
skipped_sheets = [5, 6, 7, 8]

if __name__ == "__main__":
    input_wb = openpyxl.load_workbook(excel_file)
    accuracies = []
    for i in range(max_sheets):
        if i + 1 in skipped_sheets:
            continue  # Skip the specified sheets
        input_ws = input_wb.worksheets[i]
        accuracy = calculate_accuracy(input_ws)
        accuracies.append(accuracy)
        print(f"Sheet {i+1} '{input_ws.title}' Accuracy: {accuracy:.2%}")
