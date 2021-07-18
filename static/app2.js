function setSpeed(speed, direction) {
    if (speed == "fast" && direction == "positive") {
        return Math.random()*(5-1) + 1;
    } else if (speed == "fast" && direction == "negative") {
        return Math.random()*(-1+5) -5;
    } else if (speed == "slow" && direction == "positive") {
        return Math.random()*(2-0.1) + 0.1;
    } else if (speed == "slow" && direction == "negative") {
        return Math.random()*(-0.1+2) -2;
    }
} 

// inclusive of min and max
function Randint(min, max) {
    return Math.floor(Math.random() * (max - min + 1) ) + min;
}

class Ball{
    constructor (color, size, x, y) {
        this.color= color,
        this.size= size,
        this.x= x,
        this.y= y,
        this.speedX= setSpeed("fast", "positive"),
        this.speedY= setSpeed("fast", "positive");
    }
    
    getX() {
        return this.x;
    }

    getY() {
        return this.y;
    }

    getBox() {
        if (this.y < height*vapFrac) {
            return 1;
        } else {
            return 2;
        }
    }

    bounce(direction, speed) {
        if (direction == "right") {
            this.speedX = setSpeed(speed, "positive");
        } else if (direction == "left") {
            this.speedX = setSpeed(speed, "negative");
        } else if (direction == "up") {
            this.speedY = setSpeed(speed, "negative");
        } else if (direction == "down") {
            this.speedY = setSpeed(speed, "positive");
        }
    }

    evaporate() {
        if (this.speedY <= 0) {
            return true;
        }
        return false;
    }

    update() {

        if (this.getBox() == 2) {

            if (this.getX() > width-this.size/2) {
                this.bounce("left", "slow");
            } else if (this.getX() < this.size/2) {
                this.bounce("right", "slow");
            } 

            if (vapFrac != 0) {
                if (this.getY() > height-this.size/2) {
                    this.bounce("up", "slow");
                } else if (this.getY() <= height*vapFrac + this.size/2) {
                    this.y = height*vapFrac - this.size/2 - 0.01 + this.speedY
                    crossedOver++;
                }
            } 
            else {
                if (this.getY() > height-this.size/2) {
                    this.bounce("up", "slow");
                } else if (this.getY() <= height*vapFrac + this.size/2) {
                    this.bounce("down", "slow");
                }
            }
        } 
        else {

            if (this.getX() > width-this.size/2) {
                this.bounce("left", "fast");
            } else if (this.getX() < this.size/2) {
                this.bounce("right", "fast");
            }
            if (vapFrac != 1) {
                if (this.getY() < this.size/2) {
                    this.bounce("down", "fast");
                } else if (this.getY() >= height*vapFrac-this.size/2) {
                    this.y = height*vapFrac + 0.1
                    this.y = height*vapFrac + this.size/2 + 0.1 - this.speedY
                    crossedOver--;
                }
            } else {
                if (this.getY() >= height*vapFrac-this.size/2) {
                    this.bounce("up", "fast");
                } else if (this.getY() < this.size/2) {
                    this.bounce("down", "fast");
                }
            }
        }
 
        this.x = this.getX() + this.speedX;
        this.y = this.getY() + this.speedY;
        
    }
    
}

function countBalls(box, color) {
    var numberOfBalls = 0;
    for (var i = 0; i < number; i++) {
        if (ballArray[i].getBox() == box && ballArray[i].color == color) {
            numberOfBalls++;
        }
    }
    return numberOfBalls; 
}

var ballArray = [];
var vapNumber = Math.round(number * vapFrac)
var liqNumber = number - vapNumber;
var crossedOver = 0
var upOrDown = null
var height = 240
var width = 630

for (var i = 0; i < vapNumber; i++) {
    let newball = new Ball("blue", 20, Randint(0,width), Randint(0,Math.round(height*vapFrac)-1));
    ballArray.push(newball);
}

for (var i = 0; i < liqNumber; i++) {
    let newball2 = new Ball("blue", 20, Randint(0,width), Randint(0,Math.round(height*vapFrac)-1));
    ballArray.push(newball2);
}

function setup() {
    var animation = createCanvas(630,240);
    animation.parent("animateMolecules2")
    animation.id('animateMolecules2');
}

function rectFillColor(state) {
    if (state == "liquid") {
        fill(135,206,250);
    } else if (state == "vapor") {
        fill(255,255,215);
    }  
}

function drawRect(type, minX, minY, maxX, maxY) {
    noStroke();
    rectFillColor(type);
    rect(minX, minY, maxX, maxY);
    stroke(0,0,0);
    strokeWeight(2);
    if (type == "vapor") {
        line(minX, maxY, minX, minY);
        line(minX, minY, maxX, minY);
        line(maxX, minY, maxX, maxY);
        
    } else if (type == "liquid") {
        line(minX, minY, minX, maxY);
        line(minX, maxY, maxX, maxY);
        line(maxX, maxY, maxX, minY);
    }
    
}

function draw() {
    if (transition == true) {
        if (vapFrac == 1) { // gas->liq
            vapFrac -= 0.01;
            upOrDown = "up";
        }
        else if (vapFrac == 0) { // liq->gas
            vapFrac += 0.01;
            upOrDown = "down";
        }
        else if (upOrDown == "up") {
            vapFrac -= 0.01;
        }
        else if (upOrDown == "down") {
            vapFrac += 0.01;
        }
    }
    var vaporRectx1 = 0;
    var vaporRecty1 = 0;
    var vaporRectx2 = width;
    var vaporRecty2 = vapFrac*height;

    var liquidRectx1 = 0;
    var liquidRecty1 = vapFrac*height;
    var liquidRectx2 = width;
    var liquidRecty2 = height;
    drawRect("liquid", liquidRectx1, liquidRecty1, liquidRectx2, liquidRecty2);
    drawRect("vapor", vaporRectx1, vaporRecty1, vaporRectx2, vaporRecty2);
    
    if (vapFrac != 1) {
        drawingContext.setLineDash([7, 15]);
        line(0,vapFrac*height,width,vapFrac*height);
        drawingContext.setLineDash([]);
    } else {
        line(0,vapFrac*height,width,vapFrac*height);
    }
    
    for (var i = 0; i< ballArray.length; i++) {
        stroke(ballArray[i].color);
        fill(ballArray[i].color);
        ellipse(ballArray[i].x, ballArray[i].y, ballArray[i].size, ballArray[i].size);
    }
    
    for (var i = 0; i < ballArray.length; i++) {
        ballArray[i].update();
    }

    if (vapFrac > 1) {
        vapFrac = 1;
        transition = false;
        upOrDown = null;
    }
    else if (vapFrac < 0) {
        vapFrac = 0;
        transition = false;
        upOrDown = null;
    }
}