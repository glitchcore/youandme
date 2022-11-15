#include "pattern.c"
#include <stdio.h>

int main() {
    LedPair ancors[INTERPOLATION_SIZE];

    test_ancors(ancors);

    for(uint8_t t = 0; t < INTERPOLATION_SIZE; t++) {
        printf("[%d = %d, %d=%d], ", ancors[t].a.color, ancors[t].a.value, ancors[t].b.color, ancors[t].b.value);
    }

    return 0;
}