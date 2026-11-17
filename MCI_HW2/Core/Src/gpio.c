#include "stm32f303xc.h"
#include "gpio.h"

void gpio_init(void)
{
    // Enable GPIOA clock
    RCC->AHBENR |= RCC_AHBENR_GPIOAEN;

    // PA0 analog mode for ADC
    GPIOA->MODER &= ~(3U << 0);
    GPIOA->MODER |= (3U << 0);

    // Disable pull-up/pull-down on PA0
    GPIOA->PUPDR &= ~(3U << 0);

    // PA2 alternate function mode (USART2_TX)
    GPIOA->MODER &= ~(3U << 4);
    GPIOA->MODER |= (2U << 4);

    // PA3 alternate function mode (USART2_RX)
    GPIOA->MODER &= ~(3U << 6);
    GPIOA->MODER |= (2U << 6);

    // Select AF7 for PA2 and PA3
    GPIOA->AFR[0] &= ~((15U << 8) | (15U << 12));
    GPIOA->AFR[0] |= ((7U << 8) | (7U << 12));

    // Configure UART pin speed
    GPIOA->OSPEEDR |= (3U << 4) | (3U << 6);

    // No pull-up/pull-down
    GPIOA->PUPDR &= ~((3U << 4) | (3U << 6));

    // PA6 alternate function mode (TIM3_CH1)
    // Set PA6 to alternate-function mode.
    GPIOA->MODER &= ~(3U << 12);
    GPIOA->MODER |=  (2U << 12);

    // Select AF2 (TIM3_CH1) for PA6.
    GPIOA->AFR[0] &= ~(15U << 24);
    GPIOA->AFR[0] |=  (2U << 24);
}