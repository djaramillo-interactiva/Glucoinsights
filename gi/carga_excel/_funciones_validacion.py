from datetime import datetime, date

# Funcion que valida los datos tipo string
def validar_string(dato, longitud):

    if(isinstance(dato,str)):
        if(dato != ''):
            if(len(dato) <= longitud):
                pass
            else:
                return f'El dato excede la longitud de {longitud} carácteres'
        else:
            return 'El dato esta vacio'
    else:
        return 'El dato no es de tipo texto'
    

# Funcion que valida los datos de numeros tipo enteros
def validar_longitud_numero(numero, longitud):
    numero_absoluto = abs(numero)  # Para manejar números negativos
    contador = 0

    while numero_absoluto > 0:
        contador += 1
        numero_absoluto //= 10  # Reducir el número eliminando un dígito

    if contador <= longitud:
        return True
    else:
        return False


def validar_n_enteros(dato, longitud):

    if dato != '':
        if not isinstance(dato, datetime):
            if isinstance(dato, int):
                if(dato >= 0):
                    if validar_longitud_numero(dato, longitud):
                        pass
                    else:
                        mensaje_error = f"El numero {dato} excede la longitud máxima de {longitud} carácteres"
                        return {'validate' : False , 'entero' : dato, 'error' : mensaje_error }
                else:
                    mensaje_error = 'El numero es menor o igual a cero'
                    return {'validate' : False , 'entero' : '', 'error' : mensaje_error } 
            else:   
                mensaje_error = 'El dato no es númerico'
                return {'validate' : False , 'entero' : '', 'error' : mensaje_error } 
        else:
            mensaje_error = 'El dato no es númerico'
            return {'validate' : False , 'entero' : '', 'error' : mensaje_error } 
    else:
        mensaje_error = 'El dato está vacío'
        return {'validate' : False , 'entero' : '', 'error' : mensaje_error } 



# Funcion que valida los datos de numeros tipo float
max_decimales = 2

def contar_decimales(numero):
    # Convierte el número a una cadena para trabajar con los caracteres
    numero_str = str(numero)
    
    # Verifica si hay un punto decimal en la cadena
    if '.' in numero_str:
        # Encuentra la posición del punto decimal
        indice_punto_decimal = numero_str.index('.')
        
        # Calcula la cantidad de decimales contando los caracteres después del punto
        cantidad_decimales = len(numero_str) - indice_punto_decimal - 1
        
        return cantidad_decimales
    else:
        # Si no hay punto decimal, el número no tiene decimales
        return 0

# def validar_decimales(numero):
#     if isinstance(float, int):
#         # Multiplica el número por 10 elevado a la potencia de max_decimales
#         # multiplicador = 10 ** max_decimales
#         # numero_multiplicado = numero * multiplicador
#         # decimales = contar_decimales(numero)
#         # Verifica si el número multiplicado es un número entero
        
#         return True
    
#     return False


    
    
def ajustar_decimales(numero):
    if isinstance(numero, (float, int)):
        decimales = contar_decimales(numero)
        

        if decimales > 2:
            return "float_excedet"
        else:
            multiplicador = 10 ** max_decimales
            numero_truncado = int(numero * multiplicador) / multiplicador
            return numero_truncado  # Número válido
       
    return None  # No es un número de punto flotante


def validar_n_float(dato):

    if dato != '':
        if isinstance(dato, (float, int)):
            if(dato >= 0):
                
                resultado = ajustar_decimales(dato)
                if (resultado == 0):
                    mensaje_error = f"El dato no contiene un formato decimal valido, o es 0"
                    return {'validate' : False , 'flotante' : '', 'error' : mensaje_error }
                
                if resultado == "float_excedet":
                    mensaje_error = f"El dato excede los 2 decimales"
                    return {'validate' : True , 'flotante' : dato, 'error' : mensaje_error }                    
            else:
                mensaje_error = 'El numero es menor o igual a cero'
                return {'validate' : False , 'flotante' : '', 'error' : mensaje_error }
        else:   
            mensaje_error = 'El dato no es de tipo numérico decimal'
            return {'validate' : False , 'flotante' : '', 'error' : mensaje_error }
    else:
        mensaje_error = 'El dato está vacío'
        return {'validate' : False , 'flotante' : '', 'error' : mensaje_error }
    

# Funcion que valida los datos tipo fecha

def validar_fecha_en_formatos(fecha_str):
    new_fecha = fecha_str.date()
    fecha_sin_hora = ''
    formatos = ["%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y", "%m-%d-%Y", "%m/%d/%Y"]  # Ejemplos de formatos
    for formato in formatos:
        try:
            # Devuelve la fecha si se pudo analizar en un formato válido, esta fecha se devuelve sin hora
            fecha = datetime.strptime(str(new_fecha), formato)
            fecha_sin_hora = fecha.date()
        except ValueError:
            # Intenta con el siguiente formato si la excepción ValueError se genera
            continue  

    if fecha_sin_hora != '':
        return { 'validate' : True , 'date' : fecha_sin_hora }
    else:
        return { 'validate' : False , 'date' : '' }
        

fecha_comodin = '1900-01-01'
def validar_fecha(dato):   

    if(dato != ''):
        if not isinstance(dato, int) and not isinstance (dato, float) and not isinstance (dato, str):
            validar_fecha = validar_fecha_en_formatos(dato)
            if validar_fecha['validate']:
                pass
            else:
                return(fecha_comodin)
        else:
            return(f"El dato {dato} no es de tipo fecha")
    else:
        return("La fecha esta vacia")
        