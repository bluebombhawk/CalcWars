from flask import Flask, render_template, url_for, request, redirect
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_socketio import SocketIO
import json

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
socketio = SocketIO(app)
CORS(app, resources={r'/':{'origins':'*'}})

db = SQLAlchemy(app)

# class Todo(db.Model):
#     id = db.Column(db.Integer,primary_key=True)
#     content = db.Column(db.String(200),nullable=False)
#     date_created = db.Column(db.DateTime,default=datetime.utcnow)



# Server side code start


import math
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import uuid
import time
import threading

# constants to keep players in check

x_max = 50
x_min = -50
y_max = 50
y_min = -50
vel_max = 2.5
vel_min = -2.5
acc_mult = 0.6
air_res = 0.4


class mathFunction:
  # holds an outer function which is a string and may hold an inner function which is a mathFunctionList
  def __init__(self):
    self.outer_function = None
    self.inner_function = None
  def __str__(self):
    if(self.inner_function==None):
      return str(self.outer_function)
    return(str(self.outer_function)+"\n{\n"+str(self.inner_function)+"\n}")
class mathFunctionList:
  #precondition: an input is passed in in the form of a string, with mathematical functions and operators seperated by spaces
  #postcondition: the string is seperated at spaces into an array of mathFunction objects, with each mathFunction either being a function, a value, an operator, x, or something in parentheses
  def __init__(self,input_string):
    index = 0
    temp_string = ""
    self.objects = list()
    while index<len(input_string):
      while index<len(input_string) and input_string[index] != " " and input_string[index] != "(":
        current_character = input_string[index]
        temp_string+=(current_character)
        index+=1
      if(index>=len(input_string)):
        temp_function = mathFunction()
        temp_function.outer_function = temp_string
        self.objects.append(temp_function)
        break
      current_character = input_string[index]
      if(current_character==" "):
        temp_function = mathFunction()
        temp_function.outer_function = temp_string
        temp_string = ""
        self.objects.append(temp_function)
        index+=1
      elif(current_character=="("):
        temp_function = mathFunction()
        temp_function.outer_function = temp_string
        temp_string = "("
        opening_parentheses = 1
        closing_parentheses = 0
        index+=1
        while opening_parentheses != closing_parentheses and index<len(input_string):
          current_character = input_string[index]
          temp_string+=(current_character)
          if(current_character=="("):
            opening_parentheses+=1
          elif(current_character==")"):
            closing_parentheses+=1
          index+=1
        if(opening_parentheses!=closing_parentheses):
          print("Error: improper parenthesy counts in string: "+input_string)
          return None
        temp_function.inner_function = mathFunctionList(temp_string[1:-1])
        temp_string = ""
        self.objects.append(temp_function)
  def __str__(self):
    string_to_return = "["
    for object in self.objects:
      string_to_return += "\n" + str(object)
    string_to_return += "]"
    return string_to_return


all_operators = {
  # use multiples of 10 so we can add values in between
  "^":30,
  "*":20,
  "/":20,
  "+":10,
  "-":10,
}

def custom_exponent(a,b):
  return math.pow(a,b)

def custom_multiply(a,b):
  return a*b

def custom_divide(a,b):
  return a/b

def custom_add(a,b):
  return a+b

def custom_subtract(a,b):
  return a-b

operator_functions = {
  "^":custom_exponent,
  "*":custom_multiply,
  "/":custom_divide,
  "+":custom_add,
  "-":custom_subtract,
}

def replace_x_with_val(function_list,val):
  for object in function_list.objects:
    if object.outer_function == "x":
      object.outer_function = val
    if object.inner_function != None:
      replace_x_with_val(object.inner_function,val)

def replace_y_with_val(function_list,val):
  for object in function_list.objects:
    if object.outer_function == "y":
      object.outer_function = val
    if object.inner_function != None:
      replace_y_with_val(object.inner_function,val)

def identity(x):
  return x

def negate(x):
  return -x

