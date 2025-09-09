from neopixel import Neopixel
import time
import random

pixels = Neopixel(30, 0, 15, "GRB")
pixels.brightness(255)

def set_gradient():
    pixels.clear()
    pixels.set_pixel_line_gradient(0, 10, (250, 0, 0), (0, 250, 0))
    pixels.set_pixel_line_gradient(10, 20, (0, 250, 0), (0, 0, 250))
    pixels.set_pixel_line_gradient(20, 29, (0, 0, 250), (250, 0, 0))

def set_every_n(n, offset, color):
    pixels[offset::n] = color
    pixels.show()

def flash_color(times, color):
    for i in range(times):
        pixels[:] = color
        pixels.show()
        time.sleep(0.2)
        pixels.clear()
        pixels.show()
        time.sleep(0.2)


def standard_rotation(times, sleep_time):
    for i in range(times):
        rotate()
        time.sleep(sleep_time)

def rotate():
    pixels.rotate_right()
    pixels.show()


def spread_color(color):
    for i in range(15):
        pixels[14 - i] = color
        pixels[15 + i] = color
        pixels.show()
        time.sleep(0.2)

def random_fill(color):
    pixels.clear()
    numbers = list(range(30))
    order = []
    while numbers:
        order.append(numbers.pop(random.randint(0, len(numbers) - 1)))
    print(order)
    for number in order:
        pixels[number] = color
        pixels.show()
        time.sleep(0.1)
        

def blackjack():
    set_every_n(1, 0, (0, 255, 0))
    set_every_n(6, 1, (255, 255, 255))
    standard_rotation(24, 0.1)

def win():
    option = random.randint(0, 1)
    if option == 0:
        flash_color(5, (0, 255, 0))
    elif option == 1:
        spread_color((0, 255, 0))

def lose():
    flash_color(5, (255, 0, 0))

def split():
    pixels.clear()
    spread_color((0, 0, 255))

def bust():
    pixels.clear()
    pixels[:] = (255, 0, 0)
    pixels.show()
    time.sleep(0.5)
    spread_color((0, 0, 0))
    
def push():
    random_fill((0, 0, 255))
    random_fill((0, 0, 0))
    
def surrender():
    random_fill((255, 0, 0))
    random_fill((0, 0, 0))
    
results = {"blackjack" : blackjack, "win" : win, "push" : push, "surrender" : surrender, "lose" : lose, "bust" : bust}

pixels.clear()
pixels.show()
