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

/* Decoder Functions */

/**
 * Play ONE sample of a BTc 1.0 sound data
 * @param *data Ptr. to samples array
 * @param len Array size in bytes
 * @param pin Pin ID to use for output
 * @return 1 if the sound has finished. Else return 0.
 */
uint8_t SampleBTc10 ( const uint8_t* data, size_t len, int8_t pin);

/**
 * Play ONE sample of a BTc 1.6/1.5 sound data
 * @param *data Ptr. to samples array
 * @param len Array size in bytes
 * @param this_pin This Pin ID to use for output
 * @param last_pin Last Pin ID to use for output
 * @return 1 if the sound has finished. Else return 0.
 */
uint8_t SampleBTc16 ( const uint8_t* data, size_t len, int8_t this_pin, int8_t last_pin);

/**
 * Play ONE sample of a BTc 1.7 sound data
 * @param *data Ptr. to samples array
 * @param len Array size in bytes
 * @param this_pin This Pin ID to use for output
 * @param last_pin Last Pin ID to use for output
 * @return 1 if the sound has finished. Else return 0.
 */
uint8_t SampleBTc17 ( const uint8_t* data, size_t len, int8_t this_pin, int8_t last_pin);

/* Encoder functions */

/**
 * Encodes a unsigned 8 bit sound with BTc 1.0
 * @param *in Input array of unsigned 8 bit samples
 * @param i_len Input array size
 * @param *out Output buffer were to write
 * @param *o_len Output buffer size
 * @param soft softnes contants (4, 8, 16, 21, 32, 48, 64)
 * @return Ptr. to Output buffer. NULL if there is an error, like output buffer too small.
 */
uint8_t* EncodeBTc10_8 ( const uint8_t* in, size_t i_len, uint8_t* out, size_t o_len, uint8_t soft);


#ifdef __cplusplus
}
#endif /* __cplusplus */

#endif /* BTC_SOUND_H_ */

