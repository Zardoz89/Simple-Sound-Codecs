/**
 *  @file btc_sound.c
 *  @author Luis Panadero Guardeño
 *  @brief BTc Sound codecs
 *
 *  @see http://www.romanblack.com/btc_alg.htm
 */


#include "btc_sound.h"
#include "btc_config.h"

uint8_t SampleBTc10 ( const uint8_t* data, size_t len, CfgPin pin) {
  uint8_t tmp;                    
  static size_t index = 0;   /* Index over data array */
#ifdef BTC_BIG_ENDIAN
  static uint8_t nbit = 7;        /* We begin with the MSB bit */
#else
  static uint8_t nbit = 0;        /* We begin with the LSB bit */
#endif

  tmp =  data[index] && (1 << nbit);     /* Extract desired bit */
  pin(tmp);                      /* Set HIGH/LOW the output PIN */

#ifdef BTC_BIG_ENDIAN
  nbit--;
  if (nbit > 7) { /* Underflow. Increment index */
    nbit = 7;
#else
  nbit++;
  if (nbit > 7) { /* Overflow. Increment index */
    nbit = 0;
#endif
    index++;
    if (index > len) {
      index = 0;
#ifdef BTC_BIG_ENDIAN
      nbit = 7;
#else
      nbit = 0;
#endif

      return 1;
    }
  }

  return 0; /* There is more audio data to play */

}


uint8_t SampleBTc16 ( const uint8_t* data, size_t len, CfgPin this_pin, CfgPin last_pin, CfgPin IO_last_pin) {
  uint8_t tmp;                    
  static size_t index = 0;   /* Index over data array */
  static uint8_t last_bit = 0;    /* Stores the last bit */
#ifdef BTC_BIG_ENDIAN
  static uint8_t nbit = 7;        /* We begin with the MSB bit */
#else
  static uint8_t nbit = 0;        /* We begin with the LSB bit */
#endif

  tmp = data[index] && (1 << nbit);     /* Extract desired bit */

  if (tmp > 0) {
    
    this_pin(1);      /* This to HIGH */
    if (last_bit >= 1) {
      IO_last_pin(0); /* Last to OUPUT*/
      last_pin(1);    /*  "   to HIGH */
    } else {
      IO_last_pin(1); /* Last to INPUT -> Make to get High Impendance */
    }
  } else{

    this_pin(0);      /* This to LOW */
    if (last_bit == 0) {
      IO_last_pin(0); /* Last to OUPUT*/
      last_pin(1);    /*  "   to LOW */
    } else {
      IO_last_pin(1); /* Last to INPUT -> Make to get High Impendance */
    }
  }
  last_bit = tmp;

#ifdef BTC_BIG_ENDIAN
  nbit--;
  if (nbit > 7) { /* Underflow. Increment index */
    nbit = 7;
#else
  nbit++;
  if (nbit > 7) { /* Overflow. Increment index */
    nbit = 0;
#endif
    index++;
    if (index > len) {
      index = 0;
#ifdef BTC_BIG_ENDIAN
      nbit = 7;
#else
      nbit = 0;
#endif

      return 1;
    }
  }

  return 0; /* There is more audio data to play */

}


uint8_t SampleBTc17 ( const uint8_t* data, size_t len, CfgPin this_pin, CfgPin last_pin) {
  uint8_t tmp;                    
  static size_t index = 0;   /* Index over data array */
  static uint8_t last_bit = 0;    /* Stores the last bit */
#ifdef BTC_BIG_ENDIAN
  static uint8_t nbit = 7;        /* We begin with the MSB bit */
#else
  static uint8_t nbit = 0;        /* We begin with the LSB bit */
#endif

  tmp = data[index] && (1 << nbit);     /* Extract desired bit */

  this_pin(tmp);                 /* Set HIGH/LOW the output This PIN */
  last_pin(last_bit);             /* Set HIGH/LOW the output Last PIN */
  last_bit = tmp;

#ifdef BTC_BIG_ENDIAN
  nbit--;
  if (nbit > 7) { /* Underflow. Increment index */
    nbit = 7;
#else
  nbit++;
  if (nbit > 7) { /* Overflow. Increment index */
    nbit = 0;
#endif
    index++;
    if (index > len) {
      index = 0;
#ifdef BTC_BIG_ENDIAN
      nbit = 7;
#else
      nbit = 0;
#endif

      return 1;
    }
  }

  return 0; /* There is more audio data to play */

}