all_functions = {
  "sin":math.sin, #trig. Pretty normal
  "cos":math.cos,
  "tan":math.tan,
  "arcsin":math.asin, #inverse trig. Comes in handy
  "arccos":math.acos,
  "arctan":math.atan,
  "sinh":math.sinh, #hyperbolic trig. Interesting
  "cosh":math.cosh,
  "tanh":math.tanh,
  "arcsinh":math.asinh, #why?
  "arccosh":math.acosh,
  "arctanh":math.atanh,
  "ln":math.log,
  "log":math.log10,
  "floor":math.floor,
  "ceil":math.ceil,
  "abs":abs,
  "":identity,
  "-":negate,
}
def handle_numeric(function_list):
  for object in function_list.objects:
    if(type(object.outer_function) == type("") and object.outer_function.replace(".","").isnumeric() and object.inner_function == None):
      # print("Float casting")
      object.outer_function = float(object.outer_function)
    if(object.inner_function != None):
      handle_numeric(object.inner_function)

def handle_negative(function_list):
  for object in function_list.objects:
    if type(object.outer_function) == type("a") and len(object.outer_function) > 0 and "-" == object.outer_function[0] and not (object.outer_function in all_operators.keys()):
      temp_object = mathFunction()
      temp_object.outer_function = object.outer_function[1:]
      temp_object.inner_function = object.inner_function
      negative_function = mathFunction()
      negative_function.outer_function = -1
      multiply_function = mathFunction()
      multiply_function.outer_function = "*"
      object_list = [negative_function, multiply_function, temp_object]
      math_function_list = mathFunctionList("")
      math_function_list.objects = object_list
      # print("objects",math_function_list.objects)
      object.outer_function = "" # identity function
      object.inner_function = math_function_list
    if object.inner_function != None:
      handle_negative(object.inner_function)

def replace_functions(function_list):
  for object in function_list.objects:
    if object.outer_function in all_functions.keys():
      object.outer_function = all_functions[object.outer_function]
    if object.inner_function != None:
      replace_functions(object.inner_function)

def apply_simple_functions(function_list):
  for object in function_list.objects:
    if(object.inner_function != None and len(object.inner_function.objects)==1):
      # print("Current Function",function_list)
      success = apply_simple_functions(object.inner_function)
      # print(success)
      if(success):
        # print("Found numeric inner Function")
        # print(object)
        object.outer_function = object.outer_function(object.inner_function.objects[0].outer_function)
        object.inner_function = None
    elif(object.inner_function != None):
      success = apply_simple_functions(object.inner_function)
      # print(success)
  # print("Length:",len(function_list.objects) == 1)
  # print("Type:",type(function_list.objects[0].outer_function) in (type(3),type(3.14)))
  # print("Inner:",function_list.objects[0].inner_function == None)
  return len(function_list.objects) == 1 and type(function_list.objects[0].outer_function) in (type(3),type(3.14)) and function_list.objects[0].inner_function == None

def get_strongest_operator_index(function_list,vals_to_ignore):
  objects = function_list.objects
  strongest_index = -1
  strongest_val = -1
  for i in range(len(objects)):
    if(not (i in vals_to_ignore)):
      # print("i",i)
      object = objects[i]
      # print("object",object)
      if(object.outer_function in all_operators and all_operators[object.outer_function] > strongest_val):
        strongest_val = all_operators[object.outer_function]
        strongest_index = i
  return strongest_index

def apply_simple_operators(function_list):
  list_range = range(len(function_list.objects))
  objects = function_list.objects
  vals_to_ignore = list()
  index = get_strongest_operator_index(function_list,vals_to_ignore)
  # print("index",index)
  for object in objects:
    if object.inner_function!=None:
      apply_simple_operators(object.inner_function)
  while index!=-1:
    # print(index)
    operator = objects[index].outer_function
    # print(operator)
    if(index==0 or index==len(objects)-1):
      print("Error, operator on edge")
      print("Objects: ")
      for obj in objects:
        print("\t"+str(obj))
      print("Operator: "+operator)
      print("Index: "+str(index))
      print("Length: "+str(len(objects)))
      break
    operand1 = objects[index-1]
    operand2 = objects[index+1]
    if(operand1.inner_function!=None or operand2.inner_function!=None or (not (type(operand1.outer_function) in (type(3),type(3.14)))) or (not (type(operand2.outer_function) in (type(3),type(3.14))))):
      # print("Cannot operate",operator,type(operand1.outer_function),type(operand2.outer_function))
      vals_to_ignore.append(index)
    else:
      # print("Applying Operator: "+str(operator))
      # print("Starting List: ")
      # for obj in objects:
        # print("\t"+str(obj))
      objects_start = objects[0:index-1]
      objects_end = objects[index+2:]
      value = operator_functions[operator](operand1.outer_function,operand2.outer_function)
      # print("value",value)
      function_value = mathFunction()
      function_value.outer_function = value
      objects = objects_start + [function_value] + objects_end
      # print("Ending List: ")
      # for obj in objects:
        # print("\t"+str(obj))
      for i in range(len(vals_to_ignore)):
        if vals_to_ignore[i] > index:
          vals_to_ignore[i] = vals_to_ignore[i] + 2
    function_list.objects = objects
    index = get_strongest_operator_index(function_list,vals_to_ignore)
  function_list.objects = objects

