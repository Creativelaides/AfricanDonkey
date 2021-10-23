function  validar_formulario(){
    mensaje = document.getElementById("mensaje").value;
    vEmail =  document.getElementById("email").value;
    var expReg= /^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$/;
   
    if ( vEmail == "" ){
        alert("El campo Correo Electrónico no debe estar vacío.");
        return false;
    }else if ( expReg.test( vEmail ) == false ){
        alert("Correo no válido.")
        return false;
    }else if (mensaje == ""){
        alert("El campo comentarios no debe estar vacio.")
    }

}