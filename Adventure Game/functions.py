#doesn't need any imports, not even the setup file
#FUNCTIONS: animates, checks rect collision

#takes in a list of movements and a counter that is initialized as zero outside the function to split up animation over the course of the specified time in equal increments
def animate(movements,time,count):
    count += 1
    if count >= time:
        count = 0
    image = movements[count//(time//len(movements))]
    return image, count

#returns up, down, left, or right depending on where rect1 collides with rect2 (ex: rect1 is facing up relative to rect2), returns False if no collision (or nothing???)
#rects are a tuple containing (x, y, width, height)
def collision_from_rects(rect1,rect2):
    if rect1[0] < rect2[0]+rect2[2] and rect1[0] > rect2[0]-rect1[2] and rect1[1] < rect2[1]+rect2[3] and rect1[1] > rect2[1]-rect1[3]: #checks for any collision
        return True