def remove_empty_functions(function_list):
  success = False;
  while(not success):
    success = True
    for i in range(len(function_list.objects)):
      object = function_list.objects[i]
      if ((type(object.outer_function) == type("hi") and object.outer_function in all_functions.keys() and not object.outer_function in all_operators.keys()) or callable(object.outer_function)) and object.inner_function == None:
        success = False
        # print("Removing: ",str(object))
        del function_list.objects[i]
        break
      elif object.inner_function!=None:
        remove_empty_functions(object.inner_function)
      
      

    # if object.inner_function != None and callable(object.outer_function):
    #   inner_function = object.inner_function
    #   objects = inner_function.objects
    #   if(len(objects)==1):
        
    #     apply_simple_functions(inner_function)
    #     objects = inner_function.objects
    #     object.outer_function = object.outer_function(objects[0])
    #   else:
    #     apply_simple_functions(objects)


#Spaces are VERY important. Make sure to add them, but also don't add too many. We also can't do implied multiplication, which I probably could implement, but I'm going to leave that task to you to handle client side
test_string = "-((2 * x) ^ (1 / cos(sin(5 ^ x)))) + sin(1 + x ^ 2)" 
#Issue: spaces after parentheses add extraneous identity function
#Workaround: delete functions with no parameters
# test = mathFunctionList(test_string)

# handle_negative(test)
# handle_numeric(test)
# replace_x_with_val(test,17)
# replace_functions(test)
# print(test)
# attempts = 0
# while attempts < 5 and (len(test.objects)>1 or test.objects[0].inner_function != None):
#   print("Attempt #"+str(attempts))
#   apply_simple_functions(test)
#   apply_simple_operators(test)
#   remove_empty_functions(test)
#   attempts += 1
# print(attempts)
# print("Attempting to resolve function: "+test_string)
# print(test)

def eval(slope,x,y):
  slopeList = mathFunctionList(slope)

  handle_negative(slopeList)
  handle_numeric(slopeList)
  replace_x_with_val(slopeList,x)
  replace_y_with_val(slopeList,y)
  replace_functions(slopeList)
  attempts = 0
  while attempts < 40 and (len(slopeList.objects)>1 or slopeList.objects[0].inner_function != None):
    apply_simple_functions(slopeList)
    apply_simple_operators(slopeList)
    remove_empty_functions(slopeList)
    attempts += 1
  if(len(slopeList.objects)>1):
    print("Error: expected length 1, but got",len(slopeList.objects),"instead.")
    print(slopeList)
  return slopeList.objects[0].outer_function

class eulerTable:
  def __init__(self,slope,x,y,dx):
    self.slope = slope
    self.x = float(x)
    self.y = float(y)
    self.dx = float(dx)
    self.dy = None
    self.init_time = time.time()
  def increment(self):
    self.dy = self.dx * eval(self.slope,self.x,self.y)
    self.x += self.dx
    self.y += self.dy
    x_row.append(self.x)
    y_row.append(self.y)
  def vector_increment(self,dist):
    temp_dy = self.dx * eval(self.slope,self.x,self.y)
    used_dist = math.sqrt(math.pow(temp_dy,2.0) + math.pow(self.dx,2.0))
    # print(used_dist,dist)
    if(used_dist>dist):
      return (False,0)
    self.dy = temp_dy
    self.x += self.dx
    self.y += self.dy
    # self.display()
    return (True,used_dist)
    
  def display(self):
    print("dy/dx:",self.slope,"x:",self.x,"y:",self.y,"dx:",self.dx,"dy:",self.dy)
  def __str__(self):
    return "dy/dx: "+self.slope+" x: "+str(self.x)+" y: "+str(self.y)+" dx: "+str(self.dx)+" dy: "+str(self.dy)

