import functools
from flask import Flask, request, redirect, url_for, render_template, flash,g
import sys
import os
from flask import session##guaradr la info de session del usuario

from flask import json
from flask.helpers import send_from_directory
from db import get_db, close_db
from validaciones import isUsernameValid, isEmailValid, isPasswordValid
import yagmail as yagmail
from flask import flash


from werkzeug.security import generate_password_hash,check_password_hash##compara quitando la salt
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)
app.config['UPLOAD_FOLDER']='./static/imagenes_usuario'

app.secret_key = os.urandom(24)
nombredelaredsocial="AFRIKAN DONKEY"

ALLOWED_EXTENSIONS=set(["png","jpg","jpge","gif","jfif"])
def allowed_file(filename):
    return "." in filename and filename.rsplit(".",1)[1] in ALLOWED_EXTENSIONS


@app.route('/')
@app.route('/login')
def login():
    return render_template('login.html') 

#prueba
@app.route('/cambiarfotoperfil',methods=['GET', 'POST'])
def cambiarfotoperfil():
    if request.method=='POST':
        if "archivo" not in request.files:
            return("no ha completado el formulario")
        f=request.files['archivo']

        if f.filename==" ":
            return("no hay archivo")

        if f and allowed_file(f.filename):
            filename=secure_filename(f.filename)#cambiar las diagonales por -- o slash invertidos
            f.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
            
            db = get_db()
            db.execute(
                    'UPDATE usuariosredsocial SET fotoperfil =? WHERE id = ? '
                        ,
                    (filename,g.usuario[0])
                    )
            db.commit() 
            return redirect(url_for("editperfil")) 
    return "archivo no permitido"
        
    

@app.route('/upload',methods=['GET', 'POST'])#lista para publicar
def upload():
    if request.method=='POST':
        if "archivo" not in request.files:
            return("no ha completado el formulario")
        f=request.files['archivo']

        if f.filename==" ":
            return("no hay archivo")

        if f and allowed_file(f.filename):
            filename=secure_filename(f.filename)#cambiar las diagonales por -- o slash invertidos
            comentarios=request.form['estado']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
            db = get_db()
            db.execute(
                    'INSERT INTO imagenes (id,imagen,comentarios,reacciones) VALUES (?,?,?,?) '
                        ,
                    (g.usuario[0],filename,comentarios,"")
                    )
            db.commit() 
            return redirect(url_for("fronpage")) 
        return "archivo no permitido"
        
   
#fin prueba

@app.route('/uploads/<filename>',methods=['GET', 'POST'])
def getfile(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)

@app.route('/login1',methods=['GET', 'POST'])##borreesto para probar /<email>/<password>
def login1():#
    if g.usuario:
        return redirect(url_for('fronpage'))
    if request.method == 'POST':
        email=request.form['email']
        password= request.form['password']            
        error = None
        db = get_db()
        if not email:
            error = "Usuario requerido."
            flash(error)
        if not password:
            error = "Contraseña requerida."
            flash(error)
            
        if error is not None:
            return render_template('login.html')

        else:#si no hay errores
            
            ##preba 
            user = db.execute(
                    'SELECT id,nombre,apellido,usuario,fecha_nacimiento,email,password,rol,validacion,pais,intereses,bloqueado FROM Usuariosredsocial WHERE email = ? '
                    ,     # 0    1       2        3           4           5      6      7     8        9     10         11     
                    (email,)##modifique aqui
                ).fetchone()
            
            
            
            if user is None:
                    flash('Usuario y contraseña no registrados-intenta registrarte!')
                    return render_template("login.html")
            else:
                
                if check_password_hash(user[6],password) and user[8]=="1" and user[11]=='0':
                    flash("bienvenido: "+email)
                    db = get_db()
                    user = db.execute(
                    'SELECT * FROM Usuariosredsocial WHERE email = ?'
                    ,
                    (email,)
                    ).fetchone()
                    session.clear()
                    session['id_usuario']=user[0]
                    session['nombre']=user[1]+"  "+user[2]
                    session['email']=user[5]
                    session['rol']=user[7]
                    session['fecha']=user[4]
                    session['img']=user[9]

                    flash('Bienvenido a '+nombredelaredsocial)
                    
                    return redirect(url_for('fronpage'))##prueba con /<email>
                    
                if check_password_hash(user[6],password):
                    
                    flash("cuenta no validada")
                    return render_template("login.html")
                else:
                    flash("contraseña no valida")
                    return render_template("login.html")

    else:
        return render_template("login.html")

