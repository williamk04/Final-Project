#include "LCD.h"
#include "Wifi.h"
#include "Camera.h"
#include "Servo.h"
#include "esp_timer.h"
#include "driver/uart.h"
#include <string.h>

#define IR_SENSOR_PIN GPIO_NUM_4
#define ESP_OUT_REVERSED_PIN GPIO_NUM_5
#define ESP_OUT_NORMAL_PIN GPIO_NUM_18
#define SERVO_OPEN_ANGLE 90.0f
#define SERVO_CLOSE_ANGLE 0

#define UART_RX_PIN GPIO_NUM_16
#define UART_TX_PIN GPIO_NUM_17
#define UART_BUF_SIZE 256

const uint8_t TOTAL_SLOTS_NORMAL = 3;
const uint8_t TOTAL_SLOTS_RESERVED = 3;

LCD_HandleTypeDef lcd;
Servo_Typedef servo;

/* --- Flags IR --- */
static bool flag_detected = false;
static bool flag_cplt = false;
static bool waiting_close = false;
static bool car_out = false;
static bool no_car_out = false;

static uint32_t close_start_tick = 0;
const uint32_t CLOSE_DELAY_MS = 2000;

/* --- Bộ đếm --- */
static volatile uint8_t count_vang_lai = 0;
static volatile uint8_t count_dat_cho = 0;

/* --- Debounce xe ra --- */
volatile uint64_t last_rev_us = 0;
volatile uint64_t last_norm_us = 0;

char uart_data[UART_BUF_SIZE] = {0};
char buffer_out[20];

static void IRAM_ATTR IR_Handler(void *arg)
{
    int level = gpio_get_level(IR_SENSOR_PIN);

    if (level == 0)
    {
        flag_detected = true;
        flag_cplt = false;
        gpio_set_intr_type(IR_SENSOR_PIN, GPIO_INTR_HIGH_LEVEL);
    }
    else
    {
        flag_cplt = true;
        flag_detected = false;
        gpio_set_intr_type(IR_SENSOR_PIN, GPIO_INTR_LOW_LEVEL);
    }
}

void barrier_open() { Servo_SetAngle(&servo, SERVO_OPEN_ANGLE); }
void barrier_close() { Servo_SetAngle(&servo, SERVO_CLOSE_ANGLE); }

void LCD_ShowIdle(LCD_HandleTypeDef *lcd)
{
    LCD_Clear(lcd);

    char buf[20];

    sprintf(buf, "Normal Em: %d/%d", TOTAL_SLOTS_NORMAL - count_vang_lai, TOTAL_SLOTS_NORMAL);

    LCD_SetCursor(lcd, 0, 0);
    LCD_SendString(lcd, buf);

    sprintf(buf, "Reversed Em: %d/%d", TOTAL_SLOTS_RESERVED - count_dat_cho, TOTAL_SLOTS_RESERVED);
    LCD_SetCursor(lcd, 0, 1);
    LCD_SendString(lcd, buf);
}

void uart_in_gate_init()
{
    const uart_config_t cfg = {
        .baud_rate = 115200,
        .data_bits = UART_DATA_8_BITS,
        .parity = UART_PARITY_DISABLE,
        .stop_bits = UART_STOP_BITS_1,
        .flow_ctrl = UART_HW_FLOWCTRL_DISABLE};

    uart_param_config(UART_NUM_1, &cfg);
    uart_set_pin(UART_NUM_1, UART_TX_PIN, UART_RX_PIN, UART_PIN_NO_CHANGE, UART_PIN_NO_CHANGE);
    uart_driver_install(UART_NUM_1, UART_BUF_SIZE, 0, 0, NULL, 0);
}

void uart_handle(void)
{
    char *argv[2];
    char *token = strtok(uart_data, " ");
    int i = 0;
    while (token != NULL)
    {
        argv[i++] = token;
        token = strtok(NULL, " ");
    }
    if (strcmp(argv[0], "NORMAL") == 0)
    {
        car_out = true;
        if (count_vang_lai > 0)
            count_vang_lai--;
    }
    else if (strcmp(argv[0], "RESERVED") == 0)
    {
        car_out = true;
        if (count_dat_cho > 0)
            count_dat_cho--;
    }
    else if (strcmp(argv[0], "NO_CAR") == 0)
    {
        no_car_out = true;
        return;
    }
    sprintf(buffer_out, "%s OUT", argv[1]);
}