x_row = list()
y_row = list()
class curve():
  def __init__(self,code,origin):
    self.code = code #compare code to make sure we don't kill the player with their own equation
    self.points = list()
    self.xs = list()
    self.ys = list()
    self.origin = origin
    self.init_time = time.time()


codes_to_curves = dict()
usernames = list()
codes_to_players = dict()
players_to_kill = list() # append a player here to send them the info that they've died
codes_to_threads = dict()

class player():
  def __init__(self,code,x,y,username):
    self.code = code
    self.x = x
    self.y = y
    self.xvel = 0
    self.yvel = 0
    self.xacc = 0
    self.yacc = 0
    self.radius = 1
    self.player_curve = None
    self.equation = None
    self.unsubmitted_equation = ""
    self.dx = 0.01
    self.username = username
    self.overflow_delta = 0 # this ticks up and stores the bits of time that aren't big enough to add a whole point, so that way you aren't advantaged based on random chance of connectivity
    self.unused_distance = 0
    self.dead = False
  def make_curve(self,equation):
    self.equation = eulerTable(equation,0,0,self.dx)
    self.player_curve = curve(self.code,point(self.x+1.5,self.y))
    codes_to_curves.update({self.code:self.player_curve})
    return self.player_curve
  def touching(self,curve_points):
    # No Friendly Fire
    # if(curve_points.code==self.code):
    #   return False
    # we use curve.reversed, because it is more likely that the player got hit by one of the newest points than they just decided to walk in to one of the oldest ones
    for curve_point in reversed(curve_points.points):
      tempx = curve_points.origin.x + curve_point.x - self.x
      tempy = curve_points.origin.y + curve_point.y - self.y
      if(tempx**2 + tempy**2 <= self.radius):
        print(tempx,tempy,"ouch!")
        return True
    return False
class point():
  def __init__(self,x,y):
    self.x = x
    self.y = y

def update_player_physics(code,delta):
  if not (code in codes_to_players.keys()):
    return
  tmp_player = codes_to_players[code]
  tmp_player.xvel += tmp_player.xacc * delta
  tmp_player.yvel += tmp_player.yacc * delta
  tmp_player.x += tmp_player.xvel * delta
  tmp_player.y += tmp_player.yvel * delta
  if tmp_player.x > x_max:
    tmp_player.x = x_max
  elif tmp_player.x < x_min:
    tmp_player.x = x_min
  if tmp_player.y > y_max:
    tmp_player.y = y_max
  elif tmp_player.y < y_min:
    tmp_player.y = y_min
  if tmp_player.xvel > vel_max:
    tmp_player.xvel = vel_max
  elif tmp_player.xvel < vel_min:
    tmp_player.xvel = vel_min
  if tmp_player.yvel > vel_max:
    tmp_player.yvel = vel_max
  elif tmp_player.yvel < vel_min:
    tmp_player.yvel = vel_min
  if(tmp_player.xacc==0):
    tmp_player.xvel *= max(1 - air_res * delta,0)
  if(tmp_player.yacc==0):
    tmp_player.yvel *= max(1 - air_res * delta,0)

def update_player(code,delta):
  if not (code in codes_to_players.keys()):
    return
  multiplier = 100.0
  dist_factor = 5.0
  # print(code)
  # print(delta)
  tmp_player = codes_to_players[code]
  times_to_run = int(multiplier*(delta+tmp_player.overflow_delta))
  # print(player.overflow_delta)
  tmp_player.overflow_delta = (multiplier*(delta+tmp_player.overflow_delta) - times_to_run)/multiplier
  distance = (dist_factor*delta) + tmp_player.unused_distance
  # print(times_to_run)
  # print(player.overflow_delta)
  if tmp_player.equation == None:
    tmp_player.unused_distance = 0
    tmp_player.overflow_delta = 0
    return
  eq = tmp_player.equation
  tmp_table = eulerTable(eq.slope,eq.x,eq.y,eq.dx)
  inc_output = tmp_table.vector_increment(distance)
  distance -= inc_output[1] # it's ok to do this before we check because on fail we return input
  while inc_output[0]:
    # print(eq.slope,distance)
    inc_output = tmp_table.vector_increment(distance)
    tmp_player.player_curve.points.append(point(tmp_table.x,tmp_table.y))
    if(tmp_table.x > x_max):
        tmp_player.equation = None
        tmp_player.player_curve = None
        return
    tmp_player.player_curve.xs.append(tmp_table.x+tmp_player.player_curve.origin.x)
    tmp_player.player_curve.ys.append(tmp_table.y+tmp_player.player_curve.origin.y)
    distance -= inc_output[1]
  # player.equation.display()
  tmp_player.equation.x = tmp_table.x
  tmp_player.equation.y = tmp_table.y
  tmp_player.equation.dx = tmp_table.dx
  tmp_player.equation.dy = tmp_table.dy
  tmp_player.unused_distance = distance

