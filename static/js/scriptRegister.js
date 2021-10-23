function  validar_formulario(){

    vEmail =  document.getElementById("email").value;
    var expReg= /^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$/;

    password = document.getElementById("password").value;
    vPassword = document.getElementById("vepassword").value;

   
    if ( vEmail == "" ){
        alert("El campo Correo Electrónico no debe estar vacío.");
        return false;
    }else if ( expReg.test( vEmail ) == false ){
        alert("Correo no válido.")
        return false;
    }else if ( password == "" ){
        alert("El campo Contraseña no debe estar vacío.");
        return false;
    }else if ( password.length < 8 ) {
        alert("El campo Contraseña debe tener mínimo 8 caracteres.");
        return false;
    }else if ( password!=vPassword){
        alert("La contraseña no coincide")
    }
}

const iconEye = document.querySelector(".eye");
iconEye.addEventListener('click', function(){
    const icon = document.querySelector("i")
    if(document.getElementById('password').type === 'password'){
        document.getElementById('password').type = "text"
        document.getElementById('vepassword').type = "text"
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }else{
        document.getElementById('password').type = "password"
        document.getElementById('vepassword').type = "password"
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    }
})

// const iconEye1 = document.querySelector(".eye1");
// iconEye1.addEventListener('click', function(){
//     const icon1 = document.querySelector("i")
//     if(document.getElementById('vepassword').type === 'password'){
//         document.getElementById('vepassword').type = "text"
//         icon1.classList.remove('fa-eye-slash');
//         icon1.classList.add('fa-eye');
//     }else{
//         document.getElementById('vepassword').type = "password"
//         icon1.classList.remove('fa-eye');
//         icon1.classList.add('fa-eye-slash');
//     }
// })


window.addEventListener('load',function(){

    document.getElementById('fecha').type= 'text';
    
    document.getElementById('fecha').addEventListener('blur',function(){
    
    document.getElementById('fecha').type= 'text';
    
    });
    
    document.getElementById('fecha').addEventListener('focus',function(){
    
    document.getElementById('fecha').type= 'date';
    
    });
    
    });