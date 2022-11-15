#include <stdbool.h>

#include <avr/io.h>

#define F_CPU 32768UL
// #define F_CPU 1000000UL
#include <util/delay.h>
#include <avr/interrupt.h>
#include <avr/wdt.h>

#include "pattern.c"

#define LED_0 (1<<PB0)
#define LED_1 (1<<PB1)
#define LED_2 (1<<PB2)

// #define RED_LEVEL OCR0A
// #define WHITE_LEVEL OCR0B

// #define IDLE_TIMEOUT 10

#define POWER_IDLE ~(1<<SM1)
#define POWER_DOWN (1<<SM1)

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

uint32_t SEED = 0xDEADBEEF;

#define ONE
// #define TWO

#ifdef ONE
// uint32_t MY_SEED = 0x1010;
uint32_t MY_SEED = 0x3588;
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
#endif

#ifdef TWO
uint32_t MY_SEED = 0x3588;
const uint8_t led_ddr[LedCount] = {
    LED_2 | LED_0, // red0
    LED_2 | LED_0, // green0
    LED_2 | LED_1, // blue0
    LED_2 | LED_1, // yellow
    LED_1 | LED_0, // green1
    LED_1 | LED_0, // blue1
};

const uint8_t led_port[LedCount] = {
    LED_2, // red0
    LED_0, // green0
    LED_1, // blue0
    LED_2, // yellow
    LED_0, // green1
    LED_1, // blue1
};
#endif


uint8_t ddr_a = 0;
uint8_t port_a = 0;
uint8_t ddr_b = 0;
uint8_t port_b = 0;

volatile uint32_t time = 0;
uint32_t get_time() {
    // get time base + timer offset (32 ticks per second)
    return time + TCNT1 / 32;
}

volatile bool run = false;
volatile uint32_t next_time = 0;

void set_led_a(LedColor color, uint8_t value);
void set_led_b(LedColor color, uint8_t value);

