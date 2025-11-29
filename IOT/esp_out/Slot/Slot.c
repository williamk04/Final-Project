#include "Slot.h"
#include "esp_log.h"
#include "esp_http_client.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <string.h>
#include <stdio.h>

static const char *TAG = "SLOT";

Slot_Typedef slots[SLOT_COUNT] = {
    {.name = "S1", .ir_pin = SLOT_1_IR_PIN, .status = false, .last_state = false},
    {.name = "S2", .ir_pin = SLOT_2_IR_PIN, .status = false, .last_state = false},
    {.name = "S3", .ir_pin = SLOT_3_IR_PIN, .status = false, .last_state = false},
    {.name = "S4", .ir_pin = SLOT_4_IR_PIN, .status = false, .last_state = false},
    {.name = "S5", .ir_pin = SLOT_5_IR_PIN, .status = false, .last_state = false},
    {.name = "S6", .ir_pin = SLOT_6_IR_PIN, .status = false, .last_state = false},
};

// ISR chỉ cập nhật trạng thái
static void IRAM_ATTR slot_isr_handler(void* arg){
    Slot_Typedef* slot = (Slot_Typedef*) arg;
    int ir_state = gpio_get_level(slot->ir_pin);
    slot->status = (ir_state == 0); // 0 = occupied, 1 = free
}

// Khởi tạo GPIO + ISR
void Slot_Init(void){
    uint64_t pin_mask = 0;
    for(int i=0;i<SLOT_COUNT;i++){
        pin_mask |= (1ULL << slots[i].ir_pin);
    }

    gpio_config_t io_conf = {
        .intr_type = GPIO_INTR_ANYEDGE,
        .mode = GPIO_MODE_INPUT,
        .pin_bit_mask = pin_mask,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .pull_up_en = GPIO_PULLUP_ENABLE,
    };
    gpio_config(&io_conf);
    gpio_install_isr_service(0);

    for(int i=0;i<SLOT_COUNT;i++){
        gpio_isr_handler_add(slots[i].ir_pin, slot_isr_handler, &slots[i]);
    }

    ESP_LOGI(TAG, "Slot GPIO initialized");
}

// Task loop kiểm tra thay đổi trạng thái & update Firebase
void Slot_Loop(void *arg){
    while(1){
        for(int i=0;i<SLOT_COUNT;i++){
            if(slots[i].status != slots[i].last_state){
                ESP_LOGI(TAG, "Slot %s changed: %d → %d", slots[i].name, slots[i].last_state, slots[i].status);
                slots[i].last_state = slots[i].status;
                Slot_UpdateFirebase(&slots[i]);
            }
        }
        vTaskDelay(pdMS_TO_TICKS(200));
    }
}

// Cập nhật Firebase Realtime Database
void Slot_UpdateFirebase(Slot_Typedef* slot){
    char url[256];
    sprintf(url, "https://firestore.googleapis.com/v1/projects/%s/databases/(default)/documents/parking-slots/%s?key=%s", PROJECT_ID, slot->name, API_KEY);

    char post_data[128];
    sprintf(post_data,
        "{ \"fields\": { \"status\": { \"stringValue\": \"%s\" } } }",
        slot->status ? "occupied" : "free");

    esp_http_client_config_t cfg = {
        .url = url,
        .method = HTTP_METHOD_PATCH,
        .timeout_ms = 5000
    };

    esp_http_client_handle_t client = esp_http_client_init(&cfg);
    esp_http_client_set_header(client, "Content-Type", "application/json");
    esp_http_client_set_post_field(client, post_data, strlen(post_data));

    esp_err_t err = esp_http_client_perform(client);
    if(err == ESP_OK){
        ESP_LOGI(TAG, "Updated slot %s → %s", slot->name, slot->status ? "occupied" : "free");
    } else {
        ESP_LOGE(TAG, "Failed to update slot %s: %s", slot->name, esp_err_to_name(err));
    }
    esp_http_client_cleanup(client);
}

