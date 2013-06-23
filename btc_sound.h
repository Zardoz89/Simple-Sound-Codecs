/**
 *  @file btc_sound.h
 *  @author Luis Panadero Guardeño
 *  @brief BTc Sound codecs header file
 *
 *  @see http://www.romanblack.com/btc_alg.htm
 */

#ifndef BTC_SOUND_H_
#define BTC_SOUND_H_ 1

#ifdef __cplusplus
extern "C" {
#endif /* __cplusplus */

#include <stddef.h>
#include <stdint.h>
/**
 * Function ptr. that sets pin state or change I/O state
 * state >= 1 means HIGH or INPUT; state == 0 means LOW or OUTPUT
 * For example
 * @code
 * void ThisPin (uint8_t state) {
 *  digitalWrite(10, state);
 * }
 * @endcode
 * */
typedef void (*CfgPin)(uint8_t); 

/* Decoder Functions */

/**
 * Play ONE sample of a BTc 1.0 sound data
 * @param *data Ptr. to samples array
 * @param len Array size in bytes
 * @param pin Funct. Ptr. that sets high/low state of the pin
 * @return 1 if the sound has finished. Else return 0.
 */
uint8_t SampleBTc10 ( const uint8_t* data, size_t len, CfgPin pin);

/**
 * Play ONE sample of a BTc 1.6/1.5 sound data
 * @param *data Ptr. to samples array
 * @param len Array size in bytes
 * @param this_pin Funct. Ptr. that sets high/low state of the This pin
 * @param last_pin Funct. Ptr. that sets high/low state of the Last pin
 * @param IO_last_pin Funct. Ptr. that sets input/output state of the Last pin
 * @return 1 if the sound has finished. Else return 0.
 */
uint8_t SampleBTc16 ( const uint8_t* data, size_t len, CfgPin this_pin, CfgPin last_pin, CfgPin IO_last_pin);

/**
 * Play ONE sample of a BTc 1.7 sound data
 * @param *data Ptr. to samples array
 * @param len Array size in bytes
 * @param this_pin Funct. Ptr. that sets high/low state of the This pin
 * @param last_pin Funct. Ptr. that sets high/low state of the Last pin
 * @return 1 if the sound has finished. Else return 0.
 */
uint8_t SampleBTc17 ( const uint8_t* data, size_t len, CfgPin this_pin, CfgPin last_pin);



#ifdef __cplusplus
}
#endif /* __cplusplus */

#endif /* BTC_SOUND_H_ */