ISR(TIM1_OVF_vect) {
    // increment time by 128 seconds (timer period)
    time += 8;
    if(time >= next_time) {
        run = true;
    }
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

const uint8_t LOW_MARGIN = 4;
const uint8_t HIGH_MARGIN = 120;

void set_led_a(LedColor color, uint8_t value) {
    if(value > HIGH_MARGIN) value = HIGH_MARGIN;
    if(value < LOW_MARGIN) value = LOW_MARGIN;

    a_value = value;

    if(value <= LOW_MARGIN && b_value <= LOW_MARGIN) {
        TCCR0B = 0;
        PORTB = 0;
        DDRB = 0;
        return;
    } else {
        TCCR0B = (0 << CS02) | (0 << CS01) | (1 << CS00);
    }

    OCR0A = value;
    OCR0B = OCR0A + b_value;

    if(value > LOW_MARGIN) {
        ddr_a = led_ddr[color];
        port_a = led_port[color];
    } else {
        ddr_a = 0;
        port_a = 0;
    }
}

void set_led_b(LedColor color, uint8_t value) {
    if(value > HIGH_MARGIN) value = HIGH_MARGIN;
    if(value < LOW_MARGIN) value = LOW_MARGIN;

    b_value = value;

    if(value <= LOW_MARGIN && a_value <= LOW_MARGIN) {
        TCCR0B = 0;
        PORTB = 0;
        DDRB = 0;
        return;
    } else {
        TCCR0B = (0 << CS02) | (0 << CS01) | (1 << CS00);
    }

    OCR0B = OCR0A + b_value;

    if(value > LOW_MARGIN) {
        ddr_b = led_ddr[color];
        port_b = led_port[color];
    } else {
        ddr_b = 0;
        port_b = 0;
    }
}

const uint8_t HALF_DELAY = 16;

void blink(LedPair* pair, uint32_t timestep) {
    uint8_t blink_max = MAX(pair->a.value, pair->b.value);
    uint8_t step = timestep <= HALF_DELAY ? HALF_DELAY - timestep : 1;

    for(uint8_t i = LOW_MARGIN; i < blink_max; i += step) {
        uint8_t x = i;
        set_led_a(pair->a.color, MIN(x, pair->a.value));
        set_led_b(pair->b.color, MIN(x, pair->b.value));
        if(timestep > HALF_DELAY) {
            for(uint8_t t = 0; t < (timestep - HALF_DELAY); t++) {
                _delay_ms(1);
            }
        } else {
            _delay_ms(1);
        }
    }
    for(uint8_t i = 0; i < blink_max - LOW_MARGIN; i += step) {
        uint8_t x = blink_max - i;
        set_led_a(pair->a.color, MIN(x, pair->a.value));
        set_led_b(pair->b.color, MIN(x, pair->b.value));
        if(timestep > HALF_DELAY) {
            for(uint8_t t = 0; t < (timestep - HALF_DELAY); t++) {
                _delay_ms(1);
            }
        } else {
            _delay_ms(1);
        }
    }

    set_led_a(0, 0);
    set_led_b(0, 0);
}

int main() {
    PLLCSR &= ~(1 << PCKE);
    TCCR1 |= (1 << CS13) | (0 << CS12) | (1 << CS11) | (1 << CS10);
    TCNT1 = 0;

    TCCR0A = 0x00;
    OCR0A = 220;
    TCNT0 = 0;

    TIMSK |= (1 << TOIE1) | (1 << TOIE0) | (1 << OCIE0A) | (1 << OCIE0B);

    MCUCR = (1 << SE) | (0 << SM1) | (0 << SM0);
    PRR = (1 << PRUSI) | (1 << PRADC);

    sei();

    LedColor color_seq[] = {
        Red0,
        Green1,
        Yellow,
        Blue1,
        Blue0,
        Green0
    };

    set_led_a(Blue1, 0);
    set_led_b(Red0, 0);

    next_time = get_time() + 1;

    LedPair ancors[INTERPOLATION_SIZE];

    uint32_t global_random = SEED;

    TrackParam param;

    uint32_t sequence_counter = 0;

    while(1) {
        if(run) {
            global_random = lfsr_random(global_random);
            param.angle = global_random & 0xFF;

            global_random = lfsr_random(global_random);
            param.phase = global_random & 0xFF;

            global_random = lfsr_random(global_random);
            param.x = global_random & 0xFF;

            global_random = lfsr_random(global_random);
            param.y = global_random & 0xFF;

            global_random = lfsr_random(global_random);
            uint32_t sequence_random = global_random + MY_SEED;

            // set next time
            global_random = lfsr_random(global_random);
            next_time = get_time() + (60 + (global_random & (sequence_counter < 10 ? 63 : 4095)));
            uint32_t sequence_time = sequence_counter < 10 ? 60 : 600;
            sequence_counter++;

            global_random = lfsr_random(global_random);
            bool speed = global_random & 1;

            update_param(&param);

            create_ancors(ancors, &param);

            uint32_t sequence_begin_time = get_time();

            uint8_t steps = 0;

            while(get_time() - sequence_begin_time < sequence_time) {
                sequence_random = lfsr_random(sequence_random);
                steps += sequence_random & (speed ? 1 : 3);

                uint8_t interpolation_step = steps % INTERPOLATION_SIZE;

                sequence_random = lfsr_random(sequence_random);
                blink(&ancors[interpolation_step], sequence_random & (speed ? 7 : 31));

                sequence_random = lfsr_random(sequence_random);
                for(uint16_t i = 0; i < (sequence_random & (speed ? 31 : 512)); i++) {
                    _delay_ms(1);
                }
            }

            run = false;
        } else {
            DDRB = 0;
            PORTB = 0xFF;
            __asm("sleep");
        }

        /*
        set_led_a(Red0, 120);
        _delay_ms(100);
        set_led_a(Red0, 0);
        */

        /*for(uint8_t k = 0; k < 10; k++) {

            for(uint8_t t = 0; t < INTERPOLATION_SIZE; t++) {
                set_led_a(ancors[t].a.color, ancors[t].a.value);
                set_led_b(ancors[t].b.color, ancors[t].b.value);
                _delay_ms(100);
                // printf("[%d = %d, %d=%d], ", ancors[t].a.color, ancors[t].a.value, ancors[t].b.color, ancors[t].b.value);
            }
        }*/
        /*if(run) {
            set_led_a((get_time()/8) % LedCount, 120);
            _delay_ms(100);
            set_led_a(Red0, 0);
            set_led_b(Red0, 0);

            next_time = get_time() + 8;
            // run = false;
        } else {
            
        }
        */

        /*for(uint8_t color = 0; color < LedCount; color++) {
            uint8_t color_a = color % LedCount;
            uint8_t color_b = (color + 1) % LedCount;

            set_led_a(color_b, 120);
            set_led_b(color_b, 120);

            for(uint8_t i = 0; i < 120; i++) {
                // set_led_a(color_a, 120);
                // set_led_b(color_b, 120);
                _delay_ms(5);
            }
        }*/
        
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