##decorador para session 

@app.before_request#lista
def cargar_usuario_registrado():
    ##print("entro en before request")  
    id_usuario=session.get('id_usuario')
    if id_usuario is None:
        g.usuario=None
    else:
        db=get_db()
        user=db.execute(
            'UPDATE usuariosredsocial SET estado = 1 WHERE  id = ?'
            ,
            (id_usuario,)##modifique aqui
        ).fetchone() 
        db.commit()
        g.usuario=get_db().execute(
            'SELECT id,nombre,apellido,usuario,fecha_nacimiento,email,password,rol,validacion,pais,intereses,fotoperfil,estado,bloqueado FROM Usuariosredsocial WHERE id = ? '
            ,      # 0   1       2        3            4          5     6       7     8         9     10       11        12       13
        (id_usuario,)##modifique aqui
        ).fetchone() 
        #print(g.usuario[11])

@app.before_request#lista
def cargar_listade_amigos():
    
    id_usuario=session.get('id_usuario')
    if id_usuario is None:
        g.contactos=None
    else:#hay inicio de sesion
        
        db = get_db()
        user = db.execute(##prepared stament
            'SELECT amigos FROM contactos WHERE id= ? '
            ,
            (g.usuario[0],)
        ).fetchall()
        #print("id_amigo"+user[0])
        data21=[]
        datacontactos=[]
        for j in user:
            data21.append(j[0])#contiene los id de los contactos

        for k in data21:

        ##nueva consulta para hallar los datos de los contactos
            user=get_db().execute(
                'SELECT id,nombre,apellido,usuario,fecha_nacimiento,email,password,rol,validacion,pais,intereses,fotoperfil,estado FROM Usuariosredsocial WHERE id = ? '
                 ,      # 0   1       2        3            4          5     6       7     8         9     10       11        
            (k,)##modifique aqui
            ).fetchall() 
            
            if user==[]:
                datacontactos=[("0","0","0","0","0","0","0","0","0","0","0","0","0")]#agrege un 0 de mas probando estado
            else:
                datacontactos.append(user)
        g.contactos=datacontactos

            
        """
        if datacontactos==[]:
            datacontactos.append()
            print(datacontactos)
            g.contactos=datacontactos
            print(g.contactos)
        """
       
        
"""
        if user=="0":
            data.remove(" ")
            data.append("0")
            g.contactos=data
            
        else:
            data.remove(" ")
            for k in user:
                data.append(k)
            
            data1=data[0][0].split(sep="-")
            
            for i in range(len(data1)):
                db = get_db()
                user = db.execute(
                    'SELECT id,nombre,apellido,usuario,fecha_nacimiento,email,password,rol,validacion,pais,intereses FROM Usuariosredsocial WHERE id = ? '
                        ,
                    (data1[i],)##modifique aqui
                ).fetchone()
                data3.append(user)
            g.contactos=set([num for num in data3 if data3.count(num)>1])
        print(g.contactos)
"""
@app.before_request#lista
def cargar_Mensajes():
    id_usuario=session.get('id_usuario')
    if id_usuario is None:
        g.mensajes=None
        g.mensajesenviados=None
        g.mensajesrecibidos=None
    else:
        g.mensajesenviados=get_db().execute(
            'SELECT M.ASUNTO,M.mensaje,UR.usuario,M.to_id FROM mensajes AS M INNER JOIN usuariosredsocial AS UR ON M.to_id=UR.id WHERE M.from_id=?'
            ,      
        (id_usuario,)
        ).fetchall() 
        
        g.mensajesrecibidos=get_db().execute(
            'SELECT M.ASUNTO,M.mensaje,UR.usuario,M.from_id FROM mensajes AS M INNER JOIN usuariosredsocial UR ON M.from_id=UR.id WHERE M.to_id=? '
            ,     
        (id_usuario,)
        ).fetchall() 
        g.solicitudes=get_db().execute(
            'SELECT UR.id,UR.usuario,UR.email,SA.from_id FROM solicitudesdeamistad AS SA INNER JOIN usuariosredsocial AS UR ON SA.from_id=UR.id WHERE SA.to_id=? '
            ,      
        (id_usuario,)
        ).fetchall()
        #print("solicitudes")#(id de quien envio,usuario de quien envio , email de quien envio,id de quien envio )
        #print(g.solicitudes)
        #print("mensajes enviados")#(asunto, mensaje ,usuario a quien envio , id usuario destinatario )
        #print(g.mensajesenviados)
        #print("mensajes recibidos")#(asunto, mensaje ,usuario  que envio , id usuario que envio )
        #print(g.mensajesrecibidos)
        
        
         
        