def player_loop(code):
  old_time = time.time()
  while not(code in players_to_kill):
    current_time = time.time()
    delta = current_time - old_time
    update_player(code,delta)
    update_player_physics(code,delta)
    delta = time.time() - current_time
    while delta < .01: # .01
      delta = time.time() - current_time # wait until at least 1/100th of a second has passed, otherwise running the function is pointless
    old_time = current_time
  codes_to_curves.pop(code)
  codes_to_players.pop(code)
  codes_to_threads.pop(code)
  return

def make_player(name):
  if(name in usernames):
    print("Username already in use")
    return None
  temp_code = str(uuid.uuid4())
  while(temp_code in codes_to_players.keys()):
    temp_code = str(uuid.uuid4())
  temp_x = 0 #0,0 for now, we can add an algorithm later
  temp_y = 0
  temp_player = player(temp_code,temp_x,temp_y,name)
  codes_to_curves.update({temp_code:None})
  usernames.append(name)
  codes_to_players.update({temp_code:temp_player})
  update_thread = threading.Thread(group=None,
                                   target=player_loop,
                                   name=temp_code,
                                  args=(temp_code,))
  codes_to_threads.update({temp_code:update_thread})
  update_thread.start()
  return temp_player # Yes, I know this is stupid and kind of cheating, but I didn't want to waste time doing it the "right way".
  
# test_player = make_player("abc")
# test_curve = test_player.make_curve("abs(sin(x)) + .1")
# make_player("def").make_curve("2") # If return temp_player bothered you, I recommend not reading this line

def game_loop():
    print("Starting Game Thread")
    game_old_time = time.time()
    while True:
        while time.time() - game_old_time < .100:
            pass
        game_old_time = time.time()



        tmp_codes_to_players = dict()
        for c in codes_to_players.keys():
            tmp_codes_to_players.update({c:codes_to_players[c]})
        tmp_codes_to_curves = dict()
        for c in codes_to_curves.keys():
            tmp_codes_to_curves.update({c:codes_to_curves[c]})



        for c in tmp_codes_to_players.keys():
            pla = tmp_codes_to_players[c]
            for curve in codes_to_curves.values():
                # print(pla,curve)
                if(pla.touching(curve)):
                    pla.dead = True
                    players_to_kill.append(pla.code)
                    break

target_x_val = 6.28
target_x_val = 40
steps_per_digit = 100.0
ut = eulerTable("abs(sin(x)) + .1",0,0,1/steps_per_digit)
tmp_curve = curve(1,point(0,0))
for i in range(int(target_x_val * steps_per_digit)):
  ut.increment()
  tmp_curve.points.append(point(ut.x,ut.y))
  tmp_curve.xs.append(ut.x)
  tmp_curve.ys.append(ut.y)
#   test_player.touching(test_curve)
ut.display()
# df = pd.DataFrame({"x":x_row,
#                    "y":y_row})
# # print(df.head())
# current_plot = sns.scatterplot(data=df,x="x",y="y")
# fig = current_plot.get_figure()
# fig.savefig("out.png")
# # real_val = math.log(target_x_val)
# # print("Real Val:",real_val)
# # print("Error:",abs(real_val-ut.y))

# # time.sleep(10)
# for code in codes_to_players.keys():
#   tmp_player = codes_to_players[code]
#   print(tmp_player.username)
#   print(time.time()-tmp_player.equation.init_time)
#   print(str(tmp_player.equation))


# # Server side code end
game_thread = threading.Thread(
    group=None,
    target=game_loop,
    name="game_loop",
)
game_thread.start()


