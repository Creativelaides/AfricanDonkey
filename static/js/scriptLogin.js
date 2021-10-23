function  validar_formulariologin(){

    vEmail =  document.getElementById("email").value;
    var expReg= /^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$/;

    vPassword = document.getElementById("password").value;
   
    if ( vEmail == "" ){
        alert("El campo Correo Electrónico no debe estar vacío.");
        return false;
    }else if ( expReg.test( vEmail ) == false ){
        alert("Correo no válido.")
        return false;
    }else if ( vPassword == "" ){
        alert("El campo Contraseña no debe estar vacío.");
        return false;
    }else if ( vPassword.length < 8 ) {
        alert("El campo Contraseña debe tener mínimo 8 caracteres.");
        return false;
    }

}


const iconEye5= document.querySelector(".eye2");
iconEye5.addEventListener('click', function(){
    
    const icon2 = document.querySelector("i")
    if(document.getElementById('password').type === 'password'){
        document.getElementById('password').type = "text"
        icon2.classList.remove('fa-eye-slash');
        icon2.classList.add('fa-eye');
    }else{
        document.getElementById('password').type = "password"
        icon2.classList.remove('fa-eye');
        icon2.classList.add('fa-eye-slash');
    }
},true)


