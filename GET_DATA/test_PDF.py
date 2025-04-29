import fitz

pdf_path = r"C:\WXG\Projects\WIP_V7\BIMW_-_WXG_Group\Neve_Ilan_(R25)\NIC-BEP.pdf"

# Считываем строки
doc = fitz.open(pdf_path)
lines = []
for page in doc:
    lines.extend(page.get_text("text").splitlines())
doc.close()

# Ищем ключевые строки и берём значения по фиксированным индексам
try:
    ns_index = lines.index("N/S")
    ns_value = lines[ns_index + 4].strip()
    ew_value = lines[ns_index + 5].strip()
    elev_value = lines[ns_index + 6].strip()
    angle_value = lines[ns_index + 7].strip()

    print("\n📊 Данные из BEP:")
    print(f"North/South: {ns_value}")
    print(f"East/West: {ew_value}")
    print(f"Elevation: {elev_value}")
    print(f"Angle to True North: {angle_value}")

except Exception as e:
    print("❌ Ошибка при чтении координат:", str(e))
