/**
 *  @file btc_sound.c
 *  @author Luis Panadero Guardeño
 *  @brief BTc Sound codecs
 *
 *  BTc Sound Compression Algortithm created by Roman Black
 *  @see http://www.romanblack.com/btc_alg.htm
 */


#include "btc_sound.h"
#include "btc_config.h"

uint8_t SampleBTc10 ( const uint8_t* data, size_t len, int8_t pin) {
  uint8_t tmp;                    
  static size_t index = 0;        /* Index over data array */
#ifdef BTC_BIG_ENDIAN
  static uint8_t nbit = 7;        /* We begin with the MSB bit */
#else
  static uint8_t nbit = 0;        /* We begin with the LSB bit */
#endif

  tmp =  data[index] & (1 << nbit);     /* Extract desired bit */
  SET_PIN(pin, tmp);                    /* Set HIGH/LOW the output PIN */

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


uint8_t SampleBTc16 ( const uint8_t* data, size_t len, int8_t this_pin, int8_t last_pin ) {
  uint8_t tmp;                    
  static size_t index = 0;   /* Index over data array */
  static uint8_t last_bit = 0;    /* Stores the last bit */
#ifdef BTC_BIG_ENDIAN
  static uint8_t nbit = 7;        /* We begin with the MSB bit */
#else
  static uint8_t nbit = 0;        /* We begin with the LSB bit */
#endif

  tmp = data[index] & (1 << nbit);     /* Extract desired bit */

  if (tmp > 0) {
    
    SET_PIN(this_pin, 1);    /* This to HIGH */
    if (last_bit >= 1) {
      IO_PIN(last_pin, 0); /* Last to OUPUT*/
      SET_PIN(last_pin, 1);  /*  "   to HIGH */
    } else {
      IO_PIN(last_pin, 1); /* Last to INPUT -> Make to get High Impendance */
    }
  } else{

    SET_PIN(this_pin, 0);     /* This to LOW */
    if (last_bit == 0) {
      IO_PIN(last_pin, 0); /* Last to OUPUT*/
      SET_PIN(last_pin, 0);  /*  "   to LOW */
    } else {
      IO_PIN(last_pin, 1); /* Last to INPUT -> Make to get High Impendance */
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


uint8_t SampleBTc17 ( const uint8_t* data, size_t len, int8_t this_pin, int8_t last_pin) {
  uint8_t tmp;                    
  static size_t index = 0;   /* Index over data array */
  static uint8_t last_bit = 0;    /* Stores the last bit */
#ifdef BTC_BIG_ENDIAN
  static uint8_t nbit = 7;        /* We begin with the MSB bit */
#else
  static uint8_t nbit = 0;        /* We begin with the LSB bit */
#endif

  tmp = data[index] & (1 << nbit);     /* Extract desired bit */
  tmp = tmp > 0;
  SET_PIN(this_pin, tmp);                  /* Set HIGH/LOW the output This PIN */
  SET_PIN(last_pin, last_bit);             /* Set HIGH/LOW the output Last PIN */
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


uint8_t* EncodeBTc10_8 ( const uint8_t* in, size_t i_len, uint8_t* out, size_t o_len, uint8_t soft) {
  btc_uint sample, dist, highbtc, lowbtc, lastbtc = 128;
  btc_uint disthigh, distlow;
  size_t i = 0, o = 0;

#ifdef BTC_BIG_ENDIAN
  static uint8_t nbit = 7;        /* We begin with the MSB bit */
#else
  static uint8_t nbit = 0;        /* We begin with the LSB bit */
#endif

  out[0] = 0;                     /* We cleans the first byte */
  
  while (i < i_len && o < o_len) {
    sample = in[i++];
    sample = sample / 2 + 64; /* Escalates the sample between 64 and 191 */

    /* generate a "1" (high) outcome */
    dist = (256 - lastbtc);       /* calc total distance to charge */
    dist = (dist / soft);         /* BTc4, only charge 1/4 distance */
    highbtc = (lastbtc + dist);   /* where it charges up to */

    /* generate a "0" (low) outcome */
    dist = lastbtc;               /* calc total distance to charge */
    dist = (dist / soft);         /* BTc4, only charge 1/4 distance */
    lowbtc = (lastbtc - dist);    /* where it charges down to */

    /* calc distance from high outcome (up or down) to new sample */
    if(highbtc > sample)
      disthigh = highbtc - sample;
    else
      disthigh = sample - highbtc;

    /* calc distance from low outcome (up or down) to new sample */
    if(lowbtc > sample)  
      distlow = lowbtc - sample;
    else
      distlow = sample - lowbtc;

    /* see which outcome is closest to new sample and generate the bit */
    if(disthigh > distlow) {      /* low is closest */
      /* We no write any thing, because we previus clean the buffer */
      lastbtc = lowbtc;
    } else {                       /* else high is closest */
      out[o] = out[o] | (1 << nbit);
      lastbtc = highbtc;
    }

    /* We increment output buffer bit and byte index */
#ifdef BTC_BIG_ENDIAN
    nbit--;
    if (nbit > 7) { /* Underflow. Increment index */
      nbit = 7;
#else
    nbit++;
    if (nbit > 7) { /* Overflow. Increment index */
      nbit = 0;
#endif
      o++;
    }

  } /* while */

  if ( o >= o_len && i < i_len) /* Wops! input data too big */
    return NULL;

  return out;

}



