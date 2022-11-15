#include <stdint.h>
#include <stdbool.h>

#define MAX(a,b) ((a) > (b) ? (a) : (b))
#define MIN(a,b) ((a) < (b) ? (a) : (b))

const int16_t PHASE_DECIMATOR = 8;

uint32_t SEED = 0xDEADBEEF;
uint32_t lfsr_random(uint32_t prev) {
    // 13 ^ 7 ^ 3
    uint8_t increment = ((prev >> 3) & 1) ^ ((prev >> 7) & 1) ^ ((prev >> 13) & 1);
    prev = ((prev << 1) + increment) & 0xFFFFFFFF;
    return prev;
}

uint8_t SIN_TABLE[] = {127, 130, 133, 136, 139, 142, 145, 148, 151, 154, 157, 160, 163,
166, 169, 172, 175, 178, 181, 184, 186, 189, 192, 194, 197, 200, 202, 205, 207,
209, 212, 214, 216, 218, 221, 223, 225, 227, 229, 230, 232, 234, 235, 237, 239,
240, 241, 243, 244, 245, 246, 247, 248, 249, 250, 250, 251, 252, 252, 253, 253,
253, 253, 253, 254, 253, 253, 253, 253, 253, 252, 252, 251, 250, 250, 249, 248,
247, 246, 245, 244, 243, 241, 240, 239, 237, 235, 234, 232, 230, 229, 227, 225,
223, 221, 218, 216, 214, 212, 209, 207, 205, 202, 200, 197, 194, 192, 189, 186,
184, 181, 178, 175, 172, 169, 166, 163, 160, 157, 154, 151, 148, 145, 142, 139,
136, 133, 130, 127, 123, 120, 117, 114, 111, 108, 105, 102, 99, 96, 93, 90, 87,
84, 81, 78, 75, 72, 69, 67, 64, 61, 59, 56, 53, 51, 48, 46, 44, 41, 39, 37, 35,
32, 30, 28, 26, 24, 23, 21, 19, 18, 16, 14, 13, 12, 10, 9, 8, 7, 6, 5, 4, 3, 3,
2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 2, 3, 3, 4, 5, 6, 7, 8, 9, 10,
12, 13, 14, 16, 18, 19, 21, 23, 24, 26, 28, 30, 32, 35, 37, 39, 41, 44, 46, 48,
51, 53, 56, 59, 61, 64, 67, 69, 72, 75, 78, 81, 84, 87, 90, 93, 96, 99, 102,
105, 108, 111, 114, 117, 120, 123};

int16_t fastest_sin(uint16_t x) {
    return SIN_TABLE[x % 256] - 127;
}

int16_t fastest_cos(uint16_t x) {
    return fastest_sin(x + 64);
}

typedef struct {
    uint8_t angle;
    uint8_t a_x;
    uint8_t a_y;
    uint8_t x;
    uint8_t y;
    uint8_t phase;
    int8_t rot[4];
} TrackParam;

/*
class TrackParam:
    def __init__(self):
        self.angle = 50
        self.a_x = 0
        self.a_y = 0
        self.x = 127
        self.y = 127
        self.phase = 60
*/

void update_param(TrackParam* param) {
    param->rot[0] = fastest_cos(param->angle);
    param->rot[1] = -fastest_sin(param->angle);
    param->rot[2] = fastest_sin(param->angle);
    param->rot[3] = fastest_cos(param->angle);
}

void get_track_point(uint16_t p, TrackParam* param, int16_t* res_x, int16_t* res_y) {
    int16_t x = fastest_sin(p + param->phase / PHASE_DECIMATOR);
    int16_t y = fastest_sin(p);

    *res_x = param->rot[0] * x / 127 + param->rot[1] * y / 127 + param->x;
    *res_y = param->rot[2] * x / 127 + param->rot[3] * y / 127 + param->y;

    // printf("%d: (%d, %d) -> (%d, %d)\n", p, x, y, *res_x, *res_y);
}

int32_t euclid(int16_t* a, int16_t* b) {
    int32_t dx = a[0] - b[0];
    int32_t dy = a[1] - b[1];
    uint32_t res = dx * dx + dy * dy;

    // printf("%d %d -> %d\n", dx, dy, res);
    return res;
}

int16_t LED_POSITIONS[6][2] = {
    {255, 128}, {191, 237}, {64, 237}, {1, 128}, {64, 18}, {191, 18}
};

typedef struct {
    uint8_t color;
    uint8_t value;
} Led;

typedef struct {
    Led a;
    Led b;
} LedPair;

void find_led_pair(uint8_t* led_value, LedPair* pair) {
    pair->a.value = 0;
    pair->a.color = 0;
    pair->b.value = 0;
    pair->b.color = 0;

    for(uint8_t i = 0; i < 6; i++) {
        // printf("%d ", led_value[i]);
        if(led_value[i] > pair->a.value) {
            pair->b.value = pair->a.value;
            pair->b.color = pair->a.color;

            pair->a.value = led_value[i];
            pair->a.color = i;
        } else if (led_value[i] > pair->b.value) {
            pair->b.value = led_value[i];
            pair->b.color = i;
        }
    }
}

const uint8_t INTERPOLATION_SIZE = 16;

void create_ancors(LedPair* ancors, TrackParam* param) {
    /*
    global_random = lfsr_random(global_random);
    delay_seed = global_random
    global_random = lfsr_random(global_random);
    next_delay = global_random
    */

    
    for(uint8_t t = 0; t < INTERPOLATION_SIZE; t++) {
        uint8_t led_value[6];
        for(uint8_t i = 0; i < 6; i++){
            int16_t track_point[2];
            get_track_point(t * 255 / INTERPOLATION_SIZE, param, &track_point[0], &track_point[1]);
            int16_t dist = (10000 - euclid(track_point, LED_POSITIONS[i]))/64;

            led_value[i] = MAX(0, MIN(120, dist));
        }

        find_led_pair(led_value, &ancors[t]);
    }
}
