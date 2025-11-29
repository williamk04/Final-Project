#include "Wifi.h"
#include "Servo.h"
#include "Camera.h"
#include "driver/uart.h"
#include <string.h>
#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "Slot.h"

#define IR_SENSOR_PIN 2
#define FIRE_SENSOR_PIN 4
#define RELAY_PIN 15

Servo_Typedef servo;

void Uart_Init(void);
void GPIO_Init(void);

static volatile bool flag_detected = false;
static volatile bool flag_cplt = false;
uint32_t close_start_tick = 0;
static bool waiting_close = false;

char uart_buffer[128];
void transmit_normal_out(void)
{
    sprintf(uart_buffer, "NORMAL_OUT %s\n", bien_so);
    uart_write_bytes(UART_NUM_0, (void *)uart_buffer, strlen(uart_buffer));
}

void transmit_reserved_out(void)
{
    sprintf(uart_buffer, "RESERVED_OUT %s\n", bien_so);
    uart_write_bytes(UART_NUM_0, (void *)uart_buffer, strlen(uart_buffer));
}

void transmit_error(void)
{
    uart_write_bytes(UART_NUM_0, (void *)"ERROR\n", 6);
}

void transmit_no_car_out(void){
    uart_write_bytes(UART_NUM_0, (void *)"NO_CAR_OUT\n", 11);
}

void IRAM_ATTR IR_Handler(void *arg)
{
    int ir_state = gpio_get_level(IR_SENSOR_PIN);
    if (ir_state == 0)
    {
        flag_detected = true;
        flag_cplt = false;
        gpio_set_intr_type(IR_SENSOR_PIN, GPIO_INTR_HIGH_LEVEL);
    }
    else
    {
        flag_cplt = true;
        gpio_set_intr_type(IR_SENSOR_PIN, GPIO_INTR_LOW_LEVEL);
    }
}

void IRAM_ATTR Fire_Handler(void *arg)
{
    int fire_state = gpio_get_level(FIRE_SENSOR_PIN);
    if (fire_state == 0)
    {
        // Activate relay on fire detected
        gpio_set_level(RELAY_PIN, 0);
    }
    else
    {
        // Deactivate relay when fire is cleared
        gpio_set_level(RELAY_PIN, 1);
    }
}

void app_main(void)
{
    Uart_Init();
    GPIO_Init();
    wifi_init();
    camera_init();
    Servo_Init(&servo, SERVO_TIMER, SERVO_CHANNEL, SERVO_GPIO);
    Slot_Init();
    xTaskCreate(Slot_Loop, "slot_loop", 4096, NULL, 5, NULL);

    while (1)
    {
        if (flag_detected)
        {
            flag_detected = false;
            vehicle_status_t status = capture_and_upload();
            switch (status)
            {
            case VEHICLE_NORMAL_OUT:
                transmit_normal_out();
                Servo_SetAngle(&servo, 90.0);
                break;
            case VEHICLE_RESERVED_OUT:
                transmit_reserved_out();
                Servo_SetAngle(&servo, 90.0);
                break;
            case VEHICLE_ERROR:
                transmit_error();
                break;
            default:
                break;
            }
        }
        if (flag_cplt)
        {
            flag_cplt = false;
            close_start_tick = xTaskGetTickCount();
            waiting_close = true;
        }
        if (waiting_close)
        {
            if ((xTaskGetTickCount() - close_start_tick) >= pdMS_TO_TICKS(2000))
            {
                Servo_SetAngle(&servo, 0.0);
                transmit_no_car_out();
                waiting_close = false;
            }
        }
        vTaskDelay(5 / portTICK_PERIOD_MS);
    }
}

void Uart_Init()
{
    const uart_config_t uart_config = {
        .baud_rate = 115200,
        .data_bits = UART_DATA_8_BITS,
        .parity = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE};
    uart_param_config(UART_NUM_0, &uart_config);
    uart_driver_install(UART_NUM_0, 1024 * 2, 0, 0, NULL, 0);
}

void GPIO_Init()
{
    const gpio_config_t io_conf = {
        .intr_type = GPIO_INTR_LOW_LEVEL,
        .mode = GPIO_MODE_INPUT,
        .pin_bit_mask = (1ULL << IR_SENSOR_PIN) | (1ULL << FIRE_SENSOR_PIN),
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .pull_up_en = GPIO_PULLUP_DISABLE};
    gpio_config(&io_conf);
    gpio_install_isr_service(0);
    gpio_isr_handler_add(IR_SENSOR_PIN, IR_Handler, NULL);

    const gpio_config_t relay_conf = {
        .intr_type = GPIO_INTR_DISABLE,
        .mode = GPIO_MODE_OUTPUT,
        .pin_bit_mask = (1ULL << RELAY_PIN),
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .pull_up_en = GPIO_PULLUP_DISABLE};
    gpio_config(&relay_conf);
    gpio_set_level(RELAY_PIN, 1);
}