import random

def GeneracionDeP0(p, s):
    return p ^ s

def Llave1(p, q):
    return ((p << q) | (p >> (64 - q))) & 0xFFFFFFFFFFFFFFFF

def GeneracionDeS0(s, q):
    return s | q

def GeneracionDeQ0(q, s):
    return q ^ s

def Llave2(q, p):
    return ((q << p) | (q >> (64 - p))) & 0xFFFFFFFFFFFFFFFF

def GeneracionDeS1(s, p):
    return s | p

def verificar_primo(n):
    if n < 2:
        return False
    for x in range(2, int(n**0.5) + 1):
        if n % x == 0:
            return False
    return True

def rotar_derecha(num, bits):
    return ((num >> bits) | (num << (64 - bits))) & 0xFFFFFFFFFFFFFFFF

def rotar_izquierda(num, bits):
    return ((num << bits) | (num >> (64 - bits))) & 0xFFFFFFFFFFFFFFFF

def GeneradorLlaves(id, numP, numQ, numS):
    numP0 = GeneracionDeP0(numP, numS)
    llave1 = Llave1(numP0, numQ)
    numS0 = GeneracionDeS0(numS, numQ)
    numQ0 = GeneracionDeQ0(numQ, numS0)
    llave2 = Llave2(numQ0, numP0)
    numS1 = GeneracionDeS1(numS0, numP0)

    numP1 = GeneracionDeP0(numP0, numS1)
    llave3 = Llave1(numP1, numQ0)
    numS2 = GeneracionDeS0(numS1, numQ0)
    numQ1 = GeneracionDeQ0(numQ0, numS2)
    llave4 = Llave2(numQ1, numP1)

    return [id, llave1, llave2, llave3, llave4]

# Interfaz de usuario
print("////////////////////////// UDB - DSS101 G01T  ///////////////////////")
print("////// Diego Martinez, Brian Landaverde, Hector Rodriguez ///////////")
print("///////////////////////// CIFRADO POLIMORFICO ///////////////////////") 
print("/////////////////////////////// CLIENTE /////////////////////////////\n") 

llaves = []
id = "000001"
print(f"Se le ha asignado la ID: {id}")

# Primer mensaje (FCM)
print("\nPrimer mensaje (FCM):")
numP = int(input("Un número primo menor a 100 (P): "))
while not verificar_primo(numP) or numP > 99:
    numP = int(input("Número inválido. Ingrese un número primo menor a 100 (P): "))

numQ = int(input("Un número primo menor a 100, diferente de P (Q): "))
while not verificar_primo(numQ) or numQ == numP or numQ > 99:
    numQ = int(input("Número inválido. Ingrese un número primo menor a 100 y diferente de P (Q): "))

numS = int(input("Un número semilla (1-99) (S): "))
while numS < 1 or numS > 99:
    numS = int(input("Número inválido. Ingrese un número entre 1 y 99 (S): "))

numN = 4
llaves = GeneradorLlaves(id, numP, numQ, numS)

print("\nLlaves generadas:")
for i in range(1, 5):
    print(f"Llave{i}: {llaves[i]:064b} ({llaves[i]})")

mensaje_fcm = f"{id}FCM{numP:02d}{numQ:02d}{numS:02d}{numN:02d}0000"
print(f"\nMensaje FCM para enviar al servidor:\n{mensaje_fcm}")

# Menú principal
while True:
    print("\nOpciones:")
    print("1. Mensaje Regular (RM)")
    print("2. Actualización de Llaves (KUM)")
    print("3. Eliminación de Llaves (LCM)")
    print("4. Salir")
    
    opcion = input("Seleccione una opción: ")
    
    if opcion == "1":
        # Mensaje Regular (RM)
        psn = random.sample(range(4), 4)
        print(f"\nPSN generado: {''.join(map(str, psn))}")
        
        mensaje = input("Ingrese el mensaje a cifrar (1-8 caracteres): ")
        while len(mensaje) < 1 or len(mensaje) > 8:
            mensaje = input("Mensaje inválido. Ingrese 1-8 caracteres: ")
        
        # Convertir mensaje a número de 64 bits
        mensaje_num = int(''.join(f"{ord(c):08b}" for c in mensaje.ljust(8, '\0')), 2)
        
        # Cifrado según PSN
        for op in psn:
            if op == 0:
                mensaje_num ^= llaves[1]
                print("Paso: XOR con Llave1")
            elif op == 1:
                mensaje_num = rotar_derecha(mensaje_num, llaves[2] % 64)
                print("Paso: Rotacion derecha con Llave2")
            elif op == 2:
                mensaje_num ^= llaves[3]
                print("Paso: XOR con Llave3")
            elif op == 3:
                mensaje_num = rotar_izquierda(mensaje_num, llaves[4] % 64)
                print("Paso: Rotacion izquierda con Llave4")
        
        mensaje_rm = f"{id}0RM{mensaje_num}{''.join(map(str, psn))}"
        print(f"\nMensaje RM para enviar al servidor (copie y pegue):\n{mensaje_rm}")
    
    elif opcion == "2":
        # Actualización de Llaves (KUM)
        print("\nActualización de llaves:")
        new_P = int(input("Nuevo número primo menor a 100 (P): "))
        while not verificar_primo(new_P) or new_P > 99:
            new_P = int(input("Número inválido. Ingrese un número primo menor a 100 (P): "))

        new_Q = int(input("Nuevo número primo menor a 100, diferente de P (Q): "))
        while not verificar_primo(new_Q) or new_Q == new_P or new_Q > 99:
            new_Q = int(input("Número inválido. Ingrese un número primo menor a 100 y diferente de P (Q): "))

        new_S = int(input("Nuevo número semilla (1-99) (S): "))
        while new_S < 1 or new_S > 99:
            new_S = int(input("Número inválido. Ingrese un número entre 1 y 99 (S): "))

        llaves = GeneradorLlaves(id, new_P, new_Q, new_S)
        print("\nNuevas llaves generadas:")
        for i in range(1, 5):
            print(f"Llave{i}: {llaves[i]:064b} ({llaves[i]})")

        mensaje_kum = f"{id}KUM{new_P:02d}{new_Q:02d}{new_S:02d}{numN:02d}0000"
        print(f"\nMensaje KUM para enviar al servidor (copie y pegue):\n{mensaje_kum}")
    
    elif opcion == "3":
        # Eliminación de Llaves (LCM)
        mensaje_lcm = f"{id}LCM000000000000"
        print(f"\nMensaje LCM para enviar al servidor (copie y pegue):\n{mensaje_lcm}")
        break
    
    elif opcion == "4":
        break
    
    else:
        print("Opción inválida. Intente nuevamente.")

print("\nEjecución terminada")