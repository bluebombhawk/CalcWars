const scaleFactor = 10.0
const playerSize = 1.0
const height = document.getElementById("game_display").height
const width = document.getElementById("game_display").width
var my_coords = [0,0]
let my_vel = [0,0]
let my_acc = [0,0]
const center = [0,0]
const movement_vector = document.getElementById("send_vector").value.split(",")/*.substring(1,document.getElementById("send_vector").value.length-1)*/
let code = document.getElementById("code").value
console.log("Updating Code:",code)
let username = document.getElementById("username").value
const x_min = -50 * scaleFactor
const x_max = 50 * scaleFactor
const y_max = 50 * scaleFactor
const y_min = -50 * scaleFactor
const vel_max = 2.5
const vel_min = -2.5
const acc_mult = 0.6
const air_res = 0.4
let real_coords = [0,0]
let real_vel = [0,0]
let last_local_physics_tick = Date.now()
let new_data = false;
let send_equation = false;
let other_player_xs = []
let other_player_ys = []
let other_player_x_vels = []
let other_player_y_vels = []
let other_player_x_accs = []
let other_player_y_accs = []
let real_other_x_accs = []
let real_other_y_accs = []
let real_other_x_vels = []
let real_other_y_vels = []
// import io from 'socket.io-client'

const socket = io('127.0.0.1:5000')
console.log("socket",socket)
let data = {}
let xs = []
let ys = []

// function update(){
//   console.log("Updating...");
//   return "a";
// }

drawPlayer = function(ctx,x,y){
  // console.log("Drawing Player")
  ctx.beginPath()
  // console.log("coords",x-my_coords[0]+width/2,my_coords[1]-y+height/2,playerSize*scaleFactor,0,Math.PI * 2.0)

  ctx.arc(x-my_coords[0]+width/2,my_coords[1]-y+height/2,playerSize*scaleFactor,0,Math.PI * 2.0)
  ctx.stroke()
}