@app.route('/registro', methods=['GET', 'POST'])#lista
def registro():
    if g.usuario:
        return redirect(url_for('fronpage'))
    if request.method == 'POST': 
        nombre= request.form['Nombres']  
        apellido= request.form['Apellidos'] 
        
        fecha=request.form['fecha_Nacimiento'] 
        email = request.form['email']
        usuario=nombre+"_"+apellido
        pais=request.form['pais']
        intereses=request.form['intereses']
       
        a= request.form['password']##cambio intento
        b= request.form['vepassword']

        
    
        rol="usuario"
        validacion="0"##cambiar luego a 0 por defecto para hacer validacion por codigo
        ##verificaciones
        error = None
        # Validar aquí en el servidor.
        """ if not isUsernameValid(usuario): # si el usuario está mal
            error = "El usuario debe ser alfanumerico o incluir solo '.','_','-'"
            flash(error) """
        if not isEmailValid(email):#si el email Está mal
            error = "Correo invalido"
            flash(error)
        if not isPasswordValid(a): #si password Está mal
            error = "La contraseña debe contener al menos una minúscula, una mayúscula, un número y 8 caracteres"
            flash(error)

        if a != b:
            error = 'las contraseñas no cohinciden'
            flash(error)
   
     ## verificar si hay errores 
        if error is not None:#si hay errores
            return render_template("register.html")
        else:
            
            db = get_db()
            user = db.execute(##prepared stament
                    'SELECT * FROM Usuariosredsocial WHERE email = ?'
                    ,
                    (email,)
                ).fetchone()
            
            if user is not None:
                error = "Correo electrónico ya existe."
                flash(error)
                return render_template("register.html")
            else:##ingresar a base de datos
                password=generate_password_hash(a)
                session['code']=enviarcorreodevalidacion(email)
                fotoperfil="perfilgenerico.jpg"
                db.execute(
                  'INSERT INTO Usuariosredsocial (nombre,apellido,usuario,fecha_nacimiento,email,password,rol,validacion,codigovalidacion,pais,intereses,fotoperfil,estado,bloqueado) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?) '
                    ,
                (nombre,apellido,usuario,fecha,email,password,rol,validacion,session['code'],pais,intereses,fotoperfil,'0','0')
                )
                db.commit() 

                db = get_db()
                user = db.execute(##prepared stament
                    'SELECT id FROM Usuariosredsocial WHERE email = ?'
                    ,
                    (email,)
                ).fetchone()

                db.execute(
                  'INSERT INTO contactos (id,amigos) VALUES (?,?) '
                    ,
                (user[0],'0')
                )
                db.commit() 
                
                session['email']=email
                flash('Revisa tu correo para activar tu cuenta')
                ##abrir template de validar correo
                #si presiona el codigo enviado y coincide mandarlo a login, legoinsertar los datos y redirigir a login
                #sino dejarlo alli mismo
                # 3 Abrir el formulario Login.
                ## return redirect( url_for( 'login' ) )
                return render_template("confirmacionCuenta.html",email=email)
    else:
        return render_template("register.html")


