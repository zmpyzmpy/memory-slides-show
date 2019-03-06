import processing.video.*;
import processing.serial.*;
Serial myPort; 
int sensor0;
int sensor1;

Capture cam;
int num = 0;
long tm;
PImage img;

void setup() {
  size(1024, 768);

  String[] cameras = Capture.list();

  if (cameras.length == 0) {
    println("There are no cameras available for capture.");
    exit();
  } else {
    println("Available cameras:");
    for (int i = 0; i < cameras.length; i++) {
      println(cameras[i]);
    }
  }  

  String portName = Serial.list()[4];
  myPort = new Serial(this, portName, 9600);
  cam = new Capture(this, cameras[0]);
  cam.start();
  tm = -1;
  img = copy();
}

void draw() {
  background(0);

  if (sensor0>=0) {
    cam.start();
    if (cam.available() == true) cam.read();
    image(cam, 0, 0);
  }
    if (sensor0==2) {
      img = copy();
      String name = ""+year()+"Y"+month()+"M"+day()+"D"+num+".png";
      save(name);
      num++;
      cam.stop();
      tm = millis();
    }
  if(tm>0 & millis()-tm<2000)image(img,0,0,width,height);
}

void keyPressed() {
  String name = ""+year()+"Y"+month()+"M"+day()+"D"+num+".png";
  save(name);
  num++;
}

void serialEvent(Serial myPort) {
  String inString = myPort.readStringUntil('\n');
  if (inString != null) {
    inString = trim(inString);
    int[] sensors = int(split(inString, ","));
    if (sensors.length >=2) {
      sensor0 = sensors[0];
      sensor1 = sensors[1];
      println(sensor0 + ", " +  sensor1);
    }
  }
}