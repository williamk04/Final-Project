#include "Camera.h"
#include "esp_camera.h"
#include "esp_http_client.h"
#include "esp_log.h"
#include "Wifi.h"
#include "cJSON.h"
#include <stdlib.h>
#include <string.h>

static const char *TAG = "CAMERA";
#define SERVER_URL "http://192.168.1.100:5000/upload"

char bien_so[20] = {0};
char slotID[3] = {0};

void camera_init(void)
{
    camera_config_t config = {
        .ledc_channel = LEDC_CHANNEL_0,
        .ledc_timer = LEDC_TIMER_0,
        .pin_d0 = Y2_GPIO_NUM,
        .pin_d1 = Y3_GPIO_NUM,
        .pin_d2 = Y4_GPIO_NUM,
        .pin_d3 = Y5_GPIO_NUM,
        .pin_d4 = Y6_GPIO_NUM,
        .pin_d5 = Y7_GPIO_NUM,
        .pin_d6 = Y8_GPIO_NUM,
        .pin_d7 = Y9_GPIO_NUM,
        .pin_xclk = XCLK_GPIO_NUM,
        .pin_pclk = PCLK_GPIO_NUM,
        .pin_vsync = VSYNC_GPIO_NUM,
        .pin_href = HREF_GPIO_NUM,
        .pin_sscb_sda = SIOD_GPIO_NUM,
        .pin_sscb_scl = SIOC_GPIO_NUM,
        .pin_pwdn = PWDN_GPIO_NUM,
        .pin_reset = RESET_GPIO_NUM,
        .xclk_freq_hz = 20000000,
        .pixel_format = PIXFORMAT_JPEG,
        .frame_size = FRAMESIZE_VGA,
        .jpeg_quality = 10,
        .fb_count = 1};

    esp_err_t err = esp_camera_init(&config);
    if (err != ESP_OK)
    {
        ESP_LOGE(TAG, "Camera init failed: %s", esp_err_to_name(err));
    }
    else
    {
        ESP_LOGI(TAG, "Camera initialized");
    }
}

/* Parse JSON Server */
static vehicle_status_t handle_server_response(const char *resp)
{
    if (!resp)
        return VEHICLE_ERROR;

    cJSON *root = cJSON_Parse(resp);
    if (!root)
    {
        ESP_LOGE(TAG, "JSON parse failed");
        return VEHICLE_ERROR;
    }
    // Get Vehicle Plate Text
    cJSON *detected_plate = cJSON_GetObjectItem(root, "detected_plate");
    if (detected_plate && cJSON_IsObject(detected_plate))
    {
        cJSON *plate_txt = cJSON_GetObjectItem(detected_plate, "text");
        if (plate_txt && cJSON_IsString(plate_txt))
        {
            strncpy(bien_so, plate_txt->valuestring, sizeof(bien_so) - 1);
        }
        else
        {
            strcpy(bien_so, "UNKNOWN");
        }
    }
    else
    {
        strcpy(bien_so, "UNKNOWN");
    }

    // Get firebase_record array
    cJSON *firebase_record = cJSON_GetObjectItem(root, "firebase_record");
    if (!firebase_record || !cJSON_IsArray(firebase_record))
    {
        cJSON_Delete(root);
        return VEHICLE_ERROR;
    }
    int arr_size = cJSON_GetArraySize(firebase_record);
    if (arr_size == 0)
    {
        cJSON_Delete(root);
        return VEHICLE_ERROR;
    }
    cJSON *record_obj = cJSON_GetArrayItem(firebase_record, 0);
    cJSON *message_obj = cJSON_GetArrayItem(firebase_record, 1);

    // Case: New vehicle in
    if (record_obj && cJSON_IsObject(record_obj))
    {
        cJSON *slot_id = cJSON_GetObjectItem(record_obj, "slotId");
        if (slot_id && cJSON_IsString(slot_id))
        {
            strncpy(slotID, slot_id->valuestring, sizeof(slotID) - 1);
        }
        else
        {
            strcpy(slotID, "-");
        }
        cJSON *is_reserved = cJSON_GetObjectItem(record_obj, "is_reserved");
        bool reserved = (is_reserved && cJSON_IsBool(is_reserved) && cJSON_IsTrue(is_reserved));

        if (reserved)
        {
            cJSON_Delete(root);
            return VEHICLE_RESERVED_IN; // Reserved vehicle in
        }
        else
        {
            cJSON_Delete(root);
            return VEHICLE_NORMAL_IN; // Normal vehicle in
        }
    }

    // Case: Already inside or too early to check in
    if (!record_obj && message_obj && cJSON_IsString(message_obj))
    {
        const char *msg = message_obj->valuestring;
        if (strcmp(msg, "Vehicle already inside") == 0)
        {
            cJSON_Delete(root);
            return VEHICLE_ALREADY_INSIDE;
        }
        if (strcmp(msg, "Too early to check in") == 0)
        {
            cJSON_Delete(root);
            return REVERSED_CHECK_IN_EARLY;
        }
        if(strcmp(msg, "no free slots") == 0)
        {
            cJSON_Delete(root);
            return SLOT_REVERSED_NOT_FREE;
        }
    }

    // Other cases: error
    cJSON_Delete(root);
    return VEHICLE_ERROR;
}

