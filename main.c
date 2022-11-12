#include <stdbool.h>

#include <avr/io.h>

#define F_CPU 32768UL
#include <util/delay.h>
#include <avr/interrupt.h>
#include <avr/wdt.h>

#define LED_0 (1<<PB0)
#define LED_1 (1<<PB1)
#define LED_2 (1<<PB2)

// #define RED_LEVEL OCR0A
// #define WHITE_LEVEL OCR0B

// #define IDLE_TIMEOUT 10

#define POWER_IDLE ~(1<<SM1)
#define POWER_DOWN (1<<SM1)

uint32_t time = 0;

#define LED_COUNT 6

const uint8_t led_ddr[LED_COUNT] = {
    LED_2 | LED_1,
    LED_2 | LED_1,
    LED_1 | LED_0,
    LED_1 | LED_0,
    LED_2 | LED_0,
    LED_2 | LED_0,
};

const uint8_t led_port[LED_COUNT] = {
    LED_2,
    LED_1,
    LED_1,
    LED_0,
    LED_2,
    LED_0
};

uint8_t ddr = 0;
uint8_t port = 0;

ISR(TIM1_OVF_vect) {
    time++;
    ddr = led_ddr[time % LED_COUNT];
    port = led_port[time % LED_COUNT];
}

ISR(TIM0_OVF_vect) {
    PORTB = port; // led_port[];
    DDRB = ddr; // led_ddr[time % LED_COUNT];
}

ISR(TIM0_COMPA_vect) {
    // PORTB = 0;
    // DDRB = 0;
}

ISR(TIM0_COMPB_vect) {

}


ISR(WDT_vect){
    // WDTCR |= (1 << WDTIE);
}

int main() {
    // wdt_enable(WDTO_500MS);
    // WDTCR |= (1 << WDTIE);

    PLLCSR &= ~(1 << PCKE);
    TCCR1 |= (1 << CS13) | (0 << CS12) | (0 << CS11) | (0 << CS10);
    TCNT1 = 0;

    TCCR0A = 0x00;
    TCCR0B = (0 << CS02) | (0 << CS01) | (1 << CS00);
    OCR0A = 220;
    TCNT0 = 0;

    TIMSK |= (1 << TOIE1) | (1 << TOIE0) | (1 << OCIE0A) | (1 << OCIE0B);

    // MCUCR = (1 << SE); // power-down mode

    /*
    PORTB |= WHITE;
    _delay_ms(1);
    PORTB &= ~WHITE;
    */

    sei();

    while(1) {
        // cli();

        /*_delay_ms(500);
        time++;
        uint8_t idx = time % LED_COUNT;
        OCR0B = idx;
        ddr = led_ddr[idx];
        port = led_port[idx];
        */

        // PORTB ^= LED_0;
        /*
        if(state == StateShutdown || state == StateOff) {
            state = StateOff;
            PORTB = 0;

            TCCR0B = 0;
            TIMSK0 = 0;

            MCUCR |= (1 << SM1); // power down
        } else {
            PORTB |= PWREN;

            // timer
            // set prescaler to 8 (586 Hz)
            TCCR0B = (0 << CS02) | (1 << CS01) | (0 << CS00);
            // enable Timer Overflow irq + compare A/B irq
            TIMSK0 = (1 << TOIE0) | (1 << OCIE0A) | (1 << OCIE0B);

            MCUCR &= ~(1 << SM1); // power idle
        }
        */
        // sei();
        // __asm("sleep");
    }

    return 0;
}
