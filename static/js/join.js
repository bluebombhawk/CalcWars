let name_vals = ["Mr. Benson","Elisa Alvarez-Rosenbloom",
"Abel Asefaw","Julia Barriga Cortez","Eyal Ben-Dov",
"Roza Biewald","Alaan Clarke","Amyrrah Domond",
"Luisa Fechtman Do Rego Macedo","Luke Frantzis-Dahl","Elena Gill",
"Tasnim Haji-Issa","Oliver Henke","Tessa Herrick",
"Priyota Imam","Mohammad Jihad","Chanho Lee",
"Robert Lermusiaux","Abuali Masalimov","Ruby Mckernan",
"Tashi Mulug-Labrang","Dominic Nicholson","Nahin Noor",
"Lucca Olivet","Jay Parmeshwar","Saron Saud",
"Coriolan Thienot-Berthezene","Neva Vuletic"]
name_field = document.getElementById("username");
window.onload = function(){
  name_field.placeholder = name_vals[Math.floor(Math.random()*name_vals.length)]
}