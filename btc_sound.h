/**
 *  @file btcsound.h
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

#include <stdint.h>

/**
 * Play ONE sample of a BTc 1.0 sound data
 * @param *data Ptr. to samples array
 * @param len Array size in bytes
 */
void SampleBTc10 ( const uint8_t* data, const uintptr_t len);

/**
 * Play ONE sample of a BTc 1.6/1.5 sound data
 * @param *data Ptr. to samples array
 * @param len Array size in bytes
 */
void SampleBTc16 ( const uint8_t* data, const uintptr_t len);

/**
 * Play ONE sample of a BTc 1.7 sound data
 * @param *data Ptr. to samples array
 * @param len Array size in bytes
 */
void SampleBTc17 ( const uint8_t* data, const uintptr_t len);



#ifdef __cplusplus
}
#endif /* __cplusplus */

#endif /* BTC_SOUND_H_ */

