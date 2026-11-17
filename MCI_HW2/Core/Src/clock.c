#include "stm32f303xc.h"
#include "clock.h"

void clock_init(void)
{
    // Enable HSI (8 MHz)
    RCC->CR |= RCC_CR_HSION;

    // Wait for HSI ready
    while (!(RCC->CR & RCC_CR_HSIRDY));

    // Disable PLL before changing its configuration
    RCC->CR &= ~RCC_CR_PLLON;

    while (RCC->CR & RCC_CR_PLLRDY);

    // Configure Flash latency to 1 wait state
    FLASH->ACR &= ~FLASH_ACR_LATENCY;
    FLASH->ACR |= FLASH_ACR_LATENCY_1;

    // Enable Flash prefetch
    FLASH->ACR |= FLASH_ACR_PRFTBE;

    // Select HSI/2 as PLL source
    RCC->CFGR &= ~RCC_CFGR_PLLSRC;

    // Set PLL multiplier to x12
    RCC->CFGR &= ~RCC_CFGR_PLLMUL;
    RCC->CFGR |= (10U << 18);

    // AHB prescaler = 1
    RCC->CFGR &= ~RCC_CFGR_HPRE;

    // APB1 prescaler = 2
    RCC->CFGR &= ~RCC_CFGR_PPRE1;
    RCC->CFGR |= RCC_CFGR_PPRE1_DIV2;

    // APB2 prescaler = 1
    RCC->CFGR &= ~RCC_CFGR_PPRE2;

    // Enable PLL
    RCC->CR |= RCC_CR_PLLON;

    // Wait for PLL ready
    while (!(RCC->CR & RCC_CR_PLLRDY));

    // Select PLL as system clock
    RCC->CFGR &= ~RCC_CFGR_SW;
    RCC->CFGR |= RCC_CFGR_SW_PLL;

    // Wait until PLL becomes system clock
    while ((RCC->CFGR & RCC_CFGR_SWS) != RCC_CFGR_SWS_PLL);

    // Update CMSIS system clock variable
    SystemCoreClockUpdate();
}