@app.route("/",methods=["POST","GET"])
def index():
    if request.method=="POST":
        # print(dir(request))
        print(request.form.keys())
        form_username = request.form['username']
        if(form_username==""):
            return render_template("index.html",username="",username_error="Username Field Cannot Be Left Blank")
        # code = make_player(form_username).code
        processed_vector = [0,0]
        starting_code = ""
        if 'send_vector' in request.form.keys():
            # we know we are on the second page
            starting_code = request.form["code"]
            print(request.form['send_vector'])
            movement_vector = request.form['send_vector'].split(",")
            print(movement_vector)
            for i in range(len(movement_vector)):
                direction = int(movement_vector[i])
                if(direction!=1 and direction!=0):
                    print("Improper Value")
                    processed_vector=[0,0]
                    break
                array_pos = i % 2
                sign = int((int(i/2) - 0.5) * -2) # May all who try to understand my code tremble in fear
                processed_vector[array_pos] += sign * direction
            print(processed_vector)
        else:
            # we are on the first page
            tmp_player = make_player(form_username)
            if(tmp_player==None):
                print("Returning Empty Page")
                return render_template("index.html",username_error="Username " + form_username +" Is Already In Use",username="")
            starting_code = tmp_player.code
            print("Initializing Player, with username: ",tmp_player.username)
            print(codes_to_players)
            tmp_player.make_curve("sin(x)")
        tmp_player = codes_to_players[starting_code]
        tmp_player.yacc = acc_mult * processed_vector[0]
        tmp_player.xacc = acc_mult * processed_vector[1]
        if("equation" in request.form.keys()):
            tmp_player.unsubmitted_equation = request.form["equation"]
        # new_task = Todo(content=task_content)
        print(eval(form_username,1,0))
        try:
            # db.session.add(new_task)
            # db.session.commit()
            xs = list()
            ys = list()
            for point in tmp_curve.points:
                xs.append(point.x)
                ys.append(point.y)
            xs = str(xs)[1:-1]
            ys = str(ys)[1:-1]
            # print(xs,'\n\n\n',ys)
            return render_template("index.html",username=form_username,xs=str(xs)[1:-1],ys=str(ys)[1:-1],playerx=tmp_player.x,playery=tmp_player.y,code=starting_code,equation=tmp_player.unsubmitted_equation,player_curve=tmp_player.player_curve) #xs, ys
        except Exception as e:
            print(str(e))
            print(e)
            # return "Error When Submiting Your Data. It has NOT been saved, so please copy it from this page before returning to the home page. "+str(task_content)
            # return render_template("index.html",username="")
            return "Ooops"
    else:
        return render_template("index.html",username="")

# @app.route("/delete/<int:id>")
# def delete(id):
#     task_to_delete = Todo.query.get_or_404(id)

#     try:
#         db.session.delete(task_to_delete)
#         db.session.commit()
#         return redirect("/")
#     except:
#         print("Error Deleting Data with id",id,"and task",task_to_delete)


# @app.route("/update/<int:id>",methods=["GET","POST"])
# def update(id):
#     task = Todo.query.get_or_404(id)

#     if request.method == "POST":
#         task.content = request.form['content']

#         try:
#             db.session.commit()
#         except:
#             return "Unable to update database with new contents: "+request.form["content"]
#         return redirect("../")
#     else:
#         return render_template("update.html",task=task)
@socketio.on("connect")
def player_init(data):
    print(dir(socketio))
