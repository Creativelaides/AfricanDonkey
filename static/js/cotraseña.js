function  validar_formulario(){

    password = document.getElementById("password").value;
    vPassword = document.getElementById("vePassword").value;

  
    if ( password == "" ){
        alert("El campo Contraseña no debe estar vacío.");
        return false;
    }else if ( password.length < 8 ) {
        alert("El campo Contraseña debe tener mínimo 8 caracteres.");
        return false;
    }else if ( password!=vePassword){
        alert("La contraseña no coincide")
    }
}

const iconEye1 = document.querySelector(".eye1");
iconEye1.addEventListener('click', function(){
    const icon1 = document.querySelector("i")
    console.log(icon1)
    if(document.getElementById('password').type === 'password'){
        document.getElementById('password').type = "text"
        document.getElementById('vepassword').type = "text"
        icon1.classList.remove('fa-eye-slash');
        icon1.classList.add('fa-eye');
    }else{
        document.getElementById('password').type = "password"
        document.getElementById('vepassword').type = "password"
        icon1.classList.remove('fa-eye');
        icon1.classList.add('fa-eye-slash');
    }
})