import serial
import time
import HandTrackingModule as htm

class ArduinoController:

    '''
    Class pour communication avec arduino
    '''

    # Initialiser la communication avec l'Arduino
    def __init__(self, port='COM3', baudrate=9600, timeout=1):
        self.arduino = serial.Serial(port, baudrate, timeout=timeout)
        time.sleep(2)  # Donne le temps à l'Arduino de démarrer
        print(f"Connexion établie sur le port {port} à {baudrate} baud.")

    # Envoie d'octets à Arduino
    def control_servos(self, direction1, intensitee1, direction2, intensitee2):
        data = bytearray([direction1, intensitee1, direction2, intensitee2])
        self.arduino.write(data)
        time.sleep(0.1)  # Petite pause pour assurer la communication

    # Envoie d'octets à Arduino
    def control_servos2(self, direction1, intensitee1, direction2, intensitee2, direction3, intensitee3):
        data = bytearray([direction1, intensitee1, direction2, intensitee2, direction3, intensitee3])
        self.arduino.write(data)
        time.sleep(0.1)  # Petite pause pour assurer la communication        

    # Fermer la connexion série avec l'Arduino
    def close(self):
        if self.arduino.is_open:
            self.arduino.close()
            print("Connexion série fermée.")
