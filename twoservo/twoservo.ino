#include <Servo.h>
 
Servo A;  // create servo object to control a servo
Servo B;


 
void setup() {
        Serial.begin(9600); 
        A.attach(10); //Servo connected to D9
        B.attach(5); //Servo connected to D10
}
int num;
double angles[31][2] = {
    {90 ,90   },
    {98 ,95     },//1 - OKish
    {85 ,96     },//2 - OK
    {72 ,98     },//3 - OK
    {68 ,101    },//4 - OK
    {64 ,103    },//5 - OK
    {130,97     },//6 - OK
    {103,97     },//7 - OK
    {90 ,98     },//8 - OK
    {80 ,100    },//9 - OK
    {75 ,102    },//10 - OK
    {68 ,102    },//11
    {120,99     },//12 - OK
    {104,99.5   },//13 - OK
    {94 ,101    },//14 - OK
    {86 ,102    },//15 - OK
    {81 ,105    },//16 - OK
    {129,101    },//17 - OK
    {115,101    },//18 - OK
    {105,102    },//19 - OK
    {97 ,103    },//20 - ok
    {88 ,105    },//21 - OK
    {81 ,104    },//22
    {125.5,103.5},//23 - OK
    {112,103    },//24 - OK
    {105,104    },//25 - OK
    {97 ,105    },//26 - OK
    {88 ,104    },//27
    {111,105.5  },//28 - OK
    {104,106    },//29 - OK
    {102,103.5  },
    }; 

int servoN;
int angle;
void loop()
{
  while(Serial.available() == 0);
  servoN = Serial.read();
  
  while(Serial.available() == 0);
  angle = Serial.read();
  
  if (servoN == 10){    
    A.write(90);
    delay(200);
    A.write(angles[angle][0]);
  }
  else if (servoN == 5){    
    B.write(90);
    delay(200);
    B.write(angles[angle][1]);
  }
}

