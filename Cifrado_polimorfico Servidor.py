def rotar_derecha(num, bits):
    return ((num >> bits) | (num << (64 - bits))) & 0xFFFFFFFFFFFFFFFF

def rotar_izquierda(num, bits):
    return ((num << bits) | (num >> (64 - bits))) & 0xFFFFFFFFFFFFFFFF

def procesar_fcm(llaves, id, payload):
    #Procesa mensaje de primer contacto (FCM) para generar llaves
    if any(fila[0] == id for fila in llaves):
        print("Error: ID ya registrado")
        return llaves
    
    try:
        numP = int(payload[:2])
        numQ = int(payload[2:4])
        numS = int(payload[4:6])
    except ValueError:
        print("Error: Payload debe contener valores numericos")
        return llaves
    
    # Generacion de llaves
    numP0 = numP ^ numS
    llave1 = ((numP0 << numQ) | (numP0 >> (64 - numQ))) & 0xFFFFFFFFFFFFFFFF
    numS0 = numS | numQ
    numQ0 = numQ ^ numS0
    llave2 = ((numQ0 << numP0) | (numQ0 >> (64 - numP0))) & 0xFFFFFFFFFFFFFFFF
    numS1 = numS0 | numP0
    
    numP1 = numP0 ^ numS1
    llave3 = ((numP1 << numQ0) | (numP1 >> (64 - numQ0))) & 0xFFFFFFFFFFFFFFFF
    numS2 = numS1 | numQ0
    numQ1 = numQ0 ^ numS2
    llave4 = ((numQ1 << numP1) | (numQ1 >> (64 - numP1))) & 0xFFFFFFFFFFFFFFFF
    
    llaves.append([id, llave1, llave2, llave3, llave4])
    
    print(f"\nLlaves generadas para ID {id}:")
    for i in range(1, 5):
        print(f"Llave{i}: {llaves[-1][i]:064b} ({llaves[-1][i]})")
    
    return llaves

def procesar_rm(llaves, id, payload, psn):
    """Procesa mensaje regular (RM) para descifrar contenido"""
    try:
        fila = next((i for i, fila in enumerate(llaves) if fila[0] == id), None)
    except StopIteration:
        fila = None
    
    if fila is None:
        print("Error: ID no encontrado")
        return llaves
    
    try:
        llave1, llave2, llave3, llave4 = llaves[fila][1], llaves[fila][2], llaves[fila][3], llaves[fila][4]
        mensaje_cifrado = int(payload)
        psn = [int(c) for c in psn if c.isdigit()]
    except (ValueError, IndexError):
        print("Error: Formato de payload o PSN invalido")
        return llaves
    
    if len(psn) != 4:
        print("Error: PSN debe tener exactamente 4 digitos")
        return llaves
    
    print(f"\nDescifrando mensaje con PSN: {''.join(map(str, psn))}")
    
    # Descifrado en orden inverso
    for op in reversed(psn):
        if op == 0:
            mensaje_cifrado ^= llave1
            print("Paso: XOR con Llave1")
        elif op == 1:
            mensaje_cifrado = rotar_izquierda(mensaje_cifrado, llave2 % 64)
            print("Paso: Rotacion izquierda con Llave2")
        elif op == 2:
            mensaje_cifrado ^= llave3
            print("Paso: XOR con Llave3")
        elif op == 3:
            mensaje_cifrado = rotar_derecha(mensaje_cifrado, llave4 % 64)
            print("Paso: Rotacion derecha con Llave4")
        else:
            print(f"Error: Valor PSN invalido {op}")
            return llaves
    
    # Convertir a texto
    try:
        mensaje_bin = f"{mensaje_cifrado:064b}"
        mensaje = ''.join([chr(int(mensaje_bin[i:i+8], 2)) for i in range(0, 64, 8)]).replace('\x00', '')
        print(f"\nMensaje descifrado: '{mensaje}'")
        print(f"Representacion binaria: {mensaje_bin}")
    except:
        print("Error: No se pudo convertir el mensaje descifrado a texto")
    
    return llaves

def procesar_kum(llaves, id, payload):
    """Procesa actualizacion de llaves (KUM)"""
    try:
        fila = next((i for i, fila in enumerate(llaves) if fila[0] == id), None)
    except StopIteration:
        fila = None
    
    if fila is None:
        print("Error: ID no encontrado")
        return llaves
    
    print(f"\nActualizando llaves para ID {id}")
    # Eliminar llaves antiguas
    llaves = [fila for fila in llaves if fila[0] != id]
    # Procesar como nuevo FCM
    return procesar_fcm(llaves, id, payload)

def procesar_lcm(llaves, id):
    """Procesa eliminacion de llaves (LCM)"""
    if not any(fila[0] == id for fila in llaves):
        print("Error: ID no encontrado")
        return llaves
    
    llaves = [fila for fila in llaves if fila[0] != id]
    print(f"Llaves para ID {id} eliminadas")
    return llaves

def main():
    print("////////////////////////// UDB - DSS101 G01T  ///////////////////////")
    print("////// Diego Martinez, Brian Landaverde, Hector Rodriguez ///////////")
    print("///////////////////////// CIFRADO POLIMORFICO ///////////////////////")
    print("////////////////////////////// SERVIDOR /////////////////////////////\n")

    llaves = []

    while True:
        print("\nEsperando mensaje... (deje vacio para salir)")
        mensaje = input("Ingrese el mensaje completo: ").strip()
        
        if not mensaje:
            break
        
        if len(mensaje) < 13:
            print("Error: Mensaje demasiado corto")
            continue
        
        try:
            id = mensaje[:6]
            typo = mensaje[6:9]
            
            if typo == "FCM":
                if len(mensaje) != 21:
                    print("Error: Mensaje FCM debe tener 21 caracteres")
                    continue
                payload = mensaje[9:-4]
                llaves = procesar_fcm(llaves, id, payload)
            
            elif typo == "0RM":
                if len(mensaje) < 13:
                    print("Error: Mensaje RM demasiado corto")
                    continue
                payload = mensaje[9:-4]
                psn = mensaje[-4:]
                llaves = procesar_rm(llaves, id, payload, psn)
            
            elif typo == "KUM":
                if len(mensaje) != 21:
                    print("Error: Mensaje KUM debe tener 21 caracteres")
                    continue
                payload = mensaje[9:-4]
                llaves = procesar_kum(llaves, id, payload)
            
            elif typo == "LCM":
                if len(mensaje) != 21:
                    print("Error: Mensaje LCM debe tener 21 caracteres")
                    continue
                llaves = procesar_lcm(llaves, id)
            
            else:
                print("Error: Tipo de mensaje no reconocido")
        
        except Exception as e:
            print(f"Error procesando mensaje: {str(e)}")

    print("\nServidor terminado")

if __name__ == "__main__":
    main()