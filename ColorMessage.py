import random
bold = "\033[1m"
red = "\033[31;1m"
green = "\033[32;1m"
yellow = "\033[33;1m"
blue = "\033[34;1m"
magenta = "\033[35;1m"
Cyan = "\033[36;1m"
reset = "\033[0;1m"


colors = [bold,yellow, green, blue, magenta,red,Cyan]
to_print = "tomer king"
to_print_color =""
for idx, s in enumerate(to_print):
    if s != "":
        i = random.randint(0, len(colors) - 1)
        to_print_color += colors[i] + s + reset
print(to_print_color)
