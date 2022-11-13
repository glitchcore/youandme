#include <stdbool.h>

#include <avr/io.h>

// #define F_CPU 32768UL
#define F_CPU 1000000UL
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
uint16_t seed = 0xDEAD;

typedef enum {
    Red0 = 0,
    Green0,
    Blue0,
    Yellow,
    Green1,
    Blue1,

    LedCount
} LedColor;

const uint8_t led_ddr[LedCount] = {
    LED_2 | LED_1,
    LED_2 | LED_1,
    LED_2 | LED_0,
    LED_2 | LED_0,
    LED_1 | LED_0,
    LED_1 | LED_0,
};

const uint8_t led_port[LedCount] = {
    LED_2,
    LED_1,
    LED_2,
    LED_0,
    LED_0,
    LED_1
};

uint8_t ddr_a = 0;
uint8_t port_a = 0;
uint8_t ddr_b = 0;
uint8_t port_b = 0;

uint32_t get_time() {
    // get time base + timer offset (2 ticks per second)
    return time + TCNT1 / 2;
}

bool run = false;

void set_led_a(LedColor color, uint8_t value);
void set_led_b(LedColor color, uint8_t value);

ISR(TIM1_OVF_vect) {
    // increment time by 128 seconds (timer period)
    time += 128;

    // just for test
    // set_led_a((time/128) % LedCount, 120);
}

// start led a
ISR(TIM0_OVF_vect) {
    PORTB = port_a;
    DDRB = ddr_a;
}

// start led b
ISR(TIM0_COMPA_vect) {
    PORTB = port_b;
    DDRB = ddr_b;
}

// sw off all leds
ISR(TIM0_COMPB_vect) {
    PORTB = 0;
    DDRB = 0;
}

uint8_t a_value = 0;
uint8_t b_value = 0;

void set_led_a(LedColor color, uint8_t value) {
    if(value <= 10 && b_value <= 10) {
        TCCR0B = 0;
        return;
    } else {
        TCCR0B = (0 << CS02) | (0 << CS01) | (1 << CS00);
    }

    if(value > 120) value = 120;
    if(value < 10) value = 10;

    a_value = value;

    OCR0A = value;
    OCR0B = OCR0A + b_value;

    if(value > 10) {
        ddr_a = led_ddr[color];
        port_a = led_port[color];
    } else {
        ddr_a = 0;
        port_a = 0;
    }
}

void set_led_b(LedColor color, uint8_t value) {
    if(value <= 10 && a_value <= 10) {
        TCCR0B = 0;
        return;
    } else {
        TCCR0B = (0 << CS02) | (0 << CS01) | (1 << CS00);
    }

    if(value > 120) value = 120;
    if(value < 10) value = 10;

    b_value = value;
    OCR0B = OCR0A + b_value;

    if(value > 10) {
        ddr_b = led_ddr[color];
        port_b = led_port[color];
    } else {
        ddr_b = 0;
        port_b = 0;
    }
}

int main() {
    PLLCSR &= ~(1 << PCKE);
    TCCR1 |= (1 << CS13) | (0 << CS12) | (0 << CS11) | (0 << CS10);
    TCNT1 = 0;

    TCCR0A = 0x00;
    OCR0A = 220;
    TCNT0 = 0;

    TIMSK |= (1 << TOIE1) | (1 << TOIE0) | (1 << OCIE0A) | (1 << OCIE0B);

    // MCUCR = (1 << SE); // power-down mode

    sei();

    set_led_a(Green1, 120);
    set_led_b(Red0, 120);

    while(1) {
        set_led_a(Red0, 120);
        set_led_b(Blue1, 120);
        _delay_ms(100);
        set_led_a(Green0, 120);
        set_led_b(Red0, 120);
        _delay_ms(100);
        set_led_a(Blue0, 120);
        set_led_b(Green0, 120);
        _delay_ms(100);
        set_led_a(Yellow, 120);
        set_led_b(Blue0, 120);
        _delay_ms(100);
        set_led_a(Green1, 120);
        set_led_b(Yellow, 120);
        _delay_ms(100);
        set_led_a(Blue1, 120);
        set_led_b(Green1, 120);
        _delay_ms(100);

        /*set_led_a(Yellow, 120);
        set_led_b(Red0, 30);

        _delay_ms(500);

        set_led_a(Yellow, 30);
        set_led_b(Red0, 120);

        _delay_ms(500);

        set_led_a(Yellow, 30);
        set_led_b(Red0, 30);

        _delay_ms(500);*/
        // cli();

        /*_delay_ms(500);
        time++;
        uint8_t idx = time % LED_COUNT;
        OCR0B = idx;
        ddr = led_ddr[idx];
        port = led_port[idx];
        */

        // sei();
        // __asm("sleep");
    }

    return 0;
}