##login requerido
def login_required(view):
    @functools.wraps( view ) # toma una función utilizada en un decorador y añadir la funcionalidad de copiar el nombre de la función.
    def wrapped_view(**kwargs):
        if g.usuario is None:
            return redirect( url_for( 'login' ) )
        return view( **kwargs )
    return wrapped_view

@app.route('/cerrarsesion', methods=['GET', 'POST'])#lista
@login_required
def cerrarsesion(): 
    db=get_db()
    user=db.execute(
            'UPDATE usuariosredsocial SET  estado = 0 WHERE  id = ? AND estado = ?'
            ,
            (g.usuario[0],'1')##modifique aqui
    )
    db.commit()
    session.clear()
    return render_template('login.html') 

@app.route('/recuperarcontraseña2') ##ligeramente igual a envio de contraseña (no se usa)
def recuperarcontraseña():
    ##flash("recuperando contraseña")
    return render_template("recuperarContraseña2.html")


@app.route('/send', methods=['GET', 'POST']) #enviar mensajes en general
@login_required
def send():
    
    if request.method=="POST":
        from_id=g.usuario[0]
        asunto=request.form["asunto"]
        mensaje=request.form['mensaje']
        email=request.form['email']
        print(asunto)
        error=None
        if not isEmailValid(email):#si el email Está mal
            error = "Correo invalido"
            flash(error)
        if asunto=="":
            error = "debe tener un asunto"##debo validar cuando este vacio
            flash(error)
        if mensaje=="":##debo validar cuando este vacio
            error = "no hay mensaje"
            flash(error)
        if error is None:
            db = get_db()
            user = db.execute(##prepared stament
                    'SELECT * FROM Usuariosredsocial WHERE email = ?'
                    ,
                    (email,)
                ).fetchone()
            
            if user is not None:
                error = "mensaje enviado."
                db.execute(
                        'INSERT INTO mensajes (from_id, to_id,asunto,mensaje) VALUES (?,?,?,?) '
                            ,
                        (from_id,user[0],asunto,mensaje)
                        )
                db.commit() 

                flash(error)
                return render_template("send.html")
            else:##ingresar a base de datos
                error = "email usuario no existe."
                flash(error)
            flash(error)
            return redirect(url_for('send'))
        else:
            
            return redirect(url_for('send'))
    else:
        return render_template("send.html",solicitudes=g.solicitudes,enviados=g.mensajesenviados,recibidos=g.mensajesrecibidos,usuario=g.usuario[1]+" "+g.usuario[2],rol=g.usuario[7],foto=g.usuario[11])


    

@app.route('/enviodecontraseña', methods=['GET', 'POST'])   ##aqui responderecuperacion de contraseña, en proceso
def enviocontraseña():
    email= request.form['email']
    a=recordarcontraseña(email)
    newpassword=generate_password_hash(a)
    db = get_db()
    users=db.execute(
                'UPDATE usuariosredsocial SET password = ? WHERE  email = ? '
                ,
                (newpassword,email)
    )
    db.commit()
    flash("hemos enviado un correo a "+ email +"para restablecer la contraseña, sigue las instrucciones")
    return redirect(url_for('login'))

@app.route('/soportetecnico', methods=['GET', 'POST'])#lista
def soportetecnico():
    if g.usuario:
        return redirect(url_for('fronpage'))
    if request.method == 'POST': 
        db = get_db()   
        email=request.form['email']
        mensaje=request.form['mensaje']
        error=None
        if email=="":
            error="el campo email debe ser validado"
            ##flash(error)
        if mensaje=="":
            error="el campo mensaje debe ser validado"
            ##flash(error)
        if error is None:
            db.execute(
                    'INSERT INTO smsserviciotecnico (email, comentarios) VALUES (?,?) '
                            ,
                (email,mensaje)
                        )
            db.commit() 
            flash("mensaje enviado con exito")
            return redirect(url_for('login'))
        else:
            flash("hay campos por validar")

    return render_template("soportetecnico.html")

