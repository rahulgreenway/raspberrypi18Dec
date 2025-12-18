import serial
import time

# ================= CONFIG =================
PORT = "COM5"      # 🔴 Change as per Device Manager
BAUD = 9600
SLAVE_ADDR = 0x01  # try 0xF8 if no response
# ==========================================

def crc16(data):
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc

def read_voltage_current(ser):
    # Read Input Registers (0x04)
    # Start reg = 0x0000, count = 3
    cmd = bytes([SLAVE_ADDR, 0x04, 0x00, 0x00, 0x00, 0x03])
    crc = crc16(cmd)
    cmd += bytes([crc & 0xFF, crc >> 8])

    ser.write(cmd)
    time.sleep(0.1)

    resp = ser.read(25)
    if len(resp) < 11:
        return None, None

    # Voltage (0.1V)
    voltage = ((resp[3] << 8) | resp[4]) / 10.0

    # Current (0.001A, 32-bit)
    current_raw = (resp[7] << 24) | (resp[8] << 16) | (resp[5] << 8) | resp[6]
    current = current_raw / 1000.0

    return voltage, current

def main():
    try:
        ser = serial.Serial(PORT, BAUD, timeout=1)
        print("Connected to PZEM-004T on", PORT)
    except Exception as e:
        print("Serial open error:", e)
        return

    while True:
        v, i = read_voltage_current(ser)
        if v is not None:
            print(f"Voltage: {v:.2f} V   Current: {i:.3f} A")
        else:
            print("No data / Check address & wiring")

        time.sleep(1)

if __name__ == "__main__":
    main()
