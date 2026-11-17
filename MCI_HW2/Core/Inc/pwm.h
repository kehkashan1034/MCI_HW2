#ifndef PWM_H
#define PWM_H

#include <stdint.h>

void pwm_init(uint32_t frequency_hz);
void pwm_start(void);

#endif
