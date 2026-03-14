# DE BLE Fingertip Oximeter

Интеграция для Home Assistant, добавляющая поддержку пульсоксиметра Contec PC-60FW через Bluetooth.

![PC-60FW Oximeter](custom_components/de_ble_fingertip_oximeter/brand/icon.png)

## Поддерживаемые устройства

- **Модель:** PC-60FW (пульсоксиметр)
- **Производитель:** Contec
- **Bluetooth-сервис:** `6e400001-b5a3-f393-e0a9-e50e24dcca9e`

## Возможности

- Автоматическое обнаружение пульсоксиметра через Bluetooth
- Отображение уровня насыщения крови кислородом (SpO₂) в процентах
- Отображение частоты пульса (BPM)
- Отображение перфузионного индекса (PI) в процентах
- Отображение уровня заряда батареи
- Сенсор статуса подключения
- Автоматическое подключение при появлении устройства
- Сохранение последних показаний при отключении

## Установка

### Через HACS (рекомендуется)

1. Убедитесь, что у вас установлен [HACS](https://hacs.xyz/)
2. Откройте HACS в Home Assistant
3. Нажмите на три точки в правом верхнем углу
4. Выберите "Пользовательские репозитории"
5. Добавьте:
   - **URL:** `https://github.com/de-andrei/de_ble_fingertip_oximeter`
   - **Категория:** `Integration`
6. Нажмите "Добавить"
7. Найдите "DE BLE Fingertip Oximeter" в списке интеграций HACS
8. Нажмите "Скачать"
9. Перезапустите Home Assistant

### Ручная установка

1. Скачайте последний релиз из [репозитория](https://github.com/de-andrei/de_ble_fingertip_oximeter/releases)
2. Распакуйте папку `custom_components/de_ble_fingertip_oximeter` в директорию `config/custom_components/` вашего Home Assistant
3. Перезапустите Home Assistant

## Настройка

1. Перейдите в **Настройки** → **Устройства и службы**
2. Нажмите **"Добавить интеграцию"**
3. Найдите **"DE BLE Fingertip Oximeter"** в списке
4. Выберите ваш пульсоксиметр PC-60FW из списка обнаруженных устройств
5. Нажмите "Отправить"

## Сенсоры

После настройки будут созданы следующие сенсоры:

| Сущность | Имя | Описание |
|----------|-----|----------|
| `sensor.pulse_oximeter_spo2` | SpO₂ | Уровень насыщения крови кислородом (%) |
| `sensor.pulse_oximeter_pulse` | Pulse | Частота пульса (уд/мин) |
| `sensor.pulse_oximeter_perfusion_index` | Perfusion Index | Перфузионный индекс (%) |
| `sensor.pulse_oximeter_battery` | Battery | Уровень заряда батареи (%) |
| `sensor.pulse_oximeter_connection_status` | Connection Status | Статус подключения к устройству |