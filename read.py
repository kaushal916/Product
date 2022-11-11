# import yaml
# with open("config.yaml", "r") as yamlfile:
#     data = yaml.load(yamlfile, Loader=yaml.FullLoader)
    
#     print(data['database']['username'])
    
    
# a = data['database']['username']
# print(a)



from curses.ascii import isdigit
from tkinter.tix import Tree


a = '12312a'

if a.isdigit() == True:
    print("The number is disit ")
else:
    print("the number contain some string ")
    
    
