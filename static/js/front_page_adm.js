function contac(){
    var padre = document.getElementById('padre');
    var datos = Array('Ronald', 'Gladys', 'Katherin'),
    for (let i = 0; i <= datos.length -1; i++){
        div = document.createElement('div');
        div.setAtribute('id', 'ancla'+i.toString());
        padre.appendChild(div);
        document.getElementById('ancla'+i.toString()).innerHTML = '<button>${datos(i)}</button>';
    }
}
