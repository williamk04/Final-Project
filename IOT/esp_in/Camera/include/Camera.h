#ifndef CAMERA_H
#define CAMERA_H

#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM     0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27

#define Y2_GPIO_NUM       5
#define Y3_GPIO_NUM       18
#define Y4_GPIO_NUM       19
#define Y5_GPIO_NUM       21
#define Y6_GPIO_NUM       36
#define Y7_GPIO_NUM       39
#define Y8_GPIO_NUM       34
#define Y9_GPIO_NUM       35

#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

typedef enum {
    VEHICLE_ERROR = 0,         // Không xác định
    VEHICLE_NORMAL_IN = 1,       // Xe vãng lai mới vào được
    VEHICLE_ALREADY_INSIDE = 2,  // Xe vãng lai đã ở bên trong bãi
    VEHICLE_RESERVED_IN = 3,     // Xe đặt chỗ và vào thành công
    REVERSED_CHECK_IN_EARLY = 4,    // Xe đặt chỗ vào quá sớm
    SLOT_REVERSED_NOT_FREE = 5
} vehicle_status_t;

extern char bien_so[20];
extern char slotID[3];

void camera_init(void);
vehicle_status_t capture_and_upload(void);
#endif // CAMERA_H