@app.route('/nuevacontraseña', methods=['GET', 'POST']) ##se usa para cambiar contraseña--lista
@login_required
def nuevacontraseña():
    if request.method=="POST":
        a=request.form['password']
        vepassword=request.form['vepassword']
        if a==vepassword:
            password=generate_password_hash(a)
            db = get_db()
            user = db.execute(##prepared stament
                'UPDATE usuariosredsocial SET  password = ? WHERE  password = ? '
                ,
                (password,g.usuario[6])
            ).fetchone()
            db.commit() 
            flash("ya puedes iniciar sesion con tu nueva contraseña")
            enviarcorreodecambiocontraseña(g.usuario[5])
            return redirect( url_for( 'login' ) )
        else:
            flash("contraseñas no coinciden")

    return render_template("nuevaContraseña.html")#se redirigue al formulario validacion de cuenta con el usuario

@app.route('/confirmacioncuenta', methods=['GET', 'POST'])#lista
def confirmarcuenta():
    codigo=request.form["codigo_validacion"]
    ##print(codigo)
    if codigo==session['code']:
        db = get_db()
        user = db.execute(##prepared stament
                'UPDATE usuariosredsocial SET  validacion = 1 WHERE  email = ? AND validacion = ?'
                ,
                (session['email'],'0')##sesion creada al registrarse se limpia al logearse
            ).fetchone()
        db.commit() 
        flash("ya puedes iniciar sesion")
        return redirect( url_for( 'login1' ) )
    else:
        flash("los codigos no coinciden")
        return render_template("confirmacionCuenta.html")

@app.route('/contraseñaok', methods=['GET', 'POST'])##no se usa
def contraseñaok():
    return render_template("contraseñaOk.html")


@app.route('/recuperarcontraseña1', methods=['GET', 'POST']) ##no se utiliza
def corrreo():
    
    return render_template("recuperaciondecontraseña.html")

@app.route('/linkactivacion', methods=['GET', 'POST'])##no se usa
def activacion():
    return render_template("linkActivacionRegister.html")


##aqui responde el enviando corre pa contraseña
@app.route('/index', methods=['GET', 'POST'])##borrar mas adelante no se usa 
def enviodecorreo():
    return redirect(url_for('login'))

@app.route('/mensajeservicio', methods=['GET', 'POST'])##sobra borrar mas adelante
def mensajeservicio():

    return redirect(url_for('login1'))

@app.route('/perfil', methods=['GET', 'POST'])##en desarrollo
@login_required
def profile():
    ##prueba
    data5=[""]
    data6=[""]
    db = get_db()
    
    user = db.execute(##prepared stament
        'SELECT M.imagen,M.comentarios,M.reacciones,M.id,UR.email FROM imagenes AS M INNER JOIN usuariosredsocial AS UR ON M.id=UR.id WHERE M.id= ? ORDER BY num DESC '
        ,
        (g.usuario[0],)
        ).fetchall()

    
    if user==[]:
        data5.clear()
        data5.append("NO TIENES PUBLICACIONES AUN")
    else:
        data5.clear()
        for k in user:
            data5.append(k)
    
    
    ##fin prueba
    return render_template("profile.html",nombre=g.usuario[1]+g.usuario[2],email=g.usuario[5],rol=g.usuario[7],fecha=g.usuario[4],pais=g.usuario[9],intereses=g.usuario[10],foto=g.usuario[11],actividad=data5)

@app.route('/editarperfil', methods=['GET', 'POST'])#casi lista-falta actualizar la informacion
@login_required
def editprofile():
    if request.method=='POST':
        nombre=request.form['nombre']
        pais=request.form['pais']
        fecha=request.form['fecha']
        intereses=request.form['intereses']
        db = get_db()
        users=db.execute(
                'UPDATE usuariosredsocial SET nombre = ?,pais=?,fecha_nacimiento=?, intereses=? WHERE id = ? '
                ,
                (nombre,pais,fecha,intereses,g.usuario[0])
        )
        db.commit()
       
        return redirect(url_for('frompage'))
    return render_template("editperfil.html",nombre=g.usuario[1]+" "+g.usuario[2],email=g.usuario[5],rol=g.usuario[7],fecha=g.usuario[4],pais=g.usuario[9],intereses=g.usuario[10],foto=g.usuario[11])


