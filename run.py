import time
from lan import Lan
from pyModbusTCP.client import ModbusClient
import struct
from PyQt5.QtCore import QUrl, QSize, QTimer, QDateTime, Qt, QPoint, QThread, pyqtSignal


class PlcMeter(QThread):
    def __init__(self, meter_host, meter_port, plc_host, plc_port):
        self.meter_host = meter_host
        self.meter_port = meter_port
        self.plc_host = plc_host
        self.plc_port = plc_port
        self.timeout = 1
        self._running = True
        self.plc_client = None
        self.lan_conn = Lan(self.timeout)
        # self.client = PlcMeter(meter_host=self.meter_host, meter_port=self.meter_port, plc_host=self.plc_host,plc_port=self.plc_port)
        self._running = True

    def connect_to_plc(self):
        """Establish a connection to the PLC."""
        try:
            self.plc_client = ModbusClient(self.plc_host, self.plc_port, auto_open=True, timeout=self.timeout)
            if self.plc_client:
                return True
            else:
                print("Failed to connect to PLC.")
                return False
        except Exception as e:
            print(f"Error connecting to PLC: {e}")
            return False

    def check_plc_comm(self):
        """Check if PLC is reachable."""
        try:
            return ModbusClient(self.plc_host, self.plc_port, auto_open=True, timeout=1)
        except Exception as e:
            print(f"PLC communication check failed: {e}")
            return False

    def read_plc_data(self):
        """Read data from the PLC."""
        if self.plc_client:
            try:
                data = self.plc_client.read_holding_registers(900, 1)
                # data = "data ada ada"
                if data:
                    return data
                else:
                    print("Failed to read PLC data.")
            except Exception as e:
                print(f"Error reading PLC data: {e}")
        return None

    def check_meter_comm(self):
        """Check if the meter is reachable."""
        try:
            return self.lan_conn.open(self.meter_host, self.meter_port)
        except Exception as e:
            print(f"Meter communication check failed: {e}")
            return False

    def send_command_meter(self, msg):
        """Send a command to the meter and get a response."""
        try:
            response = self.lan_conn.SendQueryMsg(msg, self.timeout)
            return response
        except Exception as e:
            print(f"Error sending command to meter: {e}")
            return None

    # Step 2: Convert floats to Modbus register format
    def float_to_modbus(self,value):
        # Convert float to 4-byte big-endian format
        byte_data = struct.pack('>f', value)
        # Convert bytes to two 16-bit Modbus registers
        registers = [int.from_bytes(byte_data[i:i + 2], byteorder='big') for i in range(0, len(byte_data), 2)]
        return registers

    def operate(self):
        """Main loop to check communication and send commands."""

        if self.check_plc_comm() or self.check_meter_comm():
            # issenddata=True
            while True:
                try:
                    if self.check_plc_comm():
                    # if 1:
                        plc_data = self.read_plc_data()
                        # print(plc_data)
                        if not plc_data:
                            print("Retrying PLC communication...")
                            self.connect_to_plc()
                            time.sleep(1)
                    else:
                        print("Reconnecting to PLC...")
                        self.connect_to_plc()
                    # plc_data[0]=1
                    if plc_data[0] == 1:
                        # self.plc_client.write_single_register(900, 0)

                        # logging.info("Sending remote command to the meter...")
                        self.check_meter_comm()
                        # Logic to check remote is enable or not

                        # self.send_command_meter(":SYSTem:REMote ON")

                        # logging.info("Fetching data from the meter...")
                        response = self.send_command_meter(":FETCH?")
                        if response:
                            # res_values = [round(float(num), 4) for num in response.split(", ")]
                            # Step 1: Convert to float and round to 4 decimal places
                            res_values_list=[ num for num in response.split(",")]

                            temp_resister = res_values_list[1]
                            c_res = temp_resister.replace(" ", "")

                            res_values_list[0]=  abs(round(float(res_values_list[0]),7))
                            res_values_list[1] = abs(round(float(c_res),4))

                            res_values_list[0]=round(res_values_list[0]*1000,4)

                            # Step 3: Convert each float to Modbus registers
                            modbus_registers = [self.float_to_modbus(value) for value in res_values_list]


                            self.plc_client.write_single_register(901, modbus_registers[0][1])
                            self.plc_client.write_single_register(902, modbus_registers[0][0])
                            self.plc_client.write_single_register(903, modbus_registers[1][1])
                            self.plc_client.write_single_register(904, modbus_registers[1][0])
                            time.sleep(1)
                            self.plc_client.write_single_register(900, 0)
                            self.plc_client.write_single_register(905, 1)
                        else:
                            print("Failed to fetch data from the meter.")

                    time.sleep(0.3)

                except KeyboardInterrupt:
                    print("Stopping operation due to keyboard interrupt.")
                    self._running = False
                    break

                except Exception as e:
                    print(f"Unexpected error: {e}")
                    time.sleep(1)  # Wait before retrying

        else:
            print("PLC or Meter connection failed. Check communication settings.")


# if __name__ == "__main__":
#     # Meter address configurations
#     meter_host = "192.168.10.131"
#     meter_port = 23
#
#     # PLC address configurations
#     plc_host = "192.168.10.81"
#     plc_port = 502
#
#     plc_meter = PlcMeter(meter_host, meter_port, plc_host, plc_port)
#     plc_meter.operate()
