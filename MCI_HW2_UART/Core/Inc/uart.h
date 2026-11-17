#ifndef UART_H
#define UART_H

#include <stdint.h>

void uart_init(void);
void uart_send_byte(uint8_t data);
void uart_send_sample(uint16_t sample);
void uart_print_value(uint16_t value);

#endif