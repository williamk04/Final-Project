#ifndef SLOT_H
#define SLOT_H

#include <stdbool.h>
#include "driver/gpio.h"

// Firebase
#define API_KEY  "AIzaSyBlrUW3w3PLOx-FAer1_cJh9wNmrGR4yBk"
#define PROJECT_ID "parking-project-9830e"


// IR pins
#define SLOT_1_IR_PIN GPIO_NUM_34
#define SLOT_2_IR_PIN GPIO_NUM_35
#define SLOT_3_IR_PIN GPIO_NUM_32
#define SLOT_4_IR_PIN GPIO_NUM_33
#define SLOT_5_IR_PIN GPIO_NUM_25
#define SLOT_6_IR_PIN GPIO_NUM_26

#define SLOT_COUNT 6
#define DEBOUNCE_MS 50

typedef struct {
    char name[5];
    gpio_num_t ir_pin;
    bool status;       // hiện tại
    bool last_state;   // trạng thái trước để so sánh thay đổi
} Slot_Typedef;

// Khởi tạo GPIO & ISR cho tất cả slot
void Slot_Init(void);

// Task loop kiểm tra thay đổi & update Firebase
void Slot_Loop(void *arg);

// Cập nhật trạng thái slot lên Firebase
void Slot_UpdateFirebase(Slot_Typedef* slot);

#endif