/*
 * Upload image and read full response robustly (handles missing content-length)
 * Returns allocated response string in *out_resp (caller must free) on success.
 */
static esp_err_t upload_image_and_get_response(const uint8_t *img, size_t img_len, char **out_resp)
{
    if (!img || img_len == 0 || !out_resp)
        return ESP_ERR_INVALID_ARG;
    *out_resp = NULL;

    esp_http_client_config_t config = {
        .url = SERVER_URL,
        .method = HTTP_METHOD_POST,
        .timeout_ms = 20000};

    esp_http_client_handle_t client = esp_http_client_init(&config);
    if (!client)
    {
        ESP_LOGE(TAG, "http client init failed");
        return ESP_FAIL;
    }

    esp_http_client_set_header(client, "Content-Type", "image/jpeg");
    esp_http_client_set_post_field(client, (const char *)img, img_len);

    esp_err_t err = esp_http_client_perform(client);
    if (err != ESP_OK)
    {
        ESP_LOGE(TAG, "HTTP POST failed: %s", esp_err_to_name(err));
        esp_http_client_cleanup(client);
        return err;
    }

    int status = esp_http_client_get_status_code(client);
    if (status != 200) {
        ESP_LOGE(TAG, "Server returned status %d", status);
        esp_http_client_cleanup(client);
        return ESP_FAIL;
    }
    ESP_LOGI(TAG, "HTTP status = %d", status);

    // read response: handle both content-length present or absent
    int content_len = esp_http_client_get_content_length(client);
    if (content_len > 0)
    {
        char *buf = malloc(content_len + 1);
        if (!buf)
        {
            ESP_LOGE(TAG, "No memory for response buffer");
            esp_http_client_cleanup(client);
            return ESP_ERR_NO_MEM;
        }
        int read_len = esp_http_client_read(client, buf, content_len);
        if (read_len <= 0)
        {
            ESP_LOGW(TAG, "Failed to read response body");
            free(buf);
            esp_http_client_cleanup(client);
            return ESP_FAIL;
        }
        buf[read_len] = '\0';
        *out_resp = buf;
        esp_http_client_cleanup(client);
        return ESP_OK;
    }
    else
    {
        // fallback: read in chunks until no more data (or up to a max)
        const size_t CHUNK = 1024;
        size_t cap = CHUNK;
        char *buf = malloc(cap);
        if (!buf)
        {
            ESP_LOGE(TAG, "No memory for response chunk");
            esp_http_client_cleanup(client);
            return ESP_ERR_NO_MEM;
        }
        size_t len_total = 0;
        while (1)
        {
            int r = esp_http_client_read(client, buf + len_total, CHUNK);
            if (r > 0)
            {
                len_total += r;
                // expand if needed
                if (len_total + CHUNK > cap)
                {
                    char *tmp = realloc(buf, cap + CHUNK);
                    if (!tmp)
                    {
                        ESP_LOGE(TAG, "realloc failed");
                        free(buf);
                        esp_http_client_cleanup(client);
                        return ESP_ERR_NO_MEM;
                    }
                    buf = tmp;
                    cap += CHUNK;
                }
                continue;
            }
            else
            {
                if (r < 0)
                {
                    ESP_LOGW(TAG, "Read returned %d", r);
                }
                break;
            }
        }
        char *final = realloc(buf, len_total + 1);
        if (!final)
        {
            buf[len_total] = '\0';
            *out_resp = buf;
        }
        else
        {
            final[len_total] = '\0';
            *out_resp = final;
        }
        esp_http_client_cleanup(client);
        return (len_total > 0) ? ESP_OK : ESP_FAIL;
    }
}

/*
 * capture_and_upload:
 * - returns vehicle_status_t for caller decision.
 */
vehicle_status_t capture_and_upload(void)
{
    if (!wifi_is_connected())
    {
        ESP_LOGE(TAG, "WiFi not connected");
        return VEHICLE_ERROR;
    }

    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb)
    {
        ESP_LOGE(TAG, "Camera capture failed");
        return VEHICLE_ERROR;
    }

    char *resp = NULL;
    esp_err_t r = upload_image_and_get_response(fb->buf, fb->len, &resp);

    // ensure we always return frame buffer
    esp_camera_fb_return(fb);

    if (r != ESP_OK)
    {
        ESP_LOGE(TAG, "Upload failed");
        if (resp)
            free(resp);
        return VEHICLE_ERROR;
    }

    ESP_LOGI(TAG, "Server response: %s", resp ? resp : "<empty>");

    vehicle_status_t vs = handle_server_response(resp);
    free(resp);
    return vs;
}
