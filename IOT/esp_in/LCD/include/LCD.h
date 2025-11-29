#ifndef LCD_H
#define LCD_H

#include <driver/i2c.h>
#include <driver/gpio.h>

#ifdef __cplusplus
extern "C" {
#endif

#define LCD_I2C_ADDRESS 0x27
#define LCD_WIDTH 16
#define LCD_HEIGHT 2

typedef struct{
    i2c_port_t i2c_port;
    gpio_num_t scl_pin;
    gpio_num_t sda_pin;
    uint8_t address;
    uint8_t cols;
    uint8_t rows;
}LCD_HandleTypeDef;

void LCD_Init(LCD_HandleTypeDef *lcd, i2c_port_t i2c_port, uint8_t address, uint8_t cols, uint8_t rows, gpio_num_t scl_pin, gpio_num_t sda_pin);
void LCD_Clear(LCD_HandleTypeDef *lcd);
void LCD_SetCursor(LCD_HandleTypeDef *lcd, uint8_t col, uint8_t row);
void LCD_SendString(LCD_HandleTypeDef *lcd, const char *str);
void LCD_SendChar(LCD_HandleTypeDef *lcd, char c);
void LCD_CreateChar(LCD_HandleTypeDef *lcd, uint8_t location, uint8_t charmap[]);
#ifdef __cplusplus
}
#endif
#endif // LCD_H
