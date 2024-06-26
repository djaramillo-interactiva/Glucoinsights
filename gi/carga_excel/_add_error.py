errores = []

def add_error(numero_fila, documento_p, mensaje_error, nombre_campo):
    errores.append({'numero_fila': numero_fila, 'documento_p': documento_p, 'mensaje_error' :  mensaje_error, 'columna' : nombre_campo }) 

errores_total = []
    
def add_errors_array(errors):
    temp_list = list(errors)
    errores_total.append(temp_list)    

user_loggin_id = []

def add_user_id(id_user):
    user_loggin_id.append(id_user)