data3=[]
data4=[]
@app.route('/fronpage', methods=['GET', 'POST'])##lista
@login_required
def fronpage():
    #data=[""]
    data5=[""]
    
    ##publicaciones
    db = get_db()
    
    user = db.execute(##prepared stament
        'SELECT I.imagen,I.comentarios,I.reacciones,UR.email,UR.id,I.num FROM usuariosredsocial AS UR INNER JOIN imagenes AS I ON UR.id=I.id WHERE UR.id= ? UNION ALL SELECT I.imagen,I.comentarios,I.reacciones,UR.email,UR.id,I.num FROM usuariosredsocial AS UR INNER JOIN imagenes AS I ON UR.id=I.id INNER JOIN contactos AS C ON I.id=C.amigos  WHERE C.id=?  ORDER BY I.num DESC '
        ,
        (g.usuario[0],g.usuario[0])
        ).fetchall()
    if user==[]:
        data5.clear()
        data5.append("NO TIENES PUBLICACIONES AUN")
    else:
        data5.clear()
        for k in user:
            data5.append(k)
    
    if g.usuario[7]=="usuario":
        return render_template("front_page_adm.html",usuario=g.usuario[1]+" "+g.usuario[2],rol=g.usuario[7],data2=g.contactos,foto=g.usuario[11],actividad=data5)
    else:
        return render_template("front_page_adm_super.html",usuario=g.usuario[1]+" "+g.usuario[2],rol=g.usuario[7],data2=g.contactos,foto=g.usuario[11],actividad=data5)

@app.route('/solicitudamistad/<id>', methods=['GET', 'POST'])#lista
@login_required
def solicitudamistad(id):
    if request.method == 'POST': 
        flash("solicitud enviada a"+id) 
        db = get_db()
             
        from_id=g.usuario[0]
        to_id=id
        asunto="Solicitud de amistad"
        mensaje=asunto
        db.execute(
                    'INSERT INTO solicitudesdeamistad (from_id, to_id,asunto) VALUES (?,?,?) '
                            ,
                (from_id,id,asunto)
                        )
        db.commit() 
                
        return redirect(url_for("fronpage")) 

@app.route('/resultadobusqueda', methods=['GET', 'POST'])#lista
@login_required
def busqueda():
    if request.method == 'POST': 
        data=[""]
        nombrebusqueda=request.form['search']
        if nombrebusqueda=="":
            data.append("no hay concidencias")
        else:
            db = get_db()
            user = db.execute(##prepared stament
                    'SELECT * FROM Usuariosredsocial WHERE nombre LIKE ? OR apellido LIKE ? '
                    ,
                    (nombrebusqueda,nombrebusqueda)
                    ).fetchall()
            
            if user is None:
                data.remove("")
                data.append("no hay concidencias")
            else:
                data.remove("")
                for k in user:
                    data.append(k)
            
            session["id_busqueda"]=g.usuario[0]
        return render_template("resultaBusqueda.html",data1=data)



@app.route('/sendsms/<email>', methods=['GET', 'POST'])#enviar mensajes a amigos
@login_required
def sendsms(email):
    
    if request.method=="POST":
        from_id=g.usuario[0]
        asunto=request.form["asunto"]
        mensaje=request.form['mensaje']
        email=email
        
        error=None
        
        if asunto=="":
            error = "debe tener un asunto"##debo validar cuando este vacio
            flash(error)
        if mensaje=="":##debo validar cuando este vacio
            error = "no hay mensaje"
            flash(error)
        if error is None:
            db = get_db()
            user = db.execute(##prepared stament
                    'SELECT * FROM Usuariosredsocial WHERE email = ?'
                    ,
                    (email,)
                ).fetchone()
            
            if user is not None:
                error = "mensaje enviado."
                db.execute(
                        'INSERT INTO mensajes (from_id, to_id,asunto,mensaje) VALUES (?,?,?,?) '
                            ,
                        (from_id,user[0],asunto,mensaje)
                        )
                db.commit() 

                flash(error)
                return redirect(url_for('fronpage'))
               
            
        else:
           return render_template("sendsms.html",email=email)
           
            
    else:
        
        return render_template("sendsms.html",email=email,usuario=g.usuario[1]+" "+g.usuario[2],rol=g.usuario[7],foto=g.usuario[11],from_email=g.usuario[5])