@socketio.on("message")
def update(data):
    print("data",data)
    # print(dir(request))
    
    processed_vector = [0,0]
    form_username = data['username']
    # code = request.form["code"]
    if(form_username==""):
        return render_template("index.html",username="",username_error="Username Field Cannot Be Left Blank")
    if(not("Initializing Connection" in data.keys()) and data['code'] in codes_to_players.keys()):
        # print(data.keys())
        
        # code = make_player(form_username).code

        # print(request.form['send_vector'])
        # movement_vector = request.form['send_vector'].split(",")
        movement_vector = data['send_vector']
        # print(movement_vector)
        for i in range(len(movement_vector)):
            direction = int(movement_vector[i])
            if(direction!=1 and direction!=0):
                print("Improper Value")
                processed_vector=[0,0]
                break
            array_pos = i % 2
            sign = int((int(i/2) - 0.5) * -2) # May all who try to understand my code tremble in fear
            processed_vector[array_pos] += sign * direction
        # print(processed_vector)
        # else:
        #     # we are on the first page
        #     tmp_player = make_player(form_username)
        #     if(tmp_player==None):
        #         print("Returning Empty Page")
        #         return render_template("index.html",username_error="Username " + form_username +" Is Already In Use",username="")
        #     code = tmp_player.code
        #     tmp_player.make_curve("sin(x)")
        tmp_player = codes_to_players[data["code"]]
        tmp_player.yacc = acc_mult * processed_vector[0]
        tmp_player.xacc = acc_mult * processed_vector[1]
        # print("xacc",tmp_player.xacc,"xvel",tmp_player.xvel,"xcoord",tmp_player.x)
        if("equation" in data.keys()):
            tmp_player.unsubmitted_equation = data["equation"]
        # new_task = Todo(content=task_content)
        # print(eval(form_username,1,0))
        try:
            # db.session.add(new_task)
            # db.session.commit()
            xs = list()
            ys = list()
            # for point in tmp_curve.points:
            #     xs.append(point.x)
            #     ys.append(point.y)
            # xs = str(xs)[1:-1]
            # ys = str(ys)[1:-1]
            other_player_xs = list()
            other_player_ys = list()
            other_player_x_vels = list()
            other_player_y_vels = list()
            other_player_x_accs = list()
            other_player_y_accs = list()
            other_player_names = list()
            for c in codes_to_players.keys():
                if(c != data["code"]):
                    other_player_xs.append(codes_to_players[c].x)
                    other_player_ys.append(codes_to_players[c].y)
                    other_player_x_vels.append(codes_to_players[c].xvel)
                    other_player_y_vels.append(codes_to_players[c].yvel)
                    other_player_x_accs.append(codes_to_players[c].xacc)
                    other_player_y_accs.append(codes_to_players[c].yacc)
                    other_player_names.append(codes_to_players[c].username)
            if(data['send_equation']==True):
                tmp_player.player_curve = None
                tmp_player.make_curve(data['equation'])
            if(tmp_player.player_curve!=None):
                xs = tmp_player.player_curve.xs
                ys = tmp_player.player_curve.ys
            print(form_username,tmp_player.x,tmp_player.y,data["code"],other_player_xs,other_player_ys)
            # print(xs,'\n\n\n',ys)
            socketio.send({
                'username':tmp_player.username,
                'code':data["code"],
                'dead':tmp_player.dead,
                'xs':xs,
                'ys':ys,
                'x':tmp_player.x,
                'y':tmp_player.y,
                'x_vel':tmp_player.xvel,
                'y_vel':tmp_player.yvel,
                'x_acc':tmp_player.xacc,
                'y_acc':tmp_player.yacc,
                'other_player_xs':other_player_xs,
                'other_player_ys':other_player_ys,
                'other_player_x_vels':other_player_x_vels,
                'other_player_y_vels':other_player_y_vels,
                'other_player_x_accs':other_player_x_accs,
                'other_player_y_accs':other_player_y_accs,
                'other_player_names':other_player_names,
            })
            # return render_template("index.html",username=eval(form_username,1,0),xs=str(xs)[1:-1],ys=str(ys)[1:-1],playerx=tmp_player.x,playery=tmp_player.y,code=code,equation=tmp_player.unsubmitted_equation,player_curve=tmp_player.player_curve) #xs, ys
        except Exception as e:
            print(str(e))
            print(e)
            # return "Error When Submiting Your Data. It has NOT been saved, so please copy it from this page before returning to the home page. "+str(task_content)
            # return render_template("index.html",username="")
            return "Ooops"
    # else:
    #     print("Initializing Player")
    #     print(usernames)
    #     tmp_player = make_player(form_username)
    #     if(tmp_player==None):
    #         print("Returning Empty Page")
    #         return render_template("index.html",username_error="Username " + form_username +" Is Already In Use",username="")
    #     code = tmp_player.code
    #     tmp_player.make_curve("sin(x)")
    #     socketio.send(
    #         {"code":tmp_player.code},
    #     {"username":tmp_player.username})
    elif not data['code'] in codes_to_players.keys():
        socketio.send({
            'code':data['code'],
            'dead':True,
            })

if(__name__ == "__main__"):
    # app.run(debug=True)
    socketio.run(app,debug=True)