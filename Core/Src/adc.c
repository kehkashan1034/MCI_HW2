#include "stm32f303xc.h"
#include "adc.h"

volatile uint16_t adc_buffer[BUFFER_SIZE];

volatile uint16_t adc_head = 0;
volatile uint16_t adc_tail = 0;

volatile uint32_t sample_count = 0;
volatile uint32_t buffer_overflow = 0;

void adc_init(void)
{
    // Enable ADC12 clock
    RCC->AHBENR |= RCC_AHBENR_ADC12EN;

    // Select ADC clock = HCLK/2 = 24 MHz
    ADC12_COMMON->CCR &= ~(3U << 16);
    ADC12_COMMON->CCR |= (2U << 16);

    // Enable ADC voltage regulator
    ADC1->CR &= ~(3U << 28);
    ADC1->CR |= (1U << 28);

    // Wait for regulator startup
    for (volatile uint32_t i = 0; i < 500; i++);

    // Start ADC calibration
    ADC1->CR |= ADC_CR_ADCAL;

    // Wait for calibration
    while (ADC1->CR & ADC_CR_ADCAL);

    // Configure 12-bit resolution
    ADC1->CFGR &= ~ADC_CFGR_RES;

    // Select channel 1 (PA0)
    ADC1->SQR1 = (1U << 6);

    // Sampling time = 19.5 ADC cycles for channel 1
    ADC1->SMPR1 &= ~(7U << 3);
    ADC1->SMPR1 |= (4U << 3);

    // Select TIM2_TRGO as external trigger
    ADC1->CFGR &= ~(15U << 6);
    ADC1->CFGR |= (11U << 6);

    // Trigger on rising edge
    ADC1->CFGR &= ~(3U << 10);
    ADC1->CFGR |= (1U << 10);

    // Enable end-of-conversion interrupt
    ADC1->IER |= ADC_IER_EOCIE;

    // Enable ADC interrupt
    NVIC_SetPriority(ADC1_2_IRQn, 1);
    NVIC_EnableIRQ(ADC1_2_IRQn);

    // Clear ADC ready flag
    ADC1->ISR = ADC_ISR_ADRDY;

    // Enable ADC
    ADC1->CR |= ADC_CR_ADEN;

    // Wait until ADC is ready
    while (!(ADC1->ISR & ADC_ISR_ADRDY));
}

void adc_start(void)
{
    // Arm ADC for external triggering
    ADC1->CR |= ADC_CR_ADSTART;
}