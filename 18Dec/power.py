import serial
import time
import math

# ================= CONFIG =================
PORT = "COM5"      # 🔴 Change COM port
BAUD = 9600
ADDR = 0x01        # Try 0xF8 if no response
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

def read_pzem(ser):
    # Read Input Registers: 0x0000 → 0x0009 (10 registers)
    cmd = bytes([ADDR, 0x04, 0x00, 0x00, 0x00, 0x0A])
    crc = crc16(cmd)
    cmd += bytes([crc & 0xFF, crc >> 8])

    ser.write(cmd)
    time.sleep(0.1)
    resp = ser.read(40)

    if len(resp) < 25:
        return None

    # ---------- Parse data ----------
    voltage = ((resp[3] << 8) | resp[4]) / 10.0

    current_raw = (
        (resp[7] << 24) |
        (resp[8] << 16) |
        (resp[5] << 8) |
        resp[6]
    )
    current = current_raw / 1000.0

    power_raw = (
        (resp[11] << 24) |
        (resp[12] << 16) |
        (resp[9] << 8) |
        resp[10]
    )
    power = power_raw / 10.0

    energy = (
        (resp[15] << 24) |
        (resp[16] << 16) |
        (resp[13] << 8) |
        resp[14]
    ) / 1000.0

    frequency = ((resp[17] << 8) | resp[18]) / 10.0
    pf = ((resp[19] << 8) | resp[20]) / 100.0

    # ---------- Derived values ----------
    apparent_power = voltage * current
    reactive_power = math.sqrt(max(apparent_power**2 - power**2, 0))

    return {
        "Voltage (V)": voltage,
        "Current (A)": current,
        "Active Power (W)": power,
        "Energy (kWh)": energy,
        "Frequency (Hz)": frequency,
        "Power Factor": pf,
        "Apparent Power (VA)": apparent_power,
        "Reactive Power (VAR)": reactive_power
    }

def main():
    try:
        ser = serial.Serial(PORT, BAUD, timeout=1)
        print("✅ Connected to PZEM-004T on", PORT)
    except Exception as e:
        print("❌ Serial Error:", e)
        return

    while True:
        data = read_pzem(ser)
        if data:
            print("\n-----------------------------")
            for k, v in data.items():
                if "Power Factor" in k:
                    print(f"{k:20}: {v:.2f}")
                else:
                    print(f"{k:20}: {v:.3f}")
        else:
            print("⚠️ No data received")

        time.sleep(1)

if __name__ == "__main__":
    main()
