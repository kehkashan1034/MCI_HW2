#include "stm32f303xc.h"
#include "adc.h"

/* Cortex-M4 interrupt handlers */

void NMI_Handler(void)
{
}

void HardFault_Handler(void)
{
    while (1);
}

void MemManage_Handler(void)
{
    while (1);
}

void BusFault_Handler(void)
{
    while (1);
}

void UsageFault_Handler(void)
{
    while (1);
}

void SVC_Handler(void)
{
}

void DebugMon_Handler(void)
{
}

void PendSV_Handler(void)
{
}

void SysTick_Handler(void)
{
}

/* ADC interrupt handler */

void ADC1_2_IRQHandler(void)
{
    if (ADC1->ISR & ADC_ISR_EOC)
    {
        // Read ADC conversion result
        uint16_t value = ADC1->DR;

        // Calculate next buffer position
        uint16_t next = (adc_head + 1) % BUFFER_SIZE;

        // Check if buffer is full
        if (next != adc_tail)
        {
            adc_buffer[adc_head] = value;

            adc_head = next;

            sample_count++;
        }
        else
        {
            buffer_overflow++;
        }
    }
}