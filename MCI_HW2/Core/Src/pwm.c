#include "stm32f303xc.h"
#include "pwm.h"

// TIM3 clock: 48 MHz with the project clock setup.
// Prescaler 47 produces a 1 MHz counter clock.
void pwm_init(uint32_t frequency_hz)
{
    uint32_t period;

    if (frequency_hz != 100U && frequency_hz != 500U && frequency_hz != 1000U)
        frequency_hz = 100U;

    period = 1000000U / frequency_hz;

    RCC->APB1ENR |= RCC_APB1ENR_TIM3EN;
    TIM3->CR1 &= ~TIM_CR1_CEN;
    TIM3->PSC = 47U;
    TIM3->ARR = period - 1U;
    TIM3->CCR1 = period / 2U;  // 50% duty cycle

    // Channel 1 as output, PWM mode 1, preload enabled
    TIM3->CCMR1 &= ~((3U << 0) | TIM_CCMR1_OC1M);
    TIM3->CCMR1 |= (6U << 4) | TIM_CCMR1_OC1PE;

    // Active-high PWM on CH1 and output enable
    TIM3->CCER &= ~TIM_CCER_CC1P;
    TIM3->CCER |= TIM_CCER_CC1E;
    TIM3->CR1 |= TIM_CR1_ARPE;

    TIM3->EGR = TIM_EGR_UG;
    TIM3->SR = 0U;
    TIM3->CNT = 0U;
}

void pwm_start(void)
{
    TIM3->CR1 |= TIM_CR1_CEN;
}
