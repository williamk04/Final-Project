idf_component_register(SRCS "Camera.c"
                    INCLUDE_DIRS "include"
                    REQUIRES esp_http_client Wifi esp32-camera json)
