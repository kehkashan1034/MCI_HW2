#include "stm32f303xc.h"
#include "timer.h"

void timer_init(void)
{
    // Enable TIM2 clock
    RCC->APB1ENR |= RCC_APB1ENR_TIM2EN;

    // Stop timer
    TIM2->CR1 &= ~TIM_CR1_CEN;

    // Prescaler = 47
    TIM2->PSC = 47;

    // Auto reload = 99
    TIM2->ARR = 99;

    // Configure TRGO as update event
    TIM2->CR2 &= ~TIM_CR2_MMS;
    TIM2->CR2 |= (2U << 4);

    // Generate update event
    TIM2->EGR = TIM_EGR_UG;

    // Clear update flag
    TIM2->SR &= ~TIM_SR_UIF;

    // Reset counter
    TIM2->CNT = 0;
}

void timer_start(void)
{
    // Start TIM2
    TIM2->CR1 |= TIM_CR1_CEN;
}