#define REOutputA 2
#define REOutputB 3
#define REButton 4
#define JSOutputY A0
#define JSOutputX A1
#define JSButton 9
#define RxD 0
#define TxD 1
 
String command;
char commandSpecification = 'v';
char commandSpecifications[] = {'v', 'b', 'c'};
int aState, aLastState, readX, readY, x, y;
int counter = 2;
int watch = 0;

void setup() { 
  pinMode(REOutputA,INPUT);
  pinMode(REOutputB,INPUT);
  pinMode(REButton, INPUT_PULLUP);
  pinMode(JSOutputY,INPUT);
  pinMode(JSOutputX, INPUT);
  pinMode(JSButton, INPUT_PULLUP);
  Serial.begin (9600);
  // Reads the initial state of the outputA
  aLastState = digitalRead(REOutputA); 
} 
void loop() {
  readY = analogRead(JSOutputY);
  readX = analogRead(JSOutputX);
  if(x != (readY-512)/160 or y != (readX-512)/160){
      y = (readY-512)/160;
      x = (readX-512)/160;
      Serial.println("x " + String(x) + " ");
      Serial.println("y " + String(y) + " ");
      watch = 0;
    }
  if(digitalRead(JSButton) == LOW){
        Serial.println("mClick");
        delay(250);
        watch = 0;
    }
  if(digitalRead(REButton) == LOW){
    for(int i=0; i<sizeof(commandSpecifications); i++){
      if(i == sizeof(commandSpecifications)-1){
        commandSpecification = commandSpecifications[0];
        break;
      }else if(commandSpecifications[i] == commandSpecification){
        commandSpecification = commandSpecifications[i+1];
        break;
      }
    }
    delay(250);
  }
  aState = digitalRead(REOutputA); // Reads the "current" state of the outputA
  //If the previous and the current state of the outputA are different, that means a Pulse has occured
  if (aState != aLastState){
    // If the outputB state is different to the outputA state, that means the encoder is rotating clockwise
    if(counter % 2 == 0){
    //Serial.println(counter);
      if (digitalRead(REOutputB) != aState) { 
        command = String(commandSpecification) + " - ";
      } else {
        command = String(commandSpecification) + " + ";
      }
      Serial.println(command);
      watch = 0;
    }
    counter ++;
  }

  if(watch > 10000){
    Serial.println("1");
    watch = 0;
  }
  aLastState = aState;
  watch++;
}
