#define GFPINLED 13
#define BATTERYBUTTON 4
#define UNITNAME "V"
#define DEVICENUM 0
#define GFTERM ';'
#define GFSPLITTER ':'
uint32_t myTimer = 0;
bool LEDflag=false;
char target[] = "hello";
String gfbufString;
//String gfChannel[7]= { "Sunday", "Monday", "Tuesday",  "Wednesday", "Thirsday", "Friday", "Saturday" };
byte i;
int gfVolt[8]={0,0,0,0,0,0,0,0};

void setup() {
  // put your setup code here, to run once:
 pinMode(GFPINLED, OUTPUT);
 Serial.begin(9600);
 Serial.print("hello"); 
 //Serial.print('/n'); 
 //delay(5000);
}

void loop() {
  // put your main code here, to run repeatedly:
  
	if (millis()-myTimer >=200){
		myTimer=millis();
		digitalWrite(13, LEDflag);
		LEDflag=!LEDflag;
    //Serial.print(LEDflag, BIN);
    //for (byte i=0;i==7;++i) {gfVolt[i]=analogRead(i);}
    gfVolt[BATTERYBUTTON]=analogRead(BATTERYBUTTON);
    Serial.print("{");
    for (i=0;i<8;++i) {
      Serial.print(UNITNAME); Serial.print(DEVICENUM); Serial.print(i); Serial.print(':'); Serial.print(gfVolt[i]); Serial.print(GFTERM);
    }
    Serial.println("},");
	}





}
