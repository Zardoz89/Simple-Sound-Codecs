/*----------------------------------------------------- 
Author:  <Zardoz>
Date: Fri May 31 15:53:33 2013
Description: BTC 1.7 audio codec player for uMicros
Original codec by Roman Black
Audio Codec description : http://www.romanblack.com/btc_alg.htm
-----------------------------------------------------*/


#include <stdint.h>
#include <stddef.h>

#include "robby.h"

#include "btc_sound.h"

// Example of use
// Pins definitions
# define THISBIT 17
# define LASTBIT 12

void setup() {   
  pinMode(THISBIT, OUTPUT);
  pinMode(LASTBIT, OUTPUT);
  
  digitalWrite(THISBIT, LOW);
  digitalWrite(LASTBIT, LOW);

}

void loop() {
  delayMicroseconds(9);
  SampleBTc17(snd_data1, snd_data1_len, THISBIT, LASTBIT);
  
}
