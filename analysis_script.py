import csv
import sys

# Путь к файлу
file_path = '/opt/ouroboros/ouroboros/memory/data/Операции сотрудников за 12.03.2026.csv'

# Словари для хранения данных
employee_data = {}  # {uuid: {"total_output": 0, "total_norm": 0, "operations": 0}}
site_data = {}     # {"Площадка": {"total_employees": 0, "total_output": 0, "total_norm": 0, "employees_under_70": 0, "employees_over_130": 0}}

# Чтение и обработка CSV файла
try:
    with open(file_path, 'r', encoding='iso-8859-1') as file:
        reader = csv.reader(file, delimiter=';')
        headers = next(reader)  # Пропускаем заголовок
        
        for row in reader:
            # Извлечение данных из строки по индексам
            # Предполагаем, что последний столбец - UUID
            # и что "Площадка" - это второй столбец (индекс 1)
            if len(row) < 15:
                continue  # Пропускаем некорректные строки
                
            site = row[1].strip()  # Второй столбец - "Площадка"
            uuid = row[-1].strip()  # Последний столбец - UUID
            
            try:
                norm = float(row[7].replace(',', '.')) if row[7] else 0.0  # Норматив, шт
                output = int(row[9]) if row[9] else 0  # Кол-во операций
            except (ValueError, IndexError):
                continue  # Пропускаем строки с некорректными данными
            
            # Некоторые значения выработки могут быть пустыми, но мы их не используем для агрегации
            
            # Инициализация данных по сотруднику
            if uuid not in employee_data:
                employee_data[uuid] = {"total_output": 0, "total_norm": 0, "operations": 0}
            
            # Инициализация данных по площадке
            if site not in site_data:
                site_data[site] = {"total_employees": 0, "total_output": 0, "total_norm": 0, "employees_under_70": 0, "employees_over_130": 0}
            
            # Агрегация данных по сотруднику
            employee_data[uuid]["total_output"] += output
            employee_data[uuid]["total_norm"] += norm
            employee_data[uuid]["operations"] += 1
            
            # Агрегация данных по площадке
            site_data[site]["total_output"] += output
            site_data[site]["total_norm"] += norm

    # Расчет итоговой выработки для каждого сотрудника и агрегация по площадкам
    total_employees_working = len(employee_data)
    employees_under_70 = 0
    employees_over_130 = 0
    total_output_all = 0
    total_norm_all = 0

    for uuid, data in employee_data.items():
        # Поиск соответствующей площадки для сотрудника (берем первую попавшуюся строку для этого UUID)
        # Для этого нам нужно снова прочитать файл
        site = None
        with open(file_path, 'r', encoding='iso-8859-1') as file:
            reader = csv.reader(file, delimiter=';')
            headers = next(reader)  # Пропускаем заголовок
            for row in reader:
                if len(row) >= 15 and row[-1].strip() == uuid:
                    site = row[1].strip()
                    break
        
        if site is None:
            site = "Unknown"
        
        # Расчет итоговой выработки сотрудника
        if data["total_norm"] > 0:
            final_efficiency = (data["total_output"] / data["total_norm"]) * 100
        else:
            final_efficiency = 0.0
        
        # Обновление статистики по площадке
        if final_efficiency < 70:
            site_data[site]["employees_under_70"] += 1
            employees_under_70 += 1
        if final_efficiency > 130:
            site_data[site]["employees_over_130"] += 1
            employees_over_130 += 1
        
        # Увеличиваем количество уникальных сотрудников на площадке
        site_data[site]["total_employees"] += 1
        
        # Для общих итогов
        total_output_all += data["total_output"]
        total_norm_all += data["total_norm"]

    # Расчет средней выработки
    if total_norm_all > 0:
        average_efficiency = (total_output_all / total_norm_all) * 100
    else:
        average_efficiency = 0.0

    # Вывод результатов
    print("# Аналитический отчёт по операциям сотрудников СЦ Архив")
    print("## За операционный день 12.03.2026")
    print("")
    print("## 1. Общая статистика по сотрудникам")
    print("")
    print(f"- **Всего сотрудников в штатном расписании:** 780")
    print(f"- **Всего сотрудников, выполнивших операции за день:** {total_employees_working}")
    print(f"- **Средняя выработка по всем сотрудникам:** {average_efficiency:.1f}%")
    print(f"- **Сотрудников с выработкой <70%:** {employees_under_70}")
    print(f"- **Сотрудников с выработкой >130%:** {employees_over_130}")
    print("")
    print("## 2. Показатели по площадкам (Площадка)")
    print("")
    print("| Площадка | Всего сотрудников | Средняя выработка | Сотрудников <70% | Сотрудников >130% |")
    print("| :--- | :--- | :--- | :--- | :--- |")

    for site, data in site_data.items():
        if data["total_norm"] > 0:
            site_avg_efficiency = (data["total_output"] / data["total_norm"]) * 100
        else:
            site_avg_efficiency = 0.0
        
        print(f"| {site} | {data['total_employees']} | {site_avg_efficiency:.1f}% | {data['employees_under_70']} | {data['employees_over_130']} |")

except Exception as e:
    print(f"Ошибка при обработке файла: {e}")
    sys.exit(1)