startgame = function(){
var submit_button = document.getElementById("submit")
var canvas = document.getElementById("game_display")
var ctx = canvas.getContext("2d")
let fire_button = document.getElementById("fire")
fire_button.onclick = function(){
  console.log("FIRE!")
  send_equation = true
}
ctx.moveTo(0,0)
// pointxs = document.getElementById("pointxs").value.split(", ")
// pointys = document.getElementById("pointys").value.split(", ")
console.log(document.getElementById("myx"))
my_coords[0] = Math.floor(document.getElementById("myx").value*scaleFactor)
my_coords[1] = Math.floor(document.getElementById("myy").value*scaleFactor)
console.log(my_coords)
console.log("Hello,World!")
// console.log(pointxs)
ctx.moveTo(scaleFactor*pointxs[0]-my_coords[0]+width/2,my_coords[1]+height/2-scaleFactor*pointys[0])
for(var i = 0; i < pointxs.length; i++){
    ctx.lineTo(scaleFactor*pointxs[i]-my_coords[0]+width/2,my_coords[1]+height/2-scaleFactor*pointys[i])
    ctx.stroke()
}
ctx.strokeStyle = "Green"
drawPlayer(ctx,my_coords[0],my_coords[1])
ctx.strokeStyle = "Red"
for(let i = 0; i < other_player_xs.length; i++){
  drawPlayer(ctx,other_player_xs[i],other_player_ys[i])
}
ctx.strokeStyle = "Black"
drawPlayer(ctx,center[0],center[1])
// setInterval(update(),2000)
// setTimeout(function(){submit_button.click()},1000)
}
function local_physics(delta){
  tick_now = Date.now()
  delta = (tick_now - last_local_physics_tick)/1000.0
  last_local_physics_tick = tick_now
  var canvas = document.getElementById("game_display")
  var ctx = canvas.getContext("2d")
  if(!new_data){
    my_vel[0] = Math.min(Math.max(my_vel[0]+my_acc[0] * delta,vel_min),vel_max)
    my_vel[1] = Math.min(Math.max(my_vel[1]+my_acc[1] * delta,vel_min),vel_max)
    my_coords[0] = Math.min(Math.max(my_coords[0]+my_vel[0] * delta * scaleFactor,x_min),x_max)
    my_coords[1] = Math.min(Math.max(my_coords[1]+my_vel[1] * delta * scaleFactor,y_min),y_max)
    console.log("vel",my_vel)
    console.log("coords",my_coords)
    if(my_acc[0]==0){
      my_vel[0] *= (1 - air_res * delta)
    }
    if(my_acc[1]==0){
      my_vel[1] *= (1 - air_res * delta)
    }
    for(let i = 0; i < other_player_xs.length; i++){
      other_player_x_vels[i] = Math.min(Math.max(other_player_x_vels[i]+other_player_x_accs[i] * delta,vel_min),vel_max)
      other_player_y_vels[i] = Math.min(Math.max(other_player_y_vels[i]+other_player_y_accs[i] * delta,vel_min),vel_max)
      other_player_xs[i] = Math.min(Math.max(other_player_xs[i]+other_player_x_vels[i] * delta * scaleFactor,x_min),x_max)
      other_player_ys[i] = Math.min(Math.max(other_player_ys[i]+other_player_y_vels[i] * delta * scaleFactor,y_min),y_max)
      // console.log("vel",my_vel)
      // console.log("coords",my_coords)
      if(other_player_x_accs[i]==0){
        other_player_x_vels[i] *= (1 - air_res * delta)
      }
      if(other_player_y_accs[i]==0){
        other_player_y_vels[i] *= (1 - air_res * delta)
      }
    }
  }else{
    my_vel[0] = real_vel[0]
    my_vel[1] = real_vel[1]
    my_coords[0] = real_coords[0]
    my_coords[1] = real_coords[1]
    other_player_xs = real_other_xs
    other_player_ys = real_other_ys
    other_player_x_vels = real_other_x_vels
    other_player_y_vels = real_other_y_vels
    other_player_x_accs = real_other_x_accs
    other_player_y_accs = real_other_y_accs
    new_data = false
  }

  ctx.clearRect(0,0,width,height)
  ctx.beginPath()
  ctx.moveTo(scaleFactor*xs[0]-my_coords[0]+width/2,my_coords[1]+height/2-scaleFactor*ys[0])
  for(var i = 0; i < xs.length; i++){
      ctx.lineTo(scaleFactor*xs[i]-my_coords[0]+width/2,my_coords[1]+height/2-scaleFactor*ys[i])
      ctx.stroke()
  }
  ctx.strokeStyle = "Green"
  drawPlayer(ctx,my_coords[0],my_coords[1])
  ctx.strokeStyle = "Red"
  for(let i = 0; i < other_player_xs.length; i++){
    drawPlayer(ctx,other_player_xs[i],other_player_ys[i])
  }
  ctx.strokeStyle = "Black"
  drawPlayer(ctx,center[0],center[1])
}
update_data = function(){
  data['send_vector'] = movement_vector
  data['code'] = code
  data['username'] = username
  data['equation'] = document.getElementById('equation').value
  console.log(data);
  // console.log("Equation",equation)
}
interpret_data = function(msg){
  if(msg["code"]!=code){
    return // This is very stupid but might work
  }
  if(msg['dead']){
    console.log("Oh no, I'm dead!")
    document.getElementById("dead").style = ""
    return false
  }
  code = msg["code"]
  xs = msg["xs"]
  ys = msg["ys"]
  my_coords[0] = msg["x"] * scaleFactor
  my_coords[1] = msg["y"] * scaleFactor
  my_vel[0] = msg["x_vel"]
  my_vel[1] = msg["y_vel"]
  real_coords[0] = msg["x"] * scaleFactor
  real_coords[1] = msg["y"] * scaleFactor
  real_vel[0] = msg["x_vel"]
  real_vel[1] = msg["y_vel"]
  my_acc[0] = msg["x_acc"]
  my_acc[1] = msg["y_acc"]
  other_player_xs = msg["other_player_xs"].map(function(x) {return x * scaleFactor})
  other_player_ys = msg["other_player_ys"].map(function(x) {return x * scaleFactor})
  other_player_x_vels = msg["other_player_x_vels"]
  other_player_y_vels = msg["other_player_y_vels"]
  other_player_x_accs = msg["other_player_x_accs"]
  other_player_y_accs = msg["other_player_y_accs"]
  real_other_xs = msg["other_player_xs"].map(function(x) {return x * scaleFactor})
  real_other_ys = msg["other_player_ys"].map(function(x) {return x * scaleFactor})
  real_other_x_vels = msg["other_player_x_vels"]
  real_other_y_vels = msg["other_player_y_vels"]
  real_other_x_accs = msg["other_player_x_accs"]
  real_other_y_accs = msg["other_player_y_accs"]
  new_data = true;
  update_game()
  return true;
}
function update_game(){
  var submit_button = document.getElementById("submit")
  var canvas = document.getElementById("game_display")
  var ctx = canvas.getContext("2d")
  ctx.clearRect(0,0,width,height)
  ctx.beginPath()
  ctx.moveTo(scaleFactor*xs[0]-my_coords[0]+width/2,my_coords[1]+height/2-scaleFactor*ys[0])
  for(var i = 0; i < xs.length; i++){
      ctx.lineTo(scaleFactor*xs[i]-my_coords[0]+width/2,my_coords[1]+height/2-scaleFactor*ys[i])
      ctx.stroke()
  }
  ctx.strokeStyle = "Green"
  drawPlayer(ctx,my_coords[0],my_coords[1])
  ctx.strokeStyle = "Red"
  for(let i = 0; i < other_player_xs.length; i++){
    drawPlayer(ctx,other_player_xs[i],other_player_ys[i])
  }
  ctx.strokeStyle = "Black"
  drawPlayer(ctx,center[0],center[1])
}
window.onload = function(){
  console.log("abc")
  startgame()
}
document.onkeydown = function(event){
  const value_to_set = '1'
  switch(event.key){
    case 'w':
      movement_vector[0] = value_to_set
      break
    case 'ArrowUp':
      movement_vector[0] = value_to_set
      break
    case 'd':
      movement_vector[1] = value_to_set
      break
    case 'ArrowRight':
      movement_vector[1] = value_to_set
      break
    case 's':
      movement_vector[2] = value_to_set
      break
    case 'ArrowDown':
      movement_vector[2] = value_to_set
      break
    case 'a':
      movement_vector[3] = value_to_set
      break
    case 'ArrowLeft':
      movement_vector[3] = value_to_set
      break

  }
  document.getElementById("send_vector").value = movement_vector
}

document.onkeyup = function(event){
  const value_to_set = '0'
  switch(event.key){
    case 'w':
      movement_vector[0] = value_to_set
      break
    case 'ArrowUp':
      movement_vector[0] = value_to_set
      break
    case 'd':
      movement_vector[1] = value_to_set
      break
    case 'ArrowRight':
      movement_vector[1] = value_to_set
      break
    case 's':
      movement_vector[2] = value_to_set
      break
    case 'ArrowDown':
      movement_vector[2] = value_to_set
      break
    case 'a':
      movement_vector[3] = value_to_set
      break
    case 'ArrowLeft':
      movement_vector[3] = value_to_set
      break

  }
  document.getElementById("send_vector").value = movement_vector
}

socket.on('connect',function(){
  console.log("Socket Connected")
  // socket.send({
  //   "Initializing Connection":"a",
  //   "username":username,
  // })
  setInterval(local_physics,100)
  send_data()
})
socket.on('message',function(msg){
  console.log("message received",msg)
  if(interpret_data(msg)==false){
    return
  }
  setTimeout(send_data,500)
})
function send_data(){
  update_data()
  console.log('send_vector',data['send_vector'])
  data['send_equation'] = send_equation
  send_equation = false
  socket.send(data)
}