#falta enlazarlo a la plantilla
@app.route('/verusuarios', methods=['GET', 'POST'])#enviar mensajes a amigos---lista
@login_required
def verusuarios():
    db = get_db()
    user = db.execute(##prepared stament
            'SELECT * FROM Usuariosredsocial'
            ,
    ).fetchall()
    print(g.usuario[11])
    return render_template("verusuario.html",data=user,foto=g.usuario[11],rol=g.usuario[7],usuario=g.usuario[1]+" "+g.usuario[2])


@app.route('/cambiarrol/<id>/<rol>', methods=['GET', 'POST'])#listo
@login_required
def cambiarrol(id,rol):
    if request.method=="POST":
        nuevorol=request.form['rol']
        print(nuevorol)
        print(id)
        print(rol)
        db = get_db()
        users=db.execute(
                'UPDATE usuariosredsocial SET rol = ? WHERE id = ? AND rol = ?'
                ,
                (nuevorol,id,rol)
        )
        db.commit()
        db = get_db()
        user = db.execute(##prepared stament
            'SELECT * FROM Usuariosredsocial'
            
        ).fetchall()
        return redirect(url_for('verusuarios'))
    else:
        db = get_db()
        user=db.execute(
            'SELECT nombre,apellido, email,rol,fotoperfil,id,bloqueado FROM Usuariosredsocial WHERE id = ? '
            ,      # 0   1       2        3            4          5     6       7     8         9     10       11        12
        (id,)##modifique aqui
        ).fetchone() 
        

        return render_template("roll_assignment.html",usuario=user[0]+" "+user[1],email=user[2],rol=user[3],foto=g.usuario[11],id=user[5],bloqueado=user[6],rolperfil=g.usuario[7],usuarioperfil=g.usuario[1]+" "+g.usuario[2])

    #return render_template("verusuarios.html",data=user)
    

##filtrar actividad propia y de amigos



@app.route('/mensajes', methods=['GET', 'POST'])#enviar mensajes a amigos--enlazar con template send
@login_required
def mensajesusuario():


    return render_template("mensajesusuario.html",solicitudes=g.solicitudes,enviados=g.mensajesenviados,recibidos=g.mensajesrecibidos)


@app.route('/confirmarsolicitud/<id>', methods=['GET', 'POST'])#enviar mensajes a amigos--listo
@login_required
def confirmar(id): 
    db = get_db()
    db.execute(
        'DELETE FROM contactos WHERE id = ? AND  amigos = ? '
        ,
        (g.usuario[0],'0')
    )
    db.commit() 
    db = get_db()
    db.execute(
        'DELETE FROM solicitudesdeamistad WHERE from_id = ? AND  to_id = ?  '
        ,
        (id,g.usuario[0])
    )
    db.commit()
    db = get_db()
    db.execute(
        'INSERT INTO contactos (id,amigos) VALUES (?,?) '
        ,
        (g.usuario[0],id)
    )
    db.commit() 
    db = get_db()
    db.execute(
        'INSERT INTO contactos (id,amigos) VALUES (?,?) '
        ,
        (id,g.usuario[0])
    )
    db.commit() 
    return render_template("mensajesusuario.html",solicitudes=g.solicitudes,enviados=g.mensajesenviados,recibidos=g.mensajesrecibidos)




@app.route('/rechazarsolicitud/<id>', methods=['GET', 'POST'])#enviar mensajes a amigos--listo
@login_required
def rechazar(id):   
    db = get_db()
    db.execute(
        'DELETE FROM solicitudesdeamistad WHERE from_id = ? AND  to_id = ? '
        ,
        (id,g.usuario[0])
    )
    db.commit() 
    return render_template("mensajesusuario.html",solicitudes=g.solicitudes,enviados=g.mensajesenviados,recibidos=g.mensajesrecibidos)
        