void app_main(void)
{
    LCD_Init(&lcd, I2C_NUM_0, 0x27, 16, 2, GPIO_NUM_22, GPIO_NUM_21);
    LCD_Clear(&lcd);
    LCD_SendString(&lcd, "Car Parking Sys");
    vTaskDelay(1000 / portTICK_PERIOD_MS);

    LCD_Clear(&lcd);
    LCD_SendString(&lcd, "Connecting WiFi");

    wifi_init();
    vTaskDelay(2000 / portTICK_PERIOD_MS);

    LCD_Clear(&lcd);
    if (wifi_is_connected())
        LCD_SendString(&lcd, "WiFi Connected");
    else
        LCD_SendString(&lcd, "WiFi Failed!!!");
    vTaskDelay(1000 / portTICK_PERIOD_MS);
    camera_init();
    Servo_Init(&servo, SERVO_TIMER, SERVO_CHANNEL, SERVO_GPIO);
    barrier_close();

    gpio_config_t io_conf = {
        .intr_type = GPIO_INTR_LOW_LEVEL,
        .mode = GPIO_MODE_INPUT,
        .pin_bit_mask = (1ULL << IR_SENSOR_PIN),
        .pull_up_en = GPIO_PULLUP_ENABLE};
    gpio_config(&io_conf);
    gpio_install_isr_service(0);
    gpio_isr_handler_add(IR_SENSOR_PIN, IR_Handler, NULL);

    LCD_ShowIdle(&lcd);

    while (1)
    {
        /* XE VỪA XUẤT HIỆN (IR LOW) */
        int len = uart_read_bytes(UART_NUM_1, (uint8_t *)uart_data, sizeof(uart_data) - 1, 100 / portTICK_PERIOD_MS);
        if (len > 0)
        {
            if (uart_data[len - 1] == '\n')
            {
                uart_data[len - 1] = '\0';
                uart_handle();
            }
        }
        if (car_out)
        {
            LCD_SetCursor(&lcd, 0, 1);
            LCD_SendString(&lcd, buffer_out);
            car_out = false;
        }
        if (no_car_out)
        {
            LCD_SetCursor(&lcd, 0, 1);
            LCD_SendString(&lcd, "                 ");
            no_car_out = false;
        }
        if (flag_detected)
        {
            flag_detected = false;

            LCD_SetCursor(&lcd, 0, 0);
            LCD_SendString(&lcd, "Capturing...    ");

            vehicle_status_t st = capture_and_upload();

            LCD_SetCursor(&lcd, 0, 0);

            switch (st)
            {
            case VEHICLE_RESERVED_IN:
                if (count_dat_cho >= TOTAL_SLOTS_RESERVED)
                {
                    LCD_SendString(&lcd, "  Reserved Full ");
                    barrier_close();
                    break;
                }
                count_dat_cho++;
                LCD_SendString(&lcd, bien_so);
                LCD_SendString(&lcd, " IN");
                barrier_open();
                break;

            case VEHICLE_NORMAL_IN:
                if (count_vang_lai >= TOTAL_SLOTS_NORMAL)
                {
                    LCD_SendString(&lcd, "   Normal Full  ");
                    barrier_close();
                    break;
                }
                count_vang_lai++;
                LCD_SendString(&lcd, bien_so);
                LCD_SendString(&lcd, " IN");
                barrier_open();
                break;

            case VEHICLE_ALREADY_INSIDE:
                LCD_SendString(&lcd, bien_so);
                LCD_SendString(&lcd, " Inside ");
                barrier_close();
                break;
            case REVERSED_CHECK_IN_EARLY:
                LCD_SendString(&lcd, bien_so);
                LCD_SendString(&lcd, " Early");
                barrier_close();
                break;
            case SLOT_REVERSED_NOT_FREE:
                LCD_SendString(&lcd, "YOUR SLOT NOT FREE");
                barrier_close();
                break;
            default:
                LCD_SendString(&lcd, " Server Error!!!");
                barrier_close();
                break;
            }
        }

        /* XE ĐÃ ĐI QUA BARIE (IR HIGH) */
        if (flag_cplt)
        {
            flag_cplt = false;
            close_start_tick = xTaskGetTickCount();
            waiting_close = true;
        }

        /* AUTO CLOSE */
        if (waiting_close && ((xTaskGetTickCount() - close_start_tick) * portTICK_PERIOD_MS >= CLOSE_DELAY_MS))
        {
            barrier_close();
            waiting_close = false;
        }

        /* IDLE DISPLAY */
        if (!flag_detected && !flag_cplt && !waiting_close && !car_out)
        {
            LCD_ShowIdle(&lcd);
        }

        vTaskDelay(5 / portTICK_PERIOD_MS);
    }
}
