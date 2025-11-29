#include "LCD.h"

static void lcd_send_command(LCD_HandleTypeDef *lcd, uint8_t cmd)
{
    uint8_t data_u, data_l;
    uint8_t data_t[4];
    data_u = (cmd & 0xf0);
    data_l = ((cmd << 4) & 0xf0);
    data_t[0] = data_u | 0x0C; // En=1, Rs=0
    data_t[1] = data_u | 0x08; // En=0, Rs=0
    data_t[2] = data_l | 0x0C; // En=1, Rs=0
    data_t[3] = data_l | 0x08; // En=0, Rs=0
    i2c_master_write_to_device(lcd->i2c_port, lcd->address, data_t, 4, 1000 / portTICK_PERIOD_MS);
}

static void lcd_send_data(LCD_HandleTypeDef *lcd, uint8_t data)
{
    uint8_t data_u, data_l;
    uint8_t data_t[4];
    data_u = (data & 0xf0);
    data_l = ((data << 4) & 0xf0);
    data_t[0] = data_u | 0x0D; // En=1, Rs=1
    data_t[1] = data_u | 0x09; // En=0, Rs=1
    data_t[2] = data_l | 0x0D; // En=1, Rs=1
    data_t[3] = data_l | 0x09; // En=0, Rs=1
    i2c_master_write_to_device(lcd->i2c_port, lcd->address, data_t, 4, 1000 / portTICK_PERIOD_MS);
}

void LCD_Init(LCD_HandleTypeDef *lcd, i2c_port_t i2c_port, uint8_t address, uint8_t cols, uint8_t rows, gpio_num_t scl_pin, gpio_num_t sda_pin)
{
    lcd->i2c_port = i2c_port;
    lcd->address = address;
    lcd->cols = cols;
    lcd->rows = rows;

    i2c_config_t conf = {
        .mode = I2C_MODE_MASTER,
        .sda_io_num = sda_pin,
        .scl_io_num = scl_pin,
        .sda_pullup_en = GPIO_PULLUP_ENABLE,
        .scl_pullup_en = GPIO_PULLUP_ENABLE,
        .master.clk_speed = 100000,
    };
    i2c_param_config(i2c_port, &conf);
    i2c_driver_install(i2c_port, conf.mode, 0, 0, 0);
    vTaskDelay(50 / portTICK_PERIOD_MS);

    lcd_send_command(lcd, 0x30);
    vTaskDelay(5 / portTICK_PERIOD_MS);
    lcd_send_command(lcd, 0x30);
    vTaskDelay(1 / portTICK_PERIOD_MS);
    lcd_send_command(lcd, 0x30);
    vTaskDelay(10 / portTICK_PERIOD_MS);
    lcd_send_command(lcd, 0x20);
    vTaskDelay(10 / portTICK_PERIOD_MS);
    lcd_send_command(lcd, 0x28);
    vTaskDelay(1 / portTICK_PERIOD_MS);
    lcd_send_command(lcd, 0x08);
    vTaskDelay(1 / portTICK_PERIOD_MS);
    lcd_send_command(lcd, 0x01);
    vTaskDelay(2 / portTICK_PERIOD_MS);
    lcd_send_command(lcd, 0x06);
    vTaskDelay(1 / portTICK_PERIOD_MS);
    lcd_send_command(lcd, 0x0C);
    vTaskDelay(5 / portTICK_PERIOD_MS);
}

void LCD_Clear(LCD_HandleTypeDef *lcd)
{
    lcd_send_command(lcd, 0x01);
    vTaskDelay(2 / portTICK_PERIOD_MS);
}

void LCD_SetCursor(LCD_HandleTypeDef *lcd, uint8_t col, uint8_t row)
{
    uint8_t row_offsets[] = {0x00, 0x40, 0x14, 0x54};
    if (row >= lcd->rows) {
        row = lcd->rows - 1;
    }
    lcd_send_command(lcd, 0x80 | (col + row_offsets[row]));
}

void LCD_SendString(LCD_HandleTypeDef *lcd, const char *str)
{
    while (*str) {
        lcd_send_data(lcd, (uint8_t)(*str));
        str++;
    }
}

void LCD_SendChar(LCD_HandleTypeDef *lcd, char c)
{
    lcd_send_data(lcd, (uint8_t)c);
}

void LCD_CreateChar(LCD_HandleTypeDef *lcd, uint8_t location, uint8_t charmap[])
{
    location &= 0x7; // We only have 8 locations 0-7
    lcd_send_command(lcd, 0x40 | (location << 3));
    for (int i = 0; i < 8; i++) {
        lcd_send_data(lcd, charmap[i]);
    }
}