@app.route('/eliminar/<id>', methods=['GET', 'POST'])#enviar mensajes a amigos--listo
@login_required
def bloquearcuenta(id):   
    db = get_db()
    db=get_db()
    user=db.execute(
            'UPDATE usuariosredsocial SET  bloqueado = 1 WHERE  id = ? '
            ,
            (id,)##modifique aqui
    )
    db.commit()
    db = get_db()
    user = db.execute(##prepared stament
            'SELECT * FROM Usuariosredsocial'
            ,
    ).fetchall()
    return redirect(url_for('verusuarios'))

@app.route('/reactivar/<id>', methods=['GET', 'POST'])#enviar mensajes a amigos--listo
@login_required
def reactivarcuenta(id):   
    db = get_db()
    db=get_db()
    user=db.execute(
            'UPDATE usuariosredsocial SET  bloqueado = 0 WHERE  id = ? '
            ,
            (id,)##modifique aqui
    )
    db.commit()
    db = get_db()
    user = db.execute(##prepared stament
            'SELECT * FROM Usuariosredsocial'
            ,
    ).fetchall()
    return redirect(url_for('verusuarios'))
    
@app.route('/publicarfoto', methods=['GET', 'POST'])
@login_required
def method_name():
    pass

def enviarcorreodevalidacion(email):

    codigo_verificacion=app.secret_key = os.urandom(6)
    mensajecorreo='Bienvenido a '+nombredelaredsocial+', usa este codigo para validar tu cuenta : '+str(codigo_verificacion)#+enlace
    yag = yagmail.SMTP('socialburroafricano@gmail.com', 'equipo10burroafricano') 
    #contents = ['Hoy es fin de semana, quiero estudiar, estudiar me hace feliz';, '<a href="https://www.python.org/"> hipervínculo del sitio web oficial de Python </a>', './girl.jpg']
    yag.send(to=email, subject='Activa tu cuenta', contents=[mensajecorreo,'<a href="http://127.0.0.1:5000/validaciondecuenta"> validar </a>'])
    ##flash('Revisa tu correo para activar tu cuenta')
    print("codigo de verificacion es:"+str(codigo_verificacion))#prueba en verificacion
    return str(codigo_verificacion)#prueba en verificacion

def enviarcorreodecambiocontraseña(email):

    codigo_verificacion=app.secret_key = os.urandom(6)
    mensajecorreo='Bienvenido a '+nombredelaredsocial+', tu contraseña ha sido cambiada satisfactoriamente. Si tu has realizado el cambio omite este mensaje si no reportalos a servicio tecnico'
    yag = yagmail.SMTP('socialburroafricano@gmail.com', 'equipo10burroafricano') 
    #contents = ['Hoy es fin de semana, quiero estudiar, estudiar me hace feliz';, '<a href="https://www.python.org/"> hipervínculo del sitio web oficial de Python </a>', './girl.jpg']
    yag.send(to=email, subject='Cambio de contraseña', contents=[mensajecorreo,'<a href="http://127.0.0.1:5000/serviciotecnico"> servicio tecnico </a>'])
    
def recordarcontraseña(email):

    password=app.secret_key = os.urandom(8)
    mensajecorreo='Bienvenido a '+nombredelaredsocial+',hemos generado una contraseña para que puedas acceder,recuerda modificarla apenas ingreses. Contraseña para ingresar : '+str(password)#+enlace
    yag = yagmail.SMTP('socialburroafricano@gmail.com', 'equipo10burroafricano') 
    #contents = ['Hoy es fin de semana, quiero estudiar, estudiar me hace feliz';, '<a href="https://www.python.org/"> hipervínculo del sitio web oficial de Python </a>', './girl.jpg']
    yag.send(to=email, subject='Recuperar contraseña', contents=[mensajecorreo])
    
    return str(password)#prueba en verificacion


""" if __name__ == '__main__':
    #Personalizar port y hacer debug sin necesidad de personalizarlo en terminal
    app.run(debug=True, port=5500)#port=443,ssl_context('','') """
