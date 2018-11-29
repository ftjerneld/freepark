#include <RCSwitch.h>
#include <avr/sleep.h>
#include <avr/power.h>
#include <avr/wdt.h>  

#define LOGGING_FREQ_SECONDS   8                         // Seconds to wait before a new sensor reading is logged.
#define MAX_SLEEP_ITERATIONS   LOGGING_FREQ_SECONDS / 8  // Number of times to sleep (for 8 seconds) before
                                                         // a sensor reading is taken and sent to the server.
                                                         // Don't change this unless you also change the 
                                                         // watchdog timer configuration.
#define LEDPIN 13        // Arduino LED
#define US_ECHO_PIN 2    // Ultrasound reply
#define US_TRIG_PIN 4    // Ultrasound send
#define TX_PIN 12        // Transmitter data pin
#define SENSOR_ID 1000   // Sensor id x 1000
                                                         
int sleepIterations = 0;  
volatile bool watchdogActivated = false;    
unsigned long distance = 0;       //Ultrasound measured distance to obstacle  

RCSwitch mySwitch = RCSwitch();

// Define watchdog timer interrupt.
ISR(WDT_vect)
{
  // Set the watchdog activated flag.
  // Note that you shouldn't do much work inside an interrupt handler.
  watchdogActivated = true;
}

// Put the Arduino to sleep.
void sleep()
{
  // Set sleep to full power down.  Only external interrupts or 
  // the watchdog timer can wake the CPU!
  set_sleep_mode(SLEEP_MODE_PWR_DOWN);

  // Turn off the ADC while asleep.
  power_adc_disable();

  // Enable sleep and enter sleep mode.
  sleep_mode();

  // CPU is now asleep and program execution completely halts!
  // Once awake, execution will resume at this point.
  
  // When awake, disable sleep mode and turn on all devices.
  sleep_disable();
  power_all_enable();
}


void setup() {

 Serial.begin(9600);

 // Transmitter is connected to Arduino Pin #10 
 mySwitch.enableTransmit(12);

 // Optional set pulse length.
 mySwitch.setPulseLength(321);

 // set protocol (default is 1, will work for most outlets)
 mySwitch.setProtocol(1);

 // Optional set number of transmission repetitions.
 // mySwitch.setRepeatTransmit(15);

 pinMode(LEDPIN,OUTPUT);
 digitalWrite(LEDPIN, LOW);

 pinMode(US_ECHO_PIN, INPUT);
 pinMode(US_TRIG_PIN, OUTPUT);
 
 // Setup the watchdog timer to run an interrupt which
 // wakes the Arduino from sleep every 8 seconds.
  
 // Note that the default behavior of resetting the Arduino
 // with the watchdog will be disabled.
  
 // This next section of code is timing critical, so interrupts are disabled.
 // See more details of how to change the watchdog in the ATmega328P datasheet
 // around page 50, Watchdog Timer.
 noInterrupts();
  
 // Set the watchdog reset bit in the MCU status register to 0.
 MCUSR &= ~(1<<WDRF);
  
 // Set WDCE and WDE bits in the watchdog control register.
 WDTCSR |= (1<<WDCE) | (1<<WDE);

 // Set watchdog clock prescaler bits to a value of 8 seconds.
 //WDTCSR = (1<<WDP0) | (1<<WDP3); //8 sec
 WDTCSR = (1<<WDP1) | (1<<WDP2);   //1 sec
 //WDTCSR = (1<<WDP2);             //0.25 sec
    
 // Enable watchdog as interrupt only (no reset).
 WDTCSR |= (1<<WDIE);
  
 // Enable interrupts again.
 interrupts();

}

void getParkingSense()
{
  //Add routine for fetching distance from sensor
  digitalWrite(US_TRIG_PIN, HIGH); //Trigger ultrasonic detection 
  delayMicroseconds(10); 
  digitalWrite(US_TRIG_PIN, LOW); 
  distance = pulseIn(US_ECHO_PIN, HIGH); //Read ultrasonic reflection
  distance = distance/58; //Calculate distance in cm
  if (distance > 400) //kan bara mäta 4 m
  {
    distance = 999;
  }
  Serial.println(distance); //Print distance 
  delay(1000); 

  //Dummy code
  //distance = random(255);
  
}

void sendMsg(){
    
  mySwitch.send(SENSOR_ID+distance,24);

  delay(200);
}

void loop() {
 // Don't do anything unless the watchdog timer interrupt has fired.
  if (watchdogActivated)
  {
    watchdogActivated = false;
    // Increase the count of sleep iterations and take a sensor
    // reading once the max number of iterations has been hit.
    sleepIterations += 1;
    if (sleepIterations >= MAX_SLEEP_ITERATIONS) {
      // Reset the number of sleep iterations.
      sleepIterations = 0;
      // Log the sensor data (waking the CC3000, etc. as needed)
     digitalWrite(LEDPIN, HIGH);
     getParkingSense();
     sendMsg();
    }
  }
  // Go to sleep!
  digitalWrite(LEDPIN, LOW);
  sleep();
}
