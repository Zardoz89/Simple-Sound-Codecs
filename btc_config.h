/**
 * @file btc_config.h
 * @author Luis Panadero Guardeño
 * @brief Configuration of BTc Sound lib
 *
 * DON'T CHANGE THIS IF YOU NOT KNOW WHAT ARE YOU DOING
 */

#ifndef BTC_CONFIG_H_
#define BTC_CONFIG_H_ 1

#include <stdint.h>

/** Set PIN High or LOW function. Expects that if state > 0 -> HIGH */
# define SET_PIN(pin, state) digitalWrite((pin), (state))

/** Set PIN INPUT or OUTPUT mode . Expectrs that if mode > 0 -> INPUT */
# define IO_PIN(pin, mode) pinMode((pin), (mode))

# define BTC_BIG_ENDIAN /**< Sets lib to read from MSB to LSB. Undef if you desire to read the from LSB to MSB */

typedef uint_fast8_t btc_uint;  /**< Defines Encoder int type to be used */
# define BTC_UINT_MAX UINT_FAST8_MAX

#endif /* BTC_CONFIG_H_ */
