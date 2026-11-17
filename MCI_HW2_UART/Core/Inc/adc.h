#ifndef ADC_H
#define ADC_H

#include <stdint.h>

#define BUFFER_SIZE 512

extern volatile uint16_t adc_buffer[BUFFER_SIZE];

extern volatile uint16_t adc_head;
extern volatile uint16_t adc_tail;

extern volatile uint32_t sample_count;
extern volatile uint32_t buffer_overflow;

void adc_init(void);
void adc_start(